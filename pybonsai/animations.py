"""Animation effects for PyBonsai."""

import copy
import random
import sys
from time import sleep

from .draw import HIDE_CURSOR, SHOW_CURSOR


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
                    src = random.choice(window.leaf_points)
                    falling.append({
                        'x': src[0],
                        'y': src[1],
                        'char': random.choice(window.options.leaf_chars),
                        'colour': window.choose_colour(window.options.leaf_colour),
                        'vx': random.uniform(-0.3, 0.3),
                        'vy': 0
                    })
            
            # Reset to static tree
            for r in range(window.height):
                window.chars[r] = list(static_tree[r])
            
            # Update and draw falling leaves
            still_active = []
            for leaf in falling:
                # Physics
                leaf['vy'] -= gravity
                leaf['vx'] *= drag
                leaf['vx'] += random.uniform(-0.02, 0.02)
                
                leaf['x'] += leaf['vx']
                leaf['y'] += leaf['vy']
                
                # Flip character occasionally
                if random.random() < 0.1:
                    leaf['char'] = random.choice(window.options.leaf_chars)
                
                # Check bounds
                sx, sy = window.plane_to_screen(leaf['x'], leaf['y'])
                
                if 0 <= sx < window.height and 0 <= sy < window.width:
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
        print(draw.SHOW_CURSOR, end="")
        window.reset_cursor()
        print("\rStopped by user\n")
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()
        window.reset_cursor()
