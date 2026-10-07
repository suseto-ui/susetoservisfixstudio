"""
Real Hardware Integration Test Suite (`tests/test_real_hardware.py`).
Validates strict subprocess execution, missing binary runtime exceptions,
and physical port binding exceptions with zero mock fallbacks.
"""

from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
import sys

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.fastboot_engine import FastbootEngine
from core.device_communicator import RealDeviceCommunicator


class TestRealHardwareExecution(unittest.TestCase):
    """Integration test suite ensuring real hardware communication and strict exception raising."""

    def test_fastboot_engine_missing_binary_raises(self):
        """Verify that invoking FastbootEngine with a non-existent binary path raises RuntimeError."""
        engine = FastbootEngine(adb_path="nonexistent_adb_binary_xyz", fastboot_path="nonexistent_fastboot_binary_xyz")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with self.assertRaises(RuntimeError):
                loop.run_until_complete(engine.get_adb_devices())

            with self.assertRaises(RuntimeError):
                loop.run_until_complete(engine.run_fastboot_command(["devices"]))
        finally:
            loop.close()

    def test_device_communicator_invalid_port_raises(self):
        """Verify that opening a non-existent serial port raises ConnectionError or ImportError."""
        comm = RealDeviceCommunicator(port_name="COM999_NONEXISTENT", baudrate=115200, timeout=0.1)
        with self.assertRaises((ConnectionError, ImportError)):
            comm.connect_serial()


if __name__ == "__main__":
    unittest.main()
