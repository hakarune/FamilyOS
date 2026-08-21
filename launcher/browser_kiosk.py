#!/usr/bin/env python3
"""FamilyOS kiosk web browser - a bare QWebEngineView, not a full
browser app.

Deliberately NOT built on Min or Falkon: neither actually supports the
lockdown Browser.md describes (no nav bar, no new tabs, no URL entry).
Both are full browser apps with their own UI/keybinding layer that
would need to be individually audited and disabled, and both were
found to leak escape hatches (Min's Focus Mode still allows Ctrl+L to
open navigation; Falkon has no native lockdown mode at all, only a
`--fullscreen` toggle). A bare QWebEngineView has none of that
browser-chrome layer to begin with - there is no menu, no keybindings,
no toolbar unless this file adds one, so there is no escape hatch to
audit away. Min is also Electron-based and has shipped no i386 build
since Electron dropped 32-bit Linux support (~2018), which would have
broken the i386/Eee PC target outright.
"""
import os
import sys
from pathlib import Path

# Must be set before any Qt/WebEngine import - QtWebEngine reads this
# at its own initialization. Disables Chromium's automatic DNS-over-HTTPS
# upgrade (base::Feature kDnsOverHttpsUpgrade) so the system's
# locked-down /etc/resolv.conf (see overlays/etc/init.d/familyos-dns-lock)
# can't be silently bypassed by the browser resolving through an
# encrypted DoH endpoint instead. This app never exposes Chromium's own
# settings UI (bare QWebEngineView, no chrome), so the automatic-upgrade
# path is the ONLY way DoH could activate here at all - QtWebEngine
# embeds Chromium's content/net layers, not the chrome/browser layer
# that owns the pref-/enterprise-policy-driven explicit DoH mode a full
# browser exposes, so there's no separate override path to worry about.
# NOTE: this is reasoned from Chromium's architecture, not confirmed by
# running the actual built image (no way to do that in this repo's
# authoring environment) - whether the automatic-upgrade default is
# even active in this specific unbranded Chromium build (~87, bundled
# by Qt5 WebEngine 5.15) is a residual unknown. Smoke-test before
# shipping. The DoH IP blocklist in parental-tools/lib/net-rules.sh is
# defense-in-depth underneath this, not a substitute for it.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-features=DnsOverHttpsUpgrade"
os.environ.pop("QTWEBENGINE_REMOTE_DEBUGGING", None)  # defensive: no devtools

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEnginePage, QWebEngineView
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget

HOME_URL = "https://www.kidzsearch.com"

# this file lives at /opt/familyos/launcher/browser_kiosk.py in the
# installed image (repo root's launcher/ in a dev checkout) - graphics/
# is a sibling of launcher/ in both cases, see ui/main_window.py's
# INSTALL_ROOT comment for the full reasoning.
INSTALL_ROOT = Path(__file__).resolve().parent.parent
CLOSE_ICON = INSTALL_ROOT / "graphics" / "icons" / "parent" / "close.svg"
WINDOW_ICON = INSTALL_ROOT / "graphics" / "branding" / "familyos-logo-128.png"

# Domains the toddler session is allowed to navigate to at all - both
# typed/link navigation and in-page JS redirects go through this (see
# AllowlistPage.acceptNavigationRequest below). Not a substitute for
# the system-level DNS/iptables filtering - this is an additional,
# independent layer, not the only one.
ALLOWED_HOSTS = {
    "www.kidzsearch.com",
    "kidzsearch.com",
}


class AllowlistPage(QWebEnginePage):
    def acceptNavigationRequest(self, url: QUrl, _nav_type, _is_main_frame: bool) -> bool:
        if url.scheme() not in ("http", "https"):
            return False  # blocks file:/javascript:/data: etc. outright
        return url.host() in ALLOWED_HOSTS

    def createWindow(self, _win_type):
        # Blocks window.open()/target=_blank popups - without this
        # override, QWebEngineView happily opens a second, completely
        # unrestricted window that bypasses acceptNavigationRequest
        # entirely.
        return None


class KioskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("FamilyOS Browser")
        if WINDOW_ICON.exists():
            self.setWindowIcon(QIcon(str(WINDOW_ICON)))

        self._view = QWebEngineView()
        page = AllowlistPage(self._view)
        self._view.setPage(page)
        self._view.setContextMenuPolicy(Qt.NoContextMenu)

        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, False)

        page.fullScreenRequested.connect(lambda request: request.reject())
        page.featurePermissionRequested.connect(self._deny_feature_request)

        done_row = QHBoxLayout()
        done_icon = QIcon(str(CLOSE_ICON)) if CLOSE_ICON.exists() else QIcon()
        done_button = QPushButton(done_icon, "Done")
        done_button.setObjectName("browserDoneButton")
        done_button.clicked.connect(QApplication.instance().quit)
        done_row.addWidget(done_button)
        done_row.addStretch()

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addLayout(done_row)
        layout.addWidget(self._view)

        self._view.setUrl(QUrl(HOME_URL))

    @staticmethod
    def _deny_feature_request(origin, feature) -> None:
        page = QApplication.instance().activeWindow()
        # feature permission requests (geolocation/notifications/camera
        # etc.) are always denied - none of these are relevant to a
        # kid-safe search page and each is its own chrome-level prompt
        # surface if left unhandled.
        if page is not None:
            page.setFeaturePermission(
                origin, feature, QWebEnginePage.PermissionDeniedByUser
            )


def main() -> int:
    app = QApplication(sys.argv)
    window = KioskWindow()
    window.showFullScreen()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
