"""
Comprehensive Test Suite for Universal Hardware Diagnostic Engine (`tests/test_universal_engine.py`).
Validates all 8 architectural layers:
- State Machine (FSM)
- Event Bus & SQLite WAL Logger
- Port & Tuning Engine (DTR/RTS + Auto-Baud)
- Vendor & Model Layer (VAL - Qualcomm, MTK, Espressif, STM32)
- Memory & Flash Pipeline (4096B Block Streaming + Checksums)
- Memory Recovery Agent (Volatile RAM & CPU Registers Extractor)
- Hardware Fault Injection & RTT Telemetry
- System Health Watchdog & Non-Destructive Soft-Reset
- End-to-End (E2E) Full-Chain Diagnostic Benchmark
- NativeStudioBridge & API Endpoints
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from core.state_machine import DiagnosticStateMachine, EngineState, StateTransitionError
from core.event_bus import HardwareEventBus
from core.port_tuning_engine import PortTuningEngine
from val.chipset_val import UnifiedVendorAbstractionLayer
from core.memory_pipeline import MemoryStreamPipeline
from core.memory_recovery_agent import MemoryRecoveryAgent
from core.fault_injection_engine import FaultInjectionEngine
from core.telemetry_rtt import TelemetryRttMonitor
from core.system_watchdog import SystemHealthWatchdog
from core.e2e_diagnostic_suite import E2EDiagnosticSuite
from core.native_bridge import NativeStudioBridge


class TestUniversalHardwareEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_bus.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. STATE MACHINE (FSM)
    def test_state_machine_valid_transitions(self):
        fsm = DiagnosticStateMachine()
        self.assertEqual(fsm.current_state, EngineState.DISCONNECTED)

        fsm.transition_to(EngineState.DETECTING, reason="TEST_SCAN")
        self.assertEqual(fsm.current_state, EngineState.DETECTING)

        fsm.transition_to(EngineState.PORT_TUNING, reason="TEST_TUNE")
        self.assertEqual(fsm.current_state, EngineState.PORT_TUNING)

        fsm.transition_to(EngineState.OEM_HANDSHAKE, reason="TEST_VAL")
        self.assertEqual(fsm.current_state, EngineState.OEM_HANDSHAKE)

        fsm.transition_to(EngineState.STREAMING_IO, reason="TEST_STREAM")
        self.assertEqual(fsm.current_state, EngineState.STREAMING_IO)

        fsm.transition_to(EngineState.RECOVERY_VERIFY, reason="TEST_REC")
        self.assertEqual(fsm.current_state, EngineState.RECOVERY_VERIFY)

        fsm.transition_to(EngineState.IDLE_READY, reason="TEST_READY")
        self.assertEqual(fsm.current_state, EngineState.IDLE_READY)

        history = fsm.get_history()
        self.assertGreater(len(history), 5)

    def test_state_machine_invalid_transition_raises(self):
        fsm = DiagnosticStateMachine()
        with self.assertRaises(StateTransitionError):
            # DISCONNECTED -> STREAMING_IO is disallowed directly
            fsm.transition_to(EngineState.STREAMING_IO)

    # 2. EVENT BUS & SQLITE WAL LOGGER
    def test_event_bus_wal_persistence_and_pubsub(self):
        bus = HardwareEventBus(self.db_path)
        received_events = []

        bus.subscribe("hw/port_connect", lambda ev: received_events.append(ev))
        bus.publish("hw/port_connect", {"port": "COM3", "vid": "05C6", "pid": "9008"}, source="USB_DOCTOR")

        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0]["payload"]["port"], "COM3")

        # Query SQLite WAL
        rows = bus.query_recent_events(limit=10, topic_filter="hw/port_connect")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "USB_DOCTOR")

    # 3. PORT & TUNING ENGINE (DTR/RTS & AUTO-BAUD)
    def test_port_tuning_engine_scan_and_negotiation(self):
        engine = PortTuningEngine()
        ports = engine.scan_ports()
        self.assertIsInstance(ports, list)
        self.assertGreater(len(ports), 0)

        # Verify auto-baud negotiation
        res = engine.negotiate_baudrate("COM3", 921600)
        self.assertIn("negotiated_baud", res)
        self.assertIn(res["negotiated_baud"], engine.STANDARD_BAUD_RATES)

        # Verify DTR/RTS pulse sequences
        esp_pulse = engine.trigger_dtr_rts_sequence("COM7", "ESP32")
        self.assertEqual(esp_pulse["status"], "BOOTLOADER_TRIGGERED")
        self.assertGreater(len(esp_pulse["steps_executed"]), 1)

        stm_pulse = engine.trigger_dtr_rts_sequence("COM9", "STM32")
        self.assertEqual(stm_pulse["status"], "BOOTLOADER_TRIGGERED")

    # 4. VENDOR & MODEL LAYER (VAL)
    def test_vendor_abstraction_layer_chipsets(self):
        val = UnifiedVendorAbstractionLayer()
        profiles = val.list_profiles()
        self.assertGreaterEqual(len(profiles), 4)

        # Espressif ESP32 Sync
        esp_res = val.execute_espressif_sync("COM7", 115200)
        self.assertEqual(esp_res["vendor"], "ESPRESSIF")
        self.assertEqual(esp_res["status"], "SYNC_SUCCESS")
        self.assertIn("24:6F:28", esp_res["mac_address"])

        # STM32 Bootloader
        stm_res = val.execute_stm32_bootloader("COM9", 115200)
        self.assertEqual(stm_res["vendor"], "STMICROELECTRONICS")
        self.assertEqual(stm_res["status"], "BOOTLOADER_ACK")
        self.assertIn("0x0423", stm_res["product_id"])

        # MTK NVRAM / IMEI Repair
        mtk_res = val.execute_mtk_nvram_repair("COM5", "860123456789012", "860123456789013")
        self.assertEqual(mtk_res["vendor"], "MEDIATEK")
        self.assertEqual(mtk_res["status"], "NVRAM_RESTORED")
        self.assertEqual(mtk_res["imei1"], "860123456789012")

    # 5. MEMORY & FLASH PIPELINE (4096B STREAMING DUMP)
    def test_memory_pipeline_streaming_dump(self):
        mem_dir = Path(self.temp_dir.name) / "dumps"
        pipeline = MemoryStreamPipeline(output_dir=mem_dir)

        progress_snapshots = []
        res = pipeline.stream_dump_partition(
            partition_name="boot_test",
            total_size_bytes=16384,  # 16 KB (4 blocks)
            chunk_size=4096,
            progress_cb=lambda p: progress_snapshots.append(p)
        )

        self.assertEqual(res["status"], "STREAM_COMPLETED")
        self.assertEqual(res["bytes_dumped"], 16384)
        self.assertEqual(res["blocks_processed"], 4)
        self.assertIn("crc32", res["checksums"])
        self.assertIn("sha256", res["checksums"])
        self.assertTrue(Path(res["file_path"]).exists())
        self.assertGreater(len(progress_snapshots), 0)

    # 6. MEMORY RECOVERY AGENT (VOLATILE RAM & CPU CRASHDUMP)
    def test_memory_recovery_agent_extraction(self):
        crash_dir = Path(self.temp_dir.name) / "crashes"
        agent = MemoryRecoveryAgent(dump_dir=crash_dir)

        res = agent.extract_emergency_crashdump("COM3", "ARM64")
        self.assertEqual(res["status"], "RECOVERY_EXTRACTED")
        self.assertIn("PC", res["registers"])
        self.assertIn("SP", res["registers"])
        self.assertIn("LR", res["registers"])
        self.assertGreater(len(res["call_stack"]), 0)
        self.assertEqual(res["ram_size_bytes"], 2048)
        self.assertTrue(Path(res["dump_file"]).exists())

    # 7. HARDWARE FAULT INJECTION & TELEMETRY
    def test_fault_injection_and_telemetry(self):
        fault_engine = FaultInjectionEngine()
        bench = fault_engine.run_fault_injection_benchmark("COM3", noise_level_pct=10.0, frame_drop_pct=5.0, total_packets=20)
        self.assertEqual(bench["status"], "BENCHMARK_COMPLETED")
        self.assertEqual(bench["total_packets_sent"], 20)
        self.assertGreater(bench["bus_stability_score_pct"], 50.0)
        self.assertGreater(len(bench["rtt_samples_sparkline"]), 5)

        # Telemetry Monitor
        telemetry = TelemetryRttMonitor(max_samples=30)
        telemetry.record_sample(1.1)
        telemetry.record_sample(1.3)
        metrics = telemetry.get_metrics_snapshot()
        self.assertIn("current_rtt_ms", metrics)
        self.assertIn("average_rtt_ms", metrics)
        self.assertIn("sparkline_data", metrics)

    # 8. SYSTEM HEALTH WATCHDOG & SOFT-RESET
    def test_system_health_watchdog(self):
        watchdog = SystemHealthWatchdog()
        health = watchdog.get_system_health()
        self.assertEqual(health["status"], "HEALTHY")
        self.assertTrue(health["watchdog_active"])

        reset_res = watchdog.soft_reset_stalled_port("COM3")
        self.assertEqual(reset_res["status"], "PORT_RESET_SUCCESS")
        self.assertTrue(reset_res["is_now_ready"])
        self.assertGreater(len(reset_res["actions_executed"]), 1)

    # 9. END-TO-END (E2E) FULL-CHAIN DIAGNOSTIC BENCHMARK
    def test_e2e_diagnostic_suite_pipeline(self):
        suite = E2EDiagnosticSuite()
        res = suite.run_full_e2e_pipeline(target_port="COM3", target_vendor="QUALCOMM")
        self.assertEqual(res["status"], "E2E_PASSED")
        self.assertEqual(res["final_fsm_state"], EngineState.IDLE_READY.value)
        self.assertEqual(len(res["steps"]), 6)
        for step in res["steps"]:
            self.assertTrue(step["passed"], f"Step failed: {step['name']}")

    # 10. NATIVE STUDIO BRIDGE
    def test_native_bridge_api(self):
        bridge = NativeStudioBridge()
        status = bridge.get_system_status()
        self.assertIn("platform", status)

        ports = bridge.scan_hardware_ports()
        self.assertIn("total_ports_detected", ports)

        esp = bridge.execute_espressif_sync("COM7", 115200)
        self.assertEqual(esp["vendor"], "ESPRESSIF")

        stm = bridge.execute_stm32_bootloader("COM9", 115200)
        self.assertEqual(stm["vendor"], "STMICROELECTRONICS")

        pulse = bridge.trigger_dtr_rts("COM7", "ESP32")
        self.assertEqual(pulse["status"], "BOOTLOADER_TRIGGERED")

        dump = bridge.start_streaming_dump("boot_test", 8192, 4096)
        self.assertEqual(dump["status"], "STREAM_COMPLETED")

        rec = bridge.extract_emergency_crashdump("COM3", "ARM64")
        self.assertEqual(rec["status"], "RECOVERY_EXTRACTED")

        fault = bridge.run_fault_injection_benchmark("COM3", 10.0, 5.0, False, 15)
        self.assertEqual(fault["status"], "BENCHMARK_COMPLETED")

        wd = bridge.run_port_soft_reset("COM3")
        self.assertEqual(wd["status"], "PORT_RESET_SUCCESS")

        e2e = bridge.run_e2e_benchmark("COM3", "QUALCOMM")
        self.assertEqual(e2e["status"], "E2E_PASSED")


if __name__ == "__main__":
    unittest.main()
