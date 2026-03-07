"""Structured configuration models for PyBonsai."""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from math import radians
import copy
import random as _random
import shutil
import warnings
from typing import ClassVar, Optional, Tuple

from . import colors


DEFAULT_NUM_LAYERS = 8
DEFAULT_INITIAL_LEN = 15
DEFAULT_ANGLE_DEGREES = 40
DEFAULT_LEAF_LEN = 4
DEFAULT_INSTANT = False
DEFAULT_WAIT_TIME = 0.0
DEFAULT_BRANCH_CHARS = "~;:="
DEFAULT_LEAF_CHARS = "&%#@"
DEFAULT_FIXED_WINDOW = False
DEFAULT_WINDOW_WIDTH = 80
DEFAULT_WINDOW_HEIGHT = 25
DEFAULT_INFINITE_WAIT_TIME = 5.0
DEFAULT_INTENSITY = 5
DEFAULT_FALL_SPEED = 0.4
DEFAULT_TUMBLING_SPEED = 1.0
DEFAULT_FALLING_CHARS = None
DEFAULT_LOFI = False
DEFAULT_VOLUME = 50
DEFAULT_RADIO_URL = None
DEFAULT_WIND = 0.0


class TreeType(IntEnum):
    CLASSIC = 0
    FIBONACCI = 1
    OFFSET_FIBONACCI = 2
    RANDOM_FIBONACCI = 3


class RunMode(str, Enum):
    SINGLE = "single"
    INFINITE = "infinite"
    FOREST = "forest"
    FALLING_LEAVES = "falling_leaves"


TREE_TYPE_LABELS = {
    TreeType.CLASSIC: "classic",
    TreeType.FIBONACCI: "fibonacci",
    TreeType.OFFSET_FIBONACCI: "offset fibonacci",
    TreeType.RANDOM_FIBONACCI: "random fibonacci",
}

TREE_TYPE_ALIASES = {
    "classic": TreeType.CLASSIC,
    "0": TreeType.CLASSIC,
    "fibonacci": TreeType.FIBONACCI,
    "1": TreeType.FIBONACCI,
    "offset fibonacci": TreeType.OFFSET_FIBONACCI,
    "offset-fibonacci": TreeType.OFFSET_FIBONACCI,
    "offset_fibonacci": TreeType.OFFSET_FIBONACCI,
    "2": TreeType.OFFSET_FIBONACCI,
    "random fibonacci": TreeType.RANDOM_FIBONACCI,
    "random-fibonacci": TreeType.RANDOM_FIBONACCI,
    "random_fibonacci": TreeType.RANDOM_FIBONACCI,
    "3": TreeType.RANDOM_FIBONACCI,
}


