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
from . import tree
import argparse
import sys

import random
from math import radians
from os import get_terminal_size


VERSION = "1.2.2"
DESC = "PyBonsai procedurally generates ASCII art trees in your terminal."


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

    WINDOW_WIDTH = 80
    WINDOW_HEIGHT = 25

    FIXED = False

    def __init__(self):
        #set the default values
        self.num_layers = Options.NUM_LAYERS
        self.initial_len = Options.INITIAL_LEN
        self.angle_mean = radians(Options.ANGLE_MEAN)

        self.leaf_len = Options.LEAF_LEN

        self.instant = Options.INSTANT
        self.wait_time = Options.WAIT_TIME

        self.branch_chars = Options.BRANCH_CHARS
        self.leaf_chars = Options.LEAF_CHARS

        self.user_set_type = False
        self.type = random.randint(0, 3)
        self.fractal_mode = False

        self.fixed_window = Options.FIXED

        self.window_width, self.window_height = self.get_default_window()

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

    -t, --type            tree type: integer between 0 and 3 inclusive [default random]
    -S, --start-len       length of the root branch [default {Options.INITIAL_LEN}]
    -L, --leaf-len        length of each leaf [default {Options.LEAF_LEN}]
    -l, --layers          number of branch layers: more => more branches [default {Options.NUM_LAYERS}]
    -a, --angle           mean angle of branches to their parent, in degrees; more => more arched trees [default {Options.ANGLE_MEAN}]

    -f, --fixed-window    do not allow window height to increase when tree grows off screen
"""
    usage = "usage: pybonsai [-h] [--version] [-s SEED] [-i] [-w WAIT] [-c BRANCH_CHARS]\n" \
            "                  [-C LEAF_CHARS] [-x WIDTH] [-y HEIGHT] [-t {{0,1,2,3}}]\n" \
            "                  [-S START_LEN] [-L LEAF_LEN] [-l LAYERS] [-a ANGLE] [-f]"
    
    print(usage)
    print()
    print(DESC)
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
        epilog = "Based on PyBonsai by Ben Edwards.",
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
    parser.add_argument('-S', '--start-len', type=int, default=options.initial_len)
    parser.add_argument('-L', '--leaf-len', type=int, default=options.leaf_len)
    parser.add_argument('-l', '--layers', type=int, default=options.num_layers)
    parser.add_argument('-a', '--angle', type=int, default=Options.ANGLE_MEAN)
    parser.add_argument('-f', '--fixed-window', action='store_true')

    args = parser.parse_args()

    # Update options with parsed arguments
    options.instant = args.instant
    options.wait_time = args.wait
    options.branch_chars = args.branch_chars
    options.leaf_chars = args.leaf_chars
    options.window_width = args.width
    options.window_height = args.height
    options.initial_len = args.start_len
    options.leaf_len = args.leaf_len
    options.num_layers = args.layers
    options.angle_mean = radians(args.angle)
    options.fixed_window = args.fixed_window

    if args.seed is not None:
        options.set_seed(args.seed)

    if args.type is not None:
        options.type = args.type
        options.user_set_type = True
    
    return options


def get_tree(window, options):
    root_x = window.width // 2

    root_y = tree.Tree.BOX_HEIGHT + 4
    root_y = root_y + root_y % 2  #round to nearest even number (odd numbers cause off-by-one errors as chars are twice as tall as they are wide)

    root_pos = (root_x, root_y)

    if options.type == 0:
        t = tree.ClassicTree(window, root_pos, options)
    elif options.type == 1:
        t = tree.FibonacciTree(window, root_pos, options)
    elif options.type == 2:
        t = tree.OffsetFibTree(window, root_pos, options)
    else:
        t = tree.RandomOffsetFibTree(window, root_pos, options)

    return t


def main():
    options = parse_cli_args()
    window = draw.TerminalWindow(options.window_width, options.window_height, options)

    t = get_tree(window, options)

    t.draw()
    window.draw()
    window.reset_cursor()


if __name__ == "__main__":
    main()