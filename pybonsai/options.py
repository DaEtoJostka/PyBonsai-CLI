"""Configuration objects and defaults for PyBonsai."""

from dataclasses import dataclass, field
from enum import IntEnum
from math import radians
import random
import shutil
from typing import ClassVar, Optional, Tuple

from . import colors


DEFAULT_NUM_LAYERS = 8
DEFAULT_INITIAL_LEN = 15
DEFAULT_ANGLE_MEAN_DEGREES = 40
DEFAULT_LEAF_LEN = 4
DEFAULT_INSTANT = False
DEFAULT_WAIT_TIME = 0
DEFAULT_BRANCH_CHARS = "~;:="
DEFAULT_LEAF_CHARS = "&%#@"
DEFAULT_FIXED_WINDOW = False
DEFAULT_WINDOW_WIDTH = 80
DEFAULT_WINDOW_HEIGHT = 25
DEFAULT_INFINITE_WAIT_TIME = 5
DEFAULT_LEAVES_FALLING = False
DEFAULT_INTENSITY = 5
DEFAULT_FALL_SPEED = 0.4
DEFAULT_TUMBLING_SPEED = 1
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


TREE_TYPE_LABELS = {
    TreeType.CLASSIC: "classic",
    TreeType.FIBONACCI: "fibonacci",
    TreeType.OFFSET_FIBONACCI: "offset fibonacci",
    TreeType.RANDOM_FIBONACCI: "random fibonacci",
}


def get_default_window_size() -> Tuple[int, int]:
    """Return a window size that fits both the terminal and package defaults."""
    terminal_size = shutil.get_terminal_size(
        fallback=(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    )
    width = min(terminal_size.columns, DEFAULT_WINDOW_WIDTH)
    height = min(terminal_size.lines, DEFAULT_WINDOW_HEIGHT)
    return width, height


@dataclass
class Options:
    """Mutable runtime options shared across drawing and animation layers."""

    NUM_LAYERS: ClassVar[int] = DEFAULT_NUM_LAYERS
    INITIAL_LEN: ClassVar[int] = DEFAULT_INITIAL_LEN
    ANGLE_MEAN: ClassVar[int] = DEFAULT_ANGLE_MEAN_DEGREES
    LEAF_LEN: ClassVar[int] = DEFAULT_LEAF_LEN
    INSTANT: ClassVar[bool] = DEFAULT_INSTANT
    WAIT_TIME: ClassVar[float] = DEFAULT_WAIT_TIME
    BRANCH_CHARS: ClassVar[str] = DEFAULT_BRANCH_CHARS
    LEAF_CHARS: ClassVar[str] = DEFAULT_LEAF_CHARS
    FIXED: ClassVar[bool] = DEFAULT_FIXED_WINDOW
    WINDOW_WIDTH: ClassVar[int] = DEFAULT_WINDOW_WIDTH
    WINDOW_HEIGHT: ClassVar[int] = DEFAULT_WINDOW_HEIGHT
    INFINITE_WAIT_TIME: ClassVar[float] = DEFAULT_INFINITE_WAIT_TIME
    LEAVES_FALLING: ClassVar[bool] = DEFAULT_LEAVES_FALLING
    INTENSITY: ClassVar[int] = DEFAULT_INTENSITY
    FALL_SPEED: ClassVar[float] = DEFAULT_FALL_SPEED
    TUMBLING_SPEED: ClassVar[float] = DEFAULT_TUMBLING_SPEED
    FALLING_CHARS: ClassVar[Optional[str]] = DEFAULT_FALLING_CHARS
    LOFI: ClassVar[bool] = DEFAULT_LOFI
    VOLUME: ClassVar[int] = DEFAULT_VOLUME
    RADIO_URL: ClassVar[Optional[str]] = DEFAULT_RADIO_URL
    WIND: ClassVar[float] = DEFAULT_WIND

    num_layers: int = DEFAULT_NUM_LAYERS
    initial_len: int = DEFAULT_INITIAL_LEN
    angle_mean: float = field(
        default_factory=lambda: radians(DEFAULT_ANGLE_MEAN_DEGREES)
    )
    leaf_len: int = DEFAULT_LEAF_LEN
    instant: bool = DEFAULT_INSTANT
    wait_time: float = DEFAULT_WAIT_TIME
    branch_chars: str = DEFAULT_BRANCH_CHARS
    leaf_chars: str = DEFAULT_LEAF_CHARS
    fixed_window: bool = DEFAULT_FIXED_WINDOW
    window_width: Optional[int] = None
    window_height: Optional[int] = None
    save_path: Optional[str] = None
    infinite: bool = False
    new: bool = False
    infinite_wait_time: float = DEFAULT_INFINITE_WAIT_TIME
    leaves_falling: bool = DEFAULT_LEAVES_FALLING
    intensity: int = DEFAULT_INTENSITY
    fall_speed: float = DEFAULT_FALL_SPEED
    tumbling_speed: float = DEFAULT_TUMBLING_SPEED
    falling_chars: Optional[str] = DEFAULT_FALLING_CHARS
    lofi: bool = DEFAULT_LOFI
    volume: int = DEFAULT_VOLUME
    radio_url: Optional[str] = DEFAULT_RADIO_URL
    wind: float = DEFAULT_WIND
    user_set_type: bool = False
    type: int = field(
        default_factory=lambda: random.randint(TreeType.CLASSIC, TreeType.RANDOM_FIBONACCI)
    )
    branch_colour: Tuple = colors.DEFAULT_BRANCH_COLOUR
    leaf_colour: Tuple = colors.DEFAULT_LEAF_COLOUR
    soil_colour: Tuple = colors.DEFAULT_SOIL_COLOUR

    def __post_init__(self):
        default_width, default_height = get_default_window_size()

        if self.window_width is None:
            self.window_width = default_width

        if self.window_height is None:
            self.window_height = default_height

    def get_default_window(self) -> Tuple[int, int]:
        return get_default_window_size()

    def set_seed(self, seed: int):
        random.seed(seed)

        if not self.user_set_type:
            self.type = random.randint(TreeType.CLASSIC, TreeType.RANDOM_FIBONACCI)
