"""Unit tests for BrowserPermissionsGate and MultiAccountBrowserManager.
================================================================================
Verifies:
1. BrowserPermissionsGate enforces fail-closed security for browser & system actions.
2. MultiAccountBrowserManager discovers local Chrome profiles (6-78 accounts).
3. 24/7 rate-limit detection, cooldown calculation, and autonomous account rotation.
================================================================================
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.IVA.engine.agi17.browser.multi_account_browser_manager import (
    ChromeProfileInfo,
    MultiAccountBrowserManager,
)
from agents.IVA.engine.agi17.security.browser_permissions_gate import (
    BrowserPermissionsGate,
    PermissionScope,
)


class TestMultiAccountAndPermissions(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_perm_test_"))
        self._orig_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._orig_env)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_permissions_gate_enforcement(self) -> None:
        gate = BrowserPermissionsGate(storage_dir=self.temp_dir)
        gate.revoke_permission(PermissionScope.BROWSER_CONTROL)

        # Denied when non-interactive and no env override
        self.assertFalse(gate.check_permission(PermissionScope.BROWSER_CONTROL, reason="test", interactive=False))

        # Grant session permission
        gate.grant_permission(PermissionScope.BROWSER_CONTROL, reason="Operator authorized")
        self.assertTrue(gate.check_permission(PermissionScope.BROWSER_CONTROL, reason="test", interactive=False))

        # Revoke permission
        gate.revoke_permission(PermissionScope.BROWSER_CONTROL)
        self.assertFalse(gate.check_permission(PermissionScope.BROWSER_CONTROL, reason="test", interactive=False))

        # Global env override
        os.environ["IVA_PERMIT_BROWSER_CONTROL"] = "true"
        self.assertTrue(gate.check_permission(PermissionScope.BROWSER_CONTROL, reason="test", interactive=False))

    def test_02_multi_account_discovery_and_rotation(self) -> None:
        mgr = MultiAccountBrowserManager(user_data_dir=self.temp_dir / "ChromeData", storage_dir=self.temp_dir)
        profiles = mgr.list_profiles()
        self.assertGreaterEqual(len(profiles), 1)

        # Available profile selection
        first = mgr.get_next_available_profile()
        self.assertIsNotNone(first)

        # Rate limit simulation on first account (1 hour cooldown)
        success, rot_msg = mgr.mark_profile_rate_limited(first.profile_id, cooldown_sec=3600.0, reason="Daily quota exceeded")
        self.assertTrue(success)
        self.assertIn("rotating to", rot_msg)

        # First profile is now in cooldown
        self.assertFalse(first.is_available())
        self.assertGreater(first.remaining_cooldown_sec(), 0.0)

        # Next profile selected is different and available
        second = mgr.get_next_available_profile()
        self.assertNotEqual(second.profile_id, first.profile_id)
        self.assertTrue(second.is_available())

    def test_03_gemini_rate_limit_parsing(self) -> None:
        mgr = MultiAccountBrowserManager(user_data_dir=self.temp_dir / "ChromeData", storage_dir=self.temp_dir)

        # Detect 4 hour wait
        msg_4h = "You have reached your limit for video generation. Try again in 4 hours."
        wait_4h = mgr.parse_gemini_response_for_limits(msg_4h)
        self.assertEqual(wait_4h, 14400.0)

        # Detect 30 minute wait
        msg_30m = "Rate limit reached. Please check back in 30 minutes."
        wait_30m = mgr.parse_gemini_response_for_limits(msg_30m)
        self.assertEqual(wait_30m, 1800.0)

        # Normal response returns None
        normal_msg = "Here is your generated 1080p video asset."
        self.assertIsNone(mgr.parse_gemini_response_for_limits(normal_msg))


if __name__ == "__main__":
    unittest.main()
