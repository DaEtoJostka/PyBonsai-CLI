"""Output adapters for terminal rendering and file export."""

from pathlib import Path

from .draw import HIDE_CURSOR, SHOW_CURSOR


class TerminalOutput:
    def __init__(self, stream):
        self.stream = stream
        # Optional callable returning one line to show below the drawing.
        self.status = None

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
        if self.status is not None:
            lines.append(_status_line(self.status(), window.width))
        self.write("\n".join(lines))
        self.write(f"\033[{len(lines) - 1}A\033[G")
        self.flush()

    def reset_cursor(self, height):
        if self.status is not None:
            height += 1
        self.write(f"\033[{height - 1}B\r\n")
        self.flush()


def _status_line(text, width):
    # Keep the status on one row: a wrapped line would break the cursor math.
    text = " ".join(str(text or "").split())
    text = "".join(char for char in text if char.isprintable())
    limit = max(0, width - 1)
    if len(text) > limit:
        text = text[: max(0, limit - 3)] + "..."
    return f"{text[:limit]}\033[K"


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
