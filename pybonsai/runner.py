"""Pure generation and runtime execution helpers."""

from dataclasses import dataclass, field
from pathlib import Path
import time
import warnings
from typing import List, Optional

from . import animations, tree
from .draw import TerminalWindow
from .options import AppConfig, RunMode, TreeType
from .output import save_text


TREE_REGISTRY = {
    TreeType.CLASSIC: tree.ClassicTree,
    TreeType.FIBONACCI: tree.FibonacciTree,
    TreeType.OFFSET_FIBONACCI: tree.OffsetFibTree,
    TreeType.RANDOM_FIBONACCI: tree.RandomOffsetFibTree,
}


@dataclass
class GeneratedTree:
    config: AppConfig
    window: TerminalWindow
    tree_object: tree.Tree

    def to_string(self):
        return self.window.to_string()

    def to_ansi_string(self):
        return "\n".join("".join(row) for row in self.window.chars)


@dataclass
class RunResult:
    generated: Optional[GeneratedTree] = None
    messages: List[str] = field(default_factory=list)
    saved_path: Optional[Path] = None


def create_window(config: AppConfig, output=None):
    return TerminalWindow(config.render.width, config.render.height, config, output=output)


def build_tree(window, config: AppConfig):
    root_x = window.width // 2
    root_y = tree.Tree.BOX_HEIGHT + 4
    root_y += root_y % 2
    root_pos = (root_x, root_y)
    tree_class = TREE_REGISTRY.get(config.tree.type, tree.RandomOffsetFibTree)
    return tree_class(window, root_pos, config)


def generate_tree(config: AppConfig):
    runtime = config.clone_for_run()
    window = create_window(runtime)
    tree_object = build_tree(window, runtime)
    tree_object.draw()
    return GeneratedTree(runtime, window, tree_object)


def save_generated_tree(generated: GeneratedTree, path_like):
    return save_text(generated.to_string(), path_like)


def run_single_tree(window, config: AppConfig):
    tree_object = build_tree(window, config)
    tree_object.draw()
    window.draw()
    window.reset_cursor()

    result = RunResult(generated=GeneratedTree(config, window, tree_object))

    if config.output.save_path:
        result.saved_path = save_generated_tree(result.generated, config.output.save_path)
        result.messages.append(f"Saved tree to {result.saved_path}")

    return result


def run_infinite(window, config: AppConfig):
    if config.animation.mode == RunMode.FOREST:
        while True:
            window.clear_screen()
            window.clear_chars()
            window.reset_cursor()
            tree_object = build_tree(window, config)
            tree_object.draw()
            window.draw()
            time.sleep(config.animation.infinite_wait_time)

    tree_object = build_tree(window, config)
    while True:
        tree_object.draw()
        window.draw()
        time.sleep(config.animation.infinite_wait_time)


def run_leaves_falling(window, config: AppConfig):
    window.clear_screen()
    window.reset_cursor()
    tree_object = build_tree(window, config)
    tree_object.draw()
    window.draw()
    animations.animate_leaves_falling(window)
    return RunResult(generated=GeneratedTree(config, window, tree_object))


def import_to_txt(tree_object, filename_path):
    warnings.warn(
        "`import_to_txt` is deprecated; use `save_generated_tree` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return save_text(tree_object.to_string(), filename_path)
