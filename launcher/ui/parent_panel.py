"""Password-gated parent dashboard modal.

Authentication is NOT performed here: this dialog collects the parent's
password and pipes it (via stdin, never argv/env) to the privileged
helper script for the requested action. Each helper script re-checks
the password itself (via PAM) after sudo has already elevated it to
root - see parental-tools/README.md for the full auth/privilege
contract this depends on.
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
# INSTALL_ROOT comment for the full reasoning. parental-tools/ and
# graphics/ are both siblings of launcher/ there.
INSTALL_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = INSTALL_ROOT / "parental-tools"
ICONS_DIR = INSTALL_ROOT / "graphics" / "icons" / "parent"
NOT_IMPLEMENTED_EXIT_CODE = 2


def _icon(name: str) -> QIcon:
    path = ICONS_DIR / name
    return QIcon(str(path)) if path.exists() else QIcon()


class ParentPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parent Settings")
        self.setModal(True)

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

        self._password_field = QLineEdit()
        self._password_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(self._password_field)

        self._add_action_button(layout, "Internet: ON", "network-wireless.svg", "familyos-net-toggle", "on")
        self._add_action_button(layout, "Internet: OFF", "network-wireless.svg", "familyos-net-toggle", "off")
        self._add_action_button(layout, "Reboot", "reboot.svg", "familyos-power", "reboot")
        self._add_action_button(layout, "Shutdown", "shutdown.svg", "familyos-power", "poweroff")

        remount_row = QHBoxLayout()
        remount_row.addWidget(QLabel("File to add to media folder:"))
        self._remount_path_field = QLineEdit()
        remount_row.addWidget(self._remount_path_field)
        remount_button = QPushButton(_icon("folder.svg"), "Remount RW (edit config)")
        remount_button.clicked.connect(
            lambda: self._run("familyos-remount-rw", self._remount_path_field.text())
        )
        remount_row.addWidget(remount_button)
        layout.addLayout(remount_row)

        volume_row = QHBoxLayout()
        volume_row.addWidget(QLabel("Volume cap (%):"))
        self._volume_spin = QSpinBox()
        self._volume_spin.setRange(0, 100)
        self._volume_spin.setValue(65)
        volume_row.addWidget(self._volume_spin)
        volume_button = QPushButton(_icon("volume.svg"), "Set Volume Cap")
        volume_button.clicked.connect(
            lambda: self._run("familyos-volume", str(self._volume_spin.value()))
        )
        volume_row.addWidget(volume_button)
        layout.addLayout(volume_row)

    def _add_action_button(self, layout, label, icon_name, script, *args):
        button = QPushButton(_icon(icon_name), label)
        button.clicked.connect(lambda: self._run(script, *args))
        layout.addWidget(button)

    def _run(self, script_name: str, *args: str) -> None:
        password = self._password_field.text()
        script_path = TOOLS_DIR / script_name
        try:
            result = subprocess.run(
                [str(script_path), *args],
                input=password,
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
        self._password_field.clear()
