"""Application bootstrap and CLI execution."""

import os
import sys
from typing import Optional, Sequence

from . import radio
from .cli import parse_cli_args
from .errors import ConfigurationError, RadioError
from .options import AppConfig, RunMode
from .output import TerminalOutput
from .runner import create_window, run_infinite, run_leaves_falling, run_single_tree


def run(config: AppConfig, stdout=None, stderr=None):
    runtime = config.clone_for_run()
    stdout_output = TerminalOutput(stdout or sys.stdout)
    stderr_output = TerminalOutput(stderr or sys.stderr)

    start_warning = None
    if runtime.audio.enabled:
        try:
            start_warning = radio.start_radio(runtime.audio.radio_url, runtime.audio.volume)
        except RadioError as exc:
            start_warning = f"Warning: {exc}"
        # Animations clear the screen, so radio state is drawn below the tree.
        stdout_output.status = lambda: start_warning or radio.radio_status()
        _leave_room_for_status(runtime)

    window = create_window(runtime, stdout_output)
    result = None

    stdout_output.hide_cursor()
    try:
        if runtime.animation.mode in (RunMode.INFINITE, RunMode.FOREST):
            run_infinite(window, runtime)
        elif runtime.animation.mode == RunMode.FALLING_LEAVES:
            result = run_leaves_falling(window, runtime)
        else:
            result = run_single_tree(window, runtime)
    except KeyboardInterrupt:
        window.reset_cursor()
        stdout_output.write_line("Stopped by user")
    finally:
        warning = radio.stop_radio() or start_warning
        stdout_output.show_cursor()

    if warning:
        stderr_output.write_line(warning)

    if result is not None:
        for message in result.messages:
            stdout_output.write_line(message)

    return result


def _leave_room_for_status(config: AppConfig):
    # Tree and status must fit on screen together, or every frame scrolls.
    try:
        terminal_lines = os.get_terminal_size().lines
    except OSError:
        return
    if terminal_lines > 1:
        config.render.height = min(config.render.height, terminal_lines - 1)


def main(
    argv: Optional[Sequence[str]] = None,
    stdout=None,
    stderr=None,
):
    try:
        config = parse_cli_args(argv)
    except ConfigurationError as exc:
        stream = stderr or sys.stderr
        stream.write(f"Error: {exc}\n")
        stream.flush()
        return 2

    run(config, stdout=stdout, stderr=stderr)
    return 0
