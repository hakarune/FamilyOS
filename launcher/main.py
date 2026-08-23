#!/usr/bin/env python3
"""FamilyOS Launcher entry point."""
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow

STYLESHEET = Path(__file__).resolve().parent / "ui" / "style.qss"


def main() -> int:
    app = QApplication(sys.argv)
    if STYLESHEET.exists():
        app.setStyleSheet(STYLESHEET.read_text())
    window = MainWindow()
    window.showFullScreen()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
