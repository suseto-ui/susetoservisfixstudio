"""
Phase 01 Unit Test Suite: Core Bus, USB Enumerator, and SQLite WAL Persistence.
All hardware I/O and serial communication channels are mocked.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure root directory is in sys.path
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

# Ensure 'serial' is mockable even if pyserial is not yet installed in host environment
if "serial" not in sys.modules:
    mock_serial_mod = types.ModuleType("serial")
    mock_serial_mod.EIGHTBITS = 8
    mock_serial_mod.PARITY_NONE = "N"
    mock_serial_mod.STOPBITS_ONE = 1
    mock_serial_mod.Serial = MagicMock()
    sys.modules["serial"] = mock_serial_mod
    
    mock_tools_mod = types.ModuleType("serial.tools")
    mock_list_ports_mod = types.ModuleType("serial.tools.list_ports")
    mock_list_ports_mod.comports = MagicMock(return_value=[])
    mock_tools_mod.list_ports = mock_list_ports_mod
    sys.modules["serial.tools"] = mock_tools_mod
    sys.modules["serial.tools.list_ports"] = mock_list_ports_mod

from core.bus_manager import (
    SUPPORTED_BAUDRATES,
    AsyncBusManager,
    BusDataReceivedEvent,
    BusErrorEvent,
    DeviceAttachedBusEvent,
    DynamicPortTuner,
    PortTunedBusEvent,
)
from core.usb_enumerator import (
    AsyncUSBHotplugListener,
    DeviceEventType,
    USBDeviceMetadata,
    USBDeviceParser,
)
from db.database import DatabaseManager


# ==============================================================================
# 1. USB ENUMERATOR & METADATA TESTS
# ==============================================================================

def test_usb_metadata_identifier_generation():
    """Verify unique device_id generation based on serial number, port, and hash."""
    meta1 = USBDeviceMetadata(
        vid="10C4",
        pid="EA60",
        serial_number="0001A89",
        port_name="COM3",
        description="CP210x USB to UART Bridge",
    )
    assert meta1.device_id == "USB_10C4_EA60_0001A89"

    meta2 = USBDeviceMetadata(
        vid="0403",
        pid="6001",
        serial_number=None,
        port_name="COM4",
        description="FTDI FT232R",
    )
    assert meta2.device_id == "PORT_COM4_0403_6001"

    meta3 = USBDeviceMetadata(
        vid="1A86",
        pid="7523",
        serial_number=None,
        port_name=None,
        hardware_id="USB\\VID_1A86&PID_7523",
    )
    assert meta3.device_id.startswith("DEV_1A86_7523_")


def test_usb_parser_regex():
    """Test extraction of VID/PID and Windows Device Interface GUIDs from raw strings."""
    hwid = r"USB\VID_10C4&PID_EA60\0001"
    vid, pid = USBDeviceParser.parse_hardware_id(hwid)
    assert vid == "10C4"
    assert pid == "EA60"

    raw_path = r"\\?\usb#vid_0403&pid_6001#ft99#{a5dcbf10-6530-11d2-901f-00c04fb951ed}"
    guid = USBDeviceParser.extract_guid(raw_path)
    assert guid == "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"

    # Invalid / empty paths
    assert USBDeviceParser.parse_hardware_id("") == (None, None)
    assert USBDeviceParser.extract_guid("") is None


@pytest.mark.asyncio
async def test_hotplug_listener_arrival_and_removal():
    """Verify arrival and removal hotplug events via simulated reconcile ticks."""
    listener = AsyncUSBHotplugListener(poll_interval=0.05)

    dev_a = USBDeviceMetadata(
        vid="10C4",
        pid="EA60",
        serial_number="SN001",
        port_name="COM3",
        description="Silicon Labs CP210x",
    )
    dev_b = USBDeviceMetadata(
        vid="0403",
        pid="6001",
        serial_number="SN002",
        port_name="COM7",
        description="FTDI Serial Adapter",
    )

    events_received = []

    def on_event(evt):
        events_received.append(evt)

    listener.register_callback(on_event)

    # Mock initial enumeration returning empty
    with patch.object(listener, "enumerate_devices_async", return_value=[]):
        await listener.start()

    # Step 1: Device A plugged in
    with patch.object(listener, "enumerate_devices_async", return_value=[dev_a]):
        await listener._handle_reconcile_tick()

    assert len(events_received) == 1
    assert events_received[0].event_type == DeviceEventType.ARRIVED
    assert events_received[0].device.device_id == "USB_10C4_EA60_SN001"

    # Step 2: Device B plugged in (both present)
    with patch.object(listener, "enumerate_devices_async", return_value=[dev_a, dev_b]):
        await listener._handle_reconcile_tick()

    assert len(events_received) == 2
    assert events_received[1].event_type == DeviceEventType.ARRIVED
    assert events_received[1].device.device_id == "USB_0403_6001_SN002"

    # Step 3: Device A detached (only B remains)
    with patch.object(listener, "enumerate_devices_async", return_value=[dev_b]):
        await listener._handle_reconcile_tick()

    assert len(events_received) == 3
    assert events_received[2].event_type == DeviceEventType.REMOVED
    assert events_received[2].device.device_id == "USB_10C4_EA60_SN001"

    await listener.stop()


# ==============================================================================
# 2. DYNAMIC PORT TUNER & AUTO-BAUDRATE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_dynamic_port_tuner_success_first_attempt():
    """Test baudrate scanner locking onto first successful rate (115200)."""
    tuner = DynamicPortTuner(read_timeout=0.05)

    with patch("serial.Serial") as mock_serial_cls:
        mock_port = MagicMock()
        mock_port.is_open = True
        mock_port.read.return_value = b"\r\nOK\r\n"
        mock_serial_cls.return_value = mock_port

        result = await tuner.scan_port("COM3")

        assert result.success is True
        assert result.detected_baudrate == 115200
        assert mock_port.write.called
        assert mock_port.close.called


@pytest.mark.asyncio
async def test_dynamic_port_tuner_fallback_to_higher_rate():
    """Test scanner cycling through rates until detecting response at 921600."""
    tuner = DynamicPortTuner(read_timeout=0.05)

    call_count = 0

    def mock_serial_factory(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        port_mock = MagicMock()
        port_mock.is_open = True
        rate = kwargs.get("baudrate")
        if rate == 921600:
            port_mock.read.return_value = b"DIAGNOSTIC_READY\n"
        else:
            port_mock.read.return_value = b""  # Timeout
        return port_mock

    with patch("serial.Serial", side_effect=mock_serial_factory):
        result = await tuner.scan_port(
            "COM4",
            expected_response=b"DIAGNOSTIC_READY",
        )

        assert result.success is True
        assert result.detected_baudrate == 921600
        assert len(result.attempts) >= 2


@pytest.mark.asyncio
async def test_dynamic_port_tuner_all_failed():
    """Test scenario where all baud rates fail or device throws an OS exception."""
    tuner = DynamicPortTuner(read_timeout=0.01)

    with patch("serial.Serial", side_effect=OSError("Access is denied")):
        result = await tuner.scan_port("COM99")

        assert result.success is False
        assert result.detected_baudrate is None
        assert len(result.attempts) == len(SUPPORTED_BAUDRATES)
        assert "failed" in result.error_message.lower()


# ==============================================================================
# 3. ASYNC BUS MANAGER & EVENT PUB-SUB TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_async_bus_manager_pub_sub():
    """Verify pub-sub message dispatching, type filtering, and thread-safety."""
    bus = AsyncBusManager()
    await bus.start()

    hardware_events = []
    error_events = []
    all_events = []

    def on_hardware(evt):
        hardware_events.append(evt)

    def on_error(evt):
        error_events.append(evt)

    def on_all(evt):
        all_events.append(evt)

    unsub_hw = bus.subscribe(DeviceAttachedBusEvent, on_hardware)
    unsub_err = bus.subscribe(BusErrorEvent, on_error)
    unsub_all = bus.subscribe(None, on_all)

    # Publish events
    evt1 = DeviceAttachedBusEvent(port="COM3", vid="10C4", pid="EA60")
    evt2 = BusErrorEvent(port="COM3", error_code="FRAME_ERR", message="Framing parity mismatch")
    evt3 = BusDataReceivedEvent(port="COM3", data=b"\x55\xAA\x01\x02")

    await bus.publish(evt1)
    await bus.publish(evt2)
    await bus.publish(evt3)

    # Allow dispatcher loop to process
    await asyncio.sleep(0.05)

    assert len(hardware_events) == 1
    assert hardware_events[0].payload["port"] == "COM3"

    assert len(error_events) == 1
    assert error_events[0].payload["error_code"] == "FRAME_ERR"

    assert len(all_events) == 3

    # Test unsubscribe
    unsub_hw()
    await bus.publish(DeviceAttachedBusEvent(port="COM5", vid="0403", pid="6001"))
    await asyncio.sleep(0.05)

    # hardware_events count should not change
    assert len(hardware_events) == 1

    await bus.stop()


# ==============================================================================
# 4. DATABASE & WAL MODE TESTS
# ==============================================================================

def test_database_manager_wal_mode_and_crud():
    """Verify SQLite WAL mode, schema initialization, upsert, and audit logging."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "test_diagnostic.db")
        db = DatabaseManager(db_path=db_file)

        # 1. Verify WAL mode pragma
        with db.connection() as conn:
            mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            assert mode.upper() == "WAL"

        # 2. Insert and update device
        db.upsert_device(
            device_id="DEV_COM1_10C4_EA60",
            vid="10C4",
            pid="EA60",
            serial_number="SN9988",
            port_name="COM1",
            description="Silicon Labs USB-to-UART",
            manufacturer="Silicon Labs",
        )

        dev = db.get_device("DEV_COM1_10C4_EA60")
        assert dev is not None
        assert dev["vid"] == "10C4"
        assert dev["status"] == "CONNECTED"

        # Update status
        db.mark_device_status("DEV_COM1_10C4_EA60", "DISCONNECTED")
        dev_updated = db.get_device("DEV_COM1_10C4_EA60")
        assert dev_updated["status"] == "DISCONNECTED"

        # 3. Log operations
        op_id = db.log_operation(
            device_id="DEV_COM1_10C4_EA60",
            operation_type="BAUD_SCAN",
            status="SUCCESS",
            details={"baudrate": 115200, "latency_ms": 12.4},
            duration_ms=45,
        )
        assert op_id > 0

        # 4. Record backup dump
        backup_id = db.record_backup(
            device_id="DEV_COM1_10C4_EA60",
            backup_path="/backups/dev_com1_eeprom.bin",
            checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            size_bytes=65536,
            metadata={"chip": "AT24C64", "bus_speed_khz": 400},
        )
        assert backup_id > 0


if __name__ == "__main__":
    import inspect

    test_functions = [
        obj for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    print(f"Running {len(test_functions)} Phase 01 test cases...")
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
