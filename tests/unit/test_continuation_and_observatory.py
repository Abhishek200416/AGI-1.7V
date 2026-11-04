"""Unit tests for ModelContinuationEngine and AutonomousMCPSkillInstaller in IVA AGI 1.8."""

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


class TestContinuationAndSkills(unittest.TestCase):
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

        # Context length overflow
        is_lim, category = ModelContinuationEngine.is_limit_exhausted("Maximum context length exceeded: 131072 tokens")
        self.assertTrue(is_lim)
        self.assertEqual(category, "CONTEXT_OVERFLOW")

        # Normal response
        is_lim, category = ModelContinuationEngine.is_limit_exhausted("Success 200 OK")
        self.assertFalse(is_lim)
        self.assertEqual(category, "NONE")

    def test_02_accurate_token_estimation(self) -> None:
        # Prose text: ~3.8 chars per token
        prose = "The quick brown fox jumps over the lazy dog in the sunny afternoon."
        prose_tokens = ModelContinuationEngine.estimate_tokens(prose)
        self.assertGreater(prose_tokens, 10)
        self.assertLess(prose_tokens, 25)

        # Code with high syntax density: ~3.1 chars per token
        code = 'def calculate_metrics(data: List[Dict[str, Any]]) -> float: return sum(d["val"] for d in data) * 0.05;'
        code_tokens = ModelContinuationEngine.estimate_tokens(code)
        self.assertGreater(code_tokens, 20)

    def test_03_successor_model_cascade_and_cross_provider_failover(self) -> None:
        pool = [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "claude-3-5-sonnet-20241022",
        ]
        # Standard cascade from pro to flash
        succ = ModelContinuationEngine.select_next_successor_model("gemini-2.5-pro", pool)
        self.assertEqual(succ, "gemini-2.5-flash")

        # On QUOTA_EXHAUSTED for gemini, deliberately switch providers to NVIDIA or Claude to prevent hitting same quota
        cross_succ = ModelContinuationEngine.select_next_successor_model(
            failed_model="gemini-2.5-pro",
            available_pool=pool,
            limit_reason="QUOTA_EXHAUSTED",
        )
        self.assertIn("nvidia", cross_succ)

        # On code domain, prioritize code models
        code_succ = ModelContinuationEngine.select_next_successor_model(
            failed_model="gemini-2.5-flash",
            available_pool=pool,
            task_domain="code",
        )
        self.assertIn("nemotron", code_succ)

    def test_04_full_context_preservation_and_continuation_prompt(self) -> None:
        # Verify no 1500 char cutoff: full partial output preserved
        partial_code = "def render_scene():\n" + ("    x = 1\n" * 200) + "    return x\n"
        self.assertGreater(len(partial_code), 2000)

        snapshot = ContextSnapshot(
            task_id="TASK-CONT-01",
            original_prompt="Build 3D Neural Observatory with Three.js",
            partial_output=partial_code,
            tokens_consumed=ModelContinuationEngine.estimate_tokens(partial_code),
            limit_type="QUOTA_EXHAUSTED",
        )
        prompt = ModelContinuationEngine.build_continuation_prompt(snapshot, "nvidia/llama-3.1-nemotron-70b-instruct")
        self.assertIn("SYSTEM CONTINUATION HANDOFF", prompt)
        self.assertIn("nvidia/llama-3.1-nemotron-70b-instruct", prompt)
        self.assertIn("def render_scene():", prompt)
        self.assertIn("return x", prompt)
        self.assertIn("Build 3D Neural Observatory with Three.js", prompt)

    def test_05_stitch_continuation(self) -> None:
        partial = "def test_func():\n    return 42"
        continuation = "    # Continuation added\n"
        stitched = ModelContinuationEngine.stitch_continuation(partial, continuation)
        self.assertIn("def test_func():", stitched)
        self.assertIn("return 42", stitched)
        self.assertIn("Continuation added", stitched)

        # Overlapping line removal
        partial_dup = "line1\nline2"
        continuation_dup = "line2\nline3"
        stitched_dup = ModelContinuationEngine.stitch_continuation(partial_dup, continuation_dup)
        self.assertEqual(stitched_dup.strip(), "line1\nline2\nline3")

    def test_06_active_execute_continuation(self) -> None:
        def mock_invoker(model: str, p: str) -> str:
            return f"\n    # Completed by {model}\n    return True\n"

        res = ModelContinuationEngine.execute_continuation(
            failed_model="gemini-2.5-pro",
            original_prompt="Write a validation function",
            partial_output="def validate():\n",
            error_reason="HTTP 429: Quota exceeded",
            provider_or_caller=mock_invoker,
            task_domain="code",
        )
        self.assertEqual(res["status"], "CONTINUATION_COMPLETED")
        self.assertIn("validate", res["completed_output"])
        self.assertIn("Completed by", res["completed_output"])
        self.assertGreater(res["total_tokens"], 0)

    def test_07_mcp_skill_installer_gap_detection(self) -> None:
        installer = AutonomousMCPSkillInstaller(target_dir=self.temp_dir / "skills")
        needed = installer.detect_missing_skills("I want a 3D website with three.js and cyber exploit security testing")
        self.assertIn("threejs_3d_engine", needed)
        self.assertIn("cyber_exploit_tester", needed)

    def test_08_mcp_skill_installer_installs_functional_helpers(self) -> None:
        installer = AutonomousMCPSkillInstaller(target_dir=self.temp_dir / "skills")
        
        # Install cyber_exploit_tester
        res = installer.auto_install_skill("cyber_exploit_tester")
        self.assertEqual(res["status"], "INSTALLED_AND_MOUNTED")
        
        helper_path = Path(res["helper_script"])
        self.assertTrue(helper_path.exists())
        code_content = helper_path.read_text(encoding="utf-8")
        
        # Verify it has real functional code, NOT placeholder comments
        self.assertIn("class CyberExploitTester", code_content)
        self.assertIn("CWE-95", code_content)
        self.assertIn("CWE-78", code_content)

        # Execute the helper dynamically to prove functionality
        namespace = {}
        exec(code_content, namespace)
        tester = namespace["CyberExploitTester"]
        report = tester.scan_code("eval('dangerous()')")
        self.assertEqual(report["status"], "VULNERABILITIES_FOUND")
        self.assertEqual(report["findings"][0]["cwe"], "CWE-95")

    def test_09_threejs_render_helper_functional_execution(self) -> None:
        installer = AutonomousMCPSkillInstaller(target_dir=self.temp_dir / "skills")
        res = installer.auto_install_skill("threejs_3d_engine")
        self.assertEqual(res["status"], "INSTALLED_AND_MOUNTED")

        helper_code = Path(res["helper_script"]).read_text(encoding="utf-8")
        namespace = {}
        exec(helper_code, namespace)
        helper = namespace["ThreeJSRenderHelper"]

        html = helper.generate_html_boilerplate(title="Neural Cosmos")
        self.assertIn("THREE.WebGLRenderer", html)
        self.assertIn("THREE.PerspectiveCamera", html)

        val = helper.validate_threejs_script(html)
        self.assertTrue(val["valid"])


if __name__ == "__main__":
    unittest.main()
