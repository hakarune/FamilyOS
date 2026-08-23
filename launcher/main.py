#!/usr/bin/env python3
"""FamilyOS Launcher entry point."""
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow

STYLESHEET = Path(__file__).resolve().parent / "ui" / "style.qss"
# launcher/'s own parent - /opt/familyos/ in the installed image, the
# repo root in a dev checkout - same INSTALL_ROOT convention
# ui/main_window.py and ui/parent_panel.py already use for their own
# icon/asset paths.
INSTALL_ROOT = Path(__file__).resolve().parent.parent
BACKGROUND_TILE = INSTALL_ROOT / "graphics" / "branding" / "kiosk-background-tile.png"


def main() -> int:
    app = QApplication(sys.argv)
    if STYLESHEET.exists():
        # Substitutes an absolute path before applying the stylesheet -
        # see style.qss's own comment on why a bare relative url()
        # isn't reliable here.
        qss = STYLESHEET.read_text().replace(
            "%KIOSK_BACKGROUND_TILE_PATH%", str(BACKGROUND_TILE)
        )
        app.setStyleSheet(qss)
    window = MainWindow()
    window.showFullScreen()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
