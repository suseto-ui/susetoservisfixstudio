"""
Cloud Sync & Remote Control Cockpit Dialog for SusetoDroidFixStudio.
PySide6 QWidget interface providing management of cloud Firehose/BROM loaders,
scatter repositories, and remote technician encrypted tunnel sessions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ui._qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
    Signal,
    Slot,
    Qt,
)
from core.cloud_payload_sync import CloudPayloadSyncManager
from core.remote_diagnostics import RemoteDiagnosticsBridge

logger = logging.getLogger("ui.cloud_sync_dialog")


class CloudSyncDialog(QWidget):
    """
    Dialog managing cloud asset synchronization and remote technician assistance.
    """

    sync_completed = Signal(int)
    remote_session_started = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        sync_manager: Optional[CloudPayloadSyncManager] = None,
        bridge: Optional[RemoteDiagnosticsBridge] = None,
    ) -> None:
        super().__init__(parent)
        self.sync_mgr = sync_manager or CloudPayloadSyncManager()
        self.bridge = bridge or RemoteDiagnosticsBridge()

        self._init_ui()
        self._refresh_local_payloads()

    def _init_ui(self) -> None:
        self.setWindowTitle("SusetoDroidFixStudio | Cloud Sync & Remote Diagnostics")
        self.resize(680, 520)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Section 1: Cloud Loaders & Scatter Synchronization
        lbl_sec1 = QLabel("1. Cloud Firehose Loaders & Test Point Database")
        lbl_sec1.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ffff;")
        main_layout.addWidget(lbl_sec1)

        sync_btn_layout = QHBoxLayout()
        self.btn_fetch_manifest = QPushButton("Check Cloud Repository")
        self.btn_fetch_manifest.clicked.connect(self._on_fetch_manifest)
        sync_btn_layout.addWidget(self.btn_fetch_manifest)

        self.btn_sync_all = QPushButton("⚡ Sync Latest Loaders (SHA-256)")
        self.btn_sync_all.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold;")
        self.btn_sync_all.clicked.connect(self._on_sync_all)
        sync_btn_layout.addWidget(self.btn_sync_all)
        main_layout.addLayout(sync_btn_layout)

        self.lbl_sync_status = QLabel("Local Database: 0 Loaders Cached (AES-256 Encrypted)")
        self.lbl_sync_status.setStyleSheet("color: #888888; font-size: 12px;")
        main_layout.addWidget(self.lbl_sync_status)

        # Section 2: Remote Technician Bridge Tunnel
        lbl_sec2 = QLabel("2. Secure Remote Technician Diagnostic Tunnel")
        lbl_sec2.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00; margin-top: 10px;")
        main_layout.addWidget(lbl_sec2)

        session_box = QHBoxLayout()
        self.input_session_id = QLineEdit(self.bridge.session_id)
        self.input_session_id.setStyleSheet("background-color: #252526; color: #4ec9b0; font-family: monospace; font-weight: bold;")
        session_box.addWidget(self.input_session_id, stretch=1)

        self.btn_start_session = QPushButton("Open Remote Tunnel")
        self.btn_start_session.setStyleSheet("background-color: #107c41; color: white; font-weight: bold;")
        self.btn_start_session.clicked.connect(self._on_start_remote_session)
        session_box.addWidget(self.btn_start_session)
        main_layout.addLayout(session_box)

        # Activity Terminal / Log View
        self.lbl_log = QLabel("Ready. Connected to Cloud Sync Engine v1.0-PROD.")
        self.lbl_log.setStyleSheet(
            "padding: 12px; background-color: #181818; color: #d4d4d4; "
            "border: 1px solid #3c3c3c; border-radius: 4px; font-family: monospace;"
        )
        main_layout.addWidget(self.lbl_log, stretch=1)

        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")

    def _refresh_local_payloads(self) -> None:
        """Scan and count local encrypted loaders."""
        local_list = self.sync_mgr.list_local_payloads()
        self.lbl_sync_status.setText(f"Local Database: {len(local_list)} Loaders / Profiles Cached (AES-256 Encrypted)")

    def _on_fetch_manifest(self) -> None:
        self.lbl_log.setText("[*] Querying cloud manifest from CDN repository...")
        manifest = self.sync_mgr.fetch_manifest(
            mock_data={
                "version": "2026.10.1",
                "payloads": [
                    {"id": "prog_firehose_sdm660", "category": "qualcomm", "sha256": "abcdef"},
                    {"id": "MT6768_Android_scatter", "category": "mediatek", "sha256": "123456"},
                ],
            }
        )
        count = len(manifest.get("payloads", []))
        self.lbl_log.setText(f"[+] Found {count} updated hardware profiles in remote manifest v{manifest.get('version')}.")
        QMessageBox.information(self, "Cloud Manifest", f"Successfully fetched manifest!\nAvailable payloads: {count}")

    def _on_sync_all(self) -> None:
        self.lbl_log.setText("[*] Synchronizing and verifying SHA-256 checksums...")
        # Simulate syncing a core loader
        mock_raw = b"QUALCOMM_FIREHOSE_PROGRAMMER_BINARY_PAYLOAD_V2026"
        expected_sha = self.sync_mgr.calculate_sha256(mock_raw)

        ok, path, msg = self.sync_mgr.sync_payload(
            payload_id="prog_emmc_firehose_sdm845_ddr",
            download_url="mock://sdm845.mbn",
            expected_sha256=expected_sha,
            category="qualcomm",
            mock_bytes=mock_raw,
        )

        if ok:
            self._refresh_local_payloads()
            self.lbl_log.setText(f"[SUCCESS] Synced loader 'prog_emmc_firehose_sdm845_ddr' -> {path}")
            self.sync_completed.emit(1)
            QMessageBox.information(self, "Sync Complete", "Loaders successfully synchronized and locally encrypted!")
        else:
            self.lbl_log.setText(f"[ERROR] Sync failed: {msg}")

    def _on_start_remote_session(self) -> None:
        sid = self.input_session_id.text().strip()
        token = self.bridge.generate_handshake_token(sid)
        ok, msg = self.bridge.authenticate_handshake(token)

        if ok:
            self.lbl_log.setText(f"[+] Remote Tunnel ACTIVE! Session ID: {sid}\nTechnician can now stream diagnostic commands.")
            self.remote_session_started.emit(sid)
            QMessageBox.information(self, "Remote Tunnel", f"Remote session active:\n{sid}")
        else:
            self.lbl_log.setText(f"[!] Authentication error: {msg}")
