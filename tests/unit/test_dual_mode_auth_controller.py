"""Unit test suite for IVA Dual-Mode Browser Authentication & Headless RAM Optimization."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.IVA.engine.agi17.browser.dual_mode_auth_controller import (
    BrowserExecutionMode,
    BrowserTransitionState,
    DualModeAuthController,
)
from agents.IVA.engine.agi17.browser.multi_account_browser_manager import MultiAccountBrowserManager
from agents.IVA.engine.agi17.security.browser_permissions_gate import BrowserPermissionsGate, PermissionScope


class TestDualModeAuthController(unittest.TestCase):
    """Verifies interactive headed login followed by headless RAM-optimized execution."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="iva_browser_test_")
        self.profile_dir = Path(self.temp_dir) / "test_profile"
        self.gate = BrowserPermissionsGate.get_instance()
        self.gate.grant_permission(PermissionScope.BROWSER_CONTROL)
        self.controller = DualModeAuthController(
            profile_dir=self.profile_dir,
            cdp_port=9299,
            permissions_gate=self.gate,
        )

    def tearDown(self):
        self.controller.close_browser()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.Popen")
    @patch.object(DualModeAuthController, "_detect_chrome_executable", return_value=Path("/bin/fake_chrome"))
    def test_interactive_login_session_flow(self, mock_detect, mock_popen):
        """Verifies visible headed session is launched with persistent profile."""
        fake_proc = MagicMock()
        fake_proc.pid = 43210
        mock_popen.return_value = fake_proc

        state = self.controller.start_interactive_login_session(login_url="https://chatgpt.com/login")

        self.assertEqual(state.mode, BrowserExecutionMode.HEADED_LOGIN)
        self.assertEqual(state.active_pid, 43210)
        self.assertEqual(state.is_headless, False)
        self.assertEqual(state.estimated_ram_mb, 650.0)
        self.assertIn("Visible Browser Launched", state.message)

        # Verify command arguments passed to Chrome
        cmd = mock_popen.call_args[0][0]
        self.assertIn(f"--user-data-dir={self.profile_dir}", cmd)
        self.assertIn("--remote-debugging-port=9299", cmd)
        self.assertIn("https://chatgpt.com/login", cmd)
        self.assertNotIn("--headless=new", cmd)

    @patch("subprocess.Popen")
    @patch.object(DualModeAuthController, "_detect_chrome_executable", return_value=Path("/bin/fake_chrome"))
    def test_switch_to_headless_ram_optimization(self, mock_detect, mock_popen):
        """Verifies switching from headed login to headless mode preserves profile and saves RAM."""
        headed_proc = MagicMock()
        headed_proc.pid = 11111
        headless_proc = MagicMock()
        headless_proc.pid = 22222
        mock_popen.side_effect = [headed_proc, headless_proc]

        # 1. Start headed
        self.controller.start_interactive_login_session(login_url="https://gemini.google.com")
        self.assertEqual(self.controller.current_mode, BrowserExecutionMode.HEADED_LOGIN)

        # 2. Switch to headless
        state = self.controller.complete_login_and_switch_to_headless()

        self.assertEqual(state.mode, BrowserExecutionMode.HEADLESS_OPTIMIZED)
        self.assertEqual(state.active_pid, 22222)
        self.assertEqual(state.is_headless, True)
        self.assertEqual(state.estimated_ram_mb, 65.0)
        self.assertEqual(state.ram_savings_pct, 90.0)
        self.assertIn("RAM Optimized", state.message)

        # Headed process was terminated
        headed_proc.terminate.assert_called()

        # Headless command includes --headless=new and SAME profile dir
        headless_cmd = mock_popen.call_args[0][0]
        self.assertIn("--headless=new", headless_cmd)
        self.assertIn("--disable-gpu", headless_cmd)
        self.assertIn(f"--user-data-dir={self.profile_dir}", headless_cmd)

    def test_multi_account_manager_factory_integration(self):
        """Verifies MultiAccountBrowserManager exposes get_dual_mode_controller."""
        mgr = MultiAccountBrowserManager(storage_dir=Path(self.temp_dir))
        dm = mgr.get_dual_mode_controller(profile_dir=self.profile_dir)
        self.assertIsInstance(dm, DualModeAuthController)
        self.assertEqual(dm.cdp_port, mgr.cdp_port)

    @patch.object(DualModeAuthController, "cdp_list_tabs")
    def test_check_authentication_status_detection(self, mock_tabs):
        """Verifies tab inspection detects when user reaches authenticated dashboard."""
        # Scenario 1: Still on login page
        mock_tabs.return_value = [{"url": "https://chatgpt.com/auth/login", "title": "Log in", "type": "page"}]
        authed, reason = self.controller.check_authentication_status()
        self.assertFalse(authed)

        # Scenario 2: Successfully logged in and on chat session
        mock_tabs.return_value = [{"url": "https://chatgpt.com/c/67890-uuid", "title": "ChatGPT", "type": "page"}]
        authed, reason = self.controller.check_authentication_status()
        self.assertTrue(authed)
        self.assertIn("Authentication confirmed", reason)

    @patch.object(DualModeAuthController, "cdp_list_tabs")
    @patch.object(DualModeAuthController, "complete_login_and_switch_to_headless")
    def test_wait_for_auth_and_switch_auto_transition(self, mock_switch, mock_tabs):
        """Verifies automated polling transitions to headless as soon as auth succeeds."""
        mock_tabs.return_value = [{"url": "https://gemini.google.com/app", "title": "Gemini", "type": "page"}]
        expected_state = BrowserTransitionState(
            mode=BrowserExecutionMode.HEADLESS_OPTIMIZED,
            active_pid=99999,
            cdp_port=9299,
            persistent_profile_dir=str(self.profile_dir),
            target_url="https://gemini.google.com/app",
            is_headless=True,
            estimated_ram_mb=65.0,
            ram_savings_pct=90.0,
            message="Auto-transitioned",
        )
        mock_switch.return_value = expected_state

        state = self.controller.wait_for_auth_and_switch(timeout_sec=1.0, poll_interval_sec=0.1)
        self.assertEqual(state.mode, BrowserExecutionMode.HEADLESS_OPTIMIZED)
        self.assertEqual(state.active_pid, 99999)
        mock_switch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
