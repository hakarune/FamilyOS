"""Fullscreen kiosk grid window for the FamilyOS Launcher.

Loads app entries from config/apps.json and renders them as a fixed,
non-scrolling grid of large buttons. No window chrome, no exit path -
closing is only possible via the parent panel (see parent_panel.py).
"""
import json
import subprocess
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QGridLayout,
    QMainWindow,
    QPushButton,
    QToolButton,
    QWidget,
)

from ui.parent_panel import ParentPanel

APPS_CONFIG = Path(__file__).resolve().parent.parent / "config" / "apps.json"
GRID_COLUMNS = 3


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

        anchor_row = (len(self._apps) // GRID_COLUMNS) + 1
        grid.addWidget(self._build_parent_anchor(), anchor_row, 0)

    @staticmethod
    def _load_apps():
        if not APPS_CONFIG.exists():
            return []
        return json.loads(APPS_CONFIG.read_text()).get("apps", [])

    def _build_app_button(self, app: dict) -> QPushButton:
        button = QPushButton(app.get("label", "App"))
        icon_path = app.get("icon")
        if icon_path:
            button.setIcon(QIcon(icon_path))
        button.setObjectName("appCard")
        button.clicked.connect(lambda _, cmd=app.get("exec", ""): self._launch(cmd))
        return button

    def _build_parent_anchor(self) -> QToolButton:
        anchor = QToolButton()
        anchor.setText("•")  # low-profile dot, not a labeled button
        anchor.setObjectName("parentAnchor")
        anchor.clicked.connect(self._open_parent_panel)
        return anchor

    @staticmethod
    def _launch(command: str) -> None:
        if not command:
            return
        subprocess.Popen(command.split())

    def _open_parent_panel(self) -> None:
        ParentPanel(self).exec_()
