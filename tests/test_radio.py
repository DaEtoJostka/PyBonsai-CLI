import io
import subprocess
import threading
import unittest
from unittest.mock import Mock, patch

from pybonsai import radio
from pybonsai.errors import RadioError


class RadioRecoveryTests(unittest.TestCase):
    def tearDown(self):
        radio.stop_radio()

    def test_player_exit_resolves_a_fresh_youtube_url_and_restarts(self):
        second_playing = threading.Event()
        first_player = Mock(stdin=None, stderr=io.BytesIO())
        first_player.poll.return_value = 0
        second_player = Mock(stdin=None, stderr=io.BytesIO())

        def playing():
            second_playing.set()
            return None

        second_player.poll.side_effect = playing
        session = radio._RadioSession(radio.DEFAULT_SYNTHWAVE_URL, 37, "yt-dlp")
        session.retry_delay = 0.01
        with patch.object(radio, "RADIO_POLL_INTERVAL", 0.01), patch.object(
            radio, "_resolve_ytdlp_url",
            side_effect=["https://example.com/old.m3u8", "https://example.com/new.m3u8"],
        ) as resolve, patch.object(
            radio.subprocess, "Popen", side_effect=[first_player, second_player]
        ) as popen, patch.object(radio, "_terminate_process") as terminate:
            session.thread.start()
            try:
                self.assertTrue(second_playing.wait(2), "Radio did not reconnect")
            finally:
                session.stop_event.set()
                session.thread.join(2)

        self.assertFalse(session.thread.is_alive())
        self.assertEqual(resolve.call_count, 2)
        self.assertEqual(popen.call_args_list[0].args[0][-1], "https://example.com/old.m3u8")
        self.assertEqual(popen.call_args_list[1].args[0][-1], "https://example.com/new.m3u8")
        self.assertIn("37", popen.call_args.args[0])
        self.assertEqual(terminate.call_args_list[-1].args, (second_player,))
        terminate.assert_any_call(first_player)

    def test_repeated_failures_back_off_and_keep_diagnostic(self):
        session = radio._RadioSession("https://example.com/radio", 50)
        session.stop_event = Mock()
        session.stop_event.is_set.return_value = False
        session.stop_event.wait.side_effect = [False] * 6 + [True]
        with patch.object(session, "_play_once", side_effect=RadioError("HTTP 403")):
            session._run()

        self.assertEqual(
            [call.args[0] for call in session.stop_event.wait.call_args_list],
            [1, 2, 4, 8, 16, 30, 30],
        )
        self.assertIn("HTTP 403", session.warning)

    def test_stop_during_retry_does_not_restart(self):
        failed = threading.Event()
        session = radio._RadioSession("https://example.com/radio", 50)
        session.retry_delay = 30

        def fail():
            failed.set()
            raise RadioError("Station unavailable")

        with patch.object(session, "_play_once", side_effect=fail) as play:
            radio._radio_session = session
            session.thread.start()
            self.assertTrue(failed.wait(2))
            radio.stop_radio()

        self.assertFalse(session.thread.is_alive())
        self.assertTrue(session.stop_event.is_set())
        self.assertEqual(play.call_count, 1)
        self.assertIsNone(radio._radio_session)

    def test_stop_during_resolution_never_starts_player(self):
        session = radio._RadioSession(radio.DEFAULT_SYNTHWAVE_URL, 50, "yt-dlp")

        def resolve(*args):
            session.stop_event.set()
            return None

        with patch.object(radio, "_resolve_ytdlp_url", side_effect=resolve), patch.object(
            radio.subprocess, "Popen"
        ) as popen:
            session._play_once()

        popen.assert_not_called()

    def test_start_during_retry_keeps_single_session(self):
        session = Mock()
        session.thread.is_alive.return_value = True
        radio._radio_session = session
        with patch.object(radio, "_RadioSession") as session_class:
            self.assertIsNone(radio.start_radio(radio.DEFAULT_SYNTHWAVE_URL))
        session_class.assert_not_called()

    def test_successful_recovery_clears_old_error_and_backoff(self):
        session = radio._RadioSession("https://example.com/radio", 50)
        session.warning = "Old error"
        session.retry_delay = 30
        session.stop_event = Mock()
        session.stop_event.is_set.return_value = False
        session.stop_event.wait.side_effect = [False, True]
        player = Mock(stdin=None, stderr=io.BytesIO())
        player.poll.return_value = None
        with patch.object(radio, "streamlink", None), patch.object(
            radio._AudioMonitor, "check", return_value=True
        ), patch.object(radio.subprocess, "Popen", return_value=player), patch.object(
            radio, "_terminate_process"
        ):
            session._play_once()
        self.assertIsNone(session.warning)
        self.assertEqual(session.retry_delay, radio.RETRY_DELAY)

    def test_living_player_without_audio_does_not_clear_error(self):
        session = radio._RadioSession("https://example.com/radio", 50)
        session.warning = "Previous failure"
        session.retry_delay = 30
        session.stop_event = Mock()
        session.stop_event.is_set.return_value = False
        session.stop_event.wait.side_effect = [False, True]
        player = Mock(stdin=None, stderr=io.BytesIO())
        player.poll.return_value = None
        with patch.object(radio, "streamlink", None), patch.object(
            radio, "STABLE_PLAYBACK_SECONDS", 0
        ), patch.object(radio.subprocess, "Popen", return_value=player), patch.object(
            radio, "_terminate_process"
        ):
            session._play_once()
        self.assertEqual(session.warning, "Previous failure")
        self.assertEqual(session.retry_delay, 30)


