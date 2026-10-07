"""
Phase 12 Unit & Integration Test Suite:
Enterprise Multi-Tenant Fleet Manager, RBAC Enforcement, Audit Sync, and Fleet Dashboard.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.fleet_manager import FleetManager, UserRole
from core.audit_remote_sync import AuditRemoteSyncEngine
from ui._qt_compat import QApplication
from ui.fleet_dashboard_widget import FleetDashboardWidget


class TestPhase12FleetManagementAndAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication.instance() is None:
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.fleet = FleetManager(tenant_id="TENANT_LAB_PRAGUE")
        self.audit = AuditRemoteSyncEngine(tenant_id="TENANT_LAB_PRAGUE")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_station_registration_and_tenant_filtering(self):
        """Verify stations belong to specific tenants and cross-tenant filtering works."""
        self.fleet.register_station("PRG-01", "HWID-1111", "Prague Bench 1", "Tech Jiri", UserRole.TECHNICIAN)
        self.fleet.register_station("PRG-02", "HWID-2222", "Prague Bench 2", "Tech Petr", UserRole.SUPERVISOR)
        # Register a station in another tenant
        self.fleet.register_station("BRN-01", "HWID-3333", "Brno Bench 1", "Tech Jan", UserRole.TECHNICIAN, tenant_id="TENANT_LAB_BRNO")

        prague_stations = self.fleet.get_tenant_stations()
        self.assertEqual(len(prague_stations), 2)
        station_ids = [s["station_id"] for s in prague_stations]
        self.assertIn("PRG-01", station_ids)
        self.assertIn("PRG-02", station_ids)
        self.assertNotIn("BRN-01", station_ids)

    def test_tenant_isolation_security_interlock(self):
        """Verify cross-tenant station activation is blocked with PermissionError."""
        self.fleet.register_station("FOREIGN-01", "HWID-9999", "Foreign Lab", "Tech Foreign", tenant_id="OTHER_TENANT")
        with self.assertRaises(PermissionError):
            self.fleet.set_active_station("FOREIGN-01")

    def test_rbac_permission_matrix(self):
        """Verify granular permission gates across TECHNICIAN, SUPERVISOR, ADMIN."""
        # 1. Technician can read diagnostics and backup NVRAM, but cannot wipe FRP or erase bootloader
        self.assertTrue(self.fleet.is_action_permitted("READ_DIAGNOSTICS", role=UserRole.TECHNICIAN))
        self.assertTrue(self.fleet.is_action_permitted("BACKUP_NVRAM", role=UserRole.TECHNICIAN))
        self.assertFalse(self.fleet.is_action_permitted("FRP_UNLOCK", role=UserRole.TECHNICIAN))
        self.assertFalse(self.fleet.is_action_permitted("ERASE_BOOTLOADER", role=UserRole.TECHNICIAN))

        # 2. Supervisor can unlock FRP and write partitions, but cannot erase bootloader
        self.assertTrue(self.fleet.is_action_permitted("FRP_UNLOCK", role=UserRole.SUPERVISOR))
        self.assertTrue(self.fleet.is_action_permitted("WRITE_PARTITIONS", role=UserRole.SUPERVISOR))
        self.assertFalse(self.fleet.is_action_permitted("ERASE_BOOTLOADER", role=UserRole.SUPERVISOR))

        # 3. Admin has full clearance
        self.assertTrue(self.fleet.is_action_permitted("ERASE_BOOTLOADER", role=UserRole.ADMIN))
        self.assertTrue(self.fleet.is_action_permitted("MANAGE_STATIONS", role=UserRole.ADMIN))

    def test_device_identifier_anonymization(self):
        """Verify device identifiers are irreversibly hashed for customer privacy."""
        raw_serial = "SN8899AABBCCDDEEFF"
        anon1 = AuditRemoteSyncEngine.anonymize_identifier(raw_serial)
        anon2 = AuditRemoteSyncEngine.anonymize_identifier(raw_serial)

        self.assertEqual(anon1, anon2)
        self.assertEqual(len(anon1), 16)
        self.assertNotIn(raw_serial, anon1)

    def test_audit_event_recording_and_metric_counters(self):
        """Verify operation logging updates aggregate metric counters."""
        self.audit.record_operation_event("BENCH-01", "FRP_UNLOCK", "DEVICE_A", "SUCCESS")
        self.audit.record_operation_event("BENCH-01", "EDL_FLASH", "DEVICE_B", "SUCCESS")
        self.audit.record_operation_event("BENCH-02", "DONGLE_AUTH", "DEVICE_C", "SUCCESS")

        self.assertEqual(len(self.audit.buffered_records), 3)
        self.assertEqual(self.audit.metrics["frp_unlocks_total"], 1)
        self.assertEqual(self.audit.metrics["flashes_total"], 1)
        self.assertEqual(self.audit.metrics["dongle_auths_total"], 1)

    def test_signed_audit_batch_creation_and_shipping(self):
        """Verify cryptographic HMAC batch signing and flushing upon successful push."""
        self.audit.record_operation_event("BENCH-01", "NVRAM_BACKUP", "DEV_01", "SUCCESS")
        batch = self.audit.create_sync_batch()

        self.assertIn("payload", batch)
        self.assertIn("signature", batch)
        self.assertEqual(len(batch["signature"]), 64)  # SHA-256 HMAC hex
        self.assertEqual(batch["payload"]["records_count"], 1)

        ok, msg, count = self.audit.push_audit_batch()
        self.assertTrue(ok)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.audit.buffered_records), 0)
        self.assertEqual(self.audit.synced_batches_count, 1)

    def test_fleet_dashboard_widget_ui(self):
        """Verify FleetDashboardWidget initialization, UI data binding, and telemetry refresh."""
        widget = FleetDashboardWidget(fleet_manager=self.fleet, audit_sync=self.audit)
        self.assertIn("Fleet Dashboard", widget.windowTitle())

        # Record event and refresh UI
        self.audit.record_operation_event("PRG-01", "FRP_UNLOCK", "DEV_XYZ", "SUCCESS")
        widget.refresh_dashboard()

        self.assertIn("FRP Unlocks: 1", widget.lbl_metric_frp.text())
        self.assertIn("Main Flashing Bench", widget.lbl_stations_list.text())


if __name__ == "__main__":
    unittest.main()
