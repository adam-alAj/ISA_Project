"""Application entry point for the Smart Vacuum desktop UI."""

from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from src.app.main_window import MainWindow


def main() -> int:
    """Start the offline desktop application."""
    application = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
