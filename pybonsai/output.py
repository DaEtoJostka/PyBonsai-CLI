"""Output adapters for terminal rendering and file export."""

from pathlib import Path

from .draw import HIDE_CURSOR, SHOW_CURSOR


class TerminalOutput:
    def __init__(self, stream):
        self.stream = stream

    def write(self, text):
        self.stream.write(text)

    def write_line(self, text=""):
        self.stream.write(f"{text}\n")

    def flush(self):
        self.stream.flush()

    def hide_cursor(self):
        self.write(HIDE_CURSOR)
        self.flush()

    def show_cursor(self):
        self.write(SHOW_CURSOR)
        self.flush()

    def clear_screen(self):
        self.write("\033[2J")

    def render_window(self, window):
        lines = ["".join(row) for row in window.chars]
        self.write("\n".join(lines))
        self.write(f"\033[{window.height - 1}A\033[G")
        self.flush()

    def reset_cursor(self, height):
        self.write(f"\033[{height - 1}B\r\n")
        self.flush()


def resolve_save_path(path_like):
    path = Path(path_like)

    if path.parent == Path("."):
        path = Path.home() / "Downloads" / path

    return path


def save_text(text, path_like):
    path = resolve_save_path(path_like)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
