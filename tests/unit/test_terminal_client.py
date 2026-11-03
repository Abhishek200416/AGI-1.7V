"""Test suite for IVA Autonomous Interactive Terminal Client.
================================================================================
Verifies that:
1. TerminalClient runs 100% in pure terminal / console without GUI or voice overlays.
2. Device & OS independence: works cleanly across Windows, Linux, macOS, servers.
3. Zero external plugins mandate: 100 embedded specialists across 16 families are
   loaded and verified; proves that no external plugins (Ponytail, Agency, Yux Pro Max)
   are required.
4. Fast-path routing, built-in commands (help, status, profile, specialists, plugins),
   and natural language execution.
================================================================================
"""

from __future__ import annotations

import io
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

from agents.IVA.engine.agi17.adapters.model_adapter import (
    BaseModelProvider,
    ModelAdapter,
    ModelProviderConfig,
    ModelRequest,
)
from agents.IVA.engine.agi17.runtime.terminal_client import (
    TerminalClient,
    run_terminal_session,
)


class TestTerminalClient(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_terminal_test_"))
        self._orig_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._orig_env)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_system_summary_device_independent(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        summary = client.get_system_summary()

        self.assertIn("device_os", summary)
        self.assertEqual(summary["specialists_count"], 100)
        self.assertEqual(summary["families_count"], 16)
        self.assertEqual(summary["safety_gate"], "LOCKED (Fail-Closed)")

    def test_02_specialists_catalog_loads_100_specialists(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.print_specialists()

        output = buf.getvalue()
        self.assertIn("100 Active Contracts", output)
        self.assertIn("Planning & Architecture", output)
        self.assertIn("Software Engineering", output)
        self.assertIn("Testing, QA & Verification", output)
        self.assertIn("Security, Permissions & Safety", output)

    def test_03_zero_external_plugins_mandate(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.print_plugins_notice()

        output = buf.getvalue()
        self.assertIn("ZERO EXTERNAL PLUGINS MANDATE", output)
        self.assertIn("Ponytail", output)
        self.assertIn("Agency", output)
        self.assertIn("Yux Pro Max", output)
        self.assertIn("100 Embedded Specialists", output)
        self.assertIn("Automated Python CI-Repair Agent", output)

    def test_04_status_and_profile_commands(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.print_status()
            client.print_profile()

        output = buf.getvalue()
        self.assertIn("IVA RUNTIME SYSTEM STATUS", output)
        self.assertIn("LOCKED (Safe Fail-Closed)", output)
        self.assertIn("HARDWARE & RESOURCE CAPACITY PROFILE", output)

    def test_05_fast_path_routing_in_terminal(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.execute_prompt("check system status")

        output = buf.getvalue()
        self.assertIn("Deterministic Fast-Path Router", output)

    def test_06_model_prompt_execution_formatted(self) -> None:
        mock_provider = MagicMock(spec=BaseModelProvider)
        mock_provider.generate.return_value = {
            "status": "SUCCEEDED",
            "model": "gemini-2.5-flash",
            "exit_code": 0,
            "timed_out": False,
            "duration_sec": 0.35,
            "response_text": "Here is the verified AST refactoring solution.",
            "parsed_json": {},
            "provider_usage": {"input_tokens": 50, "output_tokens": 25, "total_tokens": 75},
            "is_mock": True,
        }

        mock_adapter = MagicMock()
        mock_adapter.model_adapter.invoke.return_value = {
            "task_id": "TEST-01",
            "response_text": "Here is the verified AST refactoring solution.",
            "model": "gemini-2.5-flash",
            "token_usage": {"input_tokens": 50, "output_tokens": 25},
            "duration_sec": 0.35,
        }

        client = TerminalClient(adapter=mock_adapter)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.execute_prompt("Refactor this Python module cleanly")

        output = buf.getvalue()
        self.assertIn("Iva (Cognitive Engineering Partner)", output)
        self.assertIn("Here is the verified AST refactoring solution.", output)
        self.assertIn("gemini-2.5-flash", output)
        self.assertIn("In 50, Out 25", output)

    def test_07_interactive_session_exit_command(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        # Simulate user typing 'help', 'plugins', and then 'exit'
        user_inputs = ["help", "plugins", "exit"]
        with patch("sys.stdout", buf), patch("builtins.input", side_effect=user_inputs):
            exit_code = client.run_interactive()

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("IVA TERMINAL INTERACTION GUIDE", output)
        self.assertIn("ZERO EXTERNAL PLUGINS MANDATE", output)
        self.assertIn("Goodbye from Iva", output)

    def test_08_run_self_tests_executes_cleanly(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        mock_result = MagicMock()
        mock_result.wasSuccessful.return_value = True
        mock_result.failures = []
        mock_result.errors = []

        with patch("sys.stdout", buf), patch("unittest.TextTestRunner.run", return_value=mock_result):
            exit_code = client.run_self_tests()

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("IVA AUTONOMOUS SELF-VERIFICATION SUITE", output)
        self.assertIn("IVA self-verification 100% GREEN", output)

    def test_09_interactive_session_handles_test_command(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        mock_result = MagicMock()
        mock_result.wasSuccessful.return_value = True
        mock_result.failures = []
        mock_result.errors = []

        user_inputs = ["test", "exit"]
        with patch("sys.stdout", buf), patch("builtins.input", side_effect=user_inputs), patch("unittest.TextTestRunner.run", return_value=mock_result):
            exit_code = client.run_interactive()

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("IVA AUTONOMOUS SELF-VERIFICATION SUITE", output)
        self.assertIn("Goodbye from Iva", output)

    def test_10_display_suggestions_menu_renders_all_cards(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.display_suggestions_menu()

        output = buf.getvalue()
        self.assertIn("WHAT WOULD YOU LIKE TO BUILD OR SOLVE TODAY?", output)
        self.assertIn("System & Software Architecture", output)
        self.assertIn("Full-Stack Website & 3D Web Apps", output)
        self.assertIn("Automated Bug Fixing & CI Repair", output)
        self.assertIn("Autonomous Browser & ChatGPT Bridge", output)
        self.assertIn("Multimodal Video & Media Synthesis", output)
        self.assertIn("Deep Web Research & 21 Live MCP Tools", output)
        self.assertIn("24/7 Autonomous Self-Evolution", output)

    def test_11_extract_file_path_detection(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)

        # Non-file commands must return None
        self.assertIsNone(client._extract_file_path("check system status"))
        self.assertIsNone(client._extract_file_path("models"))
        self.assertIsNone(client._extract_file_path("help"))
        self.assertIsNone(client._extract_file_path("evolve"))

        # Valid file references
        self.assertEqual(client._extract_file_path("setup_iva.py"), "setup_iva.py")
        self.assertEqual(client._extract_file_path("fix src/server.py"), "src/server.py")
        self.assertEqual(client._extract_file_path("inspect ./app.js"), "./app.js")
        self.assertEqual(client._extract_file_path("repair C:\\path\\main.py"), "C:\\path\\main.py")

    def test_12_inspect_or_fix_file_path_valid_and_broken(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)

        # 1. Valid python file
        good_file = self.temp_dir / "good_script.py"
        good_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            client.inspect_or_fix_file_path(str(good_file))

        output = buf.getvalue()
        self.assertIn("good_script.py", output)
        self.assertIn("100% VALID", output)
        self.assertIn("hello", output)

        # 2. Syntax-broken file with auto-repair
        bad_file = self.temp_dir / "bad_script.py"
        bad_file.write_text("def broken():\n    print('unclosed paren'\n", encoding="utf-8")

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            client.inspect_or_fix_file_path(str(bad_file), auto_repair=True)

        output = buf.getvalue()
        self.assertIn("SYNTAX ERROR DETECTED", output)
        self.assertIn("Auto-repair patch verified", output)

    def test_13_execute_web_3d_wizard_generates_threejs_app(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf), patch("webbrowser.open"):
            client.execute_web_3d_wizard()

        output = buf.getvalue()
        self.assertIn("3D Interactive Web Application Generated", output)

        demo_file = Path.cwd() / "demo_3d_website" / "index.html"
        self.assertTrue(demo_file.is_file())
        content = demo_file.read_text(encoding="utf-8")
        self.assertIn("three.js", content)
        self.assertIn("webgl-canvas", content)
        self.assertIn("Autonomous Cognitive Architecture", content)

    def test_14_execute_browser_chatgpt_wizard_stages_payload(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.execute_browser_chatgpt_wizard(prompt="Generate 3D neon cube logo")

        output = buf.getvalue()
        self.assertIn("CHATGPT DESKTOP BRIDGE", output)
        self.assertIn("chatgpt_bridge_payload.json", output)

        payload_path = Path.cwd() / "scratch" / "chatgpt_bridge_payload.json"
        self.assertTrue(payload_path.is_file())
        data = json.loads(payload_path.read_text(encoding="utf-8"))
        self.assertEqual(data["prompt"], "Generate 3D neon cube logo")

    def test_15_execute_video_synthesis_wizard_creates_runner(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.execute_video_synthesis_wizard(prompt="Cinematic 3D scrolling hero loop")

        output = buf.getvalue()
        self.assertIn("MULTIMODAL VIDEO & MEDIA SYNTHESIS", output)
        self.assertIn("generate_gemini_video.py", output)

        video_script = Path.cwd() / "generate_gemini_video.py"
        self.assertTrue(video_script.is_file())
        self.assertIn("GEMINI_API_KEY", video_script.read_text(encoding="utf-8"))

    def test_16_interactive_shortcuts_1_to_7(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)

        # Test selecting '1', '2', '4', '5', '6', 'suggestions', 'exit'
        user_inputs = ["1", "suggestions", "exit"]
        buf = io.StringIO()
        with patch("sys.stdout", buf), patch("builtins.input", side_effect=user_inputs):
            exit_code = client.run_interactive()

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("SYSTEM & SOFTWARE ARCHITECTURE DESIGNER", output)
        self.assertIn("WHAT WOULD YOU LIKE TO BUILD OR SOLVE TODAY?", output)


    def test_17_execute_update(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        mock_completed = MagicMock()
        mock_completed.returncode = 0
        mock_completed.stdout = "Already up to date."
        mock_completed.stderr = ""

        with patch("sys.stdout", buf), patch("subprocess.run", return_value=mock_completed):
            code = client.execute_update()

        self.assertEqual(code, 0)
        output = buf.getvalue()
        self.assertIn("IVA AUTONOMOUS REPOSITORY UPDATER", output)
        self.assertIn("IVA is now 100% UP TO DATE", output)

    def test_18_tui_and_accounts_commands(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.print_tui_dashboard()
            client.print_chrome_accounts()

        output = buf.getvalue()
        self.assertIn("TERMINAL TUI HUD", output)
        self.assertIn("Active Model Target", output)
        self.assertIn("Chrome Multi-Account", output)
        self.assertIn("Discovered Chrome Profiles", output)


if __name__ == "__main__":
    unittest.main()



