"""Password-gated parent dashboard modal.

Authentication is NOT performed here: "Unlock" only pipes the typed
password to familyos-verify-auth (via stdin, never argv/env) to decide
whether to enable the action buttons below - the real, defense-in-depth
check happens again inside each privileged helper script when it
actually runs, after sudo has already elevated it to root. See
parental-tools/README.md for the full auth/privilege contract this
depends on.
"""
import subprocess
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

# Three levels up from ui/parent_panel.py is /opt/familyos/ in the
# installed image (repo root in a dev checkout) - see main_window.py's
# INSTALL_ROOT comment for the full reasoning. graphics/ is a sibling
# of launcher/ there, so icon paths resolve from here.
INSTALL_ROOT = Path(__file__).resolve().parent.parent.parent
ICONS_DIR = INSTALL_ROOT / "graphics" / "icons" / "parent"
NOT_IMPLEMENTED_EXIT_CODE = 2

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


def _icon(name: str) -> QIcon:
    path = ICONS_DIR / name
    return QIcon(str(path)) if path.exists() else QIcon()


class ParentPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parent Settings")
        self.setModal(True)

        self._authenticated_password: str | None = None
        self._action_buttons: list[QPushButton] = []

        layout = QVBoxLayout(self)
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