class AudioMonitorTests(unittest.TestCase):
    FRAME = (
        "[Parsed_ashowinfo_0 @ 0x123] n:5 pts:10240 pts_time:0.2322 "
        "fmt:fltp channels:2 chlayout:stereo rate:44100 "
        "nb_samples:1024 checksum:00000000\n"
    )

    def make_monitor(self):
        with patch.object(radio.time, "monotonic", return_value=0):
            return radio._AudioMonitor(io.BytesIO())

    def test_missing_frames_timeout_even_with_network_and_clock_activity(self):
        monitor = self.make_monitor()
        monitor.record("[https @ 0x123] Opening 'https://example.com/live' for reading\n")
        monitor.record("  250.00 M-A:  0.000 fd=0 aq=0KB vq=0KB\r")
        self.assertFalse(monitor.check(radio.AUDIO_START_TIMEOUT - 1))
        with self.assertRaisesRegex(RadioError, "startup timeout"):
            monitor.check(radio.AUDIO_START_TIMEOUT)

    def test_stalled_audio_is_detected_before_process_exits(self):
        monitor = self.make_monitor()
        with patch.object(radio.time, "monotonic", return_value=1):
            monitor.record(self.FRAME)
        monitor.record("[https @ 0x123] HTTP error 403 Forbidden https://example.com/token\n")
        with self.assertRaisesRegex(RadioError, "stopped decoding audio.*403") as context:
            monitor.check(1 + radio.AUDIO_STALL_TIMEOUT)
        self.assertNotIn("https://example.com/token", str(context.exception))

    def test_silent_audio_frames_are_valid_progress(self):
        monitor = self.make_monitor()
        for timestamp in (1, 10, 20, 31):
            with patch.object(radio.time, "monotonic", return_value=timestamp):
                monitor.record(self.FRAME)
            self.assertEqual(monitor.check(timestamp), timestamp >= 31)
        self.assertEqual(monitor.last_frame_at, 31)

    def test_empty_frames_and_unrelated_logs_do_not_count_as_audio(self):
        monitor = self.make_monitor()
        monitor.record(self.FRAME.replace("nb_samples:1024", "nb_samples:0"))
        monitor.record("-af ashowinfo\n")
        monitor.record("Input #0: audio stream\n")
        self.assertIsNone(monitor.last_frame_at)

    def test_startup_wait_does_not_count_as_stable_playback(self):
        monitor = self.make_monitor()
        with patch.object(radio.time, "monotonic", return_value=40):
            monitor.record(self.FRAME)
        self.assertFalse(monitor.check(41))

    def test_reader_drains_frames_without_storing_the_log(self):
        monitor = self.make_monitor()
        monitor.stderr = io.BytesIO((self.FRAME * 5000).encode())
        with patch.object(radio.time, "monotonic", return_value=1):
            monitor.thread.start()
            monitor.thread.join(2)
        self.assertFalse(monitor.thread.is_alive())
        self.assertEqual(monitor.last_frame_at, 1)
        self.assertIsNone(monitor.last_error)


