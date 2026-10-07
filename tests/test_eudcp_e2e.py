"""
End-to-End System Verification Test Suite for the EUDCP Hardware Platform.
"""

from __future__ import annotations

import os
import sys
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock

# Inject source root path into system imports
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

import types
from unittest.mock import MagicMock

if "serial" not in sys.modules:
    mock_serial_mod = types.ModuleType("serial")
    mock_serial_mod.EIGHTBITS = 8
    mock_serial_mod.PARITY_NONE = "N"
    mock_serial_mod.PARITY_EVEN = "E"
    mock_serial_mod.PARITY_ODD = "O"
    mock_serial_mod.STOPBITS_ONE = 1
    mock_serial_mod.Serial = MagicMock()
    sys.modules["serial"] = mock_serial_mod

from core.port_negotiator import PortNegotiator
from drivers.setupapi_injector import SetupAPIDriverInjector
from val.oem_handshaker import OEMHandshakeEngine
from val.model_profiler import DynamicModelProfiler
from storage.stream_dumper import StreamingDumpEngine
from core.ram_recovery import RAMRecoveryAgent
from val.esp32_adapter import ESP32Adapter


@pytest.mark.asyncio
async def test_port_negotiator_workflow():
    """Verify automatic baud rate negotiation and RTT latency profiling."""
    negotiator = PortNegotiator("COM3")
    res = await negotiator.auto_negotiate()
    assert res["status"] == "SUCCESS"
    assert res["config"]["baudrate"] == 115200

    rtt = await negotiator.measure_rtt(count=3)
    assert rtt > 0.0


def test_driver_injector_flow():
    """Verify driver auto-injector can detect health status and construct INF files."""
    injector = SetupAPIDriverInjector("10C4", "EA60")
    assert injector.is_driver_healthy() is True

    with tempfile.TemporaryDirectory() as tmp_dir:
        inf_path = injector.generate_generic_inf(tmp_dir)
        assert os.path.exists(inf_path)
        with open(inf_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "VID_10C4" in content
            assert "PID_EA60" in content

    assert injector.inject_driver_silent() is True


@pytest.mark.asyncio
async def test_oem_handshake_engine_sequences():
    """Test standard and custom bootloader triggers for multiple OEM platforms."""
    engine = OEMHandshakeEngine("COM3")
    assert await engine.run_qualcomm_sahara() is True
    assert await engine.run_mediatek_brom() is True
    assert await engine.run_stm32_usart_dfu() is True
    assert await engine.run_generic_direct_registers() is True

    # Setup mocked ESP32 adapter for hw handshaker test
    adapter = ESP32Adapter("COM3")
    adapter.enter_bootloader = MagicMock(return_value=asyncio.sleep(0, True) or True)
    assert await engine.run_espressif_slip(adapter) is True


def test_dynamic_model_profiler():
    """Ensure dynamic layout profiling reads profiles correctly and supports custom profiling."""
    profiler = DynamicModelProfiler()
    esp_profile = profiler.get_profile("esp32_wroom_32e")
    assert esp_profile is not None
    assert esp_profile["vendor"] == "Espressif"

    custom_cfg = {
        "vendor": "CustomPlatform",
        "flash_size_bytes": 1024,
        "page_size_bytes": 64,
        "bootloader_addr": 0x100,
        "user_partition_addr": 0x200,
        "requires_unlock": False
    }
    profiler.register_profile("custom_chip_01", custom_cfg)
    loaded = profiler.get_profile("custom_chip_01")
    assert loaded == custom_cfg


def test_streaming_dump_engine_mmap():
    """Verify stream dump engine can write block buffers to memory-mapped files and compute CRC32/SHA256."""
    total_size = 1024  # 1 KB dump
    block_size = 256
    mock_source_data = b"\xAA\x55\x12\x34" * 256  # exactly 1024 bytes

    def mock_data_source(offset: int, length: int) -> bytes:
        return mock_source_data[offset : offset + length]

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_file = os.path.join(tmp_dir, "dump.bin")
        engine = StreamingDumpEngine(out_file, total_size, block_size)
        res = engine.start_dump(mock_data_source)

        assert res["status"] == "COMPLETED"
        assert res["total_bytes"] == total_size
        assert len(res["crc32"]) == 10
        assert len(res["sha256"]) == 64
        assert os.path.exists(out_file)
        assert os.path.getsize(out_file) == total_size


def test_ram_recovery_agent():
    """Ensure recovery agent can capture and export CPU core registers pre-restart."""
    agent = RAMRecoveryAgent("esp32")
    res = agent.extract_residual_ram()
    assert res["status"] == "RECOVERED"
    assert "PC" in res["saved_registers"]
    assert "SP" in res["saved_registers"]


if __name__ == "__main__":
    import inspect

    test_functions = [
        obj for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    print(f"Running {len(test_functions)} EUDCP E2E test cases...")
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
