"""Unit tests for TurnZeroContextRehydrator."""

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.IVA.engine.agi17.orchestration.turn_zero_context_rehydrator import (
    RehydratedContext,
    TurnZeroContextRehydrator,
)
from agents.IVA.engine.agi17.process_supervision.daemon_ipc import DaemonIpcServer


class TestTurnZeroContextRehydrator(unittest.TestCase):
    """Tests total situational rehydration on Turn-0 across IPC, preflight, and SQLite."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="iva_rehydrate_test_")
        self.workspace_root = Path(self.temp_dir)
        self.db_path = self.workspace_root / "test_memory.db"

        # Create mock sqlite database with goals table
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("""
            CREATE TABLE autonomous_goals (
                id INTEGER PRIMARY KEY,
                title TEXT,
                status TEXT,
                priority REAL
            )
        """)
        c.execute("INSERT INTO autonomous_goals VALUES (1, 'Calibrate Hawkes jump diffusion', 'ACTIVE', 10.0)")
        c.execute("INSERT INTO autonomous_goals VALUES (2, 'Deploy tri-tab browser sandbox', 'IN_PROGRESS', 8.0)")
        conn.commit()
        conn.close()

        # Spin up IPC server
        self.server = DaemonIpcServer(host="127.0.0.1", port=0, workspace_root=self.workspace_root)
        self.server.start()
        self.server.set_task_state(
            task_id="task_live_123",
            name="Continuous_Evolution_Cycle",
            phase="EVALUATING_CODE_DIFF",
            progress_pct=88.0,
        )
        self.server.record_log("Executed 100 test iterations with 100% pass", level="INFO", category="QA")

        self.rehydrator = TurnZeroContextRehydrator(
            workspace_root=self.workspace_root,
            memory_db_path=self.db_path,
        )

    def tearDown(self):
        self.server.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_rehydration_with_active_daemon_and_memory(self):
        """Verifies situational context is extracted without missing any active work."""
        ctx = self.rehydrator.rehydrate()

        self.assertIsInstance(ctx, RehydratedContext)
        self.assertTrue(ctx.is_daemon_alive)
        self.assertEqual(ctx.task_name, "Continuous_Evolution_Cycle")
        self.assertEqual(ctx.execution_phase, "EVALUATING_CODE_DIFF")
        self.assertEqual(ctx.progress_pct, 88.0)
        self.assertIn("Calibrate Hawkes jump diffusion", ctx.unresolved_goals)
        self.assertIn("IVA TURN-0 REHYDRATED CONTEXT", ctx.rehydration_prompt_block)
        self.assertIn("Continuous_Evolution_Cycle", ctx.rehydration_prompt_block)

    def test_rehydration_when_daemon_is_offline(self):
        """Verifies graceful fallback when background daemon is offline."""
        self.server.stop()

        ctx = self.rehydrator.rehydrate()
        self.assertIsInstance(ctx, RehydratedContext)
        # Should gracefully report state without crashing
        self.assertIn("IVA TURN-0 REHYDRATED CONTEXT", ctx.rehydration_prompt_block)


if __name__ == "__main__":
    unittest.main()
