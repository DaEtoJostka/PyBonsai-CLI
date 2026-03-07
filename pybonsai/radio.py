import logging
import os
import signal
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from .errors import RadioError

try:
    import streamlink
except ImportError:
    streamlink = None


DEFAULT_LOFI_URL = "https://www.youtube.com/watch?v=jfKfPfyJRdk"
DEFAULT_MEDIEVAL_URL = "https://www.youtube.com/watch?v=IxPANmjPaek"
DEFAULT_CLASSIC_URL = "https://www.youtube.com/watch?v=jXAEIWcGXwE"
DEFAULT_SYNTHWAVE_URL = "https://www.youtube.com/watch?v=4xDzrJKXOOY"
DEFAULT_SAD_URL = "https://www.youtube.com/watch?v=P6Segk8cr-c"
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
        aliases=("classical",),
        requires_streamlink=True,
    ),
    "medieval": RadioStation(
        url=DEFAULT_MEDIEVAL_URL,
        help="play a medieval music stream in the terminal",
        aliases=("medieval",),
        requires_streamlink=True,
    ),
    "synthwave": RadioStation(
        url=DEFAULT_SYNTHWAVE_URL,
        help="play a synthwave music stream in the terminal",
        aliases=("synthwave",),
        requires_streamlink=True,
    ),
    "sad": RadioStation(
        url=DEFAULT_SAD_URL,
        help="play a sad music stream in the terminal",
        aliases=("sad",),
        requires_streamlink=True,
    ),
    "jazz": RadioStation(
        url=DEFAULT_JAZZ_URL,
        help="play a jazz music stream in the terminal",
        aliases=("jazz",),
        requires_streamlink=True,
    ),
}

RADIO_ALIASES = {
    alias: preset_name
    for preset_name, preset in RADIO_PRESETS.items()
    for alias in (preset_name, *preset.aliases)
}


_radio_process = None
_radio_source_process = None
_radio_thread = None
_radio_stream = None
_radio_stop_event = threading.Event()
_streamlink_logging_configured = False


def normalise_station_name(station_name: Optional[str]) -> Optional[str]:
    if station_name is None:
        return None

    normalised = station_name.strip().lower()
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
    global _radio_process, _radio_source_process

    if _radio_process is not None and _radio_process.poll() is not None:
        _radio_process = None
        _radio_source_process = None

    if _radio_process is not None:
        return None

    if not shutil.which("ffplay"):
        return (
            "Warning: 'ffplay' not found. Cannot play radio. Install FFmpeg to enable this feature."
        )

    stream_url = url or resolve_station_url(DEFAULT_RADIO_PRESET)
    ffplay_volume = max(0, min(100, volume))

    if _requires_ytdlp(stream_url):
        yt_dlp_command = _resolve_ytdlp_command()
        if yt_dlp_command is None:
            return (
                "Warning: 'yt-dlp' not found. Install it to play YouTube live "
                "streams reliably."
            )
        return _start_ytdlp_radio(yt_dlp_command, stream_url, ffplay_volume)

    if _requires_streamlink(stream_url) and streamlink is None:
        return (
            "Warning: 'streamlink' not found. Install it to play YouTube and other "
            "web-based radio streams."
        )

    if streamlink is not None:
        stream = _resolve_stream(stream_url)
        if stream is not None:
            direct_stream_url = _stream_to_url(stream)
            if direct_stream_url is not None:
                return _start_direct_radio(direct_stream_url, ffplay_volume)
            return _start_streamlink_radio(stream, ffplay_volume)

    return _start_direct_radio(stream_url, ffplay_volume)


