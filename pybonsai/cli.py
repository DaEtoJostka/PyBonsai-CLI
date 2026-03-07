"""CLI parsing and option mapping for PyBonsai."""

import argparse
from math import radians
from typing import Optional, Sequence

from . import colors
from .metadata import DESCRIPTION, VERSION
from .options import (
    DEFAULT_ANGLE_MEAN_DEGREES,
    Options,
    TREE_TYPE_LABELS,
    TreeType,
)


class HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    """Keep help readable while still showing default values."""


def build_parser(defaults: Optional[Options] = None) -> argparse.ArgumentParser:
    defaults = defaults or Options()

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
        default=defaults.wait_time,
        help="time delay between drawing characters when not in instant mode",
    )
    parser.add_argument(
        "-c",
        "--branch-chars",
        type=str,
        default=defaults.branch_chars,
        help="string of chars randomly chosen for branches",
    )
    parser.add_argument(
        "-C",
        "--leaf-chars",
        type=str,
        default=defaults.leaf_chars,
        help="string of chars randomly chosen for leaves",
    )
    parser.add_argument(
        "-x",
        "--width",
        type=int,
        default=defaults.window_width,
        help="maximum width of the tree",
    )
    parser.add_argument(
        "-y",
        "--height",
        type=int,
        default=defaults.window_height,
        help="maximum height of the tree",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=int,
        choices=range(len(TreeType)),
        help=f'tree type [0-3]: {tree_types_help}',
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
        default=defaults.infinite_wait_time,
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
        default=defaults.intensity,
        help="intensity of falling leaves [1-10]",
    )
    parser.add_argument(
        "-d",
        "--fall-speed",
        type=float,
        default=defaults.fall_speed,
        help="speed of the falling animation",
    )
    parser.add_argument(
        "-T",
        "--tumbling-speed",
        type=float,
        default=defaults.tumbling_speed,
        help="speed of leaf character changes while falling",
    )
    parser.add_argument(
        "-K",
        "--falling-chars",
        type=str,
        default=defaults.falling_chars,
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
        default=defaults.volume,
        help="volume level for radio [0-100]",
    )
    parser.add_argument(
        "-U",
        "--radio-url",
        type=str,
        default=defaults.radio_url,
        help="custom radio stream URL",
    )
    parser.add_argument(
        "-M",
        "--wind",
        "--tilt",
        type=float,
        default=defaults.wind,
        help="wind force for falling leaves",
    )
    return parser


def _raise_validation_errors(errors):
    message = "\n".join(f"Error: {error}" for error in errors)
    raise SystemExit(message)


def _apply_bonsai_defaults(options: Options):
    options.initial_len = 11
    options.leaf_len = 4
    options.num_layers = 6
    options.angle_mean = radians(50)


def _apply_parsed_arguments(options: Options, args):
    options.instant = args.instant
    options.wait_time = args.wait
    options.branch_chars = args.branch_chars
    options.leaf_chars = args.leaf_chars
    options.window_width = args.width
    options.window_height = args.height
    options.save_path = args.save
    options.fixed_window = args.fixed_window
    options.infinite = args.infinite or args.new
    options.new = args.new
    options.infinite_wait_time = args.wait_infinite
    options.leaves_falling = args.leaves_falling
    options.intensity = args.intensity
    options.fall_speed = args.fall_speed
    options.tumbling_speed = args.tumbling_speed
    options.falling_chars = args.falling_chars
    options.lofi = args.lofi
    options.volume = args.volume
    options.radio_url = args.radio_url
    options.wind = args.wind

    if args.bonsai:
        _apply_bonsai_defaults(options)

    if args.start_len is not None:
        options.initial_len = args.start_len

    if args.leaf_len is not None:
        options.leaf_len = args.leaf_len

    if args.layers is not None:
        options.num_layers = args.layers

    if args.angle is not None:
        options.angle_mean = radians(args.angle)
    elif not args.bonsai:
        options.angle_mean = radians(DEFAULT_ANGLE_MEAN_DEGREES)

    if options.leaves_falling:
        options.infinite = False
        options.new = False

    if args.seed is not None:
        options.set_seed(args.seed)

    if args.type is not None:
        options.type = args.type
        options.user_set_type = True
    elif args.bonsai:
        options.type = int(TreeType.OFFSET_FIBONACCI)
        options.user_set_type = True


def _apply_colours(options: Options, args):
    if args.preset and not colors.apply_preset(options, args.preset):
        print(
            f"Warning: Preset '{args.preset}' not found. Available: "
            f"{', '.join(colors.PRESETS.keys())}"
        )

    try:
        if args.branch_color:
            options.branch_colour = colors.parse_color(args.branch_color)
        if args.leaf_color:
            options.leaf_colour = colors.parse_color(args.leaf_color)
        if args.soil_color:
            options.soil_colour = colors.parse_color(args.soil_color)
    except ValueError as exc:
        raise SystemExit(f"Error parsing colors: {exc}")


def _validate_args(args):
    errors = []

    if args.instant and args.wait > 0:
        errors.append("Conflicting flags: --instant and --wait cannot be used together.")

    if (args.infinite or args.new) and args.leaves_falling:
        errors.append(
            "Conflicting flags: --infinite/--new and --leaves-falling are mutually exclusive."
        )

    if args.save and (args.infinite or args.new or args.leaves_falling or args.lofi):
        errors.append(
            "Conflicting flags: --save is not supported in animation modes "
            "(--infinite, --new, --leaves-falling, or --lofi)."
        )

    if errors:
        _raise_validation_errors(errors)


def parse_cli_args(argv: Optional[Sequence[str]] = None) -> Options:
    options = Options()
    parser = build_parser(options)
    args = parser.parse_args(argv)

    _apply_parsed_arguments(options, args)
    _apply_colours(options, args)
    _validate_args(args)

    if options.lofi and not (args.infinite or args.new or args.leaves_falling):
        options.leaves_falling = True

    return options
