from .app import main, run
from .cli import parse_cli_args
from .metadata import VERSION
from .options import (
    AnimationOptions,
    AppConfig,
    AudioOptions,
    Options,
    OutputOptions,
    PaletteOptions,
    RenderOptions,
    RunMode,
    StyleOptions,
    TreeOptions,
    TreeType,
)
from .runner import GeneratedTree, generate_tree, save_generated_tree

__version__ = VERSION

__all__ = [
    "AnimationOptions",
    "AppConfig",
    "AudioOptions",
    "GeneratedTree",
    "Options",
    "OutputOptions",
    "PaletteOptions",
    "RenderOptions",
    "RunMode",
    "StyleOptions",
    "TreeOptions",
    "TreeType",
    "__version__",
    "generate_tree",
    "main",
    "parse_cli_args",
    "run",
    "save_generated_tree",
]
