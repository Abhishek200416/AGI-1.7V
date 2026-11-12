"""Unit tests for UniversalAPIProvider automated fallback and free model routing."""

import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from agents.IVA.engine.agi17.adapters.model_adapter import ModelRequest
from agents.IVA.engine.agi17.adapters.universal_api_provider import UniversalAPIProvider


class TestApiFallbackAndFreeModels(unittest.TestCase):
    """Verifies automatic failover to free models and local cognitive fallback."""

    def test_respects_active_provider_from_env(self):
        """Verifies ACTIVE_PROVIDER env var takes precedence in provider detection."""
        with patch.dict("os.environ", {
            "ACTIVE_PROVIDER": "openrouter",
            "NVIDIA_API_KEY": "nvapi-test1234",
            "OPENROUTER_API_KEY": "sk-or-v1-test5678",
        }):
            provider = UniversalAPIProvider.create_from_env()
            self.assertEqual(provider.provider_brand, "openrouter")
            self.assertIn("openrouter.ai", provider.base_url)

    @patch("urllib.request.urlopen")
    def test_openrouter_404_or_402_auto_fallbacks_to_free_model(self, mock_urlopen):
        """Verifies when a primary model returns 404/402, it automatically tries free models."""
        provider = UniversalAPIProvider(
            provider_type="openrouter",
            api_key="sk-or-v1-mockkey",
            model_name="anthropic/claude-3.5-sonnet",
            base_url="https://openrouter.ai/api/v1",
        )

        # First call fails with 404 (Function / model not found)
        err_fp = MagicMock()
        err_fp.read.return_value = b'{"error": "Model not available"}'
        http_404 = urllib.error.HTTPError("url", 404, "Not Found", {}, err_fp)

        # Second call (fallback to free model) succeeds
        success_resp = MagicMock()
        success_resp.__enter__.return_value = success_resp
        success_resp.read.return_value = b'{"choices": [{"message": {"content": "Hello from free fallback model!"}}], "usage": {"prompt_tokens": 5, "completion_tokens": 8, "total_tokens": 13}}'

        mock_urlopen.side_effect = [http_404, success_resp]

        req = ModelRequest(task_id="test_fallback_1", prompt="hi")
        res = provider.generate(req)

        self.assertEqual(res.get("status"), "SUCCEEDED")
        self.assertIn("Hello from free fallback model!", res.get("response_text", ""))
        self.assertIn(":free", res.get("model", ""))

    @patch("urllib.request.urlopen")
    def test_local_cognitive_fallback_when_all_remote_fail(self, mock_urlopen):
        """Verifies local cognitive partner response is returned if all remote calls fail."""
        provider = UniversalAPIProvider(
            provider_type="openrouter",
            api_key="sk-or-v1-mockkey",
            model_name="unreachable-model",
            base_url="https://openrouter.ai/api/v1",
        )

        # All calls fail with URLError
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        req = ModelRequest(task_id="test_local_fallback", prompt="hi")
        res = provider.generate(req)

        self.assertEqual(res.get("status"), "SUCCEEDED")
        self.assertIn("I am Iva", res.get("response_text", ""))
        self.assertIn("Local Cognitive Partner Engine", res.get("model", ""))


    def test_provider_key_auto_detection_and_multi_pool(self):
        """Verifies accurate detection of OpenRouter, NVIDIA, Gemini, Groq, Anthropic keys."""
        self.assertEqual(UniversalAPIProvider.detect_provider_from_key("sk-or-v1-abc12345"), "openrouter")
        self.assertEqual(UniversalAPIProvider.detect_provider_from_key("nvapi-xyz987654"), "nvidia")
        self.assertEqual(UniversalAPIProvider.detect_provider_from_key("AIzaSyB1234567"), "gemini")
        self.assertEqual(UniversalAPIProvider.detect_provider_from_key("gsk_ultra999"), "groq")
        self.assertEqual(UniversalAPIProvider.detect_provider_from_key("sk-ant-api03-test"), "anthropic")

        # Verify pool contains OpenRouter and NVIDIA with valid active models
        with patch.dict("os.environ", {
            "OPENROUTER_API_KEY": "sk-or-v1-mock",
            "NVIDIA_API_KEY": "nvapi-mock",
            "GEMINI_API_KEY": "AIzaSyMock",
        }):
            pool = UniversalAPIProvider.get_configured_providers_pool()
            self.assertIn("openrouter", pool)
            self.assertIn("nvidia", pool)
            self.assertIn("gemini", pool)
            self.assertEqual(pool["nvidia"]["default_model"], "meta/llama-3.3-70b-instruct")
            self.assertIn("openrouter.ai", pool["openrouter"]["base_url"])


if __name__ == "__main__":
    unittest.main()
