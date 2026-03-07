#!/usr/bin/env python3

from .app import main
from .cli import parse_cli_args
from .metadata import DESCRIPTION as DESC, VERSION
from .options import AppConfig, Options

__all__ = ["AppConfig", "DESC", "VERSION", "Options", "main", "parse_cli_args"]


if __name__ == "__main__":
    raise SystemExit(main())
