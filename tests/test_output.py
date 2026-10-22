import io
import unittest
from types import SimpleNamespace

from pybonsai.output import TerminalOutput


def make_window(width=20, height=2):
    return SimpleNamespace(
        width=width, height=height, chars=[["#"] * width for _ in range(height)]
    )


class StatusLineTests(unittest.TestCase):
    def test_window_without_status_is_rendered_unchanged(self):
        stream = io.StringIO()
        TerminalOutput(stream).render_window(make_window(width=3))

        self.assertEqual(stream.getvalue(), "###\n###\033[1A\033[G")

    def test_status_is_drawn_below_the_window_and_cursor_returns_to_top(self):
        stream = io.StringIO()
        output = TerminalOutput(stream)
        output.status = lambda: "Radio: playing"
        output.render_window(make_window())

        lines = stream.getvalue().split("\n")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[-1], "Radio: playing\033[K\033[2A\033[G")

    def test_reset_cursor_moves_below_the_status_line(self):
        stream = io.StringIO()
        output = TerminalOutput(stream)
        output.reset_cursor(5)
        output.status = lambda: None
        output.reset_cursor(5)

        self.assertEqual(stream.getvalue(), "\033[4B\r\n\033[5B\r\n")

    def test_long_or_multiline_status_stays_on_one_row(self):
        stream = io.StringIO()
        output = TerminalOutput(stream)
        output.status = lambda: "Warning: line one\nline two \033[31m" + "x" * 50
        output.render_window(make_window(width=40))

        status = stream.getvalue().split("\n")[-1].split("\033[K")[0]
        self.assertEqual(len(status), 39)
        self.assertTrue(status.startswith("Warning: line one line two"))
        self.assertTrue(status.endswith("..."))
        self.assertNotIn("\033", status)


if __name__ == "__main__":
    unittest.main()
