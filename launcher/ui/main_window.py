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

# Same INSTALL_ROOT-relative reasoning as the icon paths below -
# launcher/ is a real directory (not installed piecemeal), so
# browser_kiosk.py is always a sibling of this file's own launcher/ui/
# parent, both in a dev checkout and at /opt/familyos/launcher/ in the
# installed image.
BROWSER_SCRIPT = INSTALL_ROOT / "launcher" / "browser_kiosk.py"

# Marker file whose mere presence controls whether the "Web Browser"
# app card below is shown at all - same is_dry_run()-style idiom
# lib/env-guard.sh already uses for /etc/familyos-release. Written by
# parental-tools/familyos-browser-toggle (via the Parent Panel's "Show
# Browser on Main Screen" toggle - see ui/parent_panel.py), read here
# directly with no privilege needed, same as browser_kiosk.py already
# reads /var/lib/familyos/allowed-sites.json directly. Absent by
# default (nothing at build time creates it), so a fresh image never
# shows this card until a parent explicitly turns it on.
BROWSER_VISIBLE_FLAG = Path("/var/lib/familyos/browser-visible")

# Matches config/apps.json's Media Player entry and
# parental-tools/familyos-remount-rw's own target - the one place a
# parent's added media actually lands. Special-cased in _launch()
# below: confirmed mpv 0.35.1 (the real installed version - see
# devuan-build-docs/confirmed-package-sweep.txt) documents its
# accepted arguments as only "[file|URL|PLAYLIST|-]" or "files" in its
# own man page/synopsis - no directory-argument support at all (that's
# a newer mpv feature, --directory-mode, absent from this version's
# man page entirely). Passing the bare directory, as the previous
# version of this app's exec command did, was unreliable regardless of
# whether the folder had files in it - the actual, confirmed root
# cause of "Media Player does nothing," not just the empty-folder
# content gap this was previously (and correctly, as far as it went)
# attributed to.
MEDIA_DIR = Path("/home/toddler/media")

