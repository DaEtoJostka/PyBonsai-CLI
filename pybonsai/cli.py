"""CLI parsing and mapping into structured config objects."""

import argparse
from typing import Optional, Sequence

from . import colors
from .errors import ConfigurationError
from .metadata import DESCRIPTION, VERSION
from .options import (
    AppConfig,
    RunMode,
    TREE_TYPE_LABELS,
    TreeType,
    normalise_tree_type,
)


class HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    """Keep help readable while still showing defaults."""


def _parse_tree_type(value):
    try:
        return normalise_tree_type(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_parser(defaults: Optional[AppConfig] = None) -> argparse.ArgumentParser:
    defaults = defaults or AppConfig()
    tree_types_help = ", ".join(
        f'"{label}":{int(tree_type)}' for tree_type, label in TREE_TYPE_LABELS.items()
    )

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=HelpFormatter,
        prog="pybonsai",
    )
    parser.add_argument("--version", action="version", version=f"PyBonsai version {VERSION}")
    parser.add_argument("-s", "--seed", type=int, help="seed for the random number generator")
    parser.add_argument(
        "-i",
        "--instant",
        action="store_true",
        help="display the finished tree immediately",
    )
    parser.add_argument(
        "-w",
        "--wait",
        type=float,
        default=defaults.render.wait_time,
        help="time delay between drawing characters when not in instant mode",
    )
    parser.add_argument(
        "-c",
        "--branch-chars",
        type=str,
        default=defaults.style.branch_chars,
        help="string of chars randomly chosen for branches",
    )
    parser.add_argument(
        "-C",
        "--leaf-chars",
        type=str,
        default=defaults.style.leaf_chars,
        help="string of chars randomly chosen for leaves",
    )
    parser.add_argument(
        "-x",
        "--width",
        type=int,
        default=defaults.render.width,
        help="maximum width of the tree",
    )
    parser.add_argument(
        "-y",
        "--height",
        type=int,
        default=defaults.render.height,
        help="maximum height of the tree",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=_parse_tree_type,
        help=f'tree type [0-3 or name]: {tree_types_help}',
    )
    parser.add_argument(
        "-b",
        "--bonsai",
        action="store_true",
        help="enable bonsai preset settings for a smaller tree",
    )
    parser.add_argument("-S", "--start-len", type=int, help="length of the root branch")
    parser.add_argument("-L", "--leaf-len", type=int, help="length of each leaf")
    parser.add_argument(
        "-l",
        "--layers",
        type=int,
        help="number of branch layers: more means more branches",
    )
    parser.add_argument(
        "-a",
        "--angle",
        type=int,
        help="mean angle of branches to their parent, in degrees",
    )
    parser.add_argument(
        "-o",
        "--save",
        type=str,
        metavar="PATH",
        help="save the tree to a text file",
    )
    parser.add_argument(
        "-f",
        "--fixed-window",
        action="store_true",
        help="do not allow window height to increase when tree grows off screen",
    )
    parser.add_argument(
        "-I",
        "--infinite",
        action="store_true",
        help="run in infinite mode, infinitely growing the same tree",
    )
    parser.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="run in infinite mode, automatically growing new trees",
    )
    parser.add_argument(
        "-W",
        "--wait-infinite",
        type=float,
        default=defaults.animation.infinite_wait_time,
        help="time delay between drawing in infinite mode",
    )
    parser.add_argument(
        "-p",
        "--preset",
        type=str,
        help=f'apply a color preset: {", ".join(colors.PRESETS.keys())}',
    )
    parser.add_argument(
        "-B",
        "--branch-color",
        type=str,
        help='custom color for branches, e.g. "red", "#553311", or "100,60,30"',
    )
    parser.add_argument("-e", "--leaf-color", type=str, help="custom color for leaves")
    parser.add_argument("-g", "--soil-color", type=str, help="custom color for soil")
    parser.add_argument(
        "-F",
        "--leaves-falling",
        action="store_true",
        help="animate leaves falling from the tree continuously",
    )
    parser.add_argument(
        "-N",
        "--intensity",
        type=int,
        default=defaults.animation.intensity,
        help="intensity of falling leaves [1-10]",
    )
    parser.add_argument(
        "-d",
        "--fall-speed",
        type=float,
        default=defaults.animation.fall_speed,
        help="speed of the falling animation",
    )
    parser.add_argument(
        "-T",
        "--tumbling-speed",
        type=float,
        default=defaults.animation.tumbling_speed,
        help="speed of leaf character changes while falling",
    )
    parser.add_argument(
        "-K",
        "--falling-chars",
        type=str,
        default=defaults.animation.falling_chars,
        help='custom characters for falling leaves, e.g. "01" for matrix-style',
    )
    parser.add_argument(
        "-R",
        "--lofi",
        action="store_true",
        help="play Lo-Fi radio stream in the terminal (requires ffplay)",
    )
    parser.add_argument(
        "-V",
        "--volume",
        type=int,
        default=defaults.audio.volume,
        help="volume level for radio [0-100]",
    )
    parser.add_argument(
        "-U",
        "--radio-url",
        type=str,
        default=defaults.audio.radio_url,
        help="custom radio stream URL",
    )
    parser.add_argument(
        "-M",
        "--wind",
        "--tilt",
        type=float,
        default=defaults.animation.wind,
        help="wind force for falling leaves",
    )
    return parser


