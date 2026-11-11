"""Comprehensive unit tests for UniversalReasoningGovernor across ALL models and providers."""

import unittest
from pathlib import Path
from agents.IVA.engine.agi17.orchestration.gemini_reasoning_governor import (
    GeminiReasoningGovernor,
    UniversalReasoningGovernor,
    IVAReasoningGovernor,
    ReasoningConfig,
)
from agents.IVA.engine.agi17.mcp.mcp_manager import MCPManager
from agents.IVA.engine.agi17.adapters.iva_adapter import IVAAdapter, AGI17Adapter


class TestUniversalReasoningGovernorAcrossAllModels(unittest.TestCase):
    def setUp(self):
        self.governor = UniversalReasoningGovernor()

    def test_alias_parity(self):
        self.assertIs(UniversalReasoningGovernor, GeminiReasoningGovernor)
        self.assertIs(IVAReasoningGovernor, GeminiReasoningGovernor)
        self.assertIs(IVAAdapter, AGI17Adapter)

    def test_gemini_38_flash_thinking_throttle(self):
        """Verifies Gemini 3.8 Flash clamps thinking budget to 0 on UI and small edits."""
        prompt = "Change navbar button background color to dark blue"
        patch = self.governor.get_model_payload_patch("gemini-3.8-flash", prompt)
        
        self.assertEqual(patch["task_category"], "FAST_PATH_UI")
        self.assertEqual(patch["sla_seconds"], 60.0)
        gen_cfg = patch["payload_fields"]["generationConfig"]
        self.assertEqual(gen_cfg["thinkingConfig"]["thinkingBudget"], 0)
        self.assertEqual(gen_cfg["thinking"]["thinking_level"], "low")
        self.assertIn("CRITICAL SUB-60S FAST-PATH UI DIRECTIVE", patch["system_instruction_addon"])

    def test_openai_o1_o3_reasoning_effort(self):
        """Verifies OpenAI reasoning models (o1, o3, o3-mini) receive clamped reasoning_effort."""
        prompt = "Fix typography on the homepage footer"
        patch_o1 = self.governor.get_model_payload_patch("o1", prompt)
        self.assertEqual(patch_o1["payload_fields"]["reasoning_effort"], "low")
        self.assertLessEqual(patch_o1["sla_seconds"], 60.0)

        patch_o3 = self.governor.get_model_payload_patch("o3-mini", prompt)
        self.assertEqual(patch_o3["payload_fields"]["reasoning_effort"], "low")

    def test_deepseek_r1_reasoning_effort(self):
        """Verifies DeepSeek-R1 receives clamped reasoning parameters."""
        prompt = "Update the padding of card component"
        patch = self.governor.get_model_payload_patch("deepseek-ai/deepseek-r1", prompt)
        self.assertEqual(patch["payload_fields"]["reasoning_effort"], "low")

    def test_anthropic_claude_thinking_budget(self):
        """Verifies Claude 3.7 Sonnet extended thinking is only enabled when deep reasoning is needed."""
        # Fast edit: thinking disabled / omitted
        fast_patch = self.governor.get_model_payload_patch("claude-3-7-sonnet", "Fix CSS button hover")
        self.assertNotIn("thinking", fast_patch["payload_fields"])
        self.assertEqual(fast_patch["payload_fields"]["temperature"], 0.2)

        # Deep quant math: thinking enabled with bounded budget
        deep_prompt = "Calibrate Gatheral SVI volatility smile and check Roger Lee arbitrage-free bounds"
        deep_patch = self.governor.get_model_payload_patch("claude-3-7-sonnet", deep_prompt)
        self.assertIn("thinking", deep_patch["payload_fields"])
        self.assertEqual(deep_patch["payload_fields"]["thinking"]["type"], "enabled")
        self.assertGreater(deep_patch["payload_fields"]["thinking"]["budget_tokens"], 0)

    def test_universal_models_groq_and_local(self):
        """Verifies Groq, Llama, and local models receive clean single-pass configurations."""
        patch = self.governor.get_model_payload_patch("llama-3.3-70b-versatile", "What is the capital of France?")
        self.assertEqual(patch["task_category"], "DIRECT_QUESTION")
        self.assertEqual(patch["sla_seconds"], 5.0)
        self.assertIn("CRITICAL ANTI-OVERANALYSIS DIRECTIVE", patch["system_instruction_addon"])

    def test_standalone_mcp_catalog(self):
        manager = MCPManager()
        self.assertTrue(manager.is_standalone_ready())
        catalog = manager.get_native_capability_catalog()
        self.assertTrue(catalog["standalone_mode"])
        self.assertFalse(catalog["requires_external_mcp"])


if __name__ == "__main__":
    unittest.main()
