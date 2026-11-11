"""Unit tests for GeminiReasoningGovernor and Standalone Native Capabilities."""

import unittest
from pathlib import Path
from agents.IVA.engine.agi17.orchestration.gemini_reasoning_governor import (
    GeminiReasoningGovernor,
    ReasoningConfig,
)
from agents.IVA.engine.agi17.mcp.mcp_manager import MCPManager
from agents.IVA.engine.agi17.adapters.model_adapter import ModelRequest
from agents.IVA.engine.agi17.adapters.universal_api_provider import UniversalAPIProvider


class TestGeminiReasoningGovernor(unittest.TestCase):
    def setUp(self):
        self.governor = GeminiReasoningGovernor()

    def test_classify_direct_question(self):
        prompt = "What is the capital of France?"
        category = self.governor.classify_task_intent(prompt)
        self.assertEqual(category, "DIRECT_QUESTION")

        cfg = self.governor.govern_reasoning(prompt, model_name="gemini-3.8-flash")
        self.assertEqual(cfg.thinking_level, "minimal")
        self.assertEqual(cfg.thinking_budget, 0)
        self.assertLessEqual(cfg.sla_seconds, 5.0)
        self.assertIn("CRITICAL ANTI-OVERANALYSIS DIRECTIVE", cfg.anti_overanalysis_prompt)

    def test_classify_fast_path_ui_edit(self):
        prompt = "Change the submit button color from red to blue in the navbar"
        category = self.governor.classify_task_intent(prompt)
        self.assertEqual(category, "FAST_PATH_UI")

        cfg = self.governor.govern_reasoning(prompt, model_name="gemini-3.8-flash")
        self.assertEqual(cfg.thinking_level, "low")
        self.assertEqual(cfg.thinking_budget, 0)
        self.assertLessEqual(cfg.sla_seconds, 60.0)
        self.assertIn("CRITICAL SUB-60S FAST-PATH UI DIRECTIVE", cfg.anti_overanalysis_prompt)

    def test_classify_deep_reasoning(self):
        prompt = "Calibrate Gatheral SVI volatility smile and prove Roger Lee arbitrage-free conditions"
        category = self.governor.classify_task_intent(prompt)
        self.assertEqual(category, "DEEP_REASONING")

        cfg = self.governor.govern_reasoning(prompt, model_name="gemini-3.8-flash")
        self.assertEqual(cfg.thinking_level, "high")
        self.assertGreater(cfg.thinking_budget, 0)

    def test_standalone_native_mcp_catalog(self):
        manager = MCPManager()
        self.assertTrue(manager.is_standalone_ready())
        catalog = manager.get_native_capability_catalog()
        self.assertTrue(catalog["standalone_mode"])
        self.assertFalse(catalog["requires_external_mcp"])
        self.assertIn("filesystem", catalog["native_replacements"])
        self.assertIn("memory", catalog["native_replacements"])
        self.assertIn("uiux-mcp", catalog["native_replacements"])


if __name__ == "__main__":
    unittest.main()
