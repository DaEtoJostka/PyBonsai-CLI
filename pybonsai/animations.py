"""Animation effects for PyBonsai."""

import copy
import random
import sys
from time import sleep, time

from .draw import HIDE_CURSOR, SHOW_CURSOR


TUMBLING_CHARS = ['.', ',', '-', "'", '`', '-']

def animate_leaves_falling(window):
    """Animate leaves falling from the tree canopy."""
    if not window.leaf_points:
        return
    
    # Store static tree (without falling leaves overlay)
    static_tree = copy.deepcopy(window.chars)
    
    # Falling leaves: each is {'x', 'y', 'char', 'colour', 'vx', 'vy'}
    falling = []
    
    gravity = 0.15 * window.options.fall_speed  # Scale gravity by speed
    drag = 0.98
    frame_delay = max(0.02, 0.1 / window.options.fall_speed)  # Higher speed = shorter delay
    
    sys.stdout.write(HIDE_CURSOR)
    
    try:
        while True:
            # Spawn new leaves based on intensity (probability-based for subtler effect)
            spawn_chance = window.options.intensity / 20.0  # intensity 10 = 50% chance per frame
            if random.random() < spawn_chance:
                if window.leaf_points:
                    # Weight selection by Y coordinate (higher Y = higher chance)
                    # Use choices() which supports weights
                    src = random.choice(window.leaf_points)
                    
                    falling.append({
                        'x': src[0],
                        'y': src[1],

                        'char': random.choice(TUMBLING_CHARS),
                        'colour': window.choose_colour(window.options.leaf_colour),
                        'vx': random.uniform(-0.3, 0.3),
                        'vy': 0,
                        'last_tumble': time()
                    })
            
            # Clear previous leaves (Optimization: Clean only "dirty" pixels)
            for leaf in falling:
                # Restore the character from static_tree at the leaf's previous screen position
                sx, sy = window.plane_to_screen(leaf['x'], leaf['y'])
                
                # Check bounds before accessing
                if 0 <= sx < window.height and 0 <= sy < window.width:
                    # Restore original char/color from static_tree
                    window.chars[sx][sy] = static_tree[sx][sy]

            # Update and draw falling leaves
            still_active = []
            for leaf in falling:
                # Physics
                leaf['vy'] -= gravity
                leaf['vx'] *= drag
                leaf['vx'] += random.uniform(-0.03, 0.03)
                
                leaf['x'] += leaf['vx']
                leaf['y'] += leaf['vy']
                

                # Cycle character every tumbling_speed seconds
                if time() - leaf.get('last_tumble', 0) >= window.options.tumbling_speed:
                    try:
                        current_idx = TUMBLING_CHARS.index(leaf['char'])
                        leaf['char'] = TUMBLING_CHARS[(current_idx + 1) % len(TUMBLING_CHARS)]
                    except ValueError:
                        leaf['char'] = TUMBLING_CHARS[0]
                    leaf['last_tumble'] = time()
                
                # Check bounds
                sx, sy = window.plane_to_screen(leaf['x'], leaf['y'])
                
                if 0 <= sx < window.height and 0 <= sy < window.width:
                    # Only skip drawing if the character in the static tree is a foliage character
                    is_foliage = any(c in static_tree[sx][sy] for c in window.options.leaf_chars)
                    if not is_foliage:
                        coloured = window.colour_char(leaf['char'], leaf['colour'][0], leaf['colour'][1], leaf['colour'][2])
                        window.chars[sx][sy] = coloured
                    still_active.append(leaf)
                elif leaf['y'] > 0:
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

