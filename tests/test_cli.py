import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from pybonsai.app import _leave_room_for_status, main
from pybonsai.cli import MAX_LAYERS, build_parser, parse_cli_args
from pybonsai import radio
from pybonsai.errors import ConfigurationError
from pybonsai.options import AppConfig, RunMode, TreeType, get_default_window_size


class DefaultWindowTests(unittest.TestCase):
    def test_default_window_size_respects_package_limits(self):
        with patch(
            "pybonsai.options.shutil.get_terminal_size",
            return_value=os.terminal_size((120, 50)),
        ):
            self.assertEqual(get_default_window_size(), (80, 25))


class CliParsingTests(unittest.TestCase):
    def test_bonsai_mode_applies_expected_defaults(self):
        config = parse_cli_args(["-b"])

        self.assertEqual(config.tree.initial_len, 11)
        self.assertEqual(config.tree.leaf_len, 4)
        self.assertEqual(config.tree.num_layers, 6)
        self.assertEqual(config.tree.type, TreeType.OFFSET_FIBONACCI)
        self.assertTrue(config.user_set_type)

    def test_lofi_defaults_to_falling_leaves(self):
        config = parse_cli_args(["--lofi"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.animation.mode, RunMode.FALLING_LEAVES)
        self.assertEqual(config.audio.radio_url, radio.RADIO_PRESETS["lofi"].url)

    def test_named_radio_preset_sets_station_url(self):
        config = parse_cli_args(["--lofi", "classical"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.animation.mode, RunMode.FALLING_LEAVES)
        self.assertEqual(config.audio.radio_url, radio.RADIO_PRESETS["classical"].url)

    def test_radio_preset_name_is_normalised(self):
        config = parse_cli_args(["-R", "MeDieVal"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.audio.radio_url, radio.RADIO_PRESETS["medieval"].url)

    def test_numeric_radio_preset_alias_sets_station_url(self):
        config = parse_cli_args(["--lofi", "0"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.audio.radio_url, radio.RADIO_PRESETS["classical"].url)

    def test_custom_radio_url_enables_audio(self):
        config = parse_cli_args(["--radio-url", "https://example.com/live"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.animation.mode, RunMode.FALLING_LEAVES)
        self.assertEqual(config.audio.radio_url, "https://example.com/live")

    def test_help_groups_related_options(self):
        help_text = build_parser().format_help()

        self.assertIn("General options:", help_text)
        self.assertIn("Tree options:", help_text)
        self.assertIn("Rendering:", help_text)
        self.assertIn("Colors:", help_text)
        self.assertIn("Animation:", help_text)
        self.assertIn("Audio:", help_text)

    def test_help_describes_radio_presets(self):
        help_text = " ".join(build_parser().format_help().split())

        self.assertIn("-R, --lofi [PRESET]", help_text)
        self.assertIn("play a terminal radio preset;", help_text)
        self.assertIn(
            (
                "presets: lofi (default), classical (alias: 0), "
                "medieval (alias: 1), synthwave (alias: 2), "
                "sad (alias: 3), jazz (alias: 4)"
            ),
            help_text,
        )
        self.assertNotIn("(default: None)", help_text)
        self.assertNotIn("(default: False)", help_text)

    def test_help_caps_line_length_for_wide_terminals(self):
        with patch(
            "pybonsai.cli.shutil.get_terminal_size",
            return_value=os.terminal_size((160, 50)),
        ):
            help_text = build_parser().format_help()

        self.assertLessEqual(max(len(line) for line in help_text.splitlines()), 100)

    def test_conflicting_flags_raise_configuration_error(self):
        with self.assertRaises(ConfigurationError) as context:
            parse_cli_args(["-i", "-w", "0.1"])

        self.assertIn("--instant and --wait", str(context.exception))

    def test_invalid_color_raises_configuration_error(self):
        with self.assertRaises(ConfigurationError) as context:
            parse_cli_args(["-B", "not-a-color"])

        self.assertIn("Error parsing colors", str(context.exception))

    def test_values_that_crash_or_hang_raise_configuration_error(self):
        cases = {
            ("-d", "0"): "--fall-speed",
            ("-R", "-d", "0"): "--fall-speed",
            ("-w", "-1"): "--wait",
            ("-W", "-1"): "--wait-infinite",
            ("-N", "11"): "--intensity",
            ("-V", "101"): "--volume",
            ("-x", "0"): "--width",
            ("-y", "-3"): "--height",
            ("-l", str(MAX_LAYERS + 1)): "--layers",
            ("-c", ""): "--branch-chars",
            ("-C", ""): "--leaf-chars",
        }
        for argv, flag in cases.items():
            with self.subTest(argv=argv):
                with self.assertRaises(ConfigurationError) as context:
                    parse_cli_args(list(argv))
                self.assertIn(flag, str(context.exception))

    def test_non_finite_numbers_are_rejected(self):
        for argv in (["-M", "nan"], ["-W", "inf"], ["-d", "fast"]):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()) as stderr:
                with self.assertRaises(SystemExit):
                    parse_cli_args(argv)
                self.assertIn("expected a finite number", stderr.getvalue())

    def test_boundary_values_are_accepted(self):
        config = parse_cli_args(
            ["-N", "1", "-V", "100", "-l", str(MAX_LAYERS), "-w", "0", "-M", "-0.3"]
        )

        self.assertEqual(config.animation.intensity, 1)
        self.assertEqual(config.audio.volume, 100)
        self.assertEqual(config.tree.num_layers, MAX_LAYERS)
        self.assertEqual(config.animation.wind, -0.3)


class RadioHelperTests(unittest.TestCase):
    def test_stream_to_url_prefers_manifest_url(self):
        class FakeStream:
            def to_manifest_url(self):
                return "https://example.com/master.m3u8"

            def to_url(self):
                return "https://example.com/media.m3u8"

        self.assertEqual(
            radio._stream_to_url(FakeStream()),
            "https://example.com/master.m3u8",
        )

    def test_youtube_urls_use_ytdlp_path(self):
        self.assertTrue(
            radio._requires_ytdlp("https://www.youtube.com/watch?v=jfKfPfyJRdk")
        )


class MainSmokeTests(unittest.TestCase):
    def test_radio_failure_is_reported_after_animation_stops(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch("pybonsai.app.radio.start_radio", return_value=None), patch(
            "pybonsai.app.radio.stop_radio", return_value="Warning: Station unavailable"
        ), patch("pybonsai.app.run_leaves_falling", side_effect=KeyboardInterrupt):
            self.assertEqual(main(["-R", "2"], stdout=stdout, stderr=stderr), 0)
        self.assertIn("Station unavailable", stderr.getvalue())

    def test_missing_radio_dependency_stays_visible_during_animation(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        def animate(window, config):
            # The animation clears the screen, so the warning must be redrawn with the tree.
            window.clear_screen()
            window.draw()
            self.assertIn("Warning: ffplay missing", stdout.getvalue().split("\033[2J")[-1])
            raise KeyboardInterrupt

        with patch("pybonsai.app.radio.start_radio", return_value="Warning: ffplay missing"), patch(
            "pybonsai.app.radio.stop_radio", return_value=None
        ), patch("pybonsai.app.run_leaves_falling", side_effect=animate):
            self.assertEqual(main(["-R", "-x", "60", "-y", "20"], stdout=stdout, stderr=stderr), 0)
        self.assertEqual(stderr.getvalue().count("Warning: ffplay missing"), 1)

    def test_running_radio_status_is_drawn_below_the_tree(self):
        stdout = io.StringIO()

        def animate(window, config):
            window.draw()
            raise KeyboardInterrupt

        with patch("pybonsai.app.radio.start_radio", return_value=None), patch(
            "pybonsai.app.radio.radio_status", return_value="Radio: playing"
        ), patch("pybonsai.app.radio.stop_radio", return_value=None), patch(
            "pybonsai.app.run_leaves_falling", side_effect=animate
        ):
            main(["-R", "-x", "60", "-y", "20"], stdout=stdout, stderr=io.StringIO())
        self.assertIn("Radio: playing\033[K", stdout.getvalue())

    def test_radio_status_gets_its_own_terminal_row(self):
        config = AppConfig()
        config.render.height = 25
        with patch("pybonsai.app.os.get_terminal_size", return_value=os.terminal_size((80, 24))):
            _leave_room_for_status(config)
        self.assertEqual(config.render.height, 23)

        with patch("pybonsai.app.os.get_terminal_size", side_effect=OSError):
            _leave_room_for_status(config)
        self.assertEqual(config.render.height, 23)

    def test_main_renders_and_saves_tree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "tree.txt")
            stdout = io.StringIO()
            stderr = io.StringIO()

            exit_code = main(
                ["-i", "-x", "40", "-y", "20", "-s", "1", "-o", save_path],
                stdout=stdout,
                stderr=stderr,
            )

            with open(save_path, "r") as saved_tree:
                content = saved_tree.read()

            self.assertEqual(exit_code, 0)
            self.assertTrue(content.strip())
            self.assertNotIn("\033", content)
            self.assertIn("Saved tree to", stdout.getvalue())
            self.assertEqual("", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