def stop_radio():
    """Stop the radio stream if it is running."""
    global _radio_process, _radio_source_process, _radio_thread, _radio_stream

    _radio_stop_event.set()

    if _radio_stream is not None:
        try:
            _radio_stream.close()
        except (OSError, ValueError):
            pass
        _radio_stream = None

    if _radio_process is not None:
        if _radio_process.stdin is not None:
            try:
                _radio_process.stdin.close()
            except (OSError, ValueError):
                pass
        try:
            if _radio_process.poll() is None:
                _radio_process.terminate()
                try:
                    _radio_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    _radio_process.kill()
                    _radio_process.wait()
            else:
                _radio_process.wait()
        except ProcessLookupError:
            pass
        _radio_process = None

    if _radio_source_process is not None:
        try:
            if _radio_source_process.poll() is None:
                os.killpg(_radio_source_process.pid, signal.SIGTERM)
                try:
                    _radio_source_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(_radio_source_process.pid, signal.SIGKILL)
                    _radio_source_process.wait()
            else:
                _radio_source_process.wait()
        except ProcessLookupError:
            pass
        _radio_source_process = None

    if _radio_thread is not None:
        _radio_thread.join(timeout=2)
        _radio_thread = None

    _radio_stop_event.clear()


def _resolve_stream(stream_url):
    _configure_streamlink_logging()
    session = streamlink.Streamlink()

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


def _start_direct_radio(stream_url, volume):
    global _radio_process

    try:
        _radio_process = subprocess.Popen(
            [
                "ffplay",
                "-vn",
                "-nodisp",
                "-loglevel",
                "quiet",
                "-volume",
                str(volume),
                stream_url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        raise RadioError(f"Could not start radio: {exc}") from exc

    return None


def _start_ytdlp_radio(yt_dlp_command, stream_url, volume):
    global _radio_process, _radio_source_process

    try:
        _radio_source_process = subprocess.Popen(
            [
                yt_dlp_command,
                "-q",
                "--no-warnings",
                "-f",
                YTDLP_PREFERRED_FORMAT,
                "-o",
                "-",
                stream_url,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        raise RadioError(f"Could not start yt-dlp: {exc}") from exc

    if _radio_source_process.stdout is None:
        _radio_source_process.terminate()
        _radio_source_process = None
        raise RadioError("yt-dlp did not expose a stdout pipe for playback.")

    try:
        _radio_process = subprocess.Popen(
            [
                "ffplay",
                "-vn",
                "-nodisp",
                "-loglevel",
                "quiet",
                "-volume",
                str(volume),
                "-i",
                "pipe:0",
            ],
            stdin=_radio_source_process.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        try:
            os.killpg(_radio_source_process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        _radio_source_process = None
        raise RadioError(f"Could not start radio: {exc}") from exc

    _radio_source_process.stdout.close()
    return None


def _start_streamlink_radio(stream, volume):
    global _radio_process, _radio_thread, _radio_stream

    try:
        _radio_stream = stream.open()
    except Exception as exc:
        raise RadioError(f"Could not open radio stream: {exc}") from exc

    try:
        _radio_process = subprocess.Popen(
            [
                "ffplay",
                "-vn",
                "-nodisp",
                "-loglevel",
                "quiet",
                "-volume",
                str(volume),
                "-i",
                "pipe:0",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        try:
            _radio_stream.close()
        except (OSError, ValueError):
            pass
        _radio_stream = None
        raise RadioError(f"Could not start radio: {exc}") from exc

    _radio_stop_event.clear()
    _radio_thread = threading.Thread(
        target=_pipe_stream_to_ffplay,
        args=(_radio_stream, _radio_process.stdin),
        daemon=True,
        name="pybonsai-radio",
    )
    _radio_thread.start()
    return None


def _pipe_stream_to_ffplay(stream_fd, ffplay_stdin):
    try:
        while not _radio_stop_event.is_set():
            data = stream_fd.read(STREAM_CHUNK_SIZE)
            if not data:
                break
            if ffplay_stdin is None:
                break
            ffplay_stdin.write(data)
    except (BrokenPipeError, OSError, ValueError):
        pass
    finally:
        try:
            stream_fd.close()
        except (OSError, ValueError):
            pass

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
