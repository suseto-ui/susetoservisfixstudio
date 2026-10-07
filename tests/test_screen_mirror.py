"""
Unit Tests for Screen Mirror & Touch Remote Engine (`tests/test_screen_mirror.py`).
"""

import unittest
from core.screen_mirror_engine import ScreenMirrorEngine


class TestScreenMirrorEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ScreenMirrorEngine()

    def test_get_device_telemetry(self):
        tel = self.engine.get_device_telemetry()
        self.assertIn("model", tel)
        self.assertIn("android_version", tel)
        self.assertIn("resolution", tel)
        self.assertIn("battery_level_pct", tel)
        self.assertEqual(tel["resolution"], "1080x2400")

    def test_touch_tap_dispatch(self):
        res = self.engine.dispatch_touch_tap(540, 1200)
        self.assertEqual(res["event"], "TAP")
        self.assertEqual(res["x"], 540)
        self.assertEqual(res["y"], 1200)
        self.assertEqual(res["status"], "DELIVERED")

    def test_touch_swipe_dispatch(self):
        res = self.engine.dispatch_touch_swipe(540, 1800, 540, 400, 250)
        self.assertEqual(res["event"], "SWIPE")
        self.assertEqual(res["duration_ms"], 250)
        self.assertEqual(res["status"], "DELIVERED")

    def test_keyevent_dispatch(self):
        res_back = self.engine.dispatch_keyevent("BACK")
        self.assertEqual(res_back["keycode"], 4)
        self.assertEqual(res_back["status"], "DELIVERED")

        res_home = self.engine.dispatch_keyevent("HOME")
        self.assertEqual(res_home["keycode"], 3)

    def test_text_input_dispatch(self):
        res = self.engine.dispatch_text_input("hello world")
        self.assertEqual(res["event"], "TEXT_INPUT")
        self.assertIn("input text", res["command_dispatched"])

    def test_apk_installation(self):
        res = self.engine.install_apk_package("test-app.apk")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("test-app.apk", res["package_name"])

    def test_adb_shell_command(self):
        res = self.engine.execute_adb_shell_command("getprop")
        self.assertEqual(res["returncode"], 0)
        self.assertIn("ro.product", res["stdout"])


if __name__ == "__main__":
    unittest.main()