class RadioResolverTests(unittest.TestCase):
    def setUp(self):
        runtime_args = patch.object(
            radio, "_ytdlp_js_runtime_args",
            return_value=["--js-runtimes", "node:/test/node"],
        )
        runtime_args.start()
        self.addCleanup(runtime_args.stop)

    def make_process(self, stdout="", stderr="", returncode=0):
        process = Mock(stdout=io.StringIO(), stderr=io.StringIO())
        process.returncode = returncode
        process.communicate.return_value = (stdout, stderr)
        return process

    def test_unavailable_station_reports_source_error(self):
        process = self.make_process(stderr="ERROR: This live stream is unavailable.\n", returncode=1)
        with patch.object(radio.subprocess, "Popen", return_value=process), patch.object(
            radio, "_terminate_process"
        ) as terminate:
            with self.assertRaisesRegex(RadioError, "live stream is unavailable"):
                radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, threading.Event())
        terminate.assert_called_once_with(process, process_group=True)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)

    def test_resolver_returns_url_and_ignores_user_download_configuration(self):
        process = self.make_process(stdout="https://example.com/audio.m3u8\n")
        with patch.object(radio.subprocess, "Popen", return_value=process) as popen, patch.object(
            radio, "_terminate_process"
        ):
            url = radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, threading.Event())
        self.assertEqual(url, "https://example.com/audio.m3u8")
        command = popen.call_args.args[0]
        self.assertIn("--get-url", command)
        self.assertIn("--ignore-config", command)
        self.assertIn("--no-playlist", command)
        self.assertIn("--socket-timeout", command)
        self.assertEqual(command[command.index("--js-runtimes") + 1], "node:/test/node")
        self.assertNotIn("--no-warnings", command)

    def test_missing_js_components_do_not_silently_use_an_unreliable_stream(self):
        process = self.make_process(
            stdout="https://example.com/short-lived.m3u8\n",
            stderr="WARNING: No supported JavaScript runtime could be found.\n",
        )
        with patch.object(radio.subprocess, "Popen", return_value=process), patch.object(
            radio, "_terminate_process"
        ):
            with self.assertRaisesRegex(RadioError, r"yt-dlp\[default\]"):
                radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, threading.Event())

    def test_old_external_ytdlp_gets_an_upgrade_message(self):
        process = self.make_process(
            stderr="yt-dlp: error: no such option: --js-runtimes\n", returncode=2
        )
        with patch.object(radio.subprocess, "Popen", return_value=process), patch.object(
            radio, "_terminate_process"
        ):
            with self.assertRaisesRegex(RadioError, "yt-dlp is too old"):
                radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, threading.Event())

    def test_hung_resolver_is_terminated_after_deadline(self):
        process = self.make_process()
        process.communicate.side_effect = subprocess.TimeoutExpired("yt-dlp", 1)
        with patch.object(radio.subprocess, "Popen", return_value=process), patch.object(
            radio.time, "monotonic", side_effect=[0, radio.RESOLVE_TIMEOUT + 1]
        ), patch.object(radio, "_terminate_process") as terminate:
            with self.assertRaisesRegex(RadioError, "Timed out"):
                radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, threading.Event())
        terminate.assert_called_once_with(process, process_group=True)

    def test_cancel_hung_resolver_is_prompt_and_reaps_process(self):
        stop_event = threading.Event()
        process = self.make_process()

        def cancel(**kwargs):
            stop_event.set()
            raise subprocess.TimeoutExpired("yt-dlp", 1)

        process.communicate.side_effect = cancel
        with patch.object(radio.subprocess, "Popen", return_value=process), patch.object(
            radio, "_terminate_process"
        ) as terminate:
            self.assertIsNone(radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, stop_event))
        terminate.assert_called_once_with(process, process_group=True)

    def test_invalid_or_multiple_media_urls_are_rejected(self):
        for stdout in ("", "not a URL", "https://one.test\nhttps://two.test\n"):
            with self.subTest(stdout=stdout), patch.object(
                radio.subprocess, "Popen", return_value=self.make_process(stdout=stdout)
            ), patch.object(radio, "_terminate_process"):
                with self.assertRaises(RadioError):
                    radio._resolve_ytdlp_url("yt-dlp", radio.DEFAULT_LOFI_URL, threading.Event())