def get_default_window_size() -> Tuple[int, int]:
    terminal_size = shutil.get_terminal_size(
        fallback=(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    )
    width = min(terminal_size.columns, DEFAULT_WINDOW_WIDTH)
    height = min(terminal_size.lines, DEFAULT_WINDOW_HEIGHT)
    return width, height


def normalise_tree_type(value) -> TreeType:
    if isinstance(value, TreeType):
        return value
    if isinstance(value, int):
        return TreeType(value)

    normalised = str(value).strip().lower()
    if normalised not in TREE_TYPE_ALIASES:
        raise ValueError(f"Unknown tree type: {value}")
    return TREE_TYPE_ALIASES[normalised]


@dataclass
class PaletteOptions:
    branch_colour: Tuple = colors.DEFAULT_BRANCH_COLOUR
    leaf_colour: Tuple = colors.DEFAULT_LEAF_COLOUR
    soil_colour: Tuple = colors.DEFAULT_SOIL_COLOUR


@dataclass
class StyleOptions:
    branch_chars: str = DEFAULT_BRANCH_CHARS
    leaf_chars: str = DEFAULT_LEAF_CHARS
    palette: PaletteOptions = field(default_factory=PaletteOptions)


@dataclass
class TreeOptions:
    type: Optional[TreeType] = None
    seed: Optional[int] = None
    num_layers: int = DEFAULT_NUM_LAYERS
    initial_len: int = DEFAULT_INITIAL_LEN
    leaf_len: int = DEFAULT_LEAF_LEN
    angle_degrees: float = DEFAULT_ANGLE_DEGREES

    @property
    def angle_radians(self) -> float:
        return radians(self.angle_degrees)


@dataclass
class RenderOptions:
    width: Optional[int] = None
    height: Optional[int] = None
    instant: bool = DEFAULT_INSTANT
    wait_time: float = DEFAULT_WAIT_TIME
    fixed_window: bool = DEFAULT_FIXED_WINDOW


@dataclass
class AnimationOptions:
    mode: RunMode = RunMode.SINGLE
    infinite_wait_time: float = DEFAULT_INFINITE_WAIT_TIME
    intensity: int = DEFAULT_INTENSITY
    fall_speed: float = DEFAULT_FALL_SPEED
    tumbling_speed: float = DEFAULT_TUMBLING_SPEED
    falling_chars: Optional[str] = DEFAULT_FALLING_CHARS
    wind: float = DEFAULT_WIND


@dataclass
class AudioOptions:
    enabled: bool = DEFAULT_LOFI
    volume: int = DEFAULT_VOLUME
    radio_url: Optional[str] = DEFAULT_RADIO_URL


@dataclass
class OutputOptions:
    save_path: Optional[str] = None


@dataclass
class AppConfig:
    """Top-level config exposed by the library."""

    tree: TreeOptions = field(default_factory=TreeOptions)
    style: StyleOptions = field(default_factory=StyleOptions)
    render: RenderOptions = field(default_factory=RenderOptions)
    animation: AnimationOptions = field(default_factory=AnimationOptions)
    audio: AudioOptions = field(default_factory=AudioOptions)
    output: OutputOptions = field(default_factory=OutputOptions)
    random: _random.Random = field(default_factory=_random.Random)
    user_set_type: bool = False

    _LEGACY_FIELDS: ClassVar[dict] = {
        "num_layers": ("tree", "num_layers"),
        "initial_len": ("tree", "initial_len"),
        "leaf_len": ("tree", "leaf_len"),
        "branch_chars": ("style", "branch_chars"),
        "leaf_chars": ("style", "leaf_chars"),
        "window_width": ("render", "width"),
        "window_height": ("render", "height"),
        "instant": ("render", "instant"),
        "wait_time": ("render", "wait_time"),
        "fixed_window": ("render", "fixed_window"),
        "save_path": ("output", "save_path"),
        "infinite_wait_time": ("animation", "infinite_wait_time"),
        "intensity": ("animation", "intensity"),
        "fall_speed": ("animation", "fall_speed"),
        "tumbling_speed": ("animation", "tumbling_speed"),
        "falling_chars": ("animation", "falling_chars"),
        "lofi": ("audio", "enabled"),
        "volume": ("audio", "volume"),
        "radio_url": ("audio", "radio_url"),
        "wind": ("animation", "wind"),
        "branch_colour": ("style", "palette", "branch_colour"),
        "leaf_colour": ("style", "palette", "leaf_colour"),
        "soil_colour": ("style", "palette", "soil_colour"),
    }

    def __post_init__(self):
        default_width, default_height = get_default_window_size()

        if self.render.width is None:
            self.render.width = default_width

        if self.render.height is None:
            self.render.height = default_height

        if self.tree.type is not None:
            self.tree.type = normalise_tree_type(self.tree.type)

        self._reset_random(select_type=self.tree.type is None)

    def clone_for_run(self):
        runtime = copy.deepcopy(self)
        runtime.random = _random.Random(runtime.tree.seed)
        if runtime.tree.seed is not None and not runtime.user_set_type:
            runtime.tree.type = TreeType(
                runtime.random.randint(TreeType.CLASSIC, TreeType.RANDOM_FIBONACCI)
            )
        return runtime

    def reseed(self, seed: int):
        self.tree.seed = seed
        self._reset_random(select_type=not self.user_set_type)

    def get_default_window(self) -> Tuple[int, int]:
        return get_default_window_size()

    def _reset_random(self, select_type: bool):
        self.random = _random.Random(self.tree.seed)

        if select_type:
            self.tree.type = TreeType(
                self.random.randint(TreeType.CLASSIC, TreeType.RANDOM_FIBONACCI)
            )

    def _warn_legacy(self, field_name: str, replacement: str):
        warnings.warn(
            f"`{field_name}` is deprecated; use `{replacement}` instead.",
            DeprecationWarning,
            stacklevel=3,
        )

    def __getattr__(self, name):
        if name == "type":
            self._warn_legacy("type", "tree.type")
            return int(self.tree.type) if self.tree.type is not None else None
        if name == "angle_mean":
            self._warn_legacy("angle_mean", "tree.angle_degrees")
            return self.tree.angle_radians
        if name == "infinite":
            self._warn_legacy("infinite", "animation.mode")
            return self.animation.mode in (RunMode.INFINITE, RunMode.FOREST)
        if name == "new":
            self._warn_legacy("new", "animation.mode")
            return self.animation.mode == RunMode.FOREST
        if name == "leaves_falling":
            self._warn_legacy("leaves_falling", "animation.mode")
            return self.animation.mode == RunMode.FALLING_LEAVES
        if name in self._LEGACY_FIELDS:
            path = self._LEGACY_FIELDS[name]
            self._warn_legacy(name, ".".join(path))
            value = self
            for part in path:
                value = getattr(value, part)
            return value
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in {"tree", "style", "render", "animation", "audio", "output", "random", "user_set_type"}:
            return super().__setattr__(name, value)
        if name == "type" and "tree" in self.__dict__:
            self._warn_legacy("type", "tree.type")
            self.tree.type = normalise_tree_type(value)
            self.user_set_type = True
            return
        if name == "angle_mean" and "tree" in self.__dict__:
            self._warn_legacy("angle_mean", "tree.angle_degrees")
            self.tree.angle_degrees = value * 180 / 3.141592653589793
            return
        if name == "infinite" and "animation" in self.__dict__:
            self._warn_legacy("infinite", "animation.mode")
            if value:
                self.animation.mode = RunMode.FOREST if self.animation.mode == RunMode.FOREST else RunMode.INFINITE
            elif self.animation.mode in (RunMode.INFINITE, RunMode.FOREST):
                self.animation.mode = RunMode.SINGLE
            return
        if name == "new" and "animation" in self.__dict__:
            self._warn_legacy("new", "animation.mode")
            self.animation.mode = RunMode.FOREST if value else RunMode.SINGLE
            return
        if name == "leaves_falling" and "animation" in self.__dict__:
            self._warn_legacy("leaves_falling", "animation.mode")
            self.animation.mode = RunMode.FALLING_LEAVES if value else RunMode.SINGLE
            return
        if name in self._LEGACY_FIELDS and "tree" in self.__dict__:
            path = self._LEGACY_FIELDS[name]
            self._warn_legacy(name, ".".join(path))
            target = self
            for part in path[:-1]:
                target = getattr(target, part)
            setattr(target, path[-1], value)
            return
        super().__setattr__(name, value)


class Options(AppConfig):
    """Deprecated flat config alias kept for compatibility."""

    NUM_LAYERS: ClassVar[int] = DEFAULT_NUM_LAYERS
    INITIAL_LEN: ClassVar[int] = DEFAULT_INITIAL_LEN
    ANGLE_MEAN: ClassVar[int] = DEFAULT_ANGLE_DEGREES
    LEAF_LEN: ClassVar[int] = DEFAULT_LEAF_LEN
    INSTANT: ClassVar[bool] = DEFAULT_INSTANT
    WAIT_TIME: ClassVar[float] = DEFAULT_WAIT_TIME
    BRANCH_CHARS: ClassVar[str] = DEFAULT_BRANCH_CHARS
    LEAF_CHARS: ClassVar[str] = DEFAULT_LEAF_CHARS
    FIXED: ClassVar[bool] = DEFAULT_FIXED_WINDOW
    WINDOW_WIDTH: ClassVar[int] = DEFAULT_WINDOW_WIDTH
    WINDOW_HEIGHT: ClassVar[int] = DEFAULT_WINDOW_HEIGHT
    INFINITE_WAIT_TIME: ClassVar[float] = DEFAULT_INFINITE_WAIT_TIME
    INTENSITY: ClassVar[int] = DEFAULT_INTENSITY
    FALL_SPEED: ClassVar[float] = DEFAULT_FALL_SPEED
    TUMBLING_SPEED: ClassVar[float] = DEFAULT_TUMBLING_SPEED
    FALLING_CHARS: ClassVar[Optional[str]] = DEFAULT_FALLING_CHARS
    LOFI: ClassVar[bool] = DEFAULT_LOFI
    VOLUME: ClassVar[int] = DEFAULT_VOLUME
    RADIO_URL: ClassVar[Optional[str]] = DEFAULT_RADIO_URL
    WIND: ClassVar[float] = DEFAULT_WIND

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "`Options` is deprecated; use `AppConfig` with nested sections instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        current_kwargs = {}
        legacy_kwargs = {}

        for key, value in kwargs.items():
            if key in AppConfig.__dataclass_fields__:
                current_kwargs[key] = value
            else:
                legacy_kwargs[key] = value

        super().__init__(*args, **current_kwargs)

        for key, value in legacy_kwargs.items():
            setattr(self, key, value)
