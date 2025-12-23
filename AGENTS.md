# AGENTS.md

## Project Context
**PyBonsai-CLI** is a procedural ASCII art bonsai generator for the terminal. It uses various mathematical algorithms (Fibonacci, recursive branching) to create unique trees.

## Core Architecture
- **Buffer-Based Drawing**: All drawing happens in a 2D buffer (`pybonsai/draw.py`). **NEVER** use `print()` directly for drawing.
- **Modularity**: New features should be added as separate modules (e.g., `animations.py`, `radio.py`).
- **Configuration**: The `Options` class in `pybonsai/__main__.py` centralizes all settings. Use it for state management.
- **Entry Point**: `pybonsai.__main__.py:main` orchestrates the CLI flow.

## Project Structure
- `pybonsai/tree.py`: Core generation logic (different tree types).
- `pybonsai/draw.py`: Low-level ANSI color and buffer management.
- `pybonsai/animations.py`: Handles dynamic effects (falling leaves, etc.).
- `pybonsai/colors.py`: Color presets and parsing.
- `pybonsai/radio.py`: Lo-Fi background audio logic.

## Commands & Workflow
- **Dependency Management**: Use `uv`. 
  - Add dependency: `uv add <package>`
  - Run project: `uv run pybonsai`
- **Build System**: Hatchling (see `pyproject.toml`).
- **Testing**: Run tests using `pytest` (located in `pybonsai/tests`).

## Coding Style
- **Type Hinting**: Prefer explicit type hints for function arguments and return values.
- **ANSI Colors**: Use the `Color` and `Style` utilities in `draw.py`.
- **Modularity**: Keep `tree.py` focused on generation. Move UI/Auxiliary logic to separate files.

## Guidelines for AI Agents
1. **Always use the buffer**: To draw, use `window.set_char(x, y, char, color)`.
2. **Handle Interruption**: Ensure loops (like animations or radio) handle `KeyboardInterrupt` gracefully.
3. **Respect Presets**: When adding colors, integrate them with the preset system in `colors.py`.
4. **Subprocess Management**: When calling external tools (like `ffplay`), always track PIDs and terminate on exit.
