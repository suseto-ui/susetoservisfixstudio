"""
Phase 05 E2E & System Hardening Test Suite.
"""

from __future__ import annotations

import asyncio
import os
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

from storage.wal_ledger import SQLiteWALLedger
from core.system_health_monitor import SystemHealthMonitor
from ui.system_verification_component import SystemVerificationComponent
from val.esp32_adapter import ESP32Adapter


@pytest.mark.asyncio
async def test_wal_ledger_async_logging_and_backup():
    """Verify asynchronous WAL logging, querying, and snapshot backup creation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "wal_test.db")
        ledger = SQLiteWALLedger(db_path=db_file)

        log_id = await ledger.log_event("COM3", "DEVICE_ATTACHED", {"vid": "10C4", "pid": "EA60"})
        assert log_id > 0

        logs = await ledger.query_logs(limit=10)
        assert len(logs) == 1
        assert logs[0]["port"] == "COM3"
        assert logs[0]["event_type"] == "DEVICE_ATTACHED"

        backup_path = await ledger.create_backup_snapshot()
        assert os.path.exists(backup_path)
        if os.path.exists(backup_path):
            os.remove(backup_path)


@pytest.mark.asyncio
async def test_system_health_monitor_watchdog():
    """Verify system health monitor and watchdog adapter reset recovery."""
    monitor = SystemHealthMonitor(check_interval=0.05)
    await monitor.start()

    adapter = ESP32Adapter("COM3")
    adapter.enter_bootloader = MagicMock(return_value=asyncio.sleep(0, True) or True)

    success = await monitor.trigger_watchdog_recovery(adapter)
    assert success is True
    assert monitor.fault_count == 1

    metrics = monitor.get_metrics()
    assert metrics["fault_count"] == 1
    assert metrics["status"] == "HEALTHY"

    await monitor.stop()


@pytest.mark.asyncio
async def test_system_verification_e2e_flow():
    """Verify full E2E diagnostic test runner sequence and green indicators."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "e2e_wal.db")
        ledger = SQLiteWALLedger(db_path=db_file)
        verifier = SystemVerificationComponent(ledger)

        res = await verifier.run_full_e2e_diagnostic("COM3")
        assert res["success"] is True
        assert len(res["results"]) == 5
        for r in res["results"]:
            assert r["status"] == "PASSED"

        # Verify WAL ledger recorded the audit trail
        logs = await ledger.query_logs()
        assert any(l["event_type"] == "E2E_DIAGNOSTIC_COMPLETE" for l in logs)


if __name__ == "__main__":
    import inspect

    test_functions = [
        obj for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    print(f"Running {len(test_functions)} Phase 05 test cases...")
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
