"""
Unit Tests for Auto Driver Installer & Device Auto Router (`tests/test_auto_router.py`).
"""

import tempfile
import unittest
from pathlib import Path

from core.device_auto_router import AutoRouterState, DeviceAutoRouter, DeviceMode
from drivers.auto_driver_installer import AutoDriverInstaller


class TestAutoRouterAndDriverInstaller(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.inf_dir = Path(self.temp_dir.name) / "inf"
        self.installer = AutoDriverInstaller(inf_dir=self.inf_dir)
        self.router = DeviceAutoRouter()

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. AUTO DRIVER INSTALLER
    def test_scan_unassigned_devices(self):
        unassigned = self.installer.scan_unassigned_devices()
        self.assertIsInstance(unassigned, list)
        self.assertGreater(len(unassigned), 0)
        self.assertIn("vid", unassigned[0])
        self.assertIn("pid", unassigned[0])

    def test_generate_winusb_inf(self):
        inf_path = self.installer.generate_winusb_inf("05C6", "9008", "Qualcomm Test Device")
        self.assertTrue(inf_path.exists())
        content = inf_path.read_text(encoding="utf-8")
        self.assertIn("USB\\VID_05C6&PID_9008", content)
        self.assertIn("WinUSB.sys", content)

    def test_install_driver_silently(self):
        inf_path = self.installer.generate_winusb_inf("0E8D", "0003", "MediaTek Test Device")
        res = self.installer.install_driver_silently(inf_path)
        self.assertEqual(res["status"], "INSTALLED")

    def test_auto_scan_and_inject_all(self):
        res = self.installer.auto_scan_and_inject_all()
        self.assertEqual(res["status"], "AUTO_INJECTION_COMPLETED")
        self.assertGreater(res["devices_processed"], 0)

    # 2. DEVICE AUTO ROUTER
    def test_zero_conf_pipeline_qualcomm(self):
        dev = self.router.run_zero_conf_pipeline("COM3")
        self.assertEqual(self.router.current_state, AutoRouterState.ACTION_RECOMMENDED)
        self.assertIn("mode", dev)
        self.assertEqual(dev["mode"], DeviceMode.QUALCOMM_EDL_9008.value)
        self.assertIn("recommendation", dev)
        rec = dev["recommendation"]
        self.assertIn("action_title", rec)
        self.assertIn("button_text", rec)

    def test_zero_conf_execute_action(self):
        self.router.run_zero_conf_pipeline("COM3")
        res = self.router.execute_recommended_action()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(self.router.current_state, AutoRouterState.ACTION_COMPLETED)


if __name__ == "__main__":
    unittest.main()
