"""
Unit tests for 100% Free Models selection, filtering, and dynamic swapper.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.IVA.engine.agi17.adapters.model_catalog import ModelMetadataCatalog
from setup_iva import save_key_and_model_to_env, select_model_dialog


class TestFreeModelsSelection(unittest.TestCase):
    def test_filter_free_models(self) -> None:
        mixed_models = [
            "meta-llama/llama-3.3-70b-instruct",
            "meta-llama/llama-3.3-70b-instruct:free",
            "openai/gpt-4o",
            "deepseek/deepseek-r1:free",
            "anthropic/claude-3.5-sonnet",
        ]
        free_only = ModelMetadataCatalog.filter_free_models(mixed_models)
        self.assertEqual(len(free_only), 2)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", free_only)
        self.assertIn("deepseek/deepseek-r1:free", free_only)

    def test_filter_free_models_fallback_when_none(self) -> None:
        paid_models = ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"]
        free_only = ModelMetadataCatalog.filter_free_models(paid_models)
        self.assertGreater(len(free_only), 0)
        self.assertTrue(all(":free" in m or "free" in m for m in free_only))

    def test_rank_and_sort_free_models(self) -> None:
        models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1:free",
            "google/gemini-2.0-flash-exp:free",
            "openai/gpt-4o",
        ]
        ranked_free = ModelMetadataCatalog.rank_and_sort_models(models, free_only=True)
        for item in ranked_free:
            self.assertTrue(item.get("is_free"))
            self.assertIn(":free", item["model_id"])

    def test_get_action_model_free_only(self) -> None:
        models = [
            "meta-llama/llama-3.3-70b-instruct",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "deepseek/deepseek-r1:free",
            "qwen/qwen-2.5-coder-32b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
        ]

        # Vision
        vision_m = ModelMetadataCatalog.get_action_model(models, action_type="vision", free_only=True)
        self.assertEqual(vision_m, "google/gemini-2.0-flash-exp:free")

        # Coding
        code_m = ModelMetadataCatalog.get_action_model(models, action_type="coding", free_only=True)
        self.assertIn(code_m, ["qwen/qwen-2.5-coder-32b-instruct:free", "deepseek/deepseek-r1:free"])

        # Fast
        fast_m = ModelMetadataCatalog.get_action_model(models, action_type="fast", free_only=True)
        self.assertEqual(fast_m, "meta-llama/llama-3.2-3b-instruct:free")

        # Default
        def_m = ModelMetadataCatalog.get_action_model(models, action_type="default", free_only=True)
        self.assertEqual(def_m, "meta-llama/llama-3.3-70b-instruct:free")

    def test_select_model_dialog_free_option(self) -> None:
        models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1:free",
            "openai/gpt-4o",
        ]
        # Simulate user choosing 'F' then '0' (FREE_AUTO)
        with patch("builtins.input", side_effect=["f", "0"]):
            result = select_model_dialog(models, "openrouter")
            self.assertEqual(result, "FREE_AUTO")

        # Simulate user choosing 'F' then '1' (specific free model)
        with patch("builtins.input", side_effect=["free", "1"]):
            result = select_model_dialog(models, "openrouter")
            self.assertIn(":free", result)

    def test_save_env_key_sets_free_flag(self) -> None:
        tmp_env = Path("tests/unit/test_env_tmp.env")
        try:
            save_key_and_model_to_env(
                env_path=tmp_env,
                key="sk-or-test12345",
                model="FREE_AUTO",
                provider="openrouter",
                is_active_provider=True,
            )
            content = tmp_env.read_text(encoding="utf-8")
            self.assertIn("IVA_FREE_ONLY=true", content)
            self.assertIn("ACTIVE_MODEL=FREE_AUTO", content)
        finally:
            if tmp_env.exists():
                tmp_env.unlink()


if __name__ == "__main__":
    unittest.main()
