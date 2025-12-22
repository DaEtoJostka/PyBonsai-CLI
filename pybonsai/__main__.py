#!/usr/bin/env python3


#   
#                #&                                  
#              %&@&                                  
#       &%@% %&  %@|                                 
#    &&@@&%#@%_\@@&&@#       @=&                     
#   &#@# #%##  ;&@%#  %@    @% &%                    
#     @  %  #&  %%~|       @%@%@&#                   
#                  |;;         # %                   
#                     \\        @ % %@%#             
#                      |~     =;@ __%%               
#                      =|   ~_=___  %&#              
#                      || /~         % #             
#                      |//           &               
#                      |=                            
#                      ~|                            
#                      ;|                            
#       .---.        ./||\.    .-.     
#   
#       I speak for the trees, for the trees have no voice.
#       - The Lorax, 1971
#   


from . import draw
from . import utils
from . import colors
import argparse
import sys

import random
from math import radians
from os import get_terminal_size


VERSION = "2.0.0"
DESC = "PyBonsai procedurally generates ASCII art bonsai trees in your terminal."


class Options:
    #stores all parameters that can be edited via the command line arguments
    
    #default values
    NUM_LAYERS = 8
    INITIAL_LEN = 15
    ANGLE_MEAN = 40

    LEAF_LEN = 4

    INSTANT = False
    WAIT_TIME = 0
    
    BRANCH_CHARS = "~;:="
    LEAF_CHARS = "&%#@"
    
    FIXED = False

    WINDOW_WIDTH = 80
    WINDOW_HEIGHT = 25

    INFINITE_WAIT_TIME = 5

    LEAVES_FALLING = False
    INTENSITY = 5
    FALL_SPEED = 0.5

    def __init__(self):
        #set the default values
        self.num_layers = Options.NUM_LAYERS
        self.initial_len = Options.INITIAL_LEN
        self.angle_mean = radians(Options.ANGLE_MEAN)

        self.leaf_len = Options.LEAF_LEN

        self.instant = Options.INSTANT
        self.wait_time = Options.WAIT_TIME
        self.infinite_wait_time = Options.INFINITE_WAIT_TIME

        self.branch_chars = Options.BRANCH_CHARS
        self.leaf_chars = Options.LEAF_CHARS

        # Color options
        self.branch_colour = colors.DEFAULT_BRANCH_COLOUR
        self.leaf_colour = colors.DEFAULT_LEAF_COLOUR
        self.soil_colour = colors.DEFAULT_SOIL_COLOUR

        self.user_set_type = False
        self.type = random.randint(0, 3)

        self.fixed_window = Options.FIXED

        self.window_width, self.window_height = self.get_default_window()

        self.save_path = None

        self.leaves_falling = Options.LEAVES_FALLING
        self.intensity = Options.INTENSITY
        self.fall_speed = Options.FALL_SPEED

    def get_default_window(self):
        #ensure the default values fit the current terminal size
        width, height = get_terminal_size()

        #check the default values fit the current terminal
        width = min(width, Options.WINDOW_WIDTH)
        height = min(height, Options.WINDOW_HEIGHT)

        return width, height
    
    def set_seed(self, seed):
        random.seed(seed)

        #the type must be re-chosen because the rng seed has been changed (this ensures repeatable results)
        if not self.user_set_type:
            self.type = random.randint(0, 3)


def _print_help():
    OPTION_DESCS = f"""OPTIONS:
    -h, --help            display help
        --version         display version

    -s, --seed            seed for the random number generator

    -i, --instant         instant mode: display finished tree immediately
    -w, --wait            time delay between drawing characters when not in instant mode [default {Options.WAIT_TIME}]

    -c, --branch-chars    string of chars randomly chosen for branches [default "{Options.BRANCH_CHARS}"]
    -C, --leaf-chars      string of chars randomly chosen for leaves [default "{Options.LEAF_CHARS}"]

    -x, --width           maximum width of the tree [default {Options.WINDOW_WIDTH}]
    -y, --height          maximum height of the tree [default {Options.WINDOW_HEIGHT}]

    -t, --type            tree type [0-3]: "classic":0, "fibonacci":1, "offset fibonacci":2, "random fibonacci":3 [default random]
    -b, --bonsai          enable bonsai preset settings (invokes specific defaults for small tree)
    -S, --start-len       length of the root branch [default {Options.INITIAL_LEN}]
    -L, --leaf-len        length of each leaf [default {Options.LEAF_LEN}]
    -l, --layers          number of branch layers: more => more branches [default {Options.NUM_LAYERS}]
    -a, --angle           mean angle of branches to their parent, in degrees; more => more arched trees [default {Options.ANGLE_MEAN}]

    -o, --save PATH       save the tree to a text file. If only a filename is provided, it will be saved in a user's Downloads directory.
    -f, --fixed-window    do not allow window height to increase when tree grows off screen
    
    -I, --infinite        run in infinite mode, infinitely growing same tree
    -n, --new             run in infinite mode, automatically growing new trees
    -W, --wait-infinite   time delay between drawing in infinite mode [default {Options.INFINITE_WAIT_TIME}]

    --preset              apply a color preset: {", ".join(colors.PRESETS.keys())}
    --branch-color        custom color for branches (e.g. "red", "#553311", "100,60,30")
    --leaf-color          custom color for leaves
    --soil-color          custom color for soil

    --leaves-falling      animate leaves falling from the tree continuously
    --intensity           intensity of falling leaves [1-10, default {Options.INTENSITY}]
    --fall-speed          speed of falling animation [default {Options.FALL_SPEED}]
"""
    USAGE = ("usage: pybonsai [-h] [--version] [-s SEED] [-i] [-w WAIT] "
             "[-c BRANCH_CHARS] [-C LEAF_CHARS] [-x WIDTH] [-y HEIGHT] [-t TYPE] [-b] "
             "[-S START_LEN] [-L LEAF_LEN] [-l LAYERS] [-a ANGLE] [-o PATH] [-f] "
             "[-I] [-n] [-W WAIT_INFINITE] [--preset PRESET] [--branch-color COLOR] "
             "[-I] [-n] [-W WAIT_INFINITE] [--preset PRESET] [--branch-color COLOR] "
             "[--leaf-color COLOR] [--soil-color COLOR] [--leaves-falling] "
             "[--intensity N] [--fall-speed S]")

    print()
    print(DESC)
    print()
    print(USAGE)
    print()
    print(OPTION_DESCS)
    exit()


