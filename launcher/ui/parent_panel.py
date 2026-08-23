"""Password-gated parent dashboard modal.

Authentication is NOT performed here: "Unlock" only pipes the typed
password to familyos-verify-auth (via stdin, never argv/env) to decide
whether to enable the action buttons below - the real, defense-in-depth
check happens again inside each privileged helper script when it
actually runs, after sudo has already elevated it to root. See
parental-tools/README.md for the full auth/privilege contract this
depends on.
"""
import json
import subprocess
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# Three levels up from ui/parent_panel.py is /opt/familyos/ in the
# installed image (repo root in a dev checkout) - see main_window.py's
# INSTALL_ROOT comment for the full reasoning. graphics/ is a sibling
# of launcher/ there, so icon paths resolve from here.
INSTALL_ROOT = Path(__file__).resolve().parent.parent.parent
ICONS_DIR = INSTALL_ROOT / "graphics" / "icons" / "parent"
NOT_IMPLEMENTED_EXIT_CODE = 2

# Client-side mirror of familyos-set-password's own MIN_LENGTH check -
# the script is the real, enforced gate (never trust client-side
# validation alone); this just avoids a pointless round-trip for an
# obviously-too-short password.
MIN_PASSWORD_LENGTH = 8

# NOT INSTALL_ROOT-relative: parental-tools/ is installed at
# /usr/local/lib/familyos/parental-tools (see familyos.blend's
# blend_postinst / the live-build auto/config equivalent), not under
# /opt/familyos/ alongside launcher/ and graphics/ - a previous version
# of this file assumed the same INSTALL_ROOT-relative layout as icons
# and pointed at a path that never existed
# ("/opt/familyos/parental-tools/..."), which is why every action here
# used to fail with "No such file or directory". The scripts are also
# invoked through sudo at this exact path -
# overlays/etc/sudoers.d/familyos-parent's NOPASSWD rule is scoped to
# /usr/local/bin/familyos-*, not the parental-tools/ source layout -
# since toddler has no privilege to reboot/poweroff/change iptables
# rules otherwise (a second, previously-undiscovered bug: nothing here
# was invoking sudo at all).
TOOLS_BIN_DIR = Path("/usr/local/bin")

# Same INSTALL_ROOT-relative reasoning as main_window.py's icon paths -
# launcher/ is a real directory (not installed piecemeal), so
# browser_kiosk.py is always a sibling of this file's own launcher/ui/
# parent, both in a dev checkout and at /opt/familyos/launcher/ in the
# installed image.
BROWSER_SCRIPT = INSTALL_ROOT / "launcher" / "browser_kiosk.py"


def _icon(name: str) -> QIcon:
    path = ICONS_DIR / name
    return QIcon(str(path)) if path.exists() else QIcon()


def _kid_icon(name: str) -> QIcon:
    # graphics/icons/kids/ (not ICONS_DIR, which is .../parent/) -
    # reused here since there's no parent-facing browser icon of its
    # own, and this one already exists and fits.
    path = INSTALL_ROOT / "graphics" / "icons" / "kids" / name
    return QIcon(str(path)) if path.exists() else QIcon()


class ParentPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parent Settings")
        self.setModal(True)

        self._authenticated_password: str | None = None
        # Not strictly QPushButton - also holds the sites QListWidget,
        # which every unlock-gated control here shares the same
        # enable/disable treatment with.
        self._action_buttons: list = []

        # Wrapped in a QScrollArea: this dialog has grown to ~20 rows
        # across several feature rounds (auth, allowed-sites list,
        # password change), and Openbox's rc.xml forces EVERY window,
        # including this dialog, to "maximized" - so its actual
        # on-screen size is the physical screen, not its natural
        # content size. On the smaller target resolutions (800x480),
        # the full content no longer fits, and a plain QVBoxLayout with
        # no scroll area has no way to express that - Qt just
        # compresses whichever widget has no explicit minimum size to
        # absorb the shortfall. A real boot test found the "Allowed
        # Websites" list appeared completely empty - it wasn't empty
        # (the seed data and this list are correctly wired together),
        # it was squeezed to near-zero visible height by this overflow.
        outer_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)

        password_row = QHBoxLayout()
        password_row.addWidget(QLabel("Enter parent password:"))
        lock_label = QLabel()
        lock_icon = _icon("lock.svg")
        if not lock_icon.isNull():
            lock_label.setPixmap(lock_icon.pixmap(20, 20))
        password_row.addWidget(lock_label)
        password_row.addStretch()
        layout.addLayout(password_row)

        unlock_row = QHBoxLayout()
        self._password_field = QLineEdit()
        self._password_field.setEchoMode(QLineEdit.Password)
        self._password_field.returnPressed.connect(self._unlock)
        unlock_row.addWidget(self._password_field)
        self._unlock_button = QPushButton("Unlock")
        self._unlock_button.clicked.connect(self._unlock)
        unlock_row.addWidget(self._unlock_button)
        layout.addLayout(unlock_row)

        # Every action button below starts disabled - _unlock() is the
        # only thing that enables them, and only once
        # familyos-verify-auth actually succeeds.
        self._add_action_button(layout, "Internet: ON", "network-wireless.svg", "familyos-net-toggle", "on")
        self._add_action_button(layout, "Internet: OFF", "network-wireless.svg", "familyos-net-toggle", "off")
        self._add_action_button(layout, "Reboot", "reboot.svg", "familyos-power", "reboot")
        self._add_action_button(layout, "Shutdown", "shutdown.svg", "familyos-power", "poweroff")

        remount_row = QHBoxLayout()
        remount_row.addWidget(QLabel("File to add to media folder:"))
        self._remount_path_field = QLineEdit()
        remount_row.addWidget(self._remount_path_field)
        remount_button = QPushButton(_icon("folder.svg"), "Remount RW (edit config)")
        remount_button.setEnabled(False)
        remount_button.clicked.connect(
            lambda: self._run("familyos-remount-rw", self._remount_path_field.text())
        )
        self._action_buttons.append(remount_button)
        remount_row.addWidget(remount_button)
        layout.addLayout(remount_row)

        volume_row = QHBoxLayout()
        volume_row.addWidget(QLabel("Volume cap (%):"))
        self._volume_spin = QSpinBox()
        self._volume_spin.setRange(0, 100)
        self._volume_spin.setValue(65)
        volume_row.addWidget(self._volume_spin)
        volume_button = QPushButton(_icon("volume.svg"), "Set Volume Cap")
        volume_button.setEnabled(False)
        volume_button.clicked.connect(
            lambda: self._run("familyos-volume", str(self._volume_spin.value()))
        )
        self._action_buttons.append(volume_button)
        volume_row.addWidget(volume_button)
        layout.addLayout(volume_row)

        # Web Browser is no longer a toddler-grid app (see Browser.md) -
        # this is the only way to reach it now, always parent-gated.
        # Not a privileged/sudo action (browser_kiosk.py needs no root),
        # but still start-disabled/unlock-gated like everything else
        # here for a consistent "nothing works until unlock" model.
        browser_button = QPushButton(_kid_icon("browser.svg"), "Open Browser")
        browser_button.setEnabled(False)
        browser_button.clicked.connect(self._open_browser)
        self._action_buttons.append(browser_button)
        layout.addWidget(browser_button)

        layout.addWidget(QLabel("Allowed Websites (browser homepage tiles):"))
        self._sites_list = QListWidget()
        self._sites_list.setEnabled(False)
        # Explicit floor so it always shows a few rows even under
        # layout pressure - defense-in-depth alongside the QScrollArea
        # wrapper above, not a substitute for it.
        self._sites_list.setMinimumHeight(120)
        self._action_buttons.append(self._sites_list)
        layout.addWidget(self._sites_list)

        add_site_row = QHBoxLayout()
        self._site_name_field = QLineEdit()
        self._site_name_field.setPlaceholderText("Name (e.g. PBS Kids)")
        add_site_row.addWidget(self._site_name_field)
        self._site_url_field = QLineEdit()
        self._site_url_field.setPlaceholderText("https://...")
        add_site_row.addWidget(self._site_url_field)
        add_site_button = QPushButton("Add Site")
        add_site_button.setEnabled(False)
        add_site_button.clicked.connect(self._add_site)
        self._action_buttons.append(add_site_button)
        add_site_row.addWidget(add_site_button)
        layout.addLayout(add_site_row)

        remove_site_button = QPushButton("Remove Selected Site")
        remove_site_button.setEnabled(False)
        remove_site_button.clicked.connect(self._remove_site)
        self._action_buttons.append(remove_site_button)
        layout.addWidget(remove_site_button)

        layout.addWidget(QLabel("Change Parent Password:"))
        # Deliberately a SEPARATE field from the initial unlock field
        # above, never pre-filled from self._authenticated_password -
        # changing the password re-requires proving the current one,
        # not just trusting that this dialog is already unlocked.
        # familyos-set-password re-verifies this independently via its
        # own require_parent_auth call regardless (defense-in-depth,
        # same as every other action here), but the UI shouldn't even
        # look like it's skipping that step.
        current_pw_row = QHBoxLayout()
        current_pw_row.addWidget(QLabel("Current password:"))
        self._current_pw_field = QLineEdit()
        self._current_pw_field.setEchoMode(QLineEdit.Password)
        current_pw_row.addWidget(self._current_pw_field)
        layout.addLayout(current_pw_row)

        new_pw_row = QHBoxLayout()
        new_pw_row.addWidget(QLabel("New password:"))
        self._new_pw_field = QLineEdit()
        self._new_pw_field.setEchoMode(QLineEdit.Password)
        new_pw_row.addWidget(self._new_pw_field)
        layout.addLayout(new_pw_row)

        confirm_pw_row = QHBoxLayout()
        confirm_pw_row.addWidget(QLabel("Confirm new password:"))
        self._confirm_pw_field = QLineEdit()
        self._confirm_pw_field.setEchoMode(QLineEdit.Password)
        confirm_pw_row.addWidget(self._confirm_pw_field)
        layout.addLayout(confirm_pw_row)

        change_pw_button = QPushButton(_icon("lock.svg"), "Change Password")
        change_pw_button.setEnabled(False)
        change_pw_button.clicked.connect(self._change_password)
        self._action_buttons.append(change_pw_button)
        layout.addWidget(change_pw_button)

        # Visible, discoverable way back to the toddler screen that
        # isn't "reboot the whole machine" - Openbox's rc.xml strips
        # every window's titlebar/border (decor=no, applications
        # section), including this dialog's, so there is otherwise no
        # close affordance at all beyond an undiscoverable Escape
        # keypress.
        close_button = QPushButton(_icon("close.svg"), "Close")
        close_button.clicked.connect(self.reject)
        layout.addWidget(close_button)

    def _add_action_button(self, layout, label, icon_name, script, *args):
        button = QPushButton(_icon(icon_name), label)
        button.setEnabled(False)
        button.clicked.connect(lambda: self._run(script, *args))
        self._action_buttons.append(button)
        layout.addWidget(button)

    def _unlock(self) -> None:
        password = self._password_field.text()
        script_path = TOOLS_BIN_DIR / "familyos-verify-auth"
        try:
            result = subprocess.run(
                ["sudo", str(script_path)],
                input=password,
                text=True,
                capture_output=True,
                timeout=15,
            )
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not run familyos-verify-auth: {exc}")
            return

        if result.returncode == 0:
            self._authenticated_password = password
            for button in self._action_buttons:
                button.setEnabled(True)
            self._unlock_button.setEnabled(False)
            self._password_field.setEnabled(False)
            self._refresh_sites_list()
        else:
            QMessageBox.warning(self, "Failed", result.stderr or "Authentication failed.")
        self._password_field.clear()

    def _run(self, script_name: str, *args: str) -> None:
        if self._authenticated_password is None:
            # Shouldn't be reachable - action buttons stay disabled
            # until _unlock() succeeds - but never attempt a
            # privileged action with no verified password regardless.
            return
        script_path = TOOLS_BIN_DIR / script_name
        try:
            result = subprocess.run(
                ["sudo", str(script_path), *args],
                input=self._authenticated_password,
                text=True,
                capture_output=True,
                timeout=15,
            )
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not run {script_name}: {exc}")
            return

        if result.returncode == 0:
            QMessageBox.information(self, "Done", result.stdout or "Done.")
        elif result.returncode == NOT_IMPLEMENTED_EXIT_CODE:
            QMessageBox.information(
                self, "Not available yet", "This control lands in Phase 3."
            )
        else:
            QMessageBox.warning(
                self, "Failed", result.stderr or "Authentication failed."
            )

    def _change_password(self) -> None:
        current = self._current_pw_field.text()
        new = self._new_pw_field.text()
        confirm = self._confirm_pw_field.text()

        if not current:
            QMessageBox.warning(self, "Missing info", "Enter your current password.")
            return
        if not new:
            QMessageBox.warning(self, "Missing info", "Enter a new password.")
            return
        if len(new) < MIN_PASSWORD_LENGTH:
            QMessageBox.warning(
                self, "Too short",
                f"New password must be at least {MIN_PASSWORD_LENGTH} characters.",
            )
            return
        if new != confirm:
            QMessageBox.warning(self, "Doesn't match", "New password and confirmation don't match.")
            return

        script_path = TOOLS_BIN_DIR / "familyos-set-password"
        try:
            result = subprocess.run(
                ["sudo", str(script_path)],
                # Two-line stdin protocol: line 1 is the CURRENT
                # password (consumed by familyos-set-password's own
                # require_parent_auth call - the real re-verification
                # gate), line 2 is the new password. Neither ever goes
                # via argv/env, same reason as every other script here.
                input=f"{current}\n{new}\n",
                text=True,
                capture_output=True,
                timeout=15,
            )
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not run familyos-set-password: {exc}")
            return

        self._current_pw_field.clear()
        self._new_pw_field.clear()
        self._confirm_pw_field.clear()

        if result.returncode == 0:
            QMessageBox.information(self, "Done", "Parent password changed.")
        else:
            QMessageBox.warning(
                self, "Failed",
                result.stderr or "Could not change password - check current password.",
            )

    def _open_browser(self) -> None:
        try:
            subprocess.Popen(["python3", str(BROWSER_SCRIPT)])
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not open browser: {exc}")

    def _sites_command(self, *args: str):
        """Runs familyos-sites with the already-verified password, same
        pattern as _run() - but returns the result instead of showing a
        dialog, since callers here need to parse stdout (list) or
        chain a refresh (add/remove) rather than just report success.
        """
        if self._authenticated_password is None:
            return None
        try:
            return subprocess.run(
                ["sudo", str(TOOLS_BIN_DIR / "familyos-sites"), *args],
                input=self._authenticated_password,
                text=True,
                capture_output=True,
                timeout=15,
            )
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not run familyos-sites: {exc}")
            return None

    def _refresh_sites_list(self) -> None:
        result = self._sites_command("list")
        if result is None:
            return
        if result.returncode != 0:
            QMessageBox.warning(self, "Failed", result.stderr or "Could not list sites.")
            return
        try:
            sites = json.loads(result.stdout).get("sites", [])
        except ValueError:
            sites = []

        self._sites_list.clear()
        for site in sites:
            item = QListWidgetItem(f"{site.get('name', '?')}  ({site.get('host', '?')})")
            item.setData(Qt.UserRole, site.get("host", ""))
            self._sites_list.addItem(item)

    def _add_site(self) -> None:
        name = self._site_name_field.text().strip()
        url = self._site_url_field.text().strip()
        if not name or not url:
            QMessageBox.warning(self, "Missing info", "Enter both a name and a URL.")
            return
        result = self._sites_command("add", name, url)
        if result is None:
            return
        if result.returncode == 0:
            self._site_name_field.clear()
            self._site_url_field.clear()
            self._refresh_sites_list()
        else:
            QMessageBox.warning(self, "Failed", result.stderr or "Could not add site.")

    def _remove_site(self) -> None:
        item = self._sites_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Nothing selected", "Select a site to remove first.")
            return
        host = item.data(Qt.UserRole)
        result = self._sites_command("remove", host)
        if result is None:
            return
        if result.returncode == 0:
            self._refresh_sites_list()
        else:
            QMessageBox.warning(self, "Failed", result.stderr or "Could not remove site.")
