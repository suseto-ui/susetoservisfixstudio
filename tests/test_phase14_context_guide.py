"""
Phase 14 Unit & Integration Test Suite:
Context-Aware Technician Diagnostic & Repair Advisor Engine,
IF / WHAT / WHY Step Generator, and PySide6 Interactive HUD Widget.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.context_advisor import (
    DeviceStateProfiler,
    ContextAdvisorEngine,
    AdvisorStep,
    SafetyRating,
)
from ui._qt_compat import QApplication
from ui.context_guide_wizard import ContextGuideWidget


class TestPhase14ContextGuideWizard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication.instance() is None:
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.engine = ContextAdvisorEngine()

    def test_device_state_profiler_categories(self):
        """Verify profiler correctly classifies hardware states and modes."""
        edl_state = DeviceStateProfiler.profile_device(vid="05C6", pid="9008", mode="EDL_FLASH")
        self.assertEqual(edl_state, "QUALCOMM_EDL_BRICKED")

        brom_state = DeviceStateProfiler.profile_device(vid="0E8D", pid="0003", mode="BROM_DAA")
        self.assertEqual(brom_state, "MTK_BROM_LOCKED")

        samsung_state = DeviceStateProfiler.profile_device(vid="04E8", pid="6860", mode="SAMSUNG_MTP")
        self.assertEqual(samsung_state, "SAMSUNG_MTP_FRP")

        unisoc_state = DeviceStateProfiler.profile_device(vid="1782", pid="4D00", mode="SPRD_FDL")
        self.assertEqual(unisoc_state, "UNISOC_BOOTLOADER_CORRUPT")

        fastboot_state = DeviceStateProfiler.profile_device(vid="18D1", pid="4EE0", mode="FASTBOOT")
        self.assertEqual(fastboot_state, "FASTBOOT_BOOTLOOP")

    def test_context_advisor_step_generation_and_if_what_why(self):
        """Verify generation of IF / WHAT / WHY technical steps for Qualcomm EDL."""
        steps = self.engine.analyze_and_plan(vid="05C6", pid="9008", port="COM3", mode="EDL")
        self.assertEqual(len(steps), 3)

        step1 = steps[0]
        self.assertEqual(step1.step_number, 1)
        self.assertIn("EDL", step1.condition_if)
        self.assertIn("Sahara", step1.action_what)
        self.assertIn("XBL", step1.rationale_why)
        self.assertEqual(step1.safety_rating, SafetyRating.SAFE)

        step_dict = step1.to_dict()
        self.assertIn("condition_if", step_dict)
        self.assertIn("rationale_why", step_dict)
        self.assertEqual(step_dict["safety_rating"], "SAFE")

    def test_advisor_step_progression_and_completion(self):
        """Verify advancing, previous, and completing advisor workflow steps."""
        self.engine.analyze_and_plan(vid="0E8D", pid="0003", port="COM5", mode="BROM")
        self.assertEqual(self.engine.current_step_index, 0)

        # Advance to step 2
        next_step = self.engine.advance_step()
        self.assertIsNotNone(next_step)
        self.assertEqual(next_step.step_number, 2)
        self.assertIn("NVRAM", next_step.title)

        # Advance to step 3
        next_step3 = self.engine.advance_step()
        self.assertEqual(next_step3.step_number, 3)

        # Advance past final step
        final_step = self.engine.advance_step()
        self.assertIsNone(final_step)

        # Go back to previous step
        prev_step = self.engine.previous_step()
        self.assertIsNotNone(prev_step)
        self.assertEqual(prev_step.step_number, 3)

    def test_context_guide_widget_lifecycle(self):
        """Verify ContextGuideWidget rendering, signals, and execution button."""
        widget = ContextGuideWidget()
        self.assertIn("Kontextový", widget.lbl_title.text())

        # Load Qualcomm context
        widget.load_device_context(vid="05C6", pid="9008", port="COM3", mode="EDL")
        self.assertIn("1 z 3", widget.lbl_step_counter.text())
        self.assertTrue(widget.btn_execute.isEnabled())

        # Test action signal trigger
        received_actions = []
        widget.step_action_triggered.connect(lambda aid, atitle: received_actions.append((aid, atitle)))

        widget._on_execute_clicked()
        self.assertEqual(len(received_actions), 1)
        self.assertEqual(received_actions[0][0], "EXEC_SAHARA_FIREHOSE")
        self.assertIn("2 z 3", widget.lbl_step_counter.text())


if __name__ == "__main__":
    unittest.main()