def parse_cli_args():
    if '-h' in sys.argv or '--help' in sys.argv:
        _print_help()
    #convert sys.argv into a dictionary in the form {option_name : option_value}
    options = Options()
    default_width, default_height = options.get_default_window()

    parser = argparse.ArgumentParser(
        description=DESC,
        add_help=False
    )
    parser.add_argument('--version', action='version', version=f'PyBonsai version {VERSION}')
    parser.add_argument('-s', '--seed', type=int)
    parser.add_argument('-i', '--instant', action='store_true')
    parser.add_argument('-w', '--wait', type=float, default=options.wait_time)
    parser.add_argument('-c', '--branch-chars', type=str, default=options.branch_chars)
    parser.add_argument('-C', '--leaf-chars', type=str, default=options.leaf_chars)
    parser.add_argument('-x', '--width', type=int, default=default_width)
    parser.add_argument('-y', '--height', type=int, default=default_height)
    parser.add_argument('-t', '--type', type=int, choices=range(4))
    parser.add_argument('-b', '--bonsai', action='store_true')
    parser.add_argument('-S', '--start-len', type=int)
    parser.add_argument('-L', '--leaf-len', type=int)
    parser.add_argument('-l', '--layers', type=int)
    parser.add_argument('-a', '--angle', type=int)
    parser.add_argument('-o', '--save', type=str, metavar='PATH')
    parser.add_argument('-f', '--fixed-window', action='store_true')
    parser.add_argument('-I', '--infinite', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('-W', '--wait-infinite', type=float, default=options.infinite_wait_time)

    parser.add_argument('--preset', type=str)
    parser.add_argument('--branch-color', type=str)
    parser.add_argument('--leaf-color', type=str)
    parser.add_argument('--soil-color', type=str)

    parser.add_argument('--leaves-falling', action='store_true')
    parser.add_argument('--intensity', type=int, default=options.intensity)
    parser.add_argument('--fall-speed', type=float, default=options.fall_speed)

    args = parser.parse_args()

    # Update options with parsed arguments
    start_len = 11 if args.bonsai else options.initial_len
    leaf_len = 4 if args.bonsai else options.leaf_len
    layers = 6 if args.bonsai else options.num_layers
    angle = 50 if args.bonsai else Options.ANGLE_MEAN

    # Apply arguments if they are explicitly provided, otherwise use the defaults (bonsai or normal)
    options.instant = args.instant
    options.wait_time = args.wait
    options.branch_chars = args.branch_chars
    options.leaf_chars = args.leaf_chars
    options.window_width = args.width
    options.window_height = args.height
    options.initial_len = args.start_len if args.start_len is not None else start_len
    options.leaf_len = args.leaf_len if args.leaf_len is not None else leaf_len
    options.num_layers = args.layers if args.layers is not None else layers
    options.angle_mean = radians(args.angle) if args.angle is not None else radians(angle)
    options.save_path = args.save
    options.fixed_window = args.fixed_window
    options.infinite = args.infinite or args.new
    options.new = args.new
    options.infinite_wait_time = args.wait_infinite

    options.leaves_falling = args.leaves_falling
    options.intensity = args.intensity
    options.fall_speed = args.fall_speed

    if options.leaves_falling:
        options.infinite = False
        options.new = False

    if args.seed is not None:
        options.set_seed(args.seed)

    if args.type is not None:
        options.type = args.type
        options.user_set_type = True
    elif args.bonsai:
        options.type = 2
        options.user_set_type = True

    # Handle colors: Presets first, then overrides
    if args.preset:
        preset_name = args.preset.lower()
        if preset_name in colors.PRESETS:
            preset = colors.PRESETS[preset_name]
            options.branch_colour = preset.get("branch_colour", options.branch_colour)
            options.leaf_colour = preset.get("leaf_colour", options.leaf_colour)
            options.soil_colour = preset.get("soil_colour", options.soil_colour)
        else:
            print(f"Warning: Preset '{args.preset}' not found. Available: {', '.join(colors.PRESETS.keys())}")

    # Explicit color overrides
    try:
        if args.branch_color:
            options.branch_colour = colors.parse_color(args.branch_color)
        if args.leaf_color:
            options.leaf_colour = colors.parse_color(args.leaf_color)
        if args.soil_color:
            options.soil_colour = colors.parse_color(args.soil_color)
    except ValueError as e:
        print(f"Error parsing colors: {e}")
        exit(1)
    
    return options


def main():
    options = parse_cli_args()
    window = draw.TerminalWindow(options.window_width, options.window_height, options)

    try:
        if options.infinite:
            utils.run_infinite(window, options)
        elif options.leaves_falling:
            utils.run_leaves_falling(window, options)
        else:
            utils.run_single_tree(window, options)
            
    except KeyboardInterrupt:
        print(draw.SHOW_CURSOR, end="")
        window.reset_cursor()
        print("\rStopped by user\n")


if __name__ == "__main__":
    main()