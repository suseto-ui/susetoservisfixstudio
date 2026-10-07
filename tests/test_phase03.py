"""
Phase 03 Unit & Integration Test Suite: Protocol Engine, ESPFlasher, and Progress UI.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

try:
    import pytest
except ImportError:
    class _PytestShim:
        class mark:
            @staticmethod
            def asyncio(func):
                func._is_async_test = True
                return func
    pytest = _PytestShim()  # type: ignore[assignment]

if "serial" not in sys.modules:
    mock_serial_mod = types.ModuleType("serial")
    mock_serial_mod.EIGHTBITS = 8
    mock_serial_mod.PARITY_NONE = "N"
    mock_serial_mod.STOPBITS_ONE = 1
    mock_serial_mod.Serial = MagicMock()
    sys.modules["serial"] = mock_serial_mod

from core.protocol_engine import SLIPProtocolEngine
from core.esptool_flasher import ESPFlasher
from val.esp32_adapter import ESP32Adapter
from ui.flash_progress_component import FlashProgressComponentState


def test_slip_encoding_and_decoding():
    """Verify SLIP frame packaging, escaping of END/ESC bytes, and un-framing."""
    payload = b"\xC0\xDB\x01\x02\xC0"
    encoded = SLIPProtocolEngine.encode_frame(payload)
    
    # Encoded frame must start and end with SLIP_END (0xC0)
    assert encoded[0] == 0xC0
    assert encoded[-1] == 0xC0

    decoded_list = SLIPProtocolEngine.decode_frame(encoded)
    assert len(decoded_list) == 1
    assert decoded_list[0] == payload


def test_checksum_verification():
    """Verify ESP32 ROM checksum calculation and verification."""
    data = b"\x01\x02\x03\x04\x05"
    checksum = SLIPProtocolEngine.calculate_checksum(data, initial=0xEF)
    assert isinstance(checksum, int)

    assert SLIPProtocolEngine.verify_checksum(data, checksum) is True
    assert SLIPProtocolEngine.verify_checksum(data, checksum ^ 0xFF) is False


@pytest.mark.asyncio
async def test_esptool_flasher_16kb_mock_image():
    """Simulate flashing a 16KB mock firmware image across 4 blocks with progress tracking."""
    adapter = ESP32Adapter("COM3")
    
    async def _mock_write(*args, **kwargs):
        return True
    adapter.write_flash_block = MagicMock(side_effect=_mock_write)

    telemetry_events = []
    def on_progress(p):
        telemetry_events.append(p)

    flasher = ESPFlasher(adapter=adapter, progress_callback=on_progress)
    
    # Create 16 KB mock firmware image (16 * 1024 bytes)
    mock_firmware = b"\xAA\x55\x01\x02" * 4096
    assert len(mock_firmware) == 16384

    success = await flasher.flash_image(mock_firmware, start_addr=0x1000)
    assert success is True
    assert adapter.write_flash_block.call_count == 4  # 16384 / 4096 = 4 blocks
    assert len(telemetry_events) >= 4
    assert telemetry_events[-1]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_esptool_flasher_cancellation_token():
    """Test flasher graceful abort when cancellation token is triggered."""
    adapter = ESP32Adapter("COM3")
    adapter.write_flash_block = MagicMock(return_value=True)

    cancel_token = asyncio.Event()
    cancel_token.set()  # Pre-set cancellation

    flasher = ESPFlasher(adapter=adapter)
    mock_firmware = b"\xFF" * 8192

    success = await flasher.flash_image(mock_firmware, cancel_token=cancel_token)
    assert success is False


def test_flash_progress_component_state():
    """Verify UI progress component accumulator and summary generation."""
    state = FlashProgressComponentState()
    state.update({
        "status": "WRITING",
        "percent": 50.0,
        "bytes_written": 8192,
        "total_size": 16384,
        "speed_bytes_per_sec": 102400.0,
        "elapsed_sec": 0.08,
    })

    summary = state.get_summary()
    assert summary["status"] == "WRITING"
    assert summary["percent_str"] == "50.0%"
    assert "100.00 KB/s" in summary["throughput_str"]
    assert len(summary["recent_logs"]) == 1


if __name__ == "__main__":
    import inspect

    test_functions = [
        obj for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    print(f"Running {len(test_functions)} Phase 03 test cases...")
    passed = 0
    failed = 0
    for test_fn in test_functions:
        test_name = test_fn.__name__
        try:
            if inspect.iscoroutinefunction(test_fn) or getattr(test_fn, "_is_async_test", False):
                asyncio.run(test_fn())
            else:
                test_fn()
            print(f"  [PASS] {test_name}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {test_name}: {exc}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed.")
    if failed > 0:
        sys.exit(1)
