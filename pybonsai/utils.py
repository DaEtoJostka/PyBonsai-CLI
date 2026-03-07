"""Compatibility wrappers kept temporarily for older imports."""

import warnings

from .geometry import Line, Vector
from .runner import (
    build_tree as _build_tree,
    import_to_txt as _import_to_txt,
    run_infinite as _run_infinite,
    run_leaves_falling as _run_leaves_falling,
    run_single_tree as _run_single_tree,
)


def _warn(old_name, new_name):
    warnings.warn(
        f"`pybonsai.utils.{old_name}` is deprecated; use `{new_name}` instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def get_tree(*args, **kwargs):
    _warn("get_tree", "pybonsai.runner.build_tree")
    return _build_tree(*args, **kwargs)


def import_to_txt(*args, **kwargs):
    _warn("import_to_txt", "pybonsai.runner.save_generated_tree")
    return _import_to_txt(*args, **kwargs)


def run_single_tree(*args, **kwargs):
    _warn("run_single_tree", "pybonsai.runner.run_single_tree")
    return _run_single_tree(*args, **kwargs)


def run_infinite(*args, **kwargs):
    _warn("run_infinite", "pybonsai.runner.run_infinite")
    return _run_infinite(*args, **kwargs)


def run_leaves_falling(*args, **kwargs):
    _warn("run_leaves_falling", "pybonsai.runner.run_leaves_falling")
    return _run_leaves_falling(*args, **kwargs)

__all__ = ["Line", "Vector", "get_tree", "import_to_txt", "run_infinite", "run_leaves_falling", "run_single_tree"]
