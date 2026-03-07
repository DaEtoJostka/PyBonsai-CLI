import unittest
import warnings

from pybonsai.draw import TerminalWindow
from pybonsai.options import AppConfig, Options, TreeType
from pybonsai.runner import build_tree
from pybonsai.tree import ClassicTree, FibonacciTree, OffsetFibTree, RandomOffsetFibTree


class TreeSelectionTests(unittest.TestCase):
    def test_legacy_options_accept_flat_kwargs(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            options = Options(window_width=40, window_height=20, initial_len=12)

        self.assertEqual(options.render.width, 40)
        self.assertEqual(options.render.height, 20)
        self.assertEqual(options.tree.initial_len, 12)

    def test_build_tree_uses_registry_for_all_known_types(self):
        expected_types = {
            int(TreeType.CLASSIC): ClassicTree,
            int(TreeType.FIBONACCI): FibonacciTree,
            int(TreeType.OFFSET_FIBONACCI): OffsetFibTree,
            int(TreeType.RANDOM_FIBONACCI): RandomOffsetFibTree,
        }

        for tree_type, expected_class in expected_types.items():
            with self.subTest(tree_type=tree_type):
                config = AppConfig()
                config.render.width = 40
                config.render.height = 20
                config.tree.type = tree_type
                config.user_set_type = True
                window = TerminalWindow(config.render.width, config.render.height, config)

                self.assertIsInstance(build_tree(window, config), expected_class)


if __name__ == "__main__":
    unittest.main()
