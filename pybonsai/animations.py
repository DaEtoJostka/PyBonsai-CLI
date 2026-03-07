"""Animation effects for PyBonsai."""

import copy
from time import sleep, time


DEFAULT_TUMBLING_CHARS = [".", ",", "-", "'", "`", '"', "`", "'", "-", ","]


def animate_leaves_falling(window):
    """Animate leaves falling from the tree canopy."""
    if not window.leaf_points:
        return

    if window.config.animation.falling_chars:
        tumbling_chars = list(window.config.animation.falling_chars)
    else:
        tumbling_chars = DEFAULT_TUMBLING_CHARS

    # Pre-calculate foliage screen positions (to protect only actual tree leaves)
    foliage_screen_positions = set()
    for lp in window.leaf_points:
        sx, sy = window.plane_to_screen(lp[0], lp[1])
        if 0 <= sx < window.height and 0 <= sy < window.width:
            foliage_screen_positions.add((sx, sy))

    # Store static tree (without falling leaves overlay)
    static_tree = copy.deepcopy(window.chars)

    # Falling leaves: each is {'x', 'y', 'char', 'colour', 'vx', 'vy'}
    falling = []

    gravity = 0.15 * window.config.animation.fall_speed
    drag = 0.98
    frame_delay = max(0.02, 0.1 / window.config.animation.fall_speed)
    rng = window.config.random

    while True:
        spawn_chance = window.config.animation.intensity / 10.0
        if rng.random() < spawn_chance and window.leaf_points:
            src = rng.choice(window.leaf_points)
            falling.append(
                {
                    "x": src[0],
                    "y": src[1],
                    "char": rng.choice(tumbling_chars),
                    "colour": window.choose_colour(window.config.style.palette.leaf_colour),
                    "vx": rng.uniform(-0.3, 0.3) + (window.config.animation.wind * 2),
                    "vy": 0,
                    "last_tumble": time(),
                    "tumbling_chars": tumbling_chars,
                }
            )

        for leaf in falling:
            sx, sy = window.plane_to_screen(leaf["x"], leaf["y"])
            if 0 <= sx < window.height and 0 <= sy < window.width:
                window.chars[sx][sy] = static_tree[sx][sy]

        still_active = []
        for leaf in falling:
            leaf["vy"] -= gravity
            leaf["vx"] *= drag
            leaf["vx"] += (window.config.animation.wind * 0.5) + rng.uniform(-0.1, 0.1)

            leaf["x"] += leaf["vx"]
            leaf["y"] += leaf["vy"]

            if time() - leaf.get("last_tumble", 0) >= window.config.animation.tumbling_speed:
                chars = leaf["tumbling_chars"]
                try:
                    current_idx = chars.index(leaf["char"])
                    leaf["char"] = chars[(current_idx + 1) % len(chars)]
                except ValueError:
                    leaf["char"] = chars[0]
                leaf["last_tumble"] = time()

            sx, sy = window.plane_to_screen(leaf["x"], leaf["y"])

            if 0 <= sx < window.height and 0 <= sy < window.width:
                if (sx, sy) not in foliage_screen_positions:
                    coloured = window.colour_char(
                        leaf["char"],
                        leaf["colour"][0],
                        leaf["colour"][1],
                        leaf["colour"][2],
                    )
                    window.chars[sx][sy] = coloured
                still_active.append(leaf)
            elif leaf["y"] > 0:
                still_active.append(leaf)

        falling = still_active

        window.draw()
        sleep(frame_delay)
