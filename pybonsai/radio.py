import logging
import os
import re
import signal
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from .errors import RadioError

try:
    import streamlink
except ImportError:
    streamlink = None


DEFAULT_LOFI_URL = "https://www.youtube.com/watch?v=rFZHOHl-L8A"
DEFAULT_MEDIEVAL_URL = "https://www.youtube.com/watch?v=IxPANmjPaek"
DEFAULT_CLASSIC_URL = "https://www.youtube.com/watch?v=jXAEIWcGXwE"
DEFAULT_SYNTHWAVE_URL = "https://www.youtube.com/watch?v=4xDzrJKXOOY"
DEFAULT_SAD_URL = "https://www.youtube.com/watch?v=CwPCy1GLS38"
DEFAULT_JAZZ_URL = "https://www.youtube.com/watch?v=A8jDx9TLMQc"
DEFAULT_RADIO_PRESET = "lofi"
STREAM_CHUNK_SIZE = 4096
STREAMLINK_LOGGER_NAME = "streamlink"
STREAMLINK_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
STREAMLINK_PREFERRED_STREAMS = (
    "audio_opus",
    "audio_vorbis",
    "audio_mp4a",
    "audio_aac",
    "audio",
    "best",
)
YTDLP_PREFERRED_FORMAT = "93/91/92/94/95/96/bestaudio/best"
NETWORK_TIMEOUT = 15
RESOLVE_TIMEOUT = 60
RADIO_POLL_INTERVAL = 0.25
RETRY_DELAY = 1
MAX_RETRY_DELAY = 30
STABLE_PLAYBACK_SECONDS = 30
AUDIO_START_TIMEOUT = 45
AUDIO_STALL_TIMEOUT = 15
AUDIO_FRAME_PATTERN = re.compile(
    r"\[[^\]]*ashowinfo[^\]]*\]\s+n:\s*\d+\b.*\bnb_samples:\s*[1-9]\d*\b"
)


@dataclass(frozen=True)
class RadioStation:
    url: str
    help: str
    aliases: Tuple[str, ...] = ()
    requires_streamlink: bool = False
    short_flag: Optional[str] = None


RADIO_PRESETS: Dict[str, RadioStation] = {
    "lofi": RadioStation(
        url=DEFAULT_LOFI_URL,
        help="play the default Lo-Fi radio stream in the terminal",
        short_flag="-R",
    ),
    "classical": RadioStation(
        url=DEFAULT_CLASSIC_URL,
        help="play a classical radio stream in the terminal",
        aliases=("0",),
        requires_streamlink=True,
    ),
    "medieval": RadioStation(
        url=DEFAULT_MEDIEVAL_URL,
        help="play a medieval music stream in the terminal",
        aliases=("1",),
        requires_streamlink=True,
    ),
    "synthwave": RadioStation(
        url=DEFAULT_SYNTHWAVE_URL,
        help="play a synthwave music stream in the terminal",
        aliases=("2",),
        requires_streamlink=True,
    ),
    "sad": RadioStation(
        url=DEFAULT_SAD_URL,
        help="play a sad music stream in the terminal",
        aliases=("3",),
        requires_streamlink=True,
    ),
    "jazz": RadioStation(
        url=DEFAULT_JAZZ_URL,
        help="play a jazz music stream in the terminal",
        aliases=("4",),
        requires_streamlink=True,
    ),
}

RADIO_ALIASES = {
    alias: preset_name
    for preset_name, preset in RADIO_PRESETS.items()
    for alias in (preset_name, *preset.aliases)
}


_radio_session = None
_streamlink_logging_configured = False


def normalise_station_name(station_name: Optional[str]) -> Optional[str]:
    if station_name is None:
        return None

    normalised = str(station_name).strip().lower()
    try:
        return RADIO_ALIASES[normalised]
    except KeyError as exc:
        raise RadioError(
            f"Unknown radio preset: {station_name}. Available: {describe_presets()}"
        ) from exc


def describe_presets() -> str:
    preset_descriptions = []
    for preset_name, preset in RADIO_PRESETS.items():
        details = []
        if preset_name == DEFAULT_RADIO_PRESET:
            details.append("default")

        aliases = tuple(alias for alias in preset.aliases if alias != preset_name)
        if aliases:
            details.append(f"alias: {', '.join(aliases)}")

        if details:
            preset_descriptions.append(f"{preset_name} ({'; '.join(details)})")
        else:
            preset_descriptions.append(preset_name)

    return ", ".join(preset_descriptions)


