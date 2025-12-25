"""Animation effects for PyBonsai."""

import copy
import random
import sys
from time import sleep, time

from .draw import HIDE_CURSOR, SHOW_CURSOR


DEFAULT_TUMBLING_CHARS = [".", ",", "-", "'", "`", '"', "`", "'", "-", ","]


def animate_leaves_falling(window):
    """Animate leaves falling from the tree canopy."""
    if not window.leaf_points:
        return

    # Use custom falling chars if provided, otherwise use default
    if window.options.falling_chars:
        tumbling_chars = list(window.options.falling_chars)
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

    gravity = 0.15 * window.options.fall_speed  # Scale gravity by speed
    drag = 0.98
    frame_delay = max(
        0.02, 0.1 / window.options.fall_speed
    )  # Higher speed = shorter delay

    sys.stdout.write(HIDE_CURSOR)

    try:
        while True:
            # Spawn new leaves based on intensity (probability-based for subtler effect)
            spawn_chance = (
                window.options.intensity / 10.0
            )  # intensity 1 = 10% chance, 10 = 100% per frame
            if random.random() < spawn_chance:
                if window.leaf_points:
                    # Weight selection by Y coordinate (higher Y = higher chance)
                    # Use choices() which supports weights
                    src = random.choice(window.leaf_points)

                    falling.append(
                        {
                            "x": src[0],
                            "y": src[1],
                            "char": random.choice(tumbling_chars),
                            "colour": window.choose_colour(window.options.leaf_colour),
                            "vx": random.uniform(-0.3, 0.3) + (window.options.wind * 2),
                            "vy": 0,
                            "last_tumble": time(),
                            "tumbling_chars": tumbling_chars,  # Store for this leaf
                        }
                    )

            # Clear previous leaves (Optimization: Clean only "dirty" pixels)
            for leaf in falling:
                # Restore the character from static_tree at the leaf's previous screen position
                sx, sy = window.plane_to_screen(leaf["x"], leaf["y"])

                # Check bounds before accessing
                if 0 <= sx < window.height and 0 <= sy < window.width:
                    # Restore original char/color from static_tree
                    window.chars[sx][sy] = static_tree[sx][sy]

            # Update and draw falling leaves
            still_active = []
            for leaf in falling:
                # Physics
                leaf["vy"] -= gravity
                leaf["vx"] *= drag
                leaf["vx"] += (window.options.wind * 0.5) + random.uniform(-0.1, 0.1)

                leaf["x"] += leaf["vx"]
                leaf["y"] += leaf["vy"]

                # Cycle character every tumbling_speed seconds
                if time() - leaf.get("last_tumble", 0) >= window.options.tumbling_speed:
                    chars = leaf["tumbling_chars"]
                    try:
                        current_idx = chars.index(leaf["char"])
                        leaf["char"] = chars[(current_idx + 1) % len(chars)]
                    except ValueError:
                        leaf["char"] = chars[0]
                    leaf["last_tumble"] = time()

                # Check bounds
                sx, sy = window.plane_to_screen(leaf["x"], leaf["y"])

                if 0 <= sx < window.height and 0 <= sy < window.width:
                    # Only skip drawing if this position is part of the tree foliage
                    is_foliage = (sx, sy) in foliage_screen_positions
                    if not is_foliage:
                        coloured = window.colour_char(
                            leaf["char"],
                            leaf["colour"][0],
                            leaf["colour"][1],
                            leaf["colour"][2],
                        )
                        window.chars[sx][sy] = coloured
                    still_active.append(leaf)
                elif leaf["y"] > 0:
                    # Still falling, just off-screen horizontally
                    still_active.append(leaf)

            falling = still_active

            window.draw()
            sleep(frame_delay)

    except KeyboardInterrupt:
        window.reset_cursor()
        print("\rStopped by user\n")
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()
