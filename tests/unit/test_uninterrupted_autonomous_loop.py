"""Unit tests for UninterruptedAutonomousLoop in IVA AGI 1.8."""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.IVA.engine.agi17.orchestration.uninterrupted_loop import (
    LoopExecutionResult,
    UninterruptedAutonomousLoop,
)
from agents.IVA.engine.agi17.task_control.task_state_machine import TaskState


class TestUninterruptedAutonomousLoop(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_loop_test_"))
        self.workspace_dir = self.temp_dir / "repo"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir = self.temp_dir / "storage"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Create a buggy calculator module
        self.calc_file = self.workspace_dir / "calculator.py"
        self.calc_file.write_text(
            "def add(a: int, b: int) -> int:\n    return a - b  # BUG: subtracts instead of adds\n",
            encoding="utf-8",
        )

        # Create the unit test that fails on the bug
        self.test_file = self.workspace_dir / "test_calculator.py"
        self.test_file.write_text(
            "import unittest\nfrom calculator import add\n\n"
            "class TestCalculator(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_standard_uninterrupted_loop_execution(self) -> None:
        loop = UninterruptedAutonomousLoop(
            workspace_dir=self.workspace_dir,
            primary_model="gemini-2.5-pro",
            storage_root=self.storage_dir,
        )

        # Mock model invoker that fixes the bug
        def mock_invoker(model: str, prompt: str) -> str:
            return (
                "```python\n"
                "def add(a: int, b: int) -> int:\n"
                "    return a + b\n"
                "```"
            )

        result = loop.execute_loop(
            objective="Fix addition bug in calculator.py",
            target_module_rel="calculator.py",
            test_pattern="test_calculator.py",
            model_invoker=mock_invoker,
            simulate_quota_limit=False,
        )

        self.assertEqual(result.status, "SUCCEEDED_AND_VERIFIED")
        self.assertFalse(result.initial_test_passed)
        self.assertTrue(result.final_test_passed)
        self.assertTrue(result.ast_verified)
        self.assertTrue(result.patch_applied)
        self.assertIn("a + b", result.unified_diff)
        self.assertTrue(bool(result.sha256_evidence))

        # Verify task was recorded and marked SUCCEEDED in SQLite
        tasks = loop.task_manager.store.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["state"], "SUCCEEDED")

        # Verify memory entry exists
        memories = loop.memory.retrieve(query="calculator", limit=5)
        self.assertGreater(len(memories), 0)

    def test_02_resilient_quota_continuation_in_loop(self) -> None:
        """Verifies that when primary model hits HTTP 429 quota exhaustion,
        ModelContinuationEngine cascades to successor, completes execution,
        and heals the repository without interruption.
        """
        loop = UninterruptedAutonomousLoop(
            workspace_dir=self.workspace_dir,
            primary_model="gemini-2.5-pro",
            storage_root=self.storage_dir,
        )

        # Successor invoker returns the working code
        def successor_invoker(model: str, prompt: str) -> str:
            return (
                "def add(a: int, b: int) -> int:\n"
                "    return a + b\n"
                "```"
            )

        result = loop.execute_loop(
            objective="Fix calculator under quota exhaustion",
            target_module_rel="calculator.py",
            test_pattern="test_calculator.py",
            model_invoker=successor_invoker,
            simulate_quota_limit=True,
        )

        self.assertEqual(result.status, "REPAIRED_WITH_CONTINUATION")
        self.assertTrue(result.failover_occurred)
        self.assertEqual(result.primary_model, "gemini-2.5-pro")
        self.assertIn("nvidia", result.final_model.lower())  # Cascaded to NVIDIA cross-provider
        self.assertTrue(result.final_test_passed)
        self.assertTrue(result.ast_verified)
        self.assertIn("a + b", self.calc_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
