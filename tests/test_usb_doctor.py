"""
Test Suite for USB Doctor & Hardware Port Diagnostics (`tests/test_usb_doctor.py`).
Verifies port enumeration, VID/PID parsing, chipset identification,
port access checks, and failure root-cause analysis.
"""

from __future__ import annotations

import unittest
from usb_doctor import USBDoctor, DiscoveredPort, KNOWN_CHIPSETS


class TestUSBDoctor(unittest.TestCase):
    def setUp(self) -> None:
        self.doctor = USBDoctor()

    def test_known_chipsets_database(self) -> None:
        """Verify all critical flashing modes are present in the signature database."""
        # Qualcomm EDL
        self.assertIn(("05c6", "9008"), KNOWN_CHIPSETS)
        self.assertEqual(KNOWN_CHIPSETS[("05c6", "9008")]["mode"], "QUALCOMM_EDL_9008")

        # MediaTek BROM
        self.assertIn(("0e8d", "0003"), KNOWN_CHIPSETS)
        self.assertEqual(KNOWN_CHIPSETS[("0e8d", "0003")]["mode"], "MTK_BROM")

        # Fastboot
        self.assertIn(("18d1", "d00d"), KNOWN_CHIPSETS)
        self.assertEqual(KNOWN_CHIPSETS[("18d1", "d00d")]["mode"], "FASTBOOT")

        # FTDI UART
        self.assertIn(("0403", "6001"), KNOWN_CHIPSETS)
        self.assertEqual(KNOWN_CHIPSETS[("0403", "6001")]["mode"], "UART_FTDI")

    def test_vid_pid_parsing(self) -> None:
        """Verify regex extraction of hexadecimal VID and PID strings."""
        hwid1 = r"USB\VID_05C6&PID_9008\INST_1"
        vid1, pid1 = self.doctor._parse_vid_pid(hwid1)
        self.assertEqual(vid1, "05c6")
        self.assertEqual(pid1, "9008")

        hwid2 = r"USB\VID_0E8D&PID_0003\BROM"
        vid2, pid2 = self.doctor._parse_vid_pid(hwid2)
        self.assertEqual(vid2, "0e8d")
        self.assertEqual(pid2, "0003")

        hwid_empty = "UNKNOWN_DEVICE_ID"
        vid3, pid3 = self.doctor._parse_vid_pid(hwid_empty)
        self.assertIsNone(vid3)
        self.assertIsNone(pid3)

    def test_diagnose_failures_locked_port(self) -> None:
        """Verify locked/access-denied COM port is identified as an ERROR finding."""
        locked_port = DiscoveredPort(
            device="COM4",
            description="Arduino / 3D Printer",
            hwid=r"USB\VID_2341&PID_0043\123",
            is_accessible=False,
            lock_reason="Port je uzamčen jiným programem (Access Denied)",
        )
        findings = self.doctor.diagnose_failures([locked_port])
        locked_findings = [f for f in findings if f.category == "PORT_LOCKED"]
        self.assertTrue(len(locked_findings) >= 1)
        self.assertEqual(locked_findings[0].severity, "ERROR")
        self.assertIn("COM4", locked_findings[0].title)

    def test_diagnose_failures_qualcomm_edl_detected(self) -> None:
        """Verify recognized Qualcomm EDL port triggers SUCCESS chipset finding."""
        edl_port = DiscoveredPort(
            device="COM3",
            description="Qualcomm HS-USB QDLoader 9008",
            hwid=r"USB\VID_05C6&PID_9008\9008",
            vid="05c6",
            pid="9008",
            chipset_info=KNOWN_CHIPSETS[("05c6", "9008")],
            is_accessible=True,
        )
        findings = self.doctor.diagnose_failures([edl_port])
        chipset_findings = [f for f in findings if f.category == "CHIPSET_DETECTED"]
        self.assertTrue(len(chipset_findings) >= 1)
        self.assertEqual(chipset_findings[0].severity, "SUCCESS")
        self.assertIn("Qualcomm", chipset_findings[0].title)

    def test_run_full_diagnosis_report_structure(self) -> None:
        """Verify full diagnosis returns a complete report dictionary."""
        report = self.doctor.run_full_diagnosis()
        self.assertIn("platform", report)
        self.assertIn("total_ports_detected", report)
        self.assertIn("ports", report)
        self.assertIn("findings", report)
        self.assertIsInstance(report["ports"], list)
        self.assertIsInstance(report["findings"], list)


if __name__ == "__main__":
    unittest.main()
