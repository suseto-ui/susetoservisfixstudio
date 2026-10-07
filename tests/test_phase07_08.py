import unittest
import os
import sys
import tempfile
from core.adb_fastboot import ADBFastbootBridge
from core.firmware_engine import FirmwareEngine
from core.ai_engine import AIDiagnosticEngine

class TestSusetoDroidFixStudioPhase78(unittest.TestCase):
    def setUp(self):
        self.bridge = ADBFastbootBridge()
        self.ai = AIDiagnosticEngine()

    def test_adb_bridge_execution(self):
        # Test safe execution wrapper using cross-platform python command
        success, out = self.bridge.execute_command([sys.executable, "-c", "print('DroidFixTest')"])
        self.assertTrue(success)
        self.assertIn("DroidFixTest", out)

    def test_firmware_engine_boot_analysis(self):
        # Test analyzing non-existent boot.img
        res = FirmwareEngine.analyze_boot_image("non_existent.img")
        self.assertIn("error", res)

    def test_ai_engine_empty_log(self):
        res = self.ai.analyze_log("")
        self.assertIn("prázdný", res)

    def test_report_generator(self):
        from core.report_generator import ReportGenerator
        device = {"serial": "TEST1234", "model": "Pixel Test"}
        actions = ["Záloha EFS", "Patch VBMeta"]
        path = ReportGenerator.generate_json_report(device, actions, "Zjištěna opravená chyba bootloopu.")
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
