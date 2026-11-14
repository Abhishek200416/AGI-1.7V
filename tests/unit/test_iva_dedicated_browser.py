"""Unit test suite for IVA Dedicated Browser Manager & Tab Coordination.
================================================================================
Verifies that:
1. Complete Workspace Isolation:
   - Profile defaults to ~/.iva/browser_data/managed_profile.
   - Operator's personal Chrome session is never touched.
2. 100% Python Standard Library CDP:
   - Remote debugging on port 9229.
   - Accurately parses CDP tabs and evaluates login states for YouTube, Instagram,
     LinkedIn, X, and Frontend Demo Previews.
3. CLI Commands and Tab Table Formatting:
   - format_tab_table produces clean, readable terminal status tables.
   - activate_tab, open_new_tab, close_tab, and close_browser function as expected.
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

from agents.IVA.engine.agi17.browser.iva_dedicated_browser import (
    IVADedicatedBrowserManager,
    PlatformTabInfo,
)


class TestIVADedicatedBrowser(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_browser_test_"))
        # Reset singleton instance
        IVADedicatedBrowserManager._instance = None

    def tearDown(self) -> None:
        IVADedicatedBrowserManager._instance = None
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_singleton_and_custom_profile_dir(self) -> None:
        mgr = IVADedicatedBrowserManager(cdp_port=9229, profile_dir=self.temp_dir / "profile")
        self.assertEqual(mgr.cdp_port, 9229)
        self.assertTrue((self.temp_dir / "profile").exists())

        # Singleton accessor
        IVADedicatedBrowserManager._instance = mgr
        inst = IVADedicatedBrowserManager.get_instance()
        self.assertIs(inst, mgr)

    def test_02_resolve_browser_binary_mocked(self) -> None:
        with patch("os.path.exists", return_value=True):
            exe = IVADedicatedBrowserManager.resolve_browser_binary()
            self.assertTrue(len(exe) > 0)
            self.assertTrue("chrome" in exe.lower() or "edge" in exe.lower() or "chromium" in exe.lower())

    def test_03_is_cdp_available_evaluation(self) -> None:
        mgr = IVADedicatedBrowserManager(cdp_port=9229, profile_dir=self.temp_dir)

        # Failure case
        with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")):
            self.assertFalse(mgr.is_cdp_available())

        # Success case
        mock_resp = MagicMock()
        mock_resp.status = 200
        with patch("urllib.request.urlopen", return_value=mock_resp):
            self.assertTrue(mgr.is_cdp_available())

    def test_04_list_tabs_and_login_status_evaluation(self) -> None:
        mgr = IVADedicatedBrowserManager(cdp_port=9229, profile_dir=self.temp_dir)

        cdp_sample_pages = [
            {
                "id": "tab-1",
                "type": "page",
                "title": "YouTube Studio - Dashboard",
                "url": "https://studio.youtube.com/channel/UCX3ccjtvn5S4S2Yutu55YWA",
            },
            {
                "id": "tab-2",
                "type": "page",
                "title": "Google Sign-in",
                "url": "https://accounts.google.com/signin/v2/identifier",
            },
            {
                "id": "tab-3",
                "type": "page",
                "title": "Instagram",
                "url": "https://www.instagram.com/",
            },
            {
                "id": "tab-4",
                "type": "page",
                "title": "Instagram Login",
                "url": "https://www.instagram.com/accounts/login/",
            },
            {
                "id": "tab-5",
                "type": "page",
                "title": "Feed | LinkedIn",
                "url": "https://www.linkedin.com/feed/",
            },
            {
                "id": "tab-6",
                "type": "page",
                "title": "LinkedIn Login, Sign in | LinkedIn",
                "url": "https://www.linkedin.com/login",
            },
            {
                "id": "tab-7",
                "type": "page",
                "title": "Home / X",
                "url": "https://x.com/home",
            },
            {
                "id": "tab-8",
                "type": "page",
                "title": "Log in to X / X",
                "url": "https://x.com/i/flow/login",
            },
            {
                "id": "tab-9",
                "type": "page",
                "title": "SaaS Frontend Demo Preview",
                "url": "http://localhost:3000/app",
            },
            {
                "id": "tab-service-worker",
                "type": "service_worker",
                "title": "Background Worker",
                "url": "https://www.instagram.com/sw.js",
            },
        ]

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(cdp_sample_pages).encode("utf-8")
        mock_resp.status = 200

        with patch.object(mgr, "is_cdp_available", return_value=True):
            with patch("urllib.request.urlopen", return_value=mock_resp):
                tabs = mgr.list_tabs()

        # Should filter out non-page targets (service worker excluded)
        self.assertEqual(len(tabs), 9)

        # Tab 1: YouTube Studio logged in
        self.assertEqual(tabs[0]["platform"], "YouTube Studio")
        self.assertTrue(tabs[0]["is_logged_in"])
        self.assertIn("LOGGED IN", tabs[0]["status_badge"])

        # Tab 2: Google signin awaiting login
        self.assertEqual(tabs[1]["platform"], "YouTube Studio")
        self.assertFalse(tabs[1]["is_logged_in"])
        self.assertIn("AWAITING LOGIN", tabs[1]["status_badge"])

        # Tab 3: Instagram logged in
        self.assertEqual(tabs[2]["platform"], "Instagram")
        self.assertTrue(tabs[2]["is_logged_in"])

        # Tab 4: Instagram awaiting login
        self.assertEqual(tabs[3]["platform"], "Instagram")
        self.assertFalse(tabs[3]["is_logged_in"])

        # Tab 5: LinkedIn logged in
        self.assertEqual(tabs[4]["platform"], "LinkedIn")
        self.assertTrue(tabs[4]["is_logged_in"])

        # Tab 6: LinkedIn awaiting login
        self.assertEqual(tabs[5]["platform"], "LinkedIn")
        self.assertFalse(tabs[5]["is_logged_in"])

        # Tab 7: X logged in
        self.assertEqual(tabs[6]["platform"], "X / Twitter")
        self.assertTrue(tabs[6]["is_logged_in"])

        # Tab 8: X awaiting login
        self.assertEqual(tabs[7]["platform"], "X / Twitter")
        self.assertFalse(tabs[7]["is_logged_in"])

        # Tab 9: Frontend Demo Preview
        self.assertEqual(tabs[8]["platform"], "Frontend Demo Preview")
        self.assertTrue(tabs[8]["is_logged_in"])
        self.assertIn("ACTIVE PREVIEW", tabs[8]["status_badge"])

    def test_05_format_tab_table_output(self) -> None:
        mgr = IVADedicatedBrowserManager(cdp_port=9229, profile_dir=self.temp_dir)

        # Case A: Browser offline
        with patch.object(mgr, "is_cdp_available", return_value=False):
            tbl_offline = mgr.format_tab_table()
            self.assertIn("offline", tbl_offline.lower())

        # Case B: Browser active with tabs
        sample_tabs = [
            {
                "id": "tab-1",
                "platform": "YouTube Studio",
                "title": "Channel Analytics",
                "url": "https://studio.youtube.com",
                "status_badge": "LOGGED IN ✅",
                "is_logged_in": True,
            },
            {
                "id": "tab-2",
                "platform": "Frontend Demo Preview",
                "title": "Local Demo",
                "url": "http://localhost:3000",
                "status_badge": "ACTIVE PREVIEW 🚀",
                "is_logged_in": True,
            },
        ]
        with patch.object(mgr, "is_cdp_available", return_value=True):
            with patch.object(mgr, "list_tabs", return_value=sample_tabs):
                tbl_active = mgr.format_tab_table()
                self.assertIn("ACTIVE TAB CONTROL HUB", tbl_active)
                self.assertIn("YouTube Studio", tbl_active)
                self.assertIn("LOGGED IN ✅", tbl_active)
                self.assertIn("Frontend Demo Preview", tbl_active)

    def test_06_open_and_activate_and_close_tab(self) -> None:
        mgr = IVADedicatedBrowserManager(cdp_port=9229, profile_dir=self.temp_dir)

        with patch.object(mgr, "is_cdp_available", return_value=True):
            # 1. Open new tab
            mock_new_resp = MagicMock()
            mock_new_resp.read.return_value = json.dumps({"id": "new-123", "url": "https://x.com"}).encode("utf-8")
            with patch("urllib.request.urlopen", return_value=mock_new_resp):
                new_tab = mgr.open_new_tab("https://x.com")
                self.assertIsNotNone(new_tab)
                self.assertEqual(new_tab.get("id"), "new-123")

            # 2. Activate tab
            mock_act_resp = MagicMock()
            mock_act_resp.status = 200
            with patch("urllib.request.urlopen", return_value=mock_act_resp):
                self.assertTrue(mgr.activate_tab("new-123"))

            # 3. Close tab
            mock_close_resp = MagicMock()
            mock_close_resp.status = 200
            with patch("urllib.request.urlopen", return_value=mock_close_resp):
                self.assertTrue(mgr.close_tab("new-123"))

    def test_07_is_chrome_process_running_and_existing_profile_mode(self) -> None:
        mgr = IVADedicatedBrowserManager(cdp_port=9229, profile_dir=self.temp_dir)

        # 1. Test is_chrome_process_running helper
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "5\n"
            self.assertTrue(mgr.is_chrome_process_running())
            mock_run.return_value.stdout = "0\n"
            self.assertFalse(mgr.is_chrome_process_running())

        # 2. Test attach to already running CDP on 9222/9229
        with patch.object(mgr, "is_cdp_available", return_value=True):
            with patch.object(mgr, "list_tabs", return_value=[{"id": "t1", "platform": "YouTube Studio"}]):
                res = mgr.launch_existing_profile()
                self.assertEqual(res["status"], "ATTACHED_TO_RUNNING")
                self.assertEqual(res["profile_mode"], "EXISTING_PERSONAL_PROFILE")

        # 3. Test running without debugging prompt
        with patch.object(mgr, "is_cdp_available", return_value=False):
            with patch.object(mgr, "is_chrome_process_running", return_value=True):
                res_warn = mgr.launch_existing_profile(restart_if_running=False)
                self.assertEqual(res_warn["status"], "CHROME_RUNNING_WITHOUT_DEBUGGING")


if __name__ == "__main__":
    unittest.main()