def resolve_station_url(station_name: Optional[str]) -> Optional[str]:
    station_name = normalise_station_name(station_name)
    if station_name is None:
        return None

    try:
        return RADIO_PRESETS[station_name].url
    except KeyError as exc:
        raise RadioError(f"Unknown radio station preset: {station_name}") from exc


def start_radio(url=None, volume=50):
    """Start radio playback and return a warning message when unavailable."""
    global _radio_session

    if _radio_session is not None and _radio_session.thread.is_alive():
        return None

    if not shutil.which("ffplay"):
        return (
            "Warning: 'ffplay' not found. Cannot play radio. Install FFmpeg to enable this feature."
        )

    stream_url = url or resolve_station_url(DEFAULT_RADIO_PRESET)
    ffplay_volume = max(0, min(100, volume))
    yt_dlp_command = None

    if _requires_ytdlp(stream_url):
        if sys.version_info < (3, 10):
            return "Warning: YouTube radio requires Python 3.10 or newer."
        yt_dlp_command = _resolve_ytdlp_command()
        if yt_dlp_command is None:
            return (
                "Warning: 'yt-dlp' not found. Install it to play YouTube live "
                "streams reliably."
            )
        try:
            _ytdlp_js_runtime_args()
        except RadioError as exc:
            return f"Warning: {exc}"
    elif _requires_streamlink(stream_url) and streamlink is None:
        return (
            "Warning: 'streamlink' not found. Install it to play YouTube and other "
            "web-based radio streams."
        )

    _radio_session = _RadioSession(stream_url, ffplay_volume, yt_dlp_command)
    _radio_session.thread.start()
    return None


def stop_radio():
    """Stop playback and return the last unresolved error, if any."""
    global _radio_session

    session, _radio_session = _radio_session, None
    if session is None:
        return None

    # Never clear this event: an old worker must not restart after a new session.
    session.stop_event.set()
    session.thread.join(timeout=5)
    return session.warning


def _resolve_stream(stream_url):
    _configure_streamlink_logging()
    session = streamlink.Streamlink()
    session.set_option("http-timeout", NETWORK_TIMEOUT)
    session.set_option("stream-timeout", NETWORK_TIMEOUT)

    try:
        streams = session.streams(stream_url)
    except Exception as exc:
        if _requires_streamlink(stream_url):
            raise RadioError(f"Could not resolve radio stream: {exc}") from exc
        return None

    if not streams:
        return None

    for stream_name in STREAMLINK_PREFERRED_STREAMS:
        if stream_name in streams:
            return streams[stream_name]

    audio_streams = [
        stream for stream_name, stream in streams.items() if stream_name.startswith("audio")
    ]
    if audio_streams:
        return audio_streams[0]

    return next(iter(streams.values()))


def _stream_to_url(stream):
    if hasattr(stream, "to_manifest_url"):
        try:
            return stream.to_manifest_url()
        except Exception:
            pass

    if not hasattr(stream, "to_url"):
        return None

    try:
        return stream.to_url()
    except Exception:
        return None


class _AudioMonitor:
    """Watch decoded audio frames, even when ffplay and its connection stay alive."""

    def __init__(self, stderr):
        self.stderr = stderr
        self.started_at = time.monotonic()
        self.first_frame_at = None
        self.last_frame_at = None
        self.last_error = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(
            target=self._read, daemon=True, name="pybonsai-radio-monitor"
        )

    def _read(self):
        try:
            while True:
                # Drain diagnostics continuously; frame reports must never fill
                # the pipe or accumulate in an ever-growing log file.
                line = self.stderr.readline(8192)
                if not line:
                    break
                self.record(line.decode(errors="replace"))
        except (OSError, ValueError):
            pass

    def record(self, line):
        if AUDIO_FRAME_PATTERN.search(line):
            now = time.monotonic()
            with self.lock:
                if self.first_frame_at is None:
                    self.first_frame_at = now
                self.last_frame_at = now
        elif any(word in line.lower() for word in (
            "error", "failed", "invalid", "could not", "unable",
            "timed out", "not found", "refused", "denied",
        )):
            with self.lock:
                self.last_error = _error_detail(line)

    def check(self, now):
        with self.lock:
            first, last, detail = self.first_frame_at, self.last_frame_at, self.last_error
        if last is None:
            if now - self.started_at < AUDIO_START_TIMEOUT:
                return False
            message = "Radio did not produce audio before the startup timeout."
        elif now - last >= AUDIO_STALL_TIMEOUT:
            message = f"Radio stopped decoding audio for {AUDIO_STALL_TIMEOUT:g} seconds."
        else:
            # Process uptime or an advancing playback clock does not prove that
            # audio is arriving. Only decoded frames can clear an earlier error.
            return last - first >= STABLE_PLAYBACK_SECONDS
        if detail:
            message = f"{message} {detail}"
        raise RadioError(message)


