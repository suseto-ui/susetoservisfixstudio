"""
Unit Tests for Phase 01: Driver Auto-Injector, Auto-Router & CustomTkinter GUI (`tests/test_phase01_driver_injector.py`).
"""

import os
import tempfile
import unittest

from core.driver_injector import DriverAutoInjector, UnassignedDevice
from core.auto_router import AutoRouter, DeviceMode, RecommendedAction
from ui.main_window import AutomatedDiagnosticApp


class TestPhase01DriverInjectorAndAutoRouter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.injector = DriverAutoInjector(inf_cache_dir=self.temp_dir.name)
        self.router = AutoRouter()

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. Driver Auto-Injector Tests
    def test_driver_injector_scan_unassigned(self):
        unassigned = self.injector.scan_unassigned_devices()
        self.assertIsInstance(unassigned, list)
        self.assertGreaterEqual(len(unassigned), 1)
        first = unassigned[0]
        self.assertIsInstance(first, UnassignedDevice)
        self.assertEqual(first.problem_code, 28)
        self.assertTrue(len(first.vid) == 4)
        self.assertTrue(len(first.pid) == 4)

    def test_driver_injector_generate_inf(self):
        inf_path = self.injector.generate_winusb_inf("05C6", "9008", "Qualcomm HS-USB QDLoader 9008")
        self.assertTrue(os.path.exists(inf_path))
        with open(inf_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("USB\\VID_05C6&PID_9008", content)
        self.assertIn("Class = USBDevice", content)
        self.assertIn("winusb", content.lower())

    def test_driver_injector_inject_driver(self):
        res = self.injector.inject_driver("0E8D", "0003", "MediaTek Preloader")
        self.assertEqual(res["status"], "INSTALLED")
        self.assertEqual(res["vid"], "0E8D")
        self.assertEqual(res["pid"], "0003")

    def test_driver_injector_preflight_skip_identical(self):
        # First injection: fresh install
        res1 = self.injector.inject_driver("05C6", "9008", "Qualcomm HS-USB QDLoader 9008")
        self.assertEqual(res1["status"], "INSTALLED")

        # Second injection: pre-flight check detects identical driver and skips installation
        res2 = self.injector.inject_driver("05C6", "9008", "Qualcomm HS-USB QDLoader 9008")
        self.assertEqual(res2["status"], "SKIPPED_IDENTICAL")
        self.assertTrue(res2.get("already_installed"))
        self.assertIn("Pre-flight", res2["message"])

        # Forced re-injection: overrides skip and reinstalls
        res3 = self.injector.inject_driver("05C6", "9008", "Qualcomm HS-USB QDLoader 9008", force_reinstall=True)
        self.assertEqual(res3["status"], "INSTALLED")

    def test_driver_injector_inject_all(self):
        report = self.injector.inject_all_unassigned()
        self.assertEqual(report["status"], "AUTO_INJECTION_COMPLETED")
        self.assertGreater(report["devices_processed"], 0)
        self.assertIn("devices_skipped", report)
        self.assertIn("devices_installed", report)
        self.assertIsInstance(report["results"], list)

    # 2. Auto-Router & Smart Parser Tests
    def test_auto_router_negotiate_baudrate(self):
        baud = self.router.negotiate_baudrate("COM3")
        self.assertIn(baud, [115200, 460800, 921600])

    def test_auto_router_identify_qualcomm(self):
        res = self.router.send_probe_and_identify(port="COM3", vid="05C6", pid="9008")
        self.assertEqual(res.mode, DeviceMode.QUALCOMM_EDL_9008)
        self.assertEqual(res.recommendation.action_id, "QUALCOMM_LOADER_FLASH")
        self.assertIn("Firehose", res.recommendation.action_title)
        self.assertIn("SAHARA_V2", res.probe_data["protocol"])

    def test_auto_router_identify_mediatek(self):
        res = self.router.send_probe_and_identify(port="COM5", vid="0E8D", pid="0003")
        self.assertEqual(res.mode, DeviceMode.MEDIATEK_BROM)
        self.assertEqual(res.recommendation.action_id, "MEDIATEK_SLA_DAA_BYPASS")
        self.assertIn("SLA/DAA", res.recommendation.action_title)

    def test_auto_router_identify_fastboot(self):
        res = self.router.send_probe_and_identify(port="FASTBOOT-1", vid="18D1", pid="D00D")
        self.assertEqual(res.mode, DeviceMode.FASTBOOT_BOOTLOADER)
        self.assertEqual(res.recommendation.action_id, "FASTBOOT_FLASH_WIZARD")

    def test_auto_router_identify_adb(self):
        res = self.router.send_probe_and_identify(port="ADB-SERIAL", vid="18D1", pid="4EE7")
        self.assertEqual(res.mode, DeviceMode.ANDROID_ADB)
        self.assertEqual(res.recommendation.action_id, "ADB_SCREEN_MIRROR")

    def test_auto_router_execute_recommendations(self):
        actions = ["QUALCOMM_LOADER_FLASH", "MEDIATEK_SLA_DAA_BYPASS", "FASTBOOT_FLASH_WIZARD", "ADB_SCREEN_MIRROR"]
        for act in actions:
            exec_res = self.router.execute_recommended_action(act)
            self.assertEqual(exec_res["status"], "SUCCESS")
            self.assertIn("verdict", exec_res)

    # 3. GUI Instantiation Test
    def test_gui_initialization(self):
        app = AutomatedDiagnosticApp()
        self.assertIsNotNone(app.root)
        app.append_log("Test Log Event")
        app.update_stepper(2)
        app.root.destroy()


    def test_continuous_hotplug_monitor(self):
        from core.driver_injector import ContinuousUsbHotplugMonitor
        monitor = ContinuousUsbHotplugMonitor(driver_injector=self.injector, poll_interval_sec=0.05)
        monitor.start_monitoring()
        self.assertTrue(monitor.is_monitoring)
        import time
        time.sleep(0.15)
        monitor.stop_monitoring()
        self.assertFalse(monitor.is_monitoring)


if __name__ == "__main__":
    unittest.main()

