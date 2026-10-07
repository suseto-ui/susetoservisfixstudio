"""
Enterprise Fleet Dashboard & Organization Telemetry Cockpit for SusetoDroidFixStudio.
PySide6 QWidget interface for monitoring active service benches, managing RBAC roles,
and inspecting real-time fleet metrics and audit sync status.
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
    QMessageBox,
    Signal,
    Slot,
    Qt,
)
from core.fleet_manager import FleetManager, UserRole
from core.audit_remote_sync import AuditRemoteSyncEngine

logger = logging.getLogger("ui.fleet_dashboard")


class FleetDashboardWidget(QWidget):
    """
    Fleet management cockpit for enterprise multi-station service laboratories.
    """

    station_switched = Signal(str)
    audit_synced = Signal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        fleet_manager: Optional[FleetManager] = None,
        audit_sync: Optional[AuditRemoteSyncEngine] = None,
    ) -> None:
        super().__init__(parent)
        self.fleet_mgr = fleet_manager or FleetManager()
        self.audit_sync = audit_sync or AuditRemoteSyncEngine()

        self._seed_default_stations()
        self._init_ui()

    def _seed_default_stations(self) -> None:
        """Seed sample stations if none exist."""
        if not self.fleet_mgr.stations:
            self.fleet_mgr.register_station("BENCH-01", "AAAA-1111-2222-3333", "Main Flashing Bench", "Tech Alpha", UserRole.TECHNICIAN)
            self.fleet_mgr.register_station("BENCH-02", "BBBB-4444-5555-6666", "Supervisor Bench", "Lead Engineer", UserRole.SUPERVISOR)
            self.fleet_mgr.register_station("ADMIN-LAB", "CCCC-7777-8888-9999", "HQ Diagnostics Center", "Admin Root", UserRole.ADMIN)
            self.fleet_mgr.set_active_station("BENCH-01")

    def _init_ui(self) -> None:
        self.setWindowTitle("SusetoDroidFixStudio | Enterprise Fleet Dashboard")
        self.resize(720, 540)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Title
        lbl_header = QLabel(f"Enterprise Fleet Management | Tenant: {self.fleet_mgr.tenant_id}")
        lbl_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #00ffff;")
        layout.addWidget(lbl_header)

        # Active Station & Role Status Banner
        self.lbl_active_station = QLabel(f"Active Station: {self.fleet_mgr.active_station_id} | Role: {self.fleet_mgr.active_role}")
        self.lbl_active_station.setStyleSheet(
            "padding: 8px; background-color: #0e639c; color: #ffffff; "
            "border-radius: 4px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_active_station)

        # Metrics Overview Row
        metrics_layout = QHBoxLayout()
        self.lbl_metric_frp = QLabel("FRP Unlocks: 0")
        self.lbl_metric_frp.setStyleSheet("padding: 8px; background-color: #252526; color: #4ec9b0; font-weight: bold;")
        metrics_layout.addWidget(self.lbl_metric_frp)

        self.lbl_metric_flash = QLabel("Flashes Total: 0")
        self.lbl_metric_flash.setStyleSheet("padding: 8px; background-color: #252526; color: #ce9178; font-weight: bold;")
        metrics_layout.addWidget(self.lbl_metric_flash)

        self.lbl_metric_dongle = QLabel("SmartCards Active: 1")
        self.lbl_metric_dongle.setStyleSheet("padding: 8px; background-color: #252526; color: #dcdcaa; font-weight: bold;")
        metrics_layout.addWidget(self.lbl_metric_dongle)
        layout.addLayout(metrics_layout)

        # Stations List Summary
        self.lbl_stations_list = QLabel("Connected Stations:\n- Loading...")
        self.lbl_stations_list.setStyleSheet(
            "padding: 12px; background-color: #181818; color: #d4d4d4; "
            "border: 1px solid #3c3c3c; border-radius: 4px; font-family: monospace;"
        )
        layout.addWidget(self.lbl_stations_list, stretch=1)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Fleet Telemetry")
        self.btn_refresh.clicked.connect(self.refresh_dashboard)
        btn_layout.addWidget(self.btn_refresh)

        self.btn_sync_audit = QPushButton("⚡ Ship Audit Logs (mTLS)")
        self.btn_sync_audit.setStyleSheet("background-color: #107c41; color: white; font-weight: bold;")
        self.btn_sync_audit.clicked.connect(self._on_sync_audit_clicked)
        btn_layout.addWidget(self.btn_sync_audit)

        layout.addLayout(btn_layout)
        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")
        self.refresh_dashboard()

    def refresh_dashboard(self) -> None:
        """Update telemetry numbers and connected stations roster."""
        stations = self.fleet_mgr.get_tenant_stations()
        lines = [f"Tenant Bench Stations ({len(stations)} Registered):"]
        for s in stations:
            status_tag = f"[{s.get('status')}]"
            lines.append(f"  • {s.get('station_id'):<10} | {s.get('station_name'):<22} | User: {s.get('assigned_user'):<14} | Role: {s.get('role'):<10} {status_tag}")
        self.lbl_stations_list.setText("\n".join(lines))

        # Update metrics
        m = self.audit_sync.metrics
        self.lbl_metric_frp.setText(f"FRP Unlocks: {m.get('frp_unlocks_total', 0)}")
        self.lbl_metric_flash.setText(f"Flashes Total: {m.get('flashes_total', 0)}")
        self.lbl_active_station.setText(f"Active Station: {self.fleet_mgr.active_station_id} | Role: {self.fleet_mgr.active_role}")

    def _on_sync_audit_clicked(self) -> None:
        ok, msg, count = self.audit_sync.push_audit_batch()
        if ok:
            self.refresh_dashboard()
            self.audit_synced.emit(count)
            QMessageBox.information(self, "Audit Sync", f"Audit logs shipped!\n{msg}")
        else:
            QMessageBox.critical(self, "Audit Sync Failed", f"Synchronization failed:\n{msg}")
