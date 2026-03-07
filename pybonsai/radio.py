import subprocess
import shutil

from .errors import RadioError

DEFAULT_LOFI_URL = "https://listen.reyfm.de/lofi_320kbps.mp3"

_radio_process = None


def start_radio(url=None, volume=50):
    """Start the Lo-Fi stream and return a warning message when unavailable."""
    global _radio_process

    if _radio_process is not None:
        return None

    if not shutil.which("ffplay"):
        return (
            "Warning: 'ffplay' not found. Cannot play radio. Install FFmpeg to enable this feature."
        )
        return

    stream_url = url or DEFAULT_LOFI_URL
    # Volume in ffplay is 0-100
    ffplay_volume = max(0, min(100, volume))

    try:
        _radio_process = subprocess.Popen(
            [
                "ffplay",
                "-nodisp",  # No video display
                "-loglevel",
                "quiet",  # Suppress output
                "-volume",
                str(ffplay_volume),
                stream_url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        raise RadioError(f"Could not start radio: {exc}") from exc

    return None


def stop_radio():
    """Stops the radio stream if it's running."""
    global _radio_process
    if _radio_process is not None:
        _radio_process.terminate()
        _radio_process.wait()
        _radio_process = None
