"""Exercise a live but silent player using local audio, without network or speakers."""

import os
import shutil
import subprocess
import threading
import time
import unittest
from unittest.mock import patch

from pybonsai import radio


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffplay"), "FFmpeg is required")
class RadioStallIntegrationTests(unittest.TestCase):
    def test_alive_player_with_stalled_audio_is_restarted(self):
        sample = subprocess.check_output([
            "ffmpeg", "-v", "error", "-f", "lavfi",
            "-i", "sine=frequency=440:sample_rate=44100",
            "-t", "6", "-f", "mp3", "pipe:1",
        ], timeout=10)
        finished = threading.Event()
        players, monitors, feeders, terminated_alive = [], [], [], []
        original_popen = subprocess.Popen
        original_monitor = radio._AudioMonitor
        original_terminate = radio._terminate_process

        def feed(pipe, stall):
            try:
                while not finished.is_set():
                    pipe.write(sample)
                    pipe.flush()
                    if stall:
                        # Keep the input open: ffplay cannot detect EOF, and its
                        # master clock may continue while audio decoding stops.
                        finished.wait()
                        break
            except (OSError, ValueError):
                pass

        def spawn(command, **kwargs):
            # Replace only the network input with a controlled local producer.
            command = command[:command.index("-rw_timeout")] + ["-i", "pipe:0"]
            kwargs["stdin"] = subprocess.PIPE
            kwargs["env"] = {**os.environ, "SDL_AUDIODRIVER": "dummy"}
            player = original_popen(command, **kwargs)
            players.append(player)
            feeder = threading.Thread(
                target=feed, args=(player.stdin, len(players) == 1), daemon=True
            )
            feeder.start()
            feeders.append(feeder)
            return player

        def monitor(stderr):
            result = original_monitor(stderr)
            monitors.append(result)
            return result

        def terminate(player, **kwargs):
            if player is not None and player.poll() is None:
                terminated_alive.append(player.pid)
            return original_terminate(player, **kwargs)

        session = radio._RadioSession("https://test.invalid/live.mp3", 0)
        with patch.object(radio, "streamlink", None), patch.object(
            radio.subprocess, "Popen", side_effect=spawn
        ), patch.object(radio, "_AudioMonitor", side_effect=monitor), patch.object(
            radio, "_terminate_process", side_effect=terminate
        ), patch.object(radio, "AUDIO_STALL_TIMEOUT", 1), patch.object(
            radio, "STABLE_PLAYBACK_SECONDS", 0.2
        ):
            session.thread.start()
            try:
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    if len(monitors) >= 2 and monitors[1].last_frame_at is not None:
                        if monitors[1].last_frame_at - monitors[1].first_frame_at >= 0.5:
                            break
                    time.sleep(0.05)
                self.assertEqual(len(players), 2, session.warning)
                self.assertIsNotNone(monitors[0].last_frame_at)
                self.assertIn(players[0].pid, terminated_alive)
                self.assertIsNotNone(monitors[1].last_frame_at)
                self.assertIsNone(session.warning)
            finally:
                finished.set()
                session.stop_event.set()
                session.thread.join(5)
                for feeder in feeders:
                    feeder.join(2)

        self.assertFalse(session.thread.is_alive())
        self.assertTrue(all(player.poll() is not None for player in players))
        self.assertTrue(all(not monitor.thread.is_alive() for monitor in monitors))
        self.assertTrue(all(not feeder.is_alive() for feeder in feeders))


if __name__ == "__main__":
    unittest.main()
