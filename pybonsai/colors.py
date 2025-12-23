"""
Handles color definitions, parsing, and presets for PyBonsai.
"""


def parse_color(color_string):
    """
    Parses a color string into a tuple (r, g, b).
    Supports:
    - "r,g,b" (decimal)
    - "#RRGGBB" (hex)
    - Basic color names
    """
    if not color_string:
        raise ValueError("Empty color string")

    color_string = color_string.strip().lower()

    # Basic color names map
    COLOR_NAMES = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "pink": (255, 192, 203),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "brown": (165, 42, 42),
    }

    if color_string in COLOR_NAMES:
        return COLOR_NAMES[color_string]

    # Handle hex
    if color_string.startswith("#"):
        h = color_string.lstrip("#")
        if len(h) == 3:
            h = "".join([c * 2 for c in h])
        if len(h) != 6:
            raise ValueError("Invalid hex color length")
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    # Handle decimal rgb
    try:
        parts = color_string.replace("(", "").replace(")", "").split(",")
        if len(parts) == 3:
            return tuple(int(p.strip()) for p in parts)
    except ValueError:
        pass

    raise ValueError(
        f"Invalid color format: '{color_string}'. Use 'r,g,b', '#RRGGBB', or a basic color name."
    )


# Default colors (Ranges allowed for some, as arrays of tuples)
# Format: ((r_min, r_max), (g_min, g_max), (b_min, b_max))
# OR simple (r, g, b)

DEFAULT_BRANCH_COLOUR = ((200, 255), (150, 255), (0, 0))
DEFAULT_SOIL_COLOUR = (0, 150, 0)
# Leaf range based on tree.py: (0, random(75, 255), 0)
DEFAULT_LEAF_COLOUR = ((0, 0), (75, 255), (0, 0))

PRESETS = {
    "default": {
        "branch_colour": DEFAULT_BRANCH_COLOUR,
        "leaf_colour": DEFAULT_LEAF_COLOUR,
        "soil_colour": DEFAULT_SOIL_COLOUR,
    },
    "sakura": {
        "branch_colour": ((100, 130), (50, 70), (20, 40)),  # Dark Brown
        "leaf_colour": ((240, 255), (105, 180), (180, 230)),  # Pink variations
        "soil_colour": ((40, 70), (100, 150), (30, 60)),  # Mossy green soil
    },
    "autumn": {
        "branch_colour": ((100, 140), (80, 100), (40, 60)),
        "leaf_colour": ((200, 255), (50, 150), (0, 20)),  # Red/Orange
        "soil_colour": ((90, 110), (60, 80), (20, 40)),
    },
    "icy": {
        "branch_colour": ((220, 255), (240, 255), (250, 255)),  # White/Blueish
        "leaf_colour": ((150, 200), (230, 255), (240, 255)),  # Cyan/White
        "soil_colour": ((200, 220), (220, 240), (240, 255)),
    },
    "matrix": {
        "branch_colour": ((0, 0), (100, 200), (0, 0)),
        "leaf_colour": ((0, 50), (150, 255), (0, 50)),
        "soil_colour": ((0, 0), (100, 150), (0, 0)),
    },
}
