"""IVA Autonomous Dedicated Browser Manager.
================================================================================
Manages a dedicated, persistent, isolated browser instance for IVA:
1. Complete Workspace Isolation:
   - Uses a dedicated user data profile (`~/.iva/browser_data/managed_profile`).
   - Operator's personal Chrome session, cookies, and history are NEVER touched.
2. Multi-Tab Platform Management:
   - Opens and coordinates tabs for YouTube Studio, Instagram, LinkedIn, X (Twitter),
     and local frontend demo previews.
   - Preserves authenticated sessions so the operator logs in once, and IVA
     maintains persistent access across future sessions without asking for passwords.
3. Chrome DevTools Protocol (CDP port 9229):
   - 100% Python standard library (urllib.request + json + socket + subprocess).
   - Inspects tabs, activates targets, opens new URLs, and monitors login states.
================================================================================
"""

from __future__ import annotations

import glob
import json
import logging
import os
import platform
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("IVADedicatedBrowser")


@dataclass
class PlatformTabInfo:
    platform_name: str
    target_url: str
    tab_id: Optional[str] = None
    current_title: str = ""
    current_url: str = ""
    is_logged_in: bool = False
    status_label: str = "AWAITING_LOGIN"


class IVADedicatedBrowserManager:
    """Controls IVA's dedicated test & automation browser instance."""

    DEFAULT_CDP_PORT = 9229

    PLATFORM_TARGETS: Dict[str, str] = {
        "youtube": "https://studio.youtube.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com/feed",
        "x": "https://x.com/home",
    }

    _instance: Optional["IVADedicatedBrowserManager"] = None

    def __init__(
        self,
        cdp_port: int = DEFAULT_CDP_PORT,
        profile_dir: Optional[Path] = None,
    ) -> None:
        self.cdp_port = cdp_port
        self.profile_dir = profile_dir or (Path.home() / ".iva" / "browser_data" / "managed_profile")
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.browser_process: Optional[subprocess.Popen] = None

    @classmethod
    def get_instance(cls, cdp_port: int = DEFAULT_CDP_PORT) -> "IVADedicatedBrowserManager":
        if cls._instance is None:
            cls._instance = cls(cdp_port=cdp_port)
        return cls._instance

    @staticmethod
    def resolve_browser_binary() -> str:
        """Finds Chromium or Chrome binary on the system (prioritizing Playwright Chromium)."""
        system = platform.system()
        candidates: List[str] = []

        if system == "Windows":
            # 1. Playwright managed Chromium builds (isolated developer browser)
            playwright_glob = str(Path.home() / "AppData" / "Local" / "ms-playwright" / "**" / "chrome.exe")
            matches = glob.glob(playwright_glob, recursive=True)
            if matches:
                # Pick latest build
                candidates.extend(sorted(matches, reverse=True))

            # 2. System Google Chrome
            candidates.extend([
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                str(Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"),
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ])
        elif system == "Darwin":
            candidates.extend([
                str(Path.home() / "Library" / "Caches" / "ms-playwright" / "**" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"),
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            ])
        else:
            candidates.extend([
                "google-chrome",
                "google-chrome-stable",
                "chromium",
                "chromium-browser",
            ])

        for c in candidates:
            if "*" in c:
                m = glob.glob(c, recursive=True)
                if m and os.path.exists(m[0]):
                    return m[0]
            elif os.path.exists(c):
                return c

        raise FileNotFoundError(
            "No compatible Chrome, Chromium, or Edge binary found. "
            "Please install Google Chrome or run `playwright install chromium`."
        )

    def is_cdp_available(self) -> bool:
        """Checks if the browser remote debugging port is answering."""
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json/version", timeout=1.0)
            return req.status == 200
        except Exception:
            return False

    def launch(
        self,
        urls: Optional[List[str]] = None,
        visible: bool = True,
        frontend_demo_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Launches IVA's dedicated managed browser window with pre-loaded platform tabs."""
        if self.is_cdp_available():
            logger.info("IVA Dedicated Browser already active on CDP port %d. Reusing session.", self.cdp_port)
            tabs = self.list_tabs()
            return {
                "status": "ALREADY_ACTIVE",
                "cdp_port": self.cdp_port,
                "profile_dir": str(self.profile_dir),
                "open_tabs": len(tabs),
                "tabs": tabs,
            }

        browser_exe = self.resolve_browser_binary()

        # Build initial multi-tab list
        initial_urls = list(urls) if urls else [
            self.PLATFORM_TARGETS["youtube"],
            self.PLATFORM_TARGETS["instagram"],
            self.PLATFORM_TARGETS["linkedin"],
            self.PLATFORM_TARGETS["x"],
        ]

        # Add frontend demo preview if present
        demo = frontend_demo_path or os.environ.get("IVA_FRONTEND_DEMO_PATH") or os.environ.get("IVA_CODEBASE_PATH")
        if demo:
            p_demo = Path(demo).resolve()
            index_html = p_demo / "index.html"
            if index_html.exists():
                initial_urls.append(index_html.as_uri())
            else:
                initial_urls.append("http://localhost:3000")

        urls_args = " ".join([f'"{u}"' for u in initial_urls])

        cmd = [
            browser_exe,
            f"--user-data-dir={self.profile_dir}",
            f"--remote-debugging-port={self.cdp_port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1400,920",
            "--window-position=50,30",
        ]
        if not visible:
            cmd.append("--headless=new")

        cmd.extend(initial_urls)

        logger.info("Launching IVA dedicated browser: %s (profile: %s)", browser_exe, self.profile_dir)
        try:
            self.browser_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

        # Wait up to 5 seconds for CDP port to open
        t0 = time.time()
        while time.time() - t0 < 6.0:
            if self.is_cdp_available():
                break
            time.sleep(0.3)

        tabs = self.list_tabs() if self.is_cdp_available() else []
        return {
            "status": "LAUNCHED" if self.is_cdp_available() else "STARTING",
            "pid": getattr(self.browser_process, "pid", None),
            "cdp_port": self.cdp_port,
            "profile_dir": str(self.profile_dir),
            "binary": browser_exe,
            "open_tabs": len(tabs),
            "tabs": tabs,
        }

    def list_tabs(self) -> List[Dict[str, Any]]:
        """Queries Chrome DevTools Protocol to list all open tabs and evaluate login status."""
        if not self.is_cdp_available():
            return []
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json/list", timeout=2.0)
            data = json.loads(req.read().decode("utf-8"))
            pages = [d for d in data if d.get("type") == "page"]

            results = []
            for page in pages:
                u = page.get("url", "")
                t = page.get("title", "")
                tab_id = page.get("id", "")
                platform_type = "web"

                # Classify platform and login state
                is_logged_in = False
                status_badge = "ACTIVE"

                if "youtube.com" in u or "accounts.google.com" in u:
                    platform_type = "YouTube Studio"
                    if "signin" in u or "accounts.google.com" in u:
                        status_badge = "AWAITING LOGIN 🔑"
                        is_logged_in = False
                    else:
                        status_badge = "LOGGED IN ✅"
                        is_logged_in = True
                elif "instagram.com" in u:
                    platform_type = "Instagram"
                    if "accounts/login" in u:
                        status_badge = "AWAITING LOGIN 🔑"
                        is_logged_in = False
                    elif "instagram.com" in u and "login" not in u:
                        status_badge = "LOGGED IN ✅"
                        is_logged_in = True
                elif "linkedin.com" in u:
                    platform_type = "LinkedIn"
                    if "login" in u or "checkpoint" in u:
                        status_badge = "AWAITING LOGIN 🔑"
                        is_logged_in = False
                    elif "feed" in u or "in/" in u or "company/" in u:
                        status_badge = "LOGGED IN ✅"
                        is_logged_in = True
                elif "x.com" in u or "twitter.com" in u:
                    platform_type = "X / Twitter"
                    if "login" in u or "i/flow" in u:
                        status_badge = "AWAITING LOGIN 🔑"
                        is_logged_in = False
                    elif "home" in u or "x.com" in u:
                        status_badge = "LOGGED IN ✅"
                        is_logged_in = True
                elif "localhost" in u or "127.0.0.1" in u or u.startswith("file:"):
                    platform_type = "Frontend Demo Preview"
                    status_badge = "ACTIVE PREVIEW 🚀"
                    is_logged_in = True

                results.append({
                    "id": tab_id,
                    "platform": platform_type,
                    "title": t,
                    "url": u,
                    "status_badge": status_badge,
                    "is_logged_in": is_logged_in,
                })
            return results
        except Exception as e:
            logger.debug("Failed listing CDP tabs: %s", e)
            return []

    def activate_tab(self, tab_id: str) -> bool:
        """Brings the specified tab ID into visual foreground focus."""
        if not self.is_cdp_available():
            return False
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json/activate/{tab_id}", timeout=2.0)
            return req.status == 200
        except Exception:
            return False

    def open_new_tab(self, url: str) -> Optional[Dict[str, Any]]:
        """Opens a new tab in IVA's dedicated browser."""
        if not self.is_cdp_available():
            return None
        try:
            encoded_url = urllib.parse.quote(url, safe="")
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json/new?{encoded_url}", timeout=2.0)
            return json.loads(req.read().decode("utf-8"))
        except Exception:
            return None

    def close_tab(self, tab_id: str) -> bool:
        """Closes a specific tab."""
        if not self.is_cdp_available():
            return False
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json/close/{tab_id}", timeout=2.0)
            return req.status == 200
        except Exception:
            return False

    def close_browser(self) -> bool:
        """Gracefully closes IVA's dedicated browser."""
        if self.browser_process:
            try:
                self.browser_process.terminate()
                self.browser_process = None
                return True
            except Exception:
                pass
        # Fallback process kill by remote port if process handle lost
        if platform.system() == "Windows":
            try:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "Get-Process chrome,msedge -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*managed_profile*' } | Stop-Process -Force"],
                    capture_output=True,
                    timeout=5,
                )
                return True
            except Exception:
                pass
        return False

    def format_tab_table(self) -> str:
        """Returns a formatted CLI summary table of open tabs and login states."""
        tabs = self.list_tabs()
        if not tabs:
            if not self.is_cdp_available():
                return "   ⚠️ IVA Dedicated Browser is currently offline. Type `browser open` to launch."
            return "   ℹ️ Browser is open, but no active pages detected."

        lines = [
            "   " + "═" * 74,
            "   🌐 IVA DEDICATED MANAGED BROWSER — ACTIVE TAB CONTROL HUB",
            "   " + "═" * 74,
            f"   • CDP Remote Debug Port: 127.0.0.1:{self.cdp_port} | Profile: {self.profile_dir.name}",
            "   " + "─" * 74,
        ]

        for idx, tab in enumerate(tabs, 1):
            plat = tab["platform"]
            badge = tab["status_badge"]
            u = tab["url"]
            u_short = u[:48] + "..." if len(u) > 48 else u
            lines.append(f"   [{idx}] {plat:22s} │ {badge:18s} │ {u_short}")

        lines.extend([
            "   " + "─" * 74,
            "   • Log in to any tab once — your cookies & sessions stay saved on your disk.",
            "   • IVA autonomously switches tabs, takes screenshots, and posts for you!",
            "   " + "═" * 74,
        ])
        return "\n".join(lines)
