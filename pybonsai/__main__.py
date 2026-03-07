#!/usr/bin/env python3

from .app import main
from .cli import parse_cli_args
from .metadata import DESCRIPTION as DESC, VERSION
from .options import Options

__all__ = ["DESC", "VERSION", "Options", "main", "parse_cli_args"]


if __name__ == "__main__":
    main()