class _RadioSession:
    """Own one playback worker and its cancellation event across reconnects."""

    def __init__(self, stream_url, volume, yt_dlp_command=None):
        self.stream_url = stream_url
        self.volume = volume
        self.yt_dlp_command = yt_dlp_command
        self.stop_event = threading.Event()
        self.warning = None
        self.retry_delay = RETRY_DELAY
        self.thread = threading.Thread(
            target=self._run, daemon=True, name="pybonsai-radio"
        )

    def _run(self):
        while not self.stop_event.is_set():
            try:
                self._play_once()
            except (RadioError, OSError) as exc:
                if not self.stop_event.is_set():
                    self.warning = f"Warning: {exc}"

            if self.stop_event.wait(self.retry_delay):
                break
            self.retry_delay = min(self.retry_delay * 2, MAX_RETRY_DELAY)

    def _play_once(self):
        stream_url = self.stream_url
        stream_fd = None
        player = None
        monitor = None
        pipe_thread = None
        pipe_stop = threading.Event()
        last_data = [time.monotonic()]

        try:
            if self.yt_dlp_command is not None:
                # Resolve again on every reconnect; YouTube media URLs expire.
                stream_url = _resolve_ytdlp_url(
                    self.yt_dlp_command, stream_url, self.stop_event
                )
            elif streamlink is not None:
                stream = _resolve_stream(stream_url)
                if stream is not None:
                    stream_url = _stream_to_url(stream)
                    if stream_url is None and not self.stop_event.is_set():
                        try:
                            stream_fd = stream.open()
                        except Exception as exc:
                            raise RadioError(f"Could not open radio stream: {exc}") from exc

            if self.stop_event.is_set():
                return

            player = subprocess.Popen(
                _ffplay_command(stream_url if stream_fd is None else "pipe:0", self.volume),
                stdin=subprocess.DEVNULL if stream_fd is None else subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            monitor = _AudioMonitor(player.stderr)
            monitor.thread.start()
            last_data[0] = time.monotonic()
            if stream_fd is not None:
                pipe_thread = threading.Thread(
                    target=_pipe_stream_to_ffplay,
                    args=(stream_fd, player.stdin, pipe_stop, last_data),
                    daemon=True,
                    name="pybonsai-radio-pipe",
                )
                pipe_thread.start()

            while not self.stop_event.wait(RADIO_POLL_INTERVAL):
                returncode = player.poll()
                if returncode is not None:
                    monitor.thread.join(timeout=1)
                    raise RadioError(
                        monitor.last_error or f"Radio stream ended (player exit {returncode})."
                    )
                now = time.monotonic()
                if stream_fd is not None and now - last_data[0] >= RESOLVE_TIMEOUT:
                    raise RadioError("Radio stream stopped sending audio.")
                if monitor.check(now):
                    self.warning = None
                    self.retry_delay = RETRY_DELAY
        finally:
            pipe_stop.set()
            _terminate_process(player)
            if monitor is not None:
                monitor.thread.join(timeout=1)
            if player is not None and player.stderr is not None:
                player.stderr.close()
            if stream_fd is not None:
                try:
                    stream_fd.close()
                except (OSError, ValueError):
                    pass
            if pipe_thread is not None:
                pipe_thread.join(timeout=1)
            if player is not None and player.stdin is not None:
                try:
                    player.stdin.close()
                except (OSError, ValueError):
                    pass


def _resolve_ytdlp_url(yt_dlp_command, stream_url, stop_event):
    """Resolve a media URL without piping a long-running downloader into ffplay."""
    command = [
        yt_dlp_command,
        "--ignore-config",
        "--no-playlist",
        "--no-colors",
        *_ytdlp_js_runtime_args(),
        "--socket-timeout", str(NETWORK_TIMEOUT),
        "--retries", "2",
        "--extractor-retries", "2",
        "--get-url",
        "-f", YTDLP_PREFERRED_FORMAT,
        stream_url,
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    deadline = time.monotonic() + RESOLVE_TIMEOUT
    try:
        while not stop_event.is_set():
            try:
                stdout, stderr = process.communicate(timeout=RADIO_POLL_INTERVAL)
                break
            except subprocess.TimeoutExpired:
                if time.monotonic() >= deadline:
                    raise RadioError("Timed out resolving the YouTube radio stream.")
        else:
            return None

        if "No supported JavaScript runtime could be found" in stderr:
            raise RadioError(
                "YouTube radio needs a supported Deno or Node.js runtime and "
                "yt-dlp's JavaScript components. Update 'yt-dlp[default]' and "
                "install Deno 2.3+ or Node.js 22+ on PATH."
            )
        if "no such option: --js-runtimes" in stderr:
            raise RadioError("yt-dlp is too old. Update 'yt-dlp[default]' to play YouTube radio.")
        if process.returncode:
            detail = _error_detail(stderr)
            raise RadioError(detail or "yt-dlp could not resolve the YouTube radio stream.")
        urls = stdout.strip().splitlines()
        if len(urls) != 1 or urlparse(urls[0]).scheme not in {"http", "https"}:
            raise RadioError("yt-dlp did not return a playable radio stream URL.")
        return urls[0]
    finally:
        _terminate_process(process, process_group=True)
        process.stdout.close()
        process.stderr.close()


def _ffplay_command(stream_url, volume):
    command = [
        "ffplay", "-vn", "-nodisp", "-autoexit", "-nostats",
        "-loglevel", "info", "-af", "ashowinfo", "-volume", str(volume),
    ]
    parsed = urlparse(stream_url)
    if parsed.scheme in {"http", "https"}:
        command.extend([
            "-rw_timeout", str(NETWORK_TIMEOUT * 1_000_000),
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_on_network_error", "1",
            "-reconnect_on_http_error", "429,5xx",
            "-reconnect_delay_max", "5",
        ])
        if ".m3u8" in parsed.path.lower():
            # Bound stale-playlist reloads so the worker can get a fresh URL.
            # Do not use reconnect_at_eof: EOF is normal for each HLS segment.
            command.extend(["-max_reload", "5", "-m3u8_hold_counters", "5"])
    return command + ["-i", stream_url]


def _terminate_process(process, process_group=False):
    if process is None:
        return
    use_group = process_group and os.name == "posix"
    try:
        if use_group:
            # A resolver can leave a JavaScript child behind even if it exited.
            os.killpg(process.pid, signal.SIGTERM)
        elif process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            if use_group:
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait(timeout=2)
    except ProcessLookupError:
        process.wait(timeout=2)
    finally:
        if use_group:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def _error_detail(stderr):
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return None
    errors = [line for line in lines if "error" in line.lower()]
    detail = (errors or lines)[-1]
    return re.sub(r"https?://\S+", "<stream URL>", detail)[:500]


def _pipe_stream_to_ffplay(stream_fd, ffplay_stdin, stop_event, last_data):
    try:
        while not stop_event.is_set():
            data = stream_fd.read(STREAM_CHUNK_SIZE)
            if not data or ffplay_stdin is None:
                break
            last_data[0] = time.monotonic()
            ffplay_stdin.write(data)
            ffplay_stdin.flush()
    except (BrokenPipeError, OSError, ValueError):
        pass
    finally:
        if ffplay_stdin is not None:
            try:
                ffplay_stdin.close()
            except (OSError, ValueError):
                pass


def _requires_streamlink(stream_url: str) -> bool:
    parsed = urlparse(stream_url)
    host = parsed.netloc.lower()
    if host in STREAMLINK_HOSTS:
        return True

    return any(
        station.requires_streamlink and station.url == stream_url
        for station in RADIO_PRESETS.values()
    )


def _requires_ytdlp(stream_url: str) -> bool:
    parsed = urlparse(stream_url)
    return parsed.netloc.lower() in STREAMLINK_HOSTS


def _resolve_ytdlp_command():
    python_executable = Path(sys.executable)
    local_candidates = (
        python_executable.with_name("yt-dlp"),
        python_executable.with_name("yt_dlp"),
    )

    for candidate in local_candidates:
        if candidate.exists():
            return str(candidate)

    return shutil.which("yt-dlp")


def _ytdlp_js_runtime_args():
    # yt-dlp only enables Deno by default. An installed Node must be enabled
    # explicitly; otherwise extraction can fall back to a short-lived stream.
    args = []
    for runtime in ("deno", "node"):
        executable = shutil.which(runtime)
        if executable:
            args.extend(["--js-runtimes", f"{runtime}:{executable}"])
    if not args:
        raise RadioError(
            "YouTube radio needs Deno 2.3+ or Node.js 22+ on PATH. "
            "Install either runtime, then restart PyBonsai."
        )
    return args


def _configure_streamlink_logging():
    global _streamlink_logging_configured

    if _streamlink_logging_configured:
        return

    logger = logging.getLogger(STREAMLINK_LOGGER_NAME)
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    logger.setLevel(logging.CRITICAL)
    _streamlink_logging_configured = True
