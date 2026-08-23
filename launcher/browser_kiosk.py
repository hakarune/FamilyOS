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
import json
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

# this file lives at /opt/familyos/launcher/browser_kiosk.py in the
# installed image (repo root's launcher/ in a dev checkout) - graphics/
# is a sibling of launcher/ in both cases, see ui/main_window.py's
# INSTALL_ROOT comment for the full reasoning.
INSTALL_ROOT = Path(__file__).resolve().parent.parent
CLOSE_ICON = INSTALL_ROOT / "graphics" / "icons" / "parent" / "close.svg"
HOME_ICON = INSTALL_ROOT / "graphics" / "icons" / "parent" / "settings.svg"
WINDOW_ICON = INSTALL_ROOT / "graphics" / "branding" / "familyos-logo-128.png"

# Parent-curated site list (managed by ../parental-tools/familyos-sites,
# via the Parent Panel's "Allowed Websites" section) and the local
# tile page rendered from it (../parental-tools/lib/render-homepage.py).
# Both live under /var/lib/familyos, a live-boot persistence union point
# (see iso-builder/live-build/persistence-media/persistence.conf) so
# parent edits survive a reboot when the persistence partition is
# present, degrading safely to the build-time default seed otherwise -
# same pattern already used for /home/toddler/media.
SITES_FILE = Path("/var/lib/familyos/allowed-sites.json")
HOMEPAGE_FILE = Path("/var/lib/familyos/homepage.html")
HOME_URL = QUrl.fromLocalFile(str(HOMEPAGE_FILE))

# Fallback used only if SITES_FILE is missing/unreadable/malformed (it
# shouldn't be - familyos.blend's blend_postinst always seeds it - but
# a browser that can't navigate ANYWHERE if that file is ever damaged
# is a worse failure mode than falling back to the one host this
# project has always shipped).
_FALLBACK_HOSTS = frozenset({"www.kidzsearch.com", "kidzsearch.com"})


def _load_allowed_hosts() -> frozenset:
    try:
        data = json.loads(SITES_FILE.read_text(encoding="utf-8"))
        hosts = {s["host"].lower() for s in data.get("sites", []) if s.get("host")}
        return frozenset(hosts) if hosts else _FALLBACK_HOSTS
    except (OSError, ValueError, KeyError, TypeError):
        return _FALLBACK_HOSTS


# Domains the toddler session is allowed to navigate to at all - both
# typed/link navigation and in-page JS redirects go through this (see
# AllowlistPage.acceptNavigationRequest below). Not a substitute for
# the system-level DNS/iptables filtering - this is an additional,
# independent layer, not the only one. Loaded once at process start,
# not live-reloaded while running - a parent's edit takes effect the
# next time the browser is (re)launched from the Parent Panel, not
# mid-session.
ALLOWED_HOSTS = _load_allowed_hosts()

# Known video-embed rendering infrastructure, NOT a navigable
# destination in its own right and NOT parent-editable - separate from
# ALLOWED_HOSTS on purpose, so the Parent Panel's site list only ever
# shows sites a parent actually chose. KidzSearch's KidzTube section
# embeds curated videos via YouTube's iframe embed player (confirmed:
# KidzTube curates/filters YouTube content, it does not host video
# files itself) - since acceptNavigationRequest below checks EVERY
# navigation including iframe loads (ignores the is_main_frame
# parameter deliberately, see below), an embedded player's own iframe
# navigation to youtube.com/youtube-nocookie.com would otherwise be
# blocked by the exact same mechanism that blocks top-level navigation,
# and the video simply wouldn't play. Both youtube.com and
# youtube-nocookie.com are allowed here since the exact embed domain
# KidzSearch's player code uses wasn't confirmed (kidzsearch.com blocks
# automated fetches) - see devuan-build-docs/confirmed-browser-homepage-domains.txt.
# RESIDUAL RISK, not fully resolved: standard YouTube embeds often
# still carry their own "Watch on YouTube" link/logo depending on
# player parameters KidzSearch's embed code controls, which could let a
# child navigate to the full open YouTube site from inside an embedded
# player - not confirmed either way without live testing. Flagged as an
# open item, not silently assumed safe.
TRUSTED_EMBED_HOSTS = frozenset({"www.youtube.com", "www.youtube-nocookie.com"})


class AllowlistPage(QWebEnginePage):
    def acceptNavigationRequest(self, url: QUrl, _nav_type, _is_main_frame: bool) -> bool:
        if url.scheme() == "file":
            # Exact-path match, not "any file: URL" - a URL like
            # file:///etc/passwd must NOT be let through just because
            # the scheme matches. This is the only file: URL that
            # should ever load: the local homepage this same process
            # generates from parent-curated data, nothing else.
            return Path(url.toLocalFile()).resolve() == HOMEPAGE_FILE.resolve()
        if url.scheme() not in ("http", "https"):
            return False  # blocks javascript:/data: etc. outright
        # Note: this check governs NAVIGATION (top-level page loads,
        # link clicks, JS redirects, and - since is_main_frame is
        # deliberately ignored - iframe loads too). It does NOT govern
        # sub-resource fetches an already-loaded allowed page's own
        # scripts make (video segments, XHR/fetch API calls, images,
        # trackers) - QtWebEngine's acceptNavigationRequest simply
        # isn't invoked for those. A locked-down page can still talk to
        # arbitrary third-party CDNs/analytics in the background, same
        # as visiting that site in any other browser - the system-level
        # DNS lockdown (overlays/etc/init.d/familyos-dns-lock) and
        # DoH-resolver blocklist (parental-tools/lib/net-rules.sh) are
        # the actual defense against that, not this allowlist. See
        # devuan-build-docs/confirmed-browser-homepage-domains.txt.
        return url.host().lower() in ALLOWED_HOSTS or url.host().lower() in TRUSTED_EMBED_HOSTS

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

        top_row = QHBoxLayout()
        home_icon = QIcon(str(HOME_ICON)) if HOME_ICON.exists() else QIcon()
        home_button = QPushButton(home_icon, "Home")
        home_button.setObjectName("browserHomeButton")
        home_button.clicked.connect(lambda: self._view.setUrl(HOME_URL))
        top_row.addWidget(home_button)

        done_icon = QIcon(str(CLOSE_ICON)) if CLOSE_ICON.exists() else QIcon()
        done_button = QPushButton(done_icon, "Done")
        done_button.setObjectName("browserDoneButton")
        done_button.clicked.connect(QApplication.instance().quit)
        top_row.addWidget(done_button)
        top_row.addStretch()

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addLayout(top_row)
        layout.addWidget(self._view)

        self._view.setUrl(HOME_URL)

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
