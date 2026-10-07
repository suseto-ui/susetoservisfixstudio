"""
Unit and Integration Test Suite for Phase 06 Kiosk Automation and Admin GUI.
Tests:
- OneClickAutomation pipeline orchestration
- Real-time status signals & Czech color-coded messages
- Strict exception shielding on disconnect and bad checksum
- SQLite WAL transaction logging
- Admin password hashing & verification
- KioskView and AdminView component initialization
- AppRouter view switching & hotkey authentication
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import types
if "serial" not in sys.modules:
    mock_serial_mod = types.ModuleType("serial")
    mock_serial_mod.EIGHTBITS = 8
    mock_serial_mod.PARITY_NONE = "N"
    mock_serial_mod.STOPBITS_ONE = 1
    mock_serial_mod.Serial = MagicMock()
    mock_serial_tools = types.ModuleType("serial.tools")
    mock_serial_list_ports = types.ModuleType("serial.tools.list_ports")
    mock_serial_list_ports.comports = MagicMock(return_value=[])
    sys.modules["serial"] = mock_serial_mod
    sys.modules["serial.tools"] = mock_serial_tools
    sys.modules["serial.tools.list_ports"] = mock_serial_list_ports

from core.one_click_automation import (
    AutomationState,
    AutomationStatus,
    OneClickAutomation,
)
from storage.wal_ledger import SQLiteWALLedger
from ui.admin_view import AdminAuthManager, AdminView
from ui.app_router import AppRouter, PasswordPromptDialog
from ui.kiosk_view import KioskView
from val.base_adapter import DeviceDisconnectedException


class TestKioskAutomation(unittest.IsolatedAsyncioTestCase):
    """Test suite for OneClickAutomation background engine and exception shielding."""

    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_wal_ledger.db")
        self.backup_dir = os.path.join(self.temp_dir.name, "backups")
        self.ledger = SQLiteWALLedger(db_path=self.db_path)
        self.automation = OneClickAutomation(
            ledger=self.ledger,
            backup_dir=self.backup_dir,
            db_path=self.db_path,
        )

    async def asyncTearDown(self) -> None:
        self.temp_dir.cleanup()

    async def test_full_pipeline_success(self) -> None:
        """Verify complete automated flow (detect -> adapter -> backup -> flash -> verify -> ledger)."""
        emitted_states = []

        def _on_status(status: AutomationStatus) -> None:
            emitted_states.append(status.state)

        self.automation.add_status_listener(_on_status)

        test_payload = b"TEST_FIRMWARE_PAYLOAD_ABCD" * 32
        success = await self.automation.run_full_pipeline(simulated=True, firmware_payload=test_payload)

        self.assertTrue(success)
        self.assertEqual(self.automation.current_status.state, AutomationState.SUCCESS)
        self.assertEqual(self.automation.current_status.progress_percent, 100.0)
        self.assertIn("ÚSPĚCH", self.automation.current_status.status_message)
        self.assertEqual(self.automation.current_status.color, "#2ecc71")

        # Verify emitted state sequence
        self.assertIn(AutomationState.DETECTING, emitted_states)
        self.assertIn(AutomationState.ADAPTER_SELECT, emitted_states)
        self.assertIn(AutomationState.BACKING_UP, emitted_states)
        self.assertIn(AutomationState.FLASHING, emitted_states)
        self.assertIn(AutomationState.VERIFYING, emitted_states)
        self.assertIn(AutomationState.SUCCESS, emitted_states)

        # Verify WAL ledger audit records
        logs = await self.ledger.query_logs(limit=20)
        event_types = [entry["event_type"] for entry in logs]
        self.assertIn("DEVICE_DETECTED", event_types)
        self.assertIn("ADAPTER_SELECTED", event_types)
        self.assertIn("BACKUP_COMPLETED", event_types)
        self.assertIn("OPERATION_SUCCESS", event_types)

    async def test_exception_shielding_device_disconnect(self) -> None:
        """Verify graceful exception shielding when device is disconnected mid-flash."""
        with patch.object(
            self.automation,
            "_flash_and_verify",
            side_effect=DeviceDisconnectedException("USB Cable was pulled!"),
        ):
            success = await self.automation.run_full_pipeline(simulated=True)
            self.assertFalse(success)
            self.assertEqual(self.automation.current_status.state, AutomationState.ERROR_DISCONNECTED)
            self.assertIn("ŠPATNĚ - Odpojeno", self.automation.current_status.status_message)
            self.assertEqual(self.automation.current_status.color, "#e74c3c")

            # Verify logged to WAL ledger
            logs = await self.ledger.query_logs(limit=10)
            event_types = [entry["event_type"] for entry in logs]
            self.assertIn("DISCONNECT_ERROR", event_types)

    async def test_exception_shielding_no_device_detected(self) -> None:
        """Verify graceful exception shielding when no device is detected."""
        with patch.object(self.automation, "_detect_device", return_value=None):
            success = await self.automation.run_full_pipeline(simulated=False)
            self.assertFalse(success)
            self.assertEqual(self.automation.current_status.state, AutomationState.ERROR)
            self.assertIn("CHYBA - Připojte zařízení", self.automation.current_status.status_message)
            self.assertEqual(self.automation.current_status.color, "#e74c3c")

    async def test_exception_shielding_checksum_mismatch(self) -> None:
        """Verify checksum mismatch error reporting."""
        with patch.object(
            self.automation,
            "_flash_and_verify",
            return_value=False,
        ):
            success = await self.automation.run_full_pipeline(simulated=True)
            self.assertFalse(success)

    def test_background_thread_runner(self) -> None:
        """Verify non-blocking execution via run_in_background."""
        completed_flag = []

        def _on_done(ok: bool) -> None:
            completed_flag.append(ok)

        thread = self.automation.run_in_background(simulated=True, on_complete=_on_done)
        self.assertTrue(thread.is_alive())
        thread.join(timeout=5.0)
        self.assertFalse(thread.is_alive())
        self.assertTrue(len(completed_flag) > 0)
        self.assertTrue(completed_flag[0])


class TestAdminAuthManager(unittest.TestCase):
    """Test suite for Admin password authentication and hashing."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.auth_file = Path(self.temp_dir.name) / "kiosk_auth.json"
        self.auth = AdminAuthManager(config_path=self.auth_file)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_default_password_verification(self) -> None:
        """Verify default password succeeds and wrong password fails."""
        self.assertTrue(self.auth.verify_password("admin123"))
        self.assertFalse(self.auth.verify_password("wrong_password"))

    def test_change_password_flow(self) -> None:
        """Verify changing password updates hash and rejects old password."""
        # Fail if old password incorrect
        ok, msg = self.auth.change_password("wrong_old", "new_secret_2026")
        self.assertFalse(ok)

        # Fail if new password too short
        ok, msg = self.auth.change_password("admin123", "ab")
        self.assertFalse(ok)

        # Succeed with valid credentials
        ok, msg = self.auth.change_password("admin123", "new_secret_2026")
        self.assertTrue(ok)
        self.assertTrue(self.auth.verify_password("new_secret_2026"))
        self.assertFalse(self.auth.verify_password("admin123"))


