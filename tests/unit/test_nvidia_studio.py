"""Unit tests for IVA Sovereign Studio (Powered by NVIDIA NIM)."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from applications.iva_nvidia_studio.server import StudioRequestHandler


class TestNvidiaStudio(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_studio_test_"))
        self._orig_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._orig_env)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_studio_status_metadata(self) -> None:
        handler = StudioRequestHandler.__new__(StudioRequestHandler)
        status = handler.get_studio_status()
        self.assertEqual(status["application"], "IVA Sovereign Studio")
        self.assertEqual(status["provider"], "NVIDIA NIM")
        self.assertTrue(status["has_valid_key"])
        self.assertEqual(status["status"], "ONLINE")

    def test_02_verified_active_models(self) -> None:
        handler = StudioRequestHandler.__new__(StudioRequestHandler)
        models_data = handler.get_active_models()
        self.assertIn("verified_models", models_data)
        model_ids = [m["id"] for m in models_data["verified_models"]]
        self.assertIn("nvidia/nemotron-3.5-bolt-e4b", model_ids)
        self.assertIn("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", model_ids)

    def test_03_mock_execute_generation(self) -> None:
        handler = StudioRequestHandler.__new__(StudioRequestHandler)
        mock_provider_resp = {
            "status": "SUCCEEDED",
            "model": "nvidia/nemotron-3.5-bolt-e4b",
            "response_text": "Mock Nemotron Response Text",
            "provider_usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        }
        with patch("agents.IVA.engine.agi17.adapters.universal_api_provider.UniversalAPIProvider.generate", return_value=mock_provider_resp):
            res = handler.execute_nvidia_generation("Test prompt", "nvidia/nemotron-3.5-bolt-e4b")
            self.assertEqual(res["status"], "ok")
            self.assertEqual(res["model"], "nvidia/nemotron-3.5-bolt-e4b")
            self.assertEqual(res["response"], "Mock Nemotron Response Text")
            self.assertEqual(res["usage"]["total_tokens"], 15)


if __name__ == "__main__":
    unittest.main()