class RadioDependencyTests(unittest.TestCase):
    def test_node_is_enabled_explicitly_when_deno_is_missing(self):
        paths = {"node": "/Applications/Node JS/bin/node"}
        with patch.object(radio.shutil, "which", side_effect=paths.get):
            self.assertEqual(
                radio._ytdlp_js_runtime_args(),
                ["--js-runtimes", "node:/Applications/Node JS/bin/node"],
            )

    def test_deno_and_node_are_both_available_to_the_resolver(self):
        with patch.object(radio.shutil, "which", side_effect=lambda name: f"/bin/{name}"):
            self.assertEqual(radio._ytdlp_js_runtime_args(), [
                "--js-runtimes", "deno:/bin/deno", "--js-runtimes", "node:/bin/node",
            ])

    def test_missing_runtime_is_reported_before_starting_a_worker(self):
        with patch.object(radio.shutil, "which", side_effect={"ffplay": "/bin/ffplay"}.get), patch.object(
            radio, "_resolve_ytdlp_command", return_value="yt-dlp"
        ), patch.object(radio, "_RadioSession") as session:
            self.assertIn("Node.js", radio.start_radio(radio.DEFAULT_SYNTHWAVE_URL))
        session.assert_not_called()

    def test_legacy_python_gets_a_clear_youtube_requirement(self):
        with patch.object(radio.sys, "version_info", (3, 9)), patch.object(
            radio.shutil, "which", return_value="/bin/ffplay"
        ), patch.object(radio, "_RadioSession") as session:
            self.assertIn("Python 3.10", radio.start_radio(radio.DEFAULT_SYNTHWAVE_URL))
        session.assert_not_called()

    def test_direct_audio_does_not_need_a_javascript_runtime(self):
        with patch.object(radio.shutil, "which", side_effect={"ffplay": "/bin/ffplay"}.get), patch.object(
            radio, "_RadioSession"
        ) as session:
            try:
                self.assertIsNone(radio.start_radio("https://example.com/live.mp3"))
                session.return_value.thread.start.assert_called_once()
            finally:
                radio.stop_radio()


class RadioPlayerTests(unittest.TestCase):
    def test_streamlink_source_is_closed_if_player_cannot_start(self):
        stream_fd = io.BytesIO(b"audio")
        stream = Mock()
        stream.open.return_value = stream_fd
        session = radio._RadioSession("https://example.com/live", 50)
        with patch.object(radio, "streamlink", Mock()), patch.object(
            radio, "_resolve_stream", return_value=stream
        ), patch.object(radio, "_stream_to_url", return_value=None), patch.object(
            radio.subprocess, "Popen", side_effect=OSError("Cannot start player")
        ):
            with self.assertRaises(OSError):
                session._play_once()
        self.assertTrue(stream_fd.closed)

    def test_streamlink_pipe_closes_player_input_on_source_eof(self):
        stream_fd = io.BytesIO(b"audio")
        player_input = Mock()
        last_data = [0]
        radio._pipe_stream_to_ffplay(
            stream_fd, player_input, threading.Event(), last_data
        )
        player_input.write.assert_called_once_with(b"audio")
        player_input.flush.assert_called_once()
        player_input.close.assert_called_once()
        self.assertGreater(last_data[0], 0)

    def test_http_player_exits_on_eof_and_has_bounded_network_waits(self):
        command = radio._ffplay_command("https://example.com/live.m3u8", 50)
        self.assertIn("-autoexit", command)
        self.assertIn("-rw_timeout", command)
        self.assertIn("-reconnect", command)
        self.assertIn("-m3u8_hold_counters", command)
        self.assertNotIn("-reconnect_at_eof", command)

    def test_pipe_input_does_not_receive_http_or_hls_options(self):
        command = radio._ffplay_command("pipe:0", 50)
        self.assertIn("-autoexit", command)
        self.assertNotIn("-reconnect", command)
        self.assertNotIn("-rw_timeout", command)
        self.assertNotIn("-max_reload", command)

    def test_player_that_ignores_terminate_is_killed_and_reaped(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("ffplay", 2), 0]
        radio._terminate_process(process)
        process.terminate.assert_called_once()
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)


if __name__ == "__main__":
    unittest.main()
