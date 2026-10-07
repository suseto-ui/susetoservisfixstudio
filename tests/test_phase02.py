"""
Integration Test Suite for Phase 02 (VAL and Driver Injector).
"""

import sys
import asyncio
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure root directory is in sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

if "serial" not in sys.modules:
    mock_serial_mod = types.ModuleType("serial")
    mock_serial_mod.EIGHTBITS = 8
    mock_serial_mod.PARITY_NONE = "N"
    mock_serial_mod.STOPBITS_ONE = 1
    mock_serial_mod.Serial = MagicMock()
    sys.modules["serial"] = mock_serial_mod

from val.esp32_adapter import ESP32Adapter
from val.ftdi_adapter import FTDIAdapter
from drivers.winusb_injector import WinUSBInjector

@patch("serial.Serial")
def test_esp32_adapter_bootloader(mock_serial):
    adapter = ESP32Adapter("COM3")
    result = asyncio.run(adapter.enter_bootloader())
    assert result is True
    assert mock_serial.called

def test_ftdi_adapter_bootloader():
    adapter = FTDIAdapter("COM4")
    result = asyncio.run(adapter.enter_bootloader())
    assert result is True

def test_winusb_injector():
    injector = WinUSBInjector()
    assert injector.detect_missing_drivers() is True
    assert injector.install_winusb_inf("dummy.inf") is True
