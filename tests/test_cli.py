import io
import os
import tempfile
import unittest
from unittest.mock import patch

from pybonsai.app import main
from pybonsai.cli import parse_cli_args
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
        config = parse_cli_args(["-R"])

        self.assertTrue(config.audio.enabled)
        self.assertEqual(config.animation.mode, RunMode.FALLING_LEAVES)

    def test_conflicting_flags_raise_configuration_error(self):
        with self.assertRaises(ConfigurationError) as context:
            parse_cli_args(["-i", "-w", "0.1"])

        self.assertIn("--instant and --wait", str(context.exception))

    def test_invalid_color_raises_configuration_error(self):
        with self.assertRaises(ConfigurationError) as context:
            parse_cli_args(["-B", "not-a-color"])

        self.assertIn("Error parsing colors", str(context.exception))


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
