"""Runtime orchestration for tree creation, animation modes, and saving."""

from pathlib import Path
import sys
import time

from . import animations, tree
from .draw import HIDE_CURSOR
from .options import TreeType


TREE_REGISTRY = {
    int(TreeType.CLASSIC): tree.ClassicTree,
    int(TreeType.FIBONACCI): tree.FibonacciTree,
    int(TreeType.OFFSET_FIBONACCI): tree.OffsetFibTree,
    int(TreeType.RANDOM_FIBONACCI): tree.RandomOffsetFibTree,
}


def save_tree_to_text(tree_obj, filename_path):
    with open(filename_path, "w") as file_handle:
        file_handle.write(tree_obj.to_string())


def build_tree(window, options):
    root_x = window.width // 2
    root_y = tree.Tree.BOX_HEIGHT + 4
    root_y += root_y % 2
    root_pos = (root_x, root_y)

    tree_class = TREE_REGISTRY.get(options.type, tree.RandomOffsetFibTree)
    return tree_class(window, root_pos, options)


def run_single_tree(window, options):
    sys.stdout.write(HIDE_CURSOR)
    tree_obj = build_tree(window, options)
    tree_obj.draw()
    window.draw()
    window.reset_cursor()

    if options.save_path:
        save_path = Path(options.save_path)

        if save_path.parent == Path("."):
            save_path = Path.home() / "Downloads" / save_path

        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_tree_to_text(tree_obj, save_path)
        print(f"\nSaved tree to {save_path}")


def run_infinite(window, options):
    sys.stdout.write(HIDE_CURSOR)

    if options.new:
        while True:
            window.clear_screen()
            window.clear_chars()
            window.reset_cursor()

            tree_obj = build_tree(window, options)
            tree_obj.draw()
            window.draw()
            time.sleep(options.infinite_wait_time)
    else:
        tree_obj = build_tree(window, options)
        while True:
            tree_obj.draw()
            window.draw()
            time.sleep(options.infinite_wait_time)


def run_leaves_falling(window, options):
    window.clear_screen()
    window.reset_cursor()

    tree_obj = build_tree(window, options)
    tree_obj.draw()
    window.draw()
    animations.animate_leaves_falling(window)
