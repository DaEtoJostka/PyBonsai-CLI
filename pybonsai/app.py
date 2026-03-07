"""Application bootstrap and CLI execution."""

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

    warning = None
    if runtime.audio.enabled:
        try:
            warning = radio.start_radio(runtime.audio.radio_url, runtime.audio.volume)
        except RadioError as exc:
            warning = f"Warning: {exc}"

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
        radio.stop_radio()
        stdout_output.show_cursor()

    if warning:
        stderr_output.write_line(warning)

    if result is not None:
        for message in result.messages:
            stdout_output.write_line(message)

    return result


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
