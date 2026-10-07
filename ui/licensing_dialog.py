"""
Licensing & Activation Dialog for SusetoDroidFixStudio.
PySide6 QWidget/QDialog dialog providing HWID inspection, license key verification,
and offline .lic file import.
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from ui._qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    Signal,
    Slot,
    Qt,
)
from core.licensing_engine import LicensingEngine

logger = logging.getLogger("ui.licensing_dialog")


class LicensingDialog(QWidget):
    """
    License management dialog providing hardware registration and activation workflows.
    """

    activation_succeeded = Signal(dict)
    activation_failed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None, engine: Optional[LicensingEngine] = None) -> None:
        super().__init__(parent)
        self.engine = engine or LicensingEngine()
        self.hwid = self.engine.get_hardware_id()
        self._current_status: Dict[str, Any] = {"valid": False, "reason": "UNREGISTERED"}

        self._init_ui()
        self._check_existing_license()

    def _init_ui(self) -> None:
        self.setWindowTitle("SusetoDroidFixStudio | License & Hardware Activation")
        self.resize(560, 380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Title
        lbl_header = QLabel("Hardware Fingerprint & Licensing Manager")
        lbl_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #00ffff;")
        layout.addWidget(lbl_header)

        # HWID Display Field
        lbl_hwid_desc = QLabel("System Hardware ID (HWID):")
        layout.addWidget(lbl_hwid_desc)

        hwid_layout = QHBoxLayout()
        self.input_hwid = QLineEdit(self.hwid)
        self.input_hwid.setStyleSheet("background-color: #252526; color: #4ec9b0; font-weight: bold; font-family: monospace;")
        self.input_hwid.setEnabled(False)
        hwid_layout.addWidget(self.input_hwid, stretch=1)

        self.btn_copy_hwid = QPushButton("Copy HWID")
        self.btn_copy_hwid.clicked.connect(self._on_copy_hwid)
        hwid_layout.addWidget(self.btn_copy_hwid)
        layout.addLayout(hwid_layout)

        # License Key Input
        lbl_key_desc = QLabel("Enter License Key (SDS-...):")
        layout.addWidget(lbl_key_desc)

        self.input_license_key = QLineEdit()
        self.input_license_key.setPlaceholderText("SDS-eyJwIjogeyJjbGllbnQiOiAiLi4u")
        self.input_license_key.setStyleSheet("background-color: #252526; color: #d4d4d4;")
        layout.addWidget(self.input_license_key)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_activate = QPushButton("Activate License")
        self.btn_activate.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold;")
        self.btn_activate.clicked.connect(self._on_activate_clicked)
        btn_layout.addWidget(self.btn_activate)

        self.btn_load_file = QPushButton("Load .lic Token")
        self.btn_load_file.clicked.connect(self._on_load_file_clicked)
        btn_layout.addWidget(self.btn_load_file)
        layout.addLayout(btn_layout)

        # Status Display Banner
        self.lbl_status = QLabel("STATUS: Unregistered / Trial Mode")
        self.lbl_status.setStyleSheet(
            "padding: 8px; background-color: #333333; color: #ffaa00; "
            "border-radius: 4px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_status)

        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")

    def _check_existing_license(self) -> None:
        """Attempt to load default license token from application root."""
        res = self.engine.load_and_verify_license_file("license.lic")
        if res.get("valid"):
            self._update_status_active(res)

    def _update_status_active(self, res: Dict[str, Any]) -> None:
        self._current_status = res
        client = res.get("client", "Licensed User")
        tier = res.get("tier", "STANDARD")
        expires = res.get("expires_formatted", "Never")
        self.lbl_status.setText(f"STATUS: ACTIVE [{tier}] | Client: {client} | Expires: {expires}")
        self.lbl_status.setStyleSheet(
            "padding: 8px; background-color: #107c41; color: #ffffff; "
            "border-radius: 4px; font-weight: bold;"
        )

    def _on_copy_hwid(self) -> None:
        try:
            # Copy to clipboard if available
            from ui._qt_compat import QApplication
            app = QApplication.instance()
            if app and hasattr(app, "clipboard"):
                app.clipboard().setText(self.hwid)
        except Exception:
            pass
        self.lbl_status.setText(f"HWID '{self.hwid}' copied to clipboard.")

    def _on_activate_clicked(self) -> None:
        key = self.input_license_key.text().strip()
        if not key:
            QMessageBox.warning(self, "Activation", "Please enter a valid license key.")
            return

        res = self.engine.verify_license_key(key, target_hwid=self.hwid)
        if res.get("valid"):
            self.engine.save_license_file(key, "license.lic")
            self._update_status_active(res)
            self.activation_succeeded.emit(res)
            QMessageBox.information(self, "Activation", f"Activation successful!\nClient: {res.get('client')}\nTier: {res.get('tier')}")
        else:
            reason = res.get("message", "Unknown error")
            self.lbl_status.setText(f"STATUS: Activation Failed ({reason})")
            self.lbl_status.setStyleSheet("padding: 8px; background-color: #a80000; color: #ffffff; border-radius: 4px;")
            self.activation_failed.emit(reason)
            QMessageBox.critical(self, "Activation Error", f"Activation failed:\n{reason}")

    def _on_load_file_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select License File", "", "License Files (*.lic);;All Files (*.*)"
        )
        if file_path:
            res = self.engine.load_and_verify_license_file(file_path)
            if res.get("valid"):
                self.engine.save_license_file(Path(file_path).read_text(encoding="utf-8").strip(), "license.lic")
                self._update_status_active(res)
                self.activation_succeeded.emit(res)
                QMessageBox.information(self, "License File", f"License validated from file!\nClient: {res.get('client')}")
            else:
                reason = res.get("message", "Invalid file")
                self.lbl_status.setText(f"STATUS: License Invalid ({reason})")
                self.activation_failed.emit(reason)
                QMessageBox.critical(self, "License Error", f"Invalid license file:\n{reason}")