# One color per app card, cycling through this list - the SAME palette
# parental-tools/lib/render-homepage.py uses for the browser's homepage
# tiles, reused deliberately so the whole system (launcher grid,
# browser homepage) reads as one consistent visual language rather than
# two unrelated color schemes. Matched to QSS rules of the same names
# in ui/style.qss via a "cardColor" dynamic property (Qt's supported
# mechanism for per-instance styling from a single shared stylesheet).
CARD_COLOR_NAMES = ["green", "amber", "blue", "pink", "teal", "purple"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("FamilyOS Launcher")

        central = QWidget(self)
        central.setObjectName("kioskCanvas")
        self.setCentralWidget(central)
        self._grid = QGridLayout(central)
        self._rebuild_grid()

    def _rebuild_grid(self) -> None:
        """(Re)populates the app grid from apps.json plus the
        browser-visibility flag. Called once from __init__, and again
        after the Parent Panel closes (see _open_parent_panel) so a
        "Show Browser on Main Screen" toggle flip takes effect on this
        same running session immediately, not only on next boot.
        """
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        apps = self._load_apps()

        for index, app in enumerate(apps):
            button = self._build_app_button(app, index)
            # Qt.AlignVCenter only (not a full AlignCenter): the button's
            # own QSizePolicy.Expanding still fills the cell
            # horizontally (needed for the 800px-width responsiveness
            # fix from an earlier round), but vertically, style.qss's
            # max-height cap on #appCard means the cell (stretched to
            # fill the fullscreen window - see the row-stretch loop
            # below) is now taller than the button itself. Without this,
            # an independent review correctly found Qt's default
            # top-left anchoring would leave the button hugging the top
            # of its row with an ugly blank gap below it - centering
            # distributes that leftover space evenly above and below
            # instead.
            self._grid.addWidget(button, index // GRID_COLUMNS, index % GRID_COLUMNS, Qt.AlignVCenter)

        app_rows = -(-len(apps) // GRID_COLUMNS)  # ceil div, no wasted blank row
        anchor_row = app_rows
        self._grid.addWidget(self._build_parent_anchor(), anchor_row, 0)

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
            self._grid.setRowStretch(row, 1)
        for col in range(GRID_COLUMNS):
            self._grid.setColumnStretch(col, 1)

    @staticmethod
    def _load_apps():
        apps = []
        if APPS_CONFIG.exists():
            apps = json.loads(APPS_CONFIG.read_text()).get("apps", [])
        if BROWSER_VISIBLE_FLAG.exists():
            # Appended, not written into apps.json: this card's presence
            # is parent-controlled state, not static config - see
            # BROWSER_VISIBLE_FLAG's own comment above. Launched exactly
            # like any other app card (generic _launch() below splits
            # "exec" and Popens it, no shell) - no special-casing needed
            # the way Media Player's mpv invocation requires.
            apps.append({
                "label": "Web Browser",
                "exec": f"python3 {BROWSER_SCRIPT}",
                "icon": "graphics/icons/kids/browser.svg",
            })
        return apps

    def _build_app_button(self, app: dict, index: int) -> QPushButton:
        button = QPushButton(app.get("label", "App"))
        button.setProperty("cardColor", CARD_COLOR_NAMES[index % len(CARD_COLOR_NAMES)])
        icon_path = app.get("icon")
        if icon_path:
            resolved = INSTALL_ROOT / icon_path
            if resolved.exists():
                button.setIcon(QIcon(str(resolved)))
                # Default QPushButton icon size (~16-24px) reads as
                # "no icon at all" against the branded buttons in
                # ui/style.qss - a real QEMU boot test showed the grid
                # as plain text buttons with no visible icons. 72px is
                # a deliberate compromise, not the first value tried:
                # a wider 96px icon plus unwrapped button text was
                # flagged by an independent review as risking
                # horizontal overflow on an 800px-wide screen (this
                # project's smallest target resolution) once buttons
                # became responsive instead of a fixed size - see
                # ui/style.qss's font-size for the matching reduction.
                button.setIconSize(QSize(72, 72))
        button.setObjectName("appCard")
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.clicked.connect(lambda _, cmd=app.get("exec", ""): self._launch(cmd))
        return button

    def _launch(self, command: str) -> None:
        if not command:
            return
        if command.startswith("mpv ") and str(MEDIA_DIR) in command:
            self._launch_media_player()
            return
        try:
            subprocess.Popen(command.split())
        except OSError as exc:
            # Previously unhandled: a failed launch (missing binary,
            # bad exec entry) raised inside a Qt slot, which PyQt
            # swallows silently (traceback to stderr only) - from the
            # toddler's perspective the button just "did nothing." A
            # real QEMU boot test hit exactly this for the Media
            # Player button (before the more specific mpv/directory
            # root cause above was found).
            QMessageBox.warning(
                self, "Couldn't open that", f"Could not run '{command}': {exc}"
            )

    def _launch_media_player(self) -> None:
        # Enumerates real files ourselves and passes them as individual
        # argv entries - mpv reliably accepts a list of files (this is
        # its most basic, universally-supported usage across versions),
        # unlike the bare-directory argument the previous version of
        # this method relied on (see MEDIA_DIR's own comment above for
        # why that wasn't reliable on the real installed mpv version).
        # mpv/its installed libavcodec/libavformat stack handles
        # m4a/mp4/mkv/mov/avi/mp3/ogg/flac natively - no extra package
        # needed for format coverage, confirmed via mpv's own Depends.
        media_files = []
        if MEDIA_DIR.is_dir():
            media_files = sorted(f for f in MEDIA_DIR.iterdir() if f.is_file())

        if not media_files:
            # This button doing nothing was previously indistinguishable
            # from a real failure - now it always gives feedback, even
            # when the actual reason is "no content yet" (a parent
            # hasn't added anything via Remount RW), which isn't a bug
            # to paper over with fabricated placeholder content.
            QMessageBox.information(
                self, "No media yet",
                "Ask a parent to add a video or song first "
                "(Parent Settings -> Remount RW).",
            )
            return

        try:
            subprocess.Popen(["mpv", "--fullscreen", *[str(f) for f in media_files]])
        except OSError as exc:
            QMessageBox.warning(self, "Couldn't open that", f"Could not run mpv: {exc}")

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
        # Rebuilds after the panel closes (not while it's open - a
        # modal .exec_() already blocks this thread until then) so a
        # "Show Browser on Main Screen" toggle flip shows up on the
        # toddler screen immediately, in the same running session,
        # rather than only on next boot. Cheap enough to do
        # unconditionally on every panel close rather than tracking
        # whether the toggle specifically changed.
        self._rebuild_grid()
