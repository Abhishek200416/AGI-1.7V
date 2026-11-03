"""Unit tests for ModelContinuationEngine, AutonomousMCPSkillInstaller, and 3D Observatory."""

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

from agents.IVA.engine.agi17.adapters.model_continuation_engine import (
    ContextSnapshot,
    ContinuationHandoff,
    ModelContinuationEngine,
)
from agents.IVA.engine.agi17.skills.mcp_skill_installer import AutonomousMCPSkillInstaller
from applications.iva_3d_observatory.server import ObservatoryRequestHandler


class TestContinuationAndObservatory(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_continuation_test_"))
        self._orig_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._orig_env)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_detect_limit_exhaustion_scenarios(self) -> None:
        # Rate limit 429
        is_lim, category = ModelContinuationEngine.is_limit_exhausted("HTTP 429 Too Many Requests")
        self.assertTrue(is_lim)
        self.assertEqual(category, "QUOTA_EXHAUSTED")

        # Quota exceeded
        is_lim, category = ModelContinuationEngine.is_limit_exhausted("Daily quota exceeded for model")
        self.assertTrue(is_lim)
        self.assertEqual(category, "QUOTA_EXHAUSTED")

        # Max tokens finish reason
        is_lim, category = ModelContinuationEngine.is_limit_exhausted("", finish_reason="MAX_TOKENS")
        self.assertTrue(is_lim)
        self.assertEqual(category, "MAX_TOKENS")

        # Normal response
        is_lim, category = ModelContinuationEngine.is_limit_exhausted("Success 200 OK")
        self.assertFalse(is_lim)
        self.assertEqual(category, "NONE")

    def test_02_successor_model_cascade_selection(self) -> None:
        # If gemini-2.5-pro fails, successor should cascade to flash
        pool = ["gemini-2.5-pro", "gemini-2.5-flash", "nvidia/llama-3.1-nemotron-70b-instruct"]
        successor = ModelContinuationEngine.select_next_successor_model("gemini-2.5-pro", pool)
        self.assertEqual(successor, "gemini-2.5-flash")

        # If gemini-2.5-flash also fails, successor should cascade to nemotron
        successor_2 = ModelContinuationEngine.select_next_successor_model("gemini-2.5-flash", pool)
        self.assertEqual(successor_2, "gemini-2.5-pro")

    def test_03_continuation_prompt_synthesis(self) -> None:
        snapshot = ContextSnapshot(
            task_id="TASK-CONT-01",
            original_prompt="Build 3D Neural Observatory with Three.js",
            partial_output="const scene = new THREE.Scene();",
            tokens_consumed=150,
            limit_type="QUOTA_EXHAUSTED",
        )
        prompt = ModelContinuationEngine.build_continuation_prompt(snapshot, "gemini-2.5-flash")
        self.assertIn("SYSTEM CONTINUATION HANDOFF", prompt)
        self.assertIn("gemini-2.5-flash", prompt)
        self.assertIn("const scene = new THREE.Scene();", prompt)
        self.assertIn("Build 3D Neural Observatory with Three.js", prompt)

    def test_04_mcp_skill_installer_gap_detection(self) -> None:
        installer = AutonomousMCPSkillInstaller(target_dir=self.temp_dir / "skills")
        needed = installer.detect_missing_skills("I want a 3D website with three.js and cyber exploit security testing")
        self.assertIn("threejs_3d_engine", needed)
        self.assertIn("cyber_exploit_tester", needed)

    def test_05_mcp_skill_installer_zero_friction_install(self) -> None:
        installer = AutonomousMCPSkillInstaller(target_dir=self.temp_dir / "skills")
        res = installer.auto_install_skill("threejs_3d_engine")
        self.assertEqual(res["status"], "INSTALLED_AND_MOUNTED")
        self.assertEqual(res["skill"], "threejs_3d_engine")

        skill_dir = Path(res["path"])
        self.assertTrue((skill_dir / "SKILL.md").exists())
        self.assertTrue((skill_dir / "helper.py").exists())

    def test_06_observatory_server_api_endpoints(self) -> None:
        # Mock request handler methods
        handler = ObservatoryRequestHandler.__new__(ObservatoryRequestHandler)
        status = handler.get_system_status()
        self.assertEqual(status["application"], "IVA 3D Neural Observatory")
        self.assertEqual(status["context_window_max"], 2000000)
        self.assertEqual(status["cascade_failover_status"], "ARMED")

        telemetry = handler.get_live_telemetry()
        self.assertEqual(telemetry["neural_cluster_count"], 64)
        self.assertEqual(telemetry["quantum_particle_count"], 2500)

        nodes = handler.get_neural_nodes()
        self.assertEqual(nodes["count"], 64)
        self.assertEqual(len(nodes["nodes"]), 64)


if __name__ == "__main__":
    unittest.main()
