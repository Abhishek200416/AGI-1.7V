"""Unit test suite for IVA SessionManager.
================================================================================
Tests:
1. Creation, retrieval, and persistence of CLI work sessions.
2. Tracking session turns, prompts, responses, and models.
3. Tracking touched/modified files.
4. Switching active sessions.
5. Markdown transcript export.
================================================================================
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.runtime.session_manager import SessionManager


class TestSessionManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_sess_test_"))
        self.mgr = SessionManager(storage_dir=self.temp_dir)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_initial_session_created(self) -> None:
        active = self.mgr.get_active_session()
        self.assertTrue(active.is_active)
        self.assertTrue(active.session_id.startswith("sess_"))
        self.assertEqual(len(self.mgr.list_sessions()), 1)

    def test_02_create_and_switch_sessions(self) -> None:
        s2 = self.mgr.create_session("FeatureSprint")
        self.assertTrue(s2.is_active)
        self.assertEqual(s2.name, "FeatureSprint")

        sessions = self.mgr.list_sessions()
        self.assertEqual(len(sessions), 2)

        # Switch back to first session
        s1 = [s for s in sessions if s.session_id != s2.session_id][0]
        switched = self.mgr.switch_session(s1.session_id)
        self.assertIsNotNone(switched)
        self.assertEqual(switched.session_id, s1.session_id)
        self.assertTrue(switched.is_active)

    def test_03_record_turn_and_file_change(self) -> None:
        turn = self.mgr.record_turn(
            prompt="Build 3D Scene",
            response="3D scene built in index.html",
            model="nvidia/llama-3.1-nemotron-70b-instruct",
            modified_files=["frontend/index.html", "frontend/js/app.js"],
        )
        self.assertEqual(turn.turn_index, 1)
        self.assertEqual(turn.model, "nvidia/llama-3.1-nemotron-70b-instruct")

        active = self.mgr.get_active_session()
        self.assertEqual(len(active.turns), 1)
        self.assertIn("frontend/index.html", active.modified_files)

        # Record standalone file change
        self.mgr.record_file_change("backend/server.py")
        active = self.mgr.get_active_session()
        self.assertIn("backend/server.py", active.modified_files)

    def test_04_export_session_markdown(self) -> None:
        self.mgr.record_turn(
            prompt="Hello Iva",
            response="Hello! Ready to build.",
            model="gemini-2.5-flash",
            modified_files=["app.py"],
        )
        md = self.mgr.export_session_markdown()
        self.assertIn("# IVA Session Transcript", md)
        self.assertIn("Turn 1", md)
        self.assertIn("Hello Iva", md)
        self.assertIn("app.py", md)


if __name__ == "__main__":
    unittest.main()
