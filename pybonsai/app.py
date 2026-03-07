"""Application bootstrap for the PyBonsai CLI."""

from typing import Optional, Sequence

from . import radio
from .cli import parse_cli_args
from .draw import SHOW_CURSOR, TerminalWindow
from .runner import run_infinite, run_leaves_falling, run_single_tree


def run(options):
    if options.lofi:
        radio.start_radio(options.radio_url, options.volume)

    window = TerminalWindow(options.window_width, options.window_height, options)

    try:
        if options.infinite:
            run_infinite(window, options)
        elif options.leaves_falling:
            run_leaves_falling(window, options)
        else:
            run_single_tree(window, options)
    except KeyboardInterrupt:
        window.reset_cursor()
        print("\rStopped by user\n")
    finally:
        radio.stop_radio()
        print(SHOW_CURSOR, end="", flush=True)


def main(argv: Optional[Sequence[str]] = None):
    run(parse_cli_args(argv))