class TestUIViews(unittest.TestCase):
    """Test suite for KioskView, AdminView, and AppRouter mode switching."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "ui_test_wal.db")
        self.ledger = SQLiteWALLedger(db_path=self.db_path)
        self.automation = OneClickAutomation(ledger=self.ledger, db_path=self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_kiosk_view_initialization_and_status_reaction(self) -> None:
        """Verify KioskView initializes with one button and reacts to status updates."""
        router = AppRouter()
        kiosk = KioskView(master=router.container, automation_engine=self.automation)

        # Verify center components
        self.assertIsNotNone(kiosk.btn_start)
        self.assertIn("START", kiosk.btn_start.cget("text"))
        self.assertEqual(kiosk.lbl_status_main.cget("text"), "PŘIPRAVENO - Připojte zařízení")

        # Simulate status change to DETECTING
        status = AutomationStatus(
            state=AutomationState.DETECTING,
            progress_percent=25.0,
            status_message="DETEKCE - Hledám připojené zařízení...",
            sub_message="Skenuji USB porty",
            color="#3498db",
            device_info={"port": "COM3", "chipset": "Qualcomm SM8350"},
            timestamp=time.time(),
        )
        kiosk._apply_status_to_ui(status)
        self.assertEqual(kiosk.lbl_status_main.cget("text"), "DETEKCE - Hledám připojené zařízení...")
        self.assertIn("COM3", kiosk.lbl_device_strip.cget("text"))

        # Simulate status change to ERROR_DISCONNECTED
        err_status = AutomationStatus(
            state=AutomationState.ERROR_DISCONNECTED,
            progress_percent=0.0,
            status_message="ŠPATNĚ - Odpojeno",
            sub_message="Komunikace přerušena!",
            color="#e74c3c",
            timestamp=time.time(),
        )
        kiosk._apply_status_to_ui(err_status)
        self.assertEqual(kiosk.lbl_status_main.cget("text"), "ŠPATNĚ - Odpojeno")

        router.destroy()

    def test_admin_view_initialization(self) -> None:
        """Verify AdminView contains all tabs (Port Tuner, WAL Ledger, Verification, Security)."""
        router = AppRouter()
        admin = AdminView(master=router.container, ledger=self.ledger)

        self.assertIsNotNone(admin.tabview)
        self.assertIn("Port Tuner & Telemetrie", admin.tabview._tabs)
        self.assertIn("WAL Auditní Kniha", admin.tabview._tabs)
        self.assertIn("Systémová Verifikace (E2E)", admin.tabview._tabs)
        self.assertIn("Zabezpečení & Nastavení", admin.tabview._tabs)

        router.destroy()

    def test_app_router_view_switching(self) -> None:
        """Verify AppRouter switches between KioskView and AdminView and back."""
        router = AppRouter()
        self.assertEqual(router._current_view_name, "kiosk")
        self.assertIsInstance(router._active_view_widget, KioskView)

        # Switch to Admin
        router.switch_to_view("admin")
        self.assertEqual(router._current_view_name, "admin")
        self.assertIsInstance(router._active_view_widget, AdminView)

        # Switch back to Kiosk
        router.switch_to_view("kiosk")
        self.assertEqual(router._current_view_name, "kiosk")
        self.assertIsInstance(router._active_view_widget, KioskView)

        router.destroy()


if __name__ == "__main__":
    unittest.main()
