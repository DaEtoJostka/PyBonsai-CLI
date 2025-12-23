import subprocess
import shutil

DEFAULT_LOFI_URL = "https://listen.reyfm.de/lofi_320kbps.mp3"

_radio_process = None


def start_radio(url=None, volume=50):
    """Starts the Lo-Fi radio stream using ffplay in the background."""
    global _radio_process

    if _radio_process is not None:
        return  # Already running

    if not shutil.which("ffplay"):
        print(
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
    except Exception as e:
        print(f"Warning: Could not start radio: {e}")


def stop_radio():
    """Stops the radio stream if it's running."""
    global _radio_process
    if _radio_process is not None:
        _radio_process.terminate()
        _radio_process.wait()
        _radio_process = None
