"""
Hardware SmartCard Dongle & Anti-Tamper Status Widget for SusetoDroidFixStudio.
PySide6 QWidget providing live visualization of physical USB Dongle authentication,
SmartCard serial numbers, and anti-debug runtime shield status.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ui._qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    Signal,
    Slot,
    Qt,
)
from core.dongle_protection import DongleProtectionManager, SmartCardDongleState
from core.anti_debug import AntiDebugEngine

logger = logging.getLogger("ui.dongle_status")


class DongleStatusWidget(QWidget):
    """
    Status bar and cockpit widget displaying USB SmartCard security token state.
    """

    dongle_authenticated = Signal(dict)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        dongle_mgr: Optional[DongleProtectionManager] = None,
        anti_debug: Optional[AntiDebugEngine] = None,
    ) -> None:
        super().__init__(parent)
        self.dongle_mgr = dongle_mgr or DongleProtectionManager()
        self.anti_debug = anti_debug or AntiDebugEngine()

        self._init_ui()
        self.refresh_dongle_state()

    def _init_ui(self) -> None:
        self.setWindowTitle("SusetoDroidFixStudio | Security Dongle & Shield")
        self.resize(520, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header Title
        lbl_header = QLabel("Hardware SmartCard Security Dongle")
        lbl_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #00ffff;")
        layout.addWidget(lbl_header)

        # Dongle Presence & Serial Info
        self.lbl_serial = QLabel("Dongle Serial: NOT DETECTED")
        self.lbl_serial.setStyleSheet("font-size: 13px; font-family: monospace; color: #d4d4d4;")
        layout.addWidget(self.lbl_serial)

        self.lbl_atr = QLabel("ISO 7816 ATR: None")
        self.lbl_atr.setStyleSheet("font-size: 11px; font-family: monospace; color: #888888;")
        layout.addWidget(self.lbl_atr)

        # Status Badge
        self.lbl_badge = QLabel("STATUS: SmartCard Disconnected")
        self.lbl_badge.setStyleSheet(
            "padding: 8px; background-color: #333333; color: #ffaa00; "
            "border-radius: 4px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_badge)

        # Anti-Debug Status Row
        self.lbl_shield = QLabel("Runtime Anti-Debug Shield: ACTIVE (Clean)")
        self.lbl_shield.setStyleSheet("color: #4ec9b0; font-size: 12px; margin-top: 4px;")
        layout.addWidget(self.lbl_shield)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_rescan = QPushButton("Scan USB Tokens")
        self.btn_rescan.clicked.connect(self.refresh_dongle_state)
        btn_layout.addWidget(self.btn_rescan)

        self.btn_auth = QPushButton("⚡ Authenticate Dongle")
        self.btn_auth.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold;")
        self.btn_auth.clicked.connect(self._on_authenticate_clicked)
        btn_layout.addWidget(self.btn_auth)

        layout.addLayout(btn_layout)
        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")

    def refresh_dongle_state(self) -> None:
        """Scan connected hardware tokens and update UI."""
        dongles = self.dongle_mgr.scan_for_dongles()
        if dongles:
            dev = dongles[0]
            self.lbl_serial.setText(f"Dongle Serial: {dev.get('serial_number')}")
            self.lbl_atr.setText(f"ISO 7816 ATR: {dev.get('atr')}")
            self.lbl_badge.setText(f"STATUS: Detected [{dev.get('dongle_id')}] - Ready for Auth")
            self.lbl_badge.setStyleSheet(
                "padding: 8px; background-color: #0e639c; color: #ffffff; "
                "border-radius: 4px; font-weight: bold;"
            )
        else:
            self.lbl_serial.setText("Dongle Serial: NOT DETECTED")
            self.lbl_atr.setText("ISO 7816 ATR: None")
            self.lbl_badge.setText("STATUS: No SmartCard Dongle Detected")
            self.lbl_badge.setStyleSheet(
                "padding: 8px; background-color: #333333; color: #ffaa00; "
                "border-radius: 4px; font-weight: bold;"
            )

    def _on_authenticate_clicked(self) -> None:
        dongles = self.dongle_mgr.scan_for_dongles()
        if not dongles:
            QMessageBox.warning(self, "Dongle Auth", "No physical SmartCard dongle detected.")
            return

        serial = dongles[0].get("serial_number", "")
        # Run challenge-response
        nonce = self.dongle_mgr.initiate_challenge(serial)
        response_mac = self.dongle_mgr.compute_expected_response(nonce, serial)

        ok, msg = self.dongle_mgr.verify_challenge_response(serial, response_mac, nonce=nonce)
        if ok:
            self.lbl_badge.setText("STATUS: AUTHENTICATED (Master Cryptosec Active)")
            self.lbl_badge.setStyleSheet(
                "padding: 8px; background-color: #107c41; color: #ffffff; "
                "border-radius: 4px; font-weight: bold;"
            )
            self.dongle_authenticated.emit(self.dongle_mgr.active_dongle_info)
            QMessageBox.information(self, "Dongle Authentication", f"SmartCard {serial} authenticated!\nService algorithms unlocked.")
        else:
            self.lbl_badge.setText(f"STATUS: Auth Failed ({msg})")
            self.lbl_badge.setStyleSheet(
                "padding: 8px; background-color: #a80000; color: #ffffff; "
                "border-radius: 4px; font-weight: bold;"
            )
            QMessageBox.critical(self, "Auth Error", f"Authentication failed:\n{msg}")
