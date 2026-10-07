"""
Phase 13 Unit & Integration Test Suite:
UI Refinement, Ergonomic Dark Themes, Centralized Localization, Error Translators,
Flash Progress Component, and Asynchronous Cancellation Token Engine.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.i18n_strings import I18NManager, ERROR_RESOLUTIONS
from ui.theme_manager import ThemeManager
from ui.flash_progress_component import FlashProgressComponent
from val.base_adapter import CancellationToken, OperationCancelledException
from ui._qt_compat import QApplication
from ui.main_window import MainWindow


class TestPhase13UIRefinementAndDraftCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication.instance() is None:
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.i18n = I18NManager(default_lang="cs")
        self.theme_mgr = ThemeManager()

    def test_i18n_translation_and_language_switch(self):
        """Verify translation lookups and language switching between Czech and English."""
        # Czech by default
        self.assertEqual(self.i18n.current_lang, "cs")
        self.assertIn("FRP", self.i18n.get_text("btn_execute_frp"))

        # Switch to English
        self.i18n.set_language("en")
        self.assertEqual(self.i18n.current_lang, "en")
        self.assertIn("Execute 1-Click FRP", self.i18n.get_text("btn_execute_frp"))

    def test_i18n_error_resolutions(self):
        """Verify low-level error codes are translated into human-readable steps."""
        self.i18n.set_language("cs")
        err_sahara = self.i18n.resolve_error("ERR_SAHARA_NAK")
        self.assertEqual(err_sahara["code"], "0x5A01")
        self.assertIn("Sahara", err_sahara["title"])
        self.assertGreaterEqual(len(err_sahara["steps"]), 1)

        err_brom = self.i18n.resolve_error("ERR_BROM_TIMEOUT_A0")
        self.assertEqual(err_brom["code"], "0x5A02")
        self.assertIn("Volume", err_brom["steps"][1])

        err_winusb = self.i18n.resolve_error("ERR_WINUSB_CODE_28")
        self.assertEqual(err_winusb["code"], "0x5A03")

        err_interlock = self.i18n.resolve_error("ERR_SECURITY_INTERLOCK")
        self.assertEqual(err_interlock["code"], "0x5A04")

    def test_i18n_tooltips(self):
        """Verify contextual tooltips for advanced controls."""
        tip_baud = self.i18n.get_tooltip("baudrate_autotune")
        self.assertGreater(len(tip_baud), 10)
        tip_interlock = self.i18n.get_tooltip("security_interlock")
        self.assertIn("bootloader", tip_interlock.lower())

    def test_theme_manager_stylesheets(self):
        """Verify ThemeManager generates valid QSS for Cyber/Technician and Dark Slate themes."""
        qss_cyber = self.theme_mgr.get_stylesheet("cyber_technician")
        self.assertIn("#0a0d14", qss_cyber)
        self.assertIn("#00f0ff", qss_cyber)

        qss_slate = self.theme_mgr.get_stylesheet("dark_slate")
        self.assertIn("#1e293b", qss_slate)

    def test_cancellation_token_engine(self):
        """Verify CancellationToken notifies callbacks and triggers OperationCancelledException."""
        token = CancellationToken()
        self.assertFalse(token.is_cancelled)

        callback_invoked = []
        token.register_callback(lambda: callback_invoked.append(True))

        token.cancel()
        self.assertTrue(token.is_cancelled)
        self.assertEqual(len(callback_invoked), 1)

        with self.assertRaises(OperationCancelledException):
            token.throw_if_cancelled()

    def test_flash_progress_component_metrics(self):
        """Verify throughput computation, progress update, and cancel trigger."""
        comp = FlashProgressComponent()
        comp.start_operation("Test Flash", total_bytes=1048576, total_sectors=2048)

        self.assertTrue(comp.btn_cancel.isEnabled())
        comp.update_progress(current_bytes=524288, current_sector=1024, latency_ms=4.2)

        self.assertEqual(comp.progress_bar.value(), 50)
        self.assertIn("1024 / 2048", comp.lbl_sectors.text())
        self.assertIn("4.2 ms", comp.lbl_latency.text())

        comp.complete_operation(success=True, message="Finished")
        self.assertFalse(comp.btn_cancel.isEnabled())
        self.assertEqual(comp.progress_bar.value(), 100)

    def test_main_window_gui_and_signals(self):
        """Verify MainWindow construction, signal routing, and i18n binding."""
        win = MainWindow(i18n=self.i18n, theme_mgr=self.theme_mgr)
        self.assertIn("SusetoDroidFixStudio", win.windowTitle())

        # Test simulated signals
        win.bus.device_connected.emit("COM3", "QUALCOMM_9008")
        self.assertEqual(win.active_port, "COM3")
        self.assertIn("COM3", win.lbl_port_status.text())

        win.bus.telemetry_updated.emit(12.5, 3.1, "WAL [Synced]")
        self.assertIn("12.50 Mbit/s", win.lbl_throughput.text())

        win.bus.device_disconnected.emit("COM3")
        self.assertIsNone(win.active_port)
        self.assertIn("DISCONNECTED", win.lbl_port_status.text())


if __name__ == "__main__":
    unittest.main()
