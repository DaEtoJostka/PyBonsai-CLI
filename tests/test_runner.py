import unittest

from pybonsai.draw import TerminalWindow
from pybonsai.options import Options, TreeType
from pybonsai.runner import build_tree
from pybonsai.tree import ClassicTree, FibonacciTree, OffsetFibTree, RandomOffsetFibTree


class TreeSelectionTests(unittest.TestCase):
    def test_build_tree_uses_registry_for_all_known_types(self):
        expected_types = {
            int(TreeType.CLASSIC): ClassicTree,
            int(TreeType.FIBONACCI): FibonacciTree,
            int(TreeType.OFFSET_FIBONACCI): OffsetFibTree,
            int(TreeType.RANDOM_FIBONACCI): RandomOffsetFibTree,
        }

        for tree_type, expected_class in expected_types.items():
            with self.subTest(tree_type=tree_type):
                options = Options(window_width=40, window_height=20)
                options.type = tree_type
                window = TerminalWindow(options.window_width, options.window_height, options)

                self.assertIsInstance(build_tree(window, options), expected_class)


if __name__ == "__main__":
    unittest.main()
