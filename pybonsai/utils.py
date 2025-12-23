import math
import time
import sys
from pathlib import Path

from . import tree


class Line:
    # line in form y = mx + c
    def __init__(self):
        self.start = None
        self.end = None

        self.m = None
        self.c = None

        self.is_vertical = False

    def get_y(self, x):
        if not self.is_vertical:
            return self.m * x + self.c

    def get_x(self, y):
        if self.is_vertical:
            return self.c
        elif self.m != 0:
            return (y - self.c) / self.m

    def set_end_points(self, start, end):
        self.start = start
        self.end = end

        if self.start[0] == self.end[0]:
            self.is_vertical = True
            self.m = None
            self.c = self.start[0]
        else:
            self.m = (self.start[1] - self.end[1]) / (self.start[0] - self.end[0])
            self.c = self.start[1] - self.m * self.start[0]

    def set_gradient(self, m, point):
        self.m = m
        self.c = point[1] - m * point[0]

    def get_theta(self):
        # get angle above x axis
        if self.is_vertical:
            return math.pi / 2
        else:
            return math.atan(self.m)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def mag(self):
        return (self.x**2 + self.y**2) ** 0.5

    def __iadd__(self, other_vec):
        return Vector(self.x + other_vec.x, self.y + other_vec.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def normalise(self):
        m = self.mag()

        self.x /= m
        self.y /= m


def import_to_txt(tree, filename_path):
    with open(filename_path, "w") as f:
        f.write(tree.to_string())


def get_tree(window, options):
    root_x = window.width // 2

    root_y = tree.Tree.BOX_HEIGHT + 4
    root_y = (
        root_y + root_y % 2
    )  # round to nearest even number (odd numbers cause off-by-one errors as chars are twice as tall as they are wide)

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


def run_single_tree(window, options):
    from .draw import HIDE_CURSOR

    sys.stdout.write(HIDE_CURSOR)
    t = get_tree(window, options)
    t.draw()
    window.draw()
    window.reset_cursor()

    if options.save_path:
        save_path = Path(options.save_path)

        # If only a filename is provided (no directory part), save it in the user's Downloads directory.
        if save_path.parent == Path("."):
            save_path = Path.home() / "Downloads" / save_path

        # Create parent directories if they don't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)

        import_to_txt(t, save_path)
        print(f"\nSaved tree to {save_path}")


def run_infinite(window, options):
    from .draw import HIDE_CURSOR

    sys.stdout.write(HIDE_CURSOR)
    if options.new:
        while True:
            window.clear_screen()
            window.clear_chars()
            window.reset_cursor()
            t = get_tree(window, options)
            t.draw()
            window.draw()
            time.sleep(options.infinite_wait_time)
    else:
        t = get_tree(window, options)
        while True:
            t.draw()
            window.draw()
            time.sleep(options.infinite_wait_time)


def run_leaves_falling(window, options):
    from . import animations

    window.clear_screen()
    window.reset_cursor()
    t = get_tree(window, options)
    t.draw()
    window.draw()
    animations.animate_leaves_falling(window)
