"""
Phase 11 Unit & Integration Test Suite:
OMNIS Cloud Sync Agent, AI Log Analyzer, Unbrick Orchestrator, and Setup Launcher Pipeline.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.omnis_cloud_sync import OMNISCloudAgent
from core.ai_log_analyzer import AILogAnalyzer, UnbrickOrchestrator
from setup_and_run import init_database_schema


class TestPhase11OmnisAndAIAnalyzer(unittest.TestCase):
    """Unit tests for Phase 11 OMNIS Cloud Sync, AI Log Analyzer, and Setup Launcher."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_omnis.db"

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_omnis_cloud_agent_audit_logging_and_sync(self) -> None:
        """Verify audit log recording and asynchronous batch cloud synchronization."""
        agent = OMNISCloudAgent(db_path=self.db_path)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 1. Log audit entries
            logged = loop.run_until_complete(
                agent.push_audit_log_entry_async("FRP_WIPE_EXECUTE", "TECH_007", {"chipset": "QUALCOMM"})
            )
            self.assertTrue(logged)

            # 2. Batch Sync
            sync_res = loop.run_until_complete(agent.sync_pending_events_async(batch_size=10))
            self.assertIn("events_synced", sync_res)
            self.assertGreaterEqual(sync_res["events_synced"], 1)

            # 3. Check status
            status = agent.get_sync_status()
            self.assertIn("synced_events_lifetime", status)
        finally:
            loop.close()

    def test_ai_log_analyzer_pattern_recognition_and_unbrick(self) -> None:
        """Verify AI pattern recognition for kernel panics and automated unbrick routine execution."""
        orchestrator = UnbrickOrchestrator(target_port="COM3")
        analyzer = AILogAnalyzer(unbrick_orchestrator=orchestrator)

        # Test GPT Header CRC Mismatch log
        gpt_log = """[0.123] Kernel panic - not syncing: GPT Header CRC mismatch!
[0.124] Invalid LBA 1 header signature: 0x00000000. Bad partition table detected.
"""
        res_gpt = analyzer.analyze_log_and_recommend_unbrick(gpt_log, auto_execute=True)
        self.assertEqual(res_gpt["failure_type"], "PARTITION_TABLE_CORRUPTION")
        self.assertEqual(res_gpt["recommended_routine"], "repair_partition_table")
        self.assertTrue(res_gpt["auto_executed"])
        self.assertEqual(res_gpt["execution_result"]["status"], "SUCCESS")

        # Test Bootloader VBMeta failure log
        vbmeta_log = """[1.456] avb_slot_verify.c:123: ERROR: vbmeta partition verification failed!
[1.457] Bootloader locked / XBL signed image check error.
"""
        res_vb = analyzer.analyze_log_and_recommend_unbrick(vbmeta_log, auto_execute=True)
        self.assertEqual(res_vb["failure_type"], "BOOTLOADER_VERIFICATION_FAILURE")
        self.assertEqual(res_vb["recommended_routine"], "flash_stock_bootloader")
        self.assertTrue(res_vb["auto_executed"])
        self.assertEqual(res_vb["execution_result"]["status"], "SUCCESS")

    def test_setup_database_schema_initialization(self) -> None:
        """Verify master setup database schema initialization."""
        ok = init_database_schema()
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
