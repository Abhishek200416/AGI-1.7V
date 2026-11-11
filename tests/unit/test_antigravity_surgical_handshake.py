"""Unit test suite for IVA Antigravity Surgical Handshake & Integration Probe."""

import json
import os
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.orchestration.antigravity_surgical_handshake import AntigravitySurgicalHandshake, HandshakeResult


class TestAntigravitySurgicalHandshake(unittest.TestCase):
    """Verifies that the surgical experiment runs non-destructively and achieves 100% pass."""

    def setUp(self):
        self.handshake = AntigravitySurgicalHandshake()

    def test_surgical_experiment_execution(self):
        """Runs the 5-stage surgical probe and verifies all invariants."""
        res = self.handshake.run_surgical_experiment(verbose=False)
        
        self.assertIsInstance(res, HandshakeResult)
        self.assertEqual(res.status, "SUCCESS", f"Handshake failed with details: {res.details}")
        self.assertTrue(res.ast_surgical_experiment_passed, "AST surgical patch must pass")
        self.assertLess(res.ast_experiment_latency_ms, 500.0, "AST surgical patch must complete in < 500ms")
        self.assertTrue(res.reasoning_governor_active, "Gemini reasoning governor must be active")
        self.assertTrue(res.safety_fail_closed_verified, "Fail-closed safety must be verified")
        self.assertGreaterEqual(res.specialists_bridged, 100, "Must bridge at least 100 specialists")

    def test_handshake_receipt_generation(self):
        """Verifies receipt JSON is properly written to scratch directory."""
        res = self.handshake.run_surgical_experiment(verbose=False)
        receipt_path = Path.cwd() / "scratch" / "antigravity_surgical_handshake_receipt.json"
        
        self.assertTrue(receipt_path.exists(), "Receipt JSON must exist")
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["ast_surgical_experiment_passed"], True)
        self.assertEqual(data["reasoning_governor_active"], True)
        self.assertEqual(data["safety_fail_closed_verified"], True)


if __name__ == "__main__":
    unittest.main()
