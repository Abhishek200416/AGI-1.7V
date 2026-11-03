"""Unit tests for ModelMetadataCatalog and Dynamic Action-Based Model Swapping.
================================================================================
Verifies:
1. Exact parameter size parsing (in Billions) across 550B -> 1B models.
2. Company attribution (NVIDIA, Meta, Mistral AI, Writer, IBM, Google, OpenAI, etc.).
3. Sorting strictly descending from highest B parameters to lowest B parameters.
4. Autonomous Dynamic Action Swapping across micro-routing, vision, coding, finance, reasoning.
5. UniversalAPIProvider integration with AUTO model target.
================================================================================
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.IVA.engine.agi17.adapters.model_adapter import ModelRequest
from agents.IVA.engine.agi17.adapters.model_catalog import ModelMetadataCatalog
from agents.IVA.engine.agi17.adapters.universal_api_provider import UniversalAPIProvider


class TestModelCatalog(unittest.TestCase):
    def test_01_parameter_parsing_billions(self) -> None:
        cases = [
            ("nvidia/nemotron-3-ultra-550b-a55b", 550.0),
            ("nvidia/nemotron-4-340b-instruct", 340.0),
            ("nvidia/llama-3.1-nemotron-ultra-253b-v1", 253.0),
            ("mistralai/mixtral-8x22b-v0.1", 176.0),
            ("databricks/dbrx-instruct", 132.0),
            ("mistralai/mistral-large-2-instruct", 123.0),
            ("writer/palmyra-creative-122b", 122.0),
            ("nvidia/nemotron-3-super-120b-a12b", 120.0),
            ("ai21labs/jamba-1.5-large-instruct", 94.0),
            ("meta/llama-3.2-90b-vision-instruct", 90.0),
            ("nvidia/llama-3.1-nemotron-70b-instruct", 70.0),
            ("writer/palmyra-fin-70b-32k", 70.0),
            ("nvidia/llama-3.1-nemotron-51b-instruct", 51.0),
            ("stepfun-ai/step-5-preview", 50.0),
            ("mistralai/mixtral-8x7b-instruct-v0.1", 47.0),
            ("ibm/granite-34b-code-instruct", 34.0),
            ("mistralai/codestral-22b-instruct-v0.1", 22.0),
            ("openai/gpt-oss-20b", 20.0),
            ("meta/llama-3.2-11b-vision-instruct", 11.0),
            ("ibm/granite-3.0-8b-instruct", 8.0),
            ("mistralai/mistral-7b-instruct-v0.3", 7.0),
            ("deepseek-ai/deepseek-coder-6.7b-instruct", 6.7),
            ("google/gemma-3-12b-it", 12.0),
            ("google/gemma-2b", 2.0),
            ("meta/llama-3.2-1b-instruct", 1.0),
        ]
        for m_id, expected_b in cases:
            actual_b = ModelMetadataCatalog.parse_parameter_billions(m_id)
            self.assertEqual(actual_b, expected_b, f"Failed parsing {m_id}: expected {expected_b}, got {actual_b}")

    def test_02_company_attribution(self) -> None:
        cases = [
            ("nvidia/llama-3.1-nemotron-70b-instruct", "NVIDIA"),
            ("meta/llama-3.2-90b-vision-instruct", "Meta"),
            ("mistralai/mistral-large-2-instruct", "Mistral AI"),
            ("deepseek-ai/deepseek-coder-6.7b-instruct", "DeepSeek"),
            ("writer/palmyra-creative-122b", "Writer"),
            ("databricks/dbrx-instruct", "Databricks"),
            ("ibm/granite-3.0-8b-instruct", "IBM"),
            ("openai/gpt-oss-20b", "OpenAI"),
            ("gemini-2.5-flash", "Google"),
            ("claude-3-5-sonnet-20241022", "Anthropic"),
            ("ai21labs/jamba-1.5-large-instruct", "AI21 Labs"),
        ]
        for m_id, expected_comp in cases:
            actual_comp = ModelMetadataCatalog.extract_company(m_id)
            self.assertEqual(actual_comp, expected_comp, f"Failed company for {m_id}")

    def test_03_rank_and_sort_models_descending_by_parameters(self) -> None:
        models = [
            "ibm/granite-3.0-8b-instruct",
            "nvidia/nemotron-3-ultra-550b-a55b",
            "meta/llama-3.2-11b-vision-instruct",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "writer/palmyra-creative-122b",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            "google/gemma-2b",
            "nvidia/nemotron-3-super-120b-a12b",
            "meta/llama-3.2-90b-vision-instruct",
            "mistralai/codestral-22b-instruct-v0.1",
        ]
        ranked = ModelMetadataCatalog.rank_and_sort_models(models)
        self.assertEqual(len(ranked), len(models))

        # First model must be 550B
        self.assertEqual(ranked[0]["model_id"], "nvidia/nemotron-3-ultra-550b-a55b")
        self.assertEqual(ranked[0]["params_b"], 550.0)

        # Second model must be 253B
        self.assertEqual(ranked[1]["model_id"], "nvidia/llama-3.1-nemotron-ultra-253b-v1")
        self.assertEqual(ranked[1]["params_b"], 253.0)

        # Third model must be 122B
        self.assertEqual(ranked[2]["model_id"], "writer/palmyra-creative-122b")
        self.assertEqual(ranked[2]["params_b"], 122.0)

        # Fourth model must be 120B
        self.assertEqual(ranked[3]["model_id"], "nvidia/nemotron-3-super-120b-a12b")
        self.assertEqual(ranked[3]["params_b"], 120.0)

        # Last model must be 2B
        self.assertEqual(ranked[-1]["model_id"], "google/gemma-2b")
        self.assertEqual(ranked[-1]["params_b"], 2.0)

        # Check strict descending monotonic order
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(
                ranked[i]["params_b"],
                ranked[i + 1]["params_b"],
                f"Model {ranked[i]['model_id']} ({ranked[i]['params_b']}B) is not >= {ranked[i+1]['model_id']} ({ranked[i+1]['params_b']}B)",
            )

    def test_04_dynamic_action_swapper_model_selection(self) -> None:
        available = [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            "nvidia/nemotron-3-super-120b-a12b",
            "meta/llama-3.2-90b-vision-instruct",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "mistralai/codestral-22b-instruct-v0.1",
            "meta/llama-3.2-11b-vision-instruct",
            "ibm/granite-3.0-8b-instruct",
            "mistralai/mistral-7b-instruct-v0.3",
        ]

        # Vision task -> selects 90B Vision
        vision_model = ModelMetadataCatalog.get_action_model(available, action_type="vision")
        self.assertEqual(vision_model, "meta/llama-3.2-90b-vision-instruct")

        # Fast routing / micro-task -> selects 8B or 7B ultra-fast
        fast_model = ModelMetadataCatalog.get_action_model(available, action_type="fast")
        self.assertIn(fast_model, ("ibm/granite-3.0-8b-instruct", "mistralai/mistral-7b-instruct-v0.3"))

        # Finance / Volatility -> selects Nemotron 120B
        quant_model = ModelMetadataCatalog.get_action_model(available, action_type="finance")
        self.assertEqual(quant_model, "nvidia/nemotron-3-super-120b-a12b")

        # Coding / AST -> selects Nemotron 70B or Codestral 22B
        code_model = ModelMetadataCatalog.get_action_model(available, action_type="coding")
        self.assertEqual(code_model, "nvidia/llama-3.1-nemotron-70b-instruct")

        # Frontier reasoning -> selects Nemotron 253B or 550B
        reasoning_model = ModelMetadataCatalog.get_action_model(available, action_type="reasoning")
        self.assertEqual(reasoning_model, "nvidia/llama-3.1-nemotron-ultra-253b-v1")

    def test_05_universal_api_provider_auto_swapper_resolution(self) -> None:
        provider = UniversalAPIProvider(
            provider_type="nvidia",
            api_key="nvapi-MOCK_KEY_TEST_XYZ",
            model_name="AUTO",
        )
        provider.available_models = [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            "nvidia/nemotron-3-super-120b-a12b",
            "meta/llama-3.2-90b-vision-instruct",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "ibm/granite-3.0-8b-instruct",
        ]

        # Vision request
        req_vision = ModelRequest(task_id="t1", prompt="Inspect screenshot of DOM element #buy-order-btn")
        self.assertEqual(provider.resolve_effective_model(req_vision), "meta/llama-3.2-90b-vision-instruct")

        # Coding request
        req_code = ModelRequest(task_id="t2", prompt="def refactor_order_router(): pass with unittest and pytest")
        self.assertEqual(provider.resolve_effective_model(req_code), "nvidia/llama-3.1-nemotron-70b-instruct")

        # Fast parsing request
        req_fast = ModelRequest(task_id="t3", prompt="classify this route: yes/no")
        self.assertEqual(provider.resolve_effective_model(req_fast), "ibm/granite-3.0-8b-instruct")

        # Volatility request
        req_quant = ModelRequest(task_id="t4", prompt="Calculate Hawkes jump-diffusion intensity and SVI volatility smile for NIFTY")
        self.assertEqual(provider.resolve_effective_model(req_quant), "nvidia/nemotron-3-super-120b-a12b")

        # Deep architecture request
        req_arch = ModelRequest(task_id="t5", prompt="Design the theoretical architecture proof and frontier reasoning theorem for multi-agent synthesis")
        self.assertEqual(provider.resolve_effective_model(req_arch), "nvidia/llama-3.1-nemotron-ultra-253b-v1")


if __name__ == "__main__":
    unittest.main()
