"""Unit test suite for IVA Antigravity Preflight Guardian & Background Persistence."""

import json
import os
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.orchestration.antigravity_preflight_guardian import (
    AntigravityPreflightGuardian,
    PreflightReport,
    is_pid_alive,
)
from agents.IVA.engine.agi17.orchestration.gemini_reasoning_governor import UniversalReasoningGovernor


class TestAntigravityPreflightGuardian(unittest.TestCase):
    """Verifies Turn-0 background task health auditing, code update checks, and restart recovery."""

    def setUp(self):
        self.guardian = AntigravityPreflightGuardian()

    def test_pid_liveness_check(self):
        """Verifies cross-platform PID liveness detection."""
        my_pid = os.getpid()
        self.assertTrue(is_pid_alive(my_pid), "Current process PID must be detected as alive")
        self.assertFalse(is_pid_alive(-1), "Negative PID must be false")
        self.assertFalse(is_pid_alive(9999999), "Non-existent PID must be false")

    def test_preflight_evaluation_on_chat(self):
        """Verifies Turn-0 preflight report executes quickly and reports valid state."""
        report = self.guardian.evaluate_preflight_on_chat()
        
        self.assertIsInstance(report, PreflightReport)
        self.assertIn("Preflight Verified:", report.summary_message)
        self.assertTrue(report.surgical_experiment_passed, "Surgical AST experiment must be verified")
        self.assertIn(report.task_status, ["HEALTHY_ACTIVE", "HEADLESS_IDLE", "RESTART_RECOVERED_IDLE"])
        self.assertIn("~48MB", report.ram_state)

    def test_governor_turn_zero_integration(self):
        """Verifies that the Reasoning Governor includes preflight health in auto-injected memory."""
        gov = UniversalReasoningGovernor()
        res = gov.resolve_turn_zero_memory("Hello Iva, what is the status of our background tasks?")
        
        self.assertIn("preflight_background_health", res)
        p_data = res["preflight_background_health"]
        self.assertEqual(p_data["surgical_experiment_passed"], True)
        self.assertIn("current_git_commit", p_data)


if __name__ == "__main__":
    unittest.main()