def _apply_bonsai_defaults(config: AppConfig):
    config.tree.initial_len = 11
    config.tree.leaf_len = 4
    config.tree.num_layers = 6
    config.tree.angle_degrees = 50
    config.tree.type = TreeType.OFFSET_FIBONACCI
    config.user_set_type = True


def _resolve_mode(args) -> RunMode:
    if args.new:
        return RunMode.FOREST
    if args.infinite:
        return RunMode.INFINITE
    if args.leaves_falling:
        return RunMode.FALLING_LEAVES
    return RunMode.SINGLE


def _validate_args(args):
    if args.instant and args.wait > 0:
        raise ConfigurationError(
            "Conflicting flags: --instant and --wait cannot be used together."
        )

    if (args.infinite or args.new) and args.leaves_falling:
        raise ConfigurationError(
            "Conflicting flags: --infinite/--new and --leaves-falling are mutually exclusive."
        )

    if args.save and (args.infinite or args.new or args.leaves_falling or args.lofi):
        raise ConfigurationError(
            "Conflicting flags: --save is not supported in animation modes "
            "(--infinite, --new, --leaves-falling, or --lofi)."
        )


def _apply_colours(config: AppConfig, args):
    if args.preset and not colors.apply_preset(config.style.palette, args.preset):
        raise ConfigurationError(
            f"Preset '{args.preset}' not found. Available: {', '.join(colors.PRESETS.keys())}"
        )

    try:
        if args.branch_color:
            config.style.palette.branch_colour = colors.parse_color(args.branch_color)
        if args.leaf_color:
            config.style.palette.leaf_colour = colors.parse_color(args.leaf_color)
        if args.soil_color:
            config.style.palette.soil_colour = colors.parse_color(args.soil_color)
    except ValueError as exc:
        raise ConfigurationError(f"Error parsing colors: {exc}") from exc


def parse_cli_args(argv: Optional[Sequence[str]] = None) -> AppConfig:
    config = AppConfig()
    parser = build_parser(config)
    args = parser.parse_args(argv)

    _validate_args(args)

    config.render.instant = args.instant
    config.render.wait_time = args.wait
    config.style.branch_chars = args.branch_chars
    config.style.leaf_chars = args.leaf_chars
    config.render.width = args.width
    config.render.height = args.height
    config.render.fixed_window = args.fixed_window
    config.output.save_path = args.save
    config.animation.infinite_wait_time = args.wait_infinite
    config.animation.intensity = args.intensity
    config.animation.fall_speed = args.fall_speed
    config.animation.tumbling_speed = args.tumbling_speed
    config.animation.falling_chars = args.falling_chars
    config.animation.wind = args.wind
    config.audio.enabled = args.lofi
    config.audio.volume = args.volume
    config.audio.radio_url = args.radio_url
    config.animation.mode = _resolve_mode(args)

    if args.bonsai:
        _apply_bonsai_defaults(config)

    if args.start_len is not None:
        config.tree.initial_len = args.start_len
    if args.leaf_len is not None:
        config.tree.leaf_len = args.leaf_len
    if args.layers is not None:
        config.tree.num_layers = args.layers
    if args.angle is not None:
        config.tree.angle_degrees = args.angle

    if args.type is not None:
        config.tree.type = args.type
        config.user_set_type = True

    if args.seed is not None:
        config.reseed(args.seed)

    _apply_colours(config, args)

    if config.audio.enabled and config.animation.mode == RunMode.SINGLE:
        config.animation.mode = RunMode.FALLING_LEAVES

    return config
