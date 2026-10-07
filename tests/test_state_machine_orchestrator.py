"""
Unit Tests for State Machine Orchestrator & Automation Cockpit HUD (`tests/test_state_machine_orchestrator.py`).
Tests deterministic FSM transitions, sequential queue prioritization, 5s timeout fallback,
operator overrides (Pause, Skip, Confirm, Abort), SQLite WAL audit ledger, and HUD GUI integration.
"""

import asyncio
import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from core.state_machine_orchestrator import (
    AutomatedStateMachineOrchestrator,
    InterfaceProfileCandidate,
    OrchestratorState,
    ProtocolType,
    SequentialProfileQueue,
)
from ui.automation_cockpit import AutomationCockpitHUD


class TestStateMachineOrchestrator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_ledger.db"
        self.orchestrator = AutomatedStateMachineOrchestrator(
            db_path=self.db_path,
            timeout_sec=0.5  # fast timeout for unit tests
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sqlite_wal_ledger_initialization(self):
        self.assertTrue(self.db_path.exists())
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode;")
            mode = cur.fetchone()[0]
            self.assertEqual(mode.lower(), "wal")

            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orchestrator_ledger';")
            tbl = cur.fetchone()
            self.assertIsNotNone(tbl)

    def test_sequential_profile_queue_prioritization(self):
        # EDL test candidates
        candidates = self.orchestrator._build_candidate_profiles("COM3", "05C6", "9008", "Qualcomm Test Device")
        self.assertGreaterEqual(len(candidates), 2)
        # Priority 0 must be Qualcomm EDL
        first = candidates[0]
        self.assertEqual(first.protocol, ProtocolType.QUALCOMM_EDL)
        self.assertEqual(first.priority, 0)
        self.assertEqual(first.expected_vid, "05C6")
        self.assertEqual(first.expected_pid, "9008")

        queue = SequentialProfileQueue(candidates)
        self.assertEqual(queue.total_count, len(candidates))
        self.assertEqual(queue.current_index, 0)
        self.assertEqual(queue.current_candidate().protocol, ProtocolType.QUALCOMM_EDL)

        # Advance
        next_cand = queue.advance()
        self.assertIsNotNone(next_cand)
        self.assertEqual(queue.current_index, 1)

    def test_state_machine_transitions_and_ledger_logging(self):
        transitions: list[tuple[OrchestratorState, OrchestratorState]] = []

        def _listener(old_s, new_s, reason):
            transitions.append((old_s, new_s))

        self.orchestrator.add_state_listener(_listener)

        self.orchestrator.transition_to(OrchestratorState.HOTPLUG_DETECTED, "USB device attached")
        self.orchestrator.transition_to(OrchestratorState.INTERFACE_PROFILING, "Building queue")
        self.orchestrator.transition_to(OrchestratorState.DRIVER_BINDING, "Checking WinUSB")

        self.assertEqual(self.orchestrator.current_state, OrchestratorState.DRIVER_BINDING)
        self.assertEqual(len(transitions), 3)

        # Verify ledger rows in SQLite
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.cursor()
            cur.execute("SELECT state_from, state_to, status FROM orchestrator_ledger;")
            rows = cur.fetchall()
            self.assertGreaterEqual(len(rows), 3)
            self.assertEqual(rows[0][1], "HOTPLUG_DETECTED")
            self.assertEqual(rows[1][1], "INTERFACE_PROFILING")
            self.assertEqual(rows[2][1], "DRIVER_BINDING")

    def test_operator_pause_and_resume_controls(self):
        self.orchestrator.transition_to(OrchestratorState.HANDSHAKE_VERIFICATION, "Testing handshake")
        self.orchestrator.pause_countdown()
        self.assertEqual(self.orchestrator.current_state, OrchestratorState.PAUSED)
        self.assertFalse(self.orchestrator._pause_event.is_set())

        self.orchestrator.resume_countdown()
        self.assertEqual(self.orchestrator.current_state, OrchestratorState.HANDSHAKE_VERIFICATION)
        self.assertTrue(self.orchestrator._pause_event.is_set())

    def test_operator_abort_control(self):
        self.orchestrator.abort_pipeline()
        self.assertEqual(self.orchestrator.current_state, OrchestratorState.FAILED_TERMINATED)
        self.assertTrue(self.orchestrator._abort_requested.is_set())

    def test_operator_confirm_active_profile(self):
        self.orchestrator.confirm_active_profile()
        self.assertTrue(self.orchestrator._confirm_requested.is_set())

    def test_operator_skip_active_profile(self):
        self.orchestrator.skip_active_profile()
        self.assertTrue(self.orchestrator._skip_requested.is_set())

    def test_closed_loop_pipeline_execution(self):
        # Run pipeline with fast timeout
        loop = asyncio.new_event_loop()
        try:
            res = loop.run_until_complete(
                self.orchestrator._execute_closed_loop("COM3", "05C6", "9008", "Snapdragon 8 Gen 2")
            )
            self.assertEqual(res["status"], "SUCCESS")
            self.assertEqual(self.orchestrator.current_state, OrchestratorState.IDLE_COMPLETED)
        finally:
            loop.close()

    def test_automation_cockpit_hud_headless_lifecycle(self):
        hud = AutomationCockpitHUD(orchestrator=self.orchestrator, headless=True)
        self.assertIsNotNone(hud.root)

        # Trigger countdown tick and state change
        cand = InterfaceProfileCandidate(
            profile_id="test_cand",
            protocol=ProtocolType.QUALCOMM_EDL,
            title="Qualcomm Test",
            target_port="COM3",
            expected_vid="05C6",
            expected_pid="9008",
            priority=0,
            service_action="QUALCOMM_LOADER_FLASH"
        )
        hud._render_countdown_tick(4.2, 5.0, cand)
        hud._render_state_change(OrchestratorState.DISCONNECTED, OrchestratorState.HANDSHAKE_VERIFICATION, "Test")

        hud.destroy()
        self.assertTrue(hud._is_destroyed)


if __name__ == "__main__":
    unittest.main()
