"""CLI parsing and mapping into structured config objects."""

import argparse
import shutil
from typing import Optional, Sequence

from . import colors
from . import radio
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
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    """Keep help readable while still showing defaults."""

    MAX_WIDTH = 100
    MAX_HELP_POSITION = 36

    def __init__(self, prog):
        terminal_width = shutil.get_terminal_size(
            fallback=(self.MAX_WIDTH, 24)
        ).columns
        width = min(terminal_width, self.MAX_WIDTH)
        max_help_position = min(self.MAX_HELP_POSITION, max(24, width // 3))
        super().__init__(prog, width=width, max_help_position=max_help_position)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)

        if action.nargs == 0:
            return ", ".join(action.option_strings)

        default_metavar = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default_metavar)
        return f"{', '.join(action.option_strings)} {args_string}"

    def _get_help_string(self, action):
        if action.help is None or "%(default)" in action.help:
            return action.help

        if (
            action.default is argparse.SUPPRESS
            or action.default is None
            or action.default is False
        ):
            return action.help

        return f"{action.help} (default: %(default)s)"


def _parse_tree_type(value):
    try:
        return normalise_tree_type(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_radio_preset(value):
    try:
        return radio.normalise_station_name(value)
    except radio.RadioError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_parser(defaults: Optional[AppConfig] = None) -> argparse.ArgumentParser:
    defaults = defaults or AppConfig()
    tree_types_help = ", ".join(
        f"{label} ({int(tree_type)})" for tree_type, label in TREE_TYPE_LABELS.items()
    )

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=HelpFormatter,
        prog="pybonsai",
        add_help=False,
    )
    general_group = parser.add_argument_group("General options")
    tree_group = parser.add_argument_group("Tree options")
    render_group = parser.add_argument_group("Rendering")
    colors_group = parser.add_argument_group("Colors")
    animation_group = parser.add_argument_group("Animation")
    audio_group = parser.add_argument_group("Audio")

    general_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    general_group.add_argument(
        "--version", action="version", version=f"PyBonsai version {VERSION}"
    )
    general_group.add_argument(
        "-s",
        "--seed",
        type=int,
        metavar="INT",
        help="seed for the random number generator",
    )
    general_group.add_argument(
        "-o",
        "--save",
        type=str,
        metavar="PATH",
        help="save the tree to a text file",
    )

    tree_group.add_argument(
        "-t",
        "--type",
        type=_parse_tree_type,
        metavar="TYPE",
        help=f"tree type [0-3 or name]: {tree_types_help}",
    )
    tree_group.add_argument(
        "-b",
        "--bonsai",
        action="store_true",
        help="enable bonsai preset settings for a smaller tree",
    )
    tree_group.add_argument(
        "-S",
        "--start-len",
        type=int,
        metavar="LENGTH",
        help="length of the root branch",
    )
    tree_group.add_argument(
        "-L",
        "--leaf-len",
        type=int,
        metavar="LENGTH",
        help="length of each leaf",
    )
    tree_group.add_argument(
        "-l",
        "--layers",
        type=int,
        metavar="COUNT",
        help="number of branch layers: more means more branches",
    )
    tree_group.add_argument(
        "-a",
        "--angle",
        type=int,
        metavar="DEGREES",
        help="mean angle of branches to their parent, in degrees",
    )
    tree_group.add_argument(
        "-c",
        "--branch-chars",
        type=str,
        default=defaults.style.branch_chars,
        metavar="CHARS",
        help="string of chars randomly chosen for branches",
    )
    tree_group.add_argument(
        "-C",
        "--leaf-chars",
        type=str,
        default=defaults.style.leaf_chars,
        metavar="CHARS",
        help="string of chars randomly chosen for leaves",
    )

    render_group.add_argument(
        "-i",
        "--instant",
        action="store_true",
        help="display the finished tree immediately",
    )
    render_group.add_argument(
        "-w",
        "--wait",
        type=float,
        default=defaults.render.wait_time,
        metavar="SECONDS",
        help="time delay between drawing characters when not in instant mode",
    )
    render_group.add_argument(
        "-x",
        "--width",
        type=int,
        default=defaults.render.width,
        metavar="WIDTH",
        help="maximum width of the tree",
    )
    render_group.add_argument(
        "-y",
        "--height",
        type=int,
        default=defaults.render.height,
        metavar="HEIGHT",
        help="maximum height of the tree",
    )
    render_group.add_argument(
        "-f",
        "--fixed-window",
        action="store_true",
        help="do not allow window height to increase when tree grows off screen",
    )

    colors_group.add_argument(
        "-p",
        "--preset",
        type=str,
        metavar="PRESET",
        help=f'apply a color preset: {", ".join(colors.PRESETS.keys())}',
    )
    colors_group.add_argument(
        "-B",
        "--branch-color",
        type=str,
        metavar="COLOR",
        help='custom color for branches, e.g. "red", "#553311", or "100,60,30"',
    )
    colors_group.add_argument(
        "-e",
        "--leaf-color",
        type=str,
        metavar="COLOR",
        help="custom color for leaves",
    )
    colors_group.add_argument(
        "-g", "--soil-color", type=str, metavar="COLOR", help="custom color for soil"
    )

    animation_group.add_argument(
        "-I",
        "--infinite",
        action="store_true",
        help="run in infinite mode, infinitely growing the same tree",
    )
    animation_group.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="run in infinite mode, automatically growing new trees",
    )
    animation_group.add_argument(
        "-W",
        "--wait-infinite",
        type=float,
        default=defaults.animation.infinite_wait_time,
        metavar="SECONDS",
        help="time delay between drawing in infinite mode",
    )
    animation_group.add_argument(
        "-F",
        "--leaves-falling",
        action="store_true",
        help="animate leaves falling from the tree continuously",
    )
    animation_group.add_argument(
        "-N",
        "--intensity",
        type=int,
        default=defaults.animation.intensity,
        metavar="LEVEL",
        help="intensity of falling leaves [1-10]",
    )
    animation_group.add_argument(
        "-d",
        "--fall-speed",
        type=float,
        default=defaults.animation.fall_speed,
        metavar="SPEED",
        help="speed of the falling animation",
    )
    animation_group.add_argument(
        "-T",
        "--tumbling-speed",
        type=float,
        default=defaults.animation.tumbling_speed,
        metavar="SPEED",
        help="speed of leaf character changes while falling",
    )
    animation_group.add_argument(
        "-K",
        "--falling-chars",
        type=str,
        default=defaults.animation.falling_chars,
        metavar="CHARS",
        help='custom characters for falling leaves, e.g. "01" for matrix-style',
    )
    animation_group.add_argument(
        "-M",
        "--wind",
        "--tilt",
        type=float,
        default=defaults.animation.wind,
        metavar="FORCE",
        help="wind force for falling leaves",
    )

    radio_group = audio_group.add_mutually_exclusive_group()
    radio_group.add_argument(
        "-R",
        "--lofi",
        nargs="?",
        const=radio.DEFAULT_RADIO_PRESET,
        type=_parse_radio_preset,
        metavar="PRESET",
        help=(
            "play a terminal radio preset; "
            f"presets: {radio.describe_presets()}"
        ),
    )
    audio_group.add_argument(
        "-V",
        "--volume",
        type=int,
        default=defaults.audio.volume,
        metavar="LEVEL",
        help="volume level for radio [0-100]",
    )
    radio_group.add_argument(
        "-U",
        "--radio-url",
        type=str,
        metavar="URL",
        help="custom radio stream URL",
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
    audio_requested = bool(args.lofi or args.radio_url)

    if args.instant and args.wait > 0:
        raise ConfigurationError(
            "Conflicting flags: --instant and --wait cannot be used together."
        )

    if (args.infinite or args.new) and args.leaves_falling:
        raise ConfigurationError(
            "Conflicting flags: --infinite/--new and --leaves-falling are mutually exclusive."
        )

    if args.save and (args.infinite or args.new or args.leaves_falling or audio_requested):
        raise ConfigurationError(
            "Conflicting flags: --save is not supported in animation modes "
            "(--infinite, --new, --leaves-falling, or radio playback)."
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
    config.audio.enabled = bool(args.lofi or args.radio_url)
    config.audio.volume = args.volume
    config.audio.radio_url = args.radio_url or radio.resolve_station_url(args.lofi)
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
