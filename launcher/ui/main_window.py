"""Fullscreen kiosk grid window for the FamilyOS Launcher.

Loads app entries from config/apps.json and renders them as a fixed,
non-scrolling grid of large buttons. No window chrome, no exit path -
closing is only possible via the parent panel (see parent_panel.py).
"""
import json
import subprocess
from pathlib import Path

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from ui.parent_panel import ParentPanel

APPS_CONFIG = Path(__file__).resolve().parent.parent / "config" / "apps.json"
# Three levels up from ui/main_window.py is launcher/'s own parent -
# /opt/familyos/ in the installed image, the repo root in a dev
# checkout. graphics/ is a sibling of launcher/ in both cases (see
# iso-builder/live-build/*/auto/config's install symlinks), so
# apps.json's icon paths ("graphics/icons/kids/...") resolve correctly
# from here with no leading "../" and no dependence on process CWD,
# which bare relative strings passed straight to QIcon() would need.
INSTALL_ROOT = Path(__file__).resolve().parent.parent.parent
GRID_COLUMNS = 3
PARENT_ANCHOR_ICON = INSTALL_ROOT / "graphics" / "icons" / "parent" / "settings.svg"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("FamilyOS Launcher")

        self._apps = self._load_apps()

        central = QWidget(self)
        self.setCentralWidget(central)
        grid = QGridLayout(central)

        for index, app in enumerate(self._apps):
            button = self._build_app_button(app)
            grid.addWidget(button, index // GRID_COLUMNS, index % GRID_COLUMNS)

        app_rows = -(-len(self._apps) // GRID_COLUMNS)  # ceil div, no wasted blank row
        anchor_row = app_rows
        grid.addWidget(self._build_parent_anchor(), anchor_row, 0)

        # Every app-grid row/column shares available space equally so
        # buttons scale to fit whatever the real screen resolution is,
        # per Flavor - Toddler.md's own requirement to "scale
        # dynamically down to 1024x600 and 800x480" - not a fixed
        # pixel size. A real QEMU boot test plus an independent review
        # found a previous fixed 220x220 button size risked pushing
        # the parent anchor (the only way to reach parent controls)
        # off-screen at 800x480. The anchor's own row is deliberately
        # left unstretched so it stays low-profile instead of growing
        # as tall as an app button.
        for row in range(app_rows):
            grid.setRowStretch(row, 1)
        for col in range(GRID_COLUMNS):
            grid.setColumnStretch(col, 1)

    @staticmethod
    def _load_apps():
        if not APPS_CONFIG.exists():
            return []
        return json.loads(APPS_CONFIG.read_text()).get("apps", [])

    def _build_app_button(self, app: dict) -> QPushButton:
        button = QPushButton(app.get("label", "App"))
        icon_path = app.get("icon")
        if icon_path:
            resolved = INSTALL_ROOT / icon_path
            if resolved.exists():
                button.setIcon(QIcon(str(resolved)))
                # Default QPushButton icon size (~16-24px) reads as
                # "no icon at all" next to 220px branded buttons (see
                # ui/style.qss) - a real QEMU boot test showed the
                # grid as plain text buttons with no visible icons.
                button.setIconSize(QSize(96, 96))
        button.setObjectName("appCard")
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.clicked.connect(lambda _, cmd=app.get("exec", ""): self._launch(cmd))
        return button

    def _launch(self, command: str) -> None:
        if not command:
            return
        try:
            subprocess.Popen(command.split())
        except OSError as exc:
            # Previously unhandled: a failed launch (missing binary,
            # bad exec entry) raised inside a Qt slot, which PyQt
            # swallows silently (traceback to stderr only) - from the
            # toddler's perspective the button just "did nothing." A
            # real QEMU boot test hit exactly this for the Media
            # Player button.
            QMessageBox.warning(
                self, "Couldn't open that", f"Could not run '{command}': {exc}"
            )

    def _build_parent_anchor(self) -> QToolButton:
        anchor = QToolButton()
        if PARENT_ANCHOR_ICON.exists():
            # Icon only, no visible label - stays low-profile per
            # Flavor - Toddler.md's "secured, low-profile anchor button".
            anchor.setIcon(QIcon(str(PARENT_ANCHOR_ICON)))
        else:
            anchor.setText("•")  # fallback: low-profile dot glyph
        anchor.setObjectName("parentAnchor")
        anchor.clicked.connect(self._open_parent_panel)
        return anchor

    def _open_parent_panel(self) -> None:
        ParentPanel(self).exec_()
