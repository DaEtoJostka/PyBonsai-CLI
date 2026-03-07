import io
import os
import tempfile
import unittest
from unittest.mock import patch

from pybonsai.app import main
from pybonsai.cli import parse_cli_args
from pybonsai import radio
from pybonsai.errors import ConfigurationError
from pybonsai.options import RunMode, TreeType, get_default_window_size


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
        config = parse_cli_args(["--lofi", "classic"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.animation.mode, RunMode.FALLING_LEAVES)
        self.assertEqual(config.audio.radio_url, radio.RADIO_PRESETS["classic"].url)

    def test_radio_preset_alias_is_normalised(self):
        config = parse_cli_args(["-R", "medival"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.audio.radio_url, radio.RADIO_PRESETS["medieval"].url)

    def test_custom_radio_url_enables_audio(self):
        config = parse_cli_args(["--radio-url", "https://example.com/live"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.animation.mode, RunMode.FALLING_LEAVES)
        self.assertEqual(config.audio.radio_url, "https://example.com/live")

    def test_conflicting_flags_raise_configuration_error(self):
        with self.assertRaises(ConfigurationError) as context:
            parse_cli_args(["-i", "-w", "0.1"])

        self.assertIn("--instant and --wait", str(context.exception))

    def test_invalid_color_raises_configuration_error(self):
        with self.assertRaises(ConfigurationError) as context:
            parse_cli_args(["-B", "not-a-color"])

        self.assertIn("Error parsing colors", str(context.exception))


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
