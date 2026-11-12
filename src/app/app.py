"""Application entry point for the Smart Vacuum desktop UI."""

from __future__ import annotations

import argparse
import sys
from PySide6.QtWidgets import QApplication

from src.app.main_window import MainWindow


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--theme", choices=("light", "dark"), default=None)
    return parser.parse_known_args(argv)[0]


def main() -> int:
    """Start the offline desktop application."""
    args = _parse_args(sys.argv[1:])
    application = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(theme_mode=args.theme)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
