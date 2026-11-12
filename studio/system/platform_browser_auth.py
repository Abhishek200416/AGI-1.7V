#!/usr/bin/env python3
"""
IVA Studios & Marketing — Unified External Browser Login & Session Verifier
Opens a persistent Chromium/Chrome session for ChatGPT, YouTube, Instagram,
LinkedIn, or Reddit. If login is required, opens visibly and asks the operator:
"Please log in to <PLATFORM> inside the browser window..." and polls until
authentication succeeds, then closes cleanly so automation can run off-screen.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

DEFAULT_USER_DATA_DIR = r"C:\Users\abhis\AppData\Local\ms-playwright-mcp\mcp-chrome-08d3779"

PLATFORM_AUTH_MAP = {
    "chatgpt": {
        "url": "https://chatgpt.com",
        "login_hint": 'button:has-text("Log in"), a:has-text("Log in"), button:has-text("Sign up")',
        "auth_ready": '#prompt-textarea, textarea#mobile-composer-prompt, button[data-testid="profile-button"]',
        "prompt_text": "Please log in to ChatGPT by clicking 'Log in' in the opened browser window.",
    },
    "youtube": {
        "url": "https://studio.youtube.com",
        "login_hint": 'a:has-text("Sign in"), input[type="email"]',
        "auth_ready": 'ytcp-entity-page, #create-icon, button[aria-label*="Create"]',
        "prompt_text": "Please sign in to YouTube Studio (or create/select your channel) in the opened browser window.",
    },
    "instagram": {
        "url": "https://www.instagram.com/",
        "login_hint": 'input[name="username"], button:has-text("Log in")',
        "auth_ready": 'svg[aria-label="Home"], svg[aria-label="New post"], a[href*="/direct/inbox/"]',
        "prompt_text": "Please log in to Instagram in the opened browser window.",
    },
    "linkedin": {
        "url": "https://www.linkedin.com/feed/",
        "login_hint": 'a:has-text("Sign in"), input#username',
        "auth_ready": 'button:has-text("Start a post"), a[href*="/messaging/"], nav.global-nav',
        "prompt_text": "Please log in to LinkedIn (or complete account setup) in the opened browser window.",
    },
    "reddit": {
        "url": "https://www.reddit.com/",
        "login_hint": 'a:has-text("Log In"), button:has-text("Log In")',
        "auth_ready": '#expand-user-drawer-button, a[href*="/submit"], button[aria-label*="Open inbox"]',
        "prompt_text": "Please log in to Reddit in the opened browser window.",
    },
}


def ensure_logged_in(
    platform: str,
    profile_dir: str = "Profile 3",
    user_data_dir: str = DEFAULT_USER_DATA_DIR,
    timeout_sec: int = 180,
    check_only: bool = False,
) -> dict:
    """
    Launch persistent Chrome to check/verify login state for a target platform.
    If not logged in (and check_only=False), keeps window open visibly on screen,
    asks operator cleanly, waits up to timeout_sec for authenticated DOM state,
    then closes browser and returns verified status.
    """
    plat = platform.strip().lower()
    cfg = PLATFORM_AUTH_MAP.get(plat)
    if not cfg:
        raise ValueError(f"Unsupported platform '{platform}'. Choose from {list(PLATFORM_AUTH_MAP.keys())}")

    pos = "-32000,-32000" if check_only else "80,60"
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            args=[f"--profile-directory={profile_dir}", f"--window-position={pos}", "--window-size=1280,920"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto(cfg["url"], timeout=60000)
            page.wait_for_timeout(3500)
            ready = page.locator(cfg["auth_ready"]).first
            needs_login = page.locator(cfg["login_hint"]).first
            is_auth = ready.is_visible() and not (plat == "chatgpt" and needs_login.is_visible())

            if is_auth:
                ctx.close()
                return {"platform": plat, "authenticated": True, "url": page.url}

            if check_only:
                ctx.close()
                return {"platform": plat, "authenticated": False, "url": page.url}

            print(f"\n[AUTH REQUIRED - {plat.upper()}] {cfg['prompt_text']}")
            print(f"[WAITING] Up to {timeout_sec}s for login verification (browser will auto-close once verified)...", flush=True)
            start = time.time()
            while time.time() - start < timeout_sec:
                page.wait_for_timeout(2500)
                if ready.is_visible() and not (plat == "chatgpt" and needs_login.is_visible()):
                    print(f"[VERIFIED] {plat.upper()} login confirmed! Closing login window cleanly.", flush=True)
                    ctx.close()
                    return {"platform": plat, "authenticated": True, "url": page.url}

            ctx.close()
            return {"platform": plat, "authenticated": False, "error": "Timed out waiting for operator login."}
        except Exception as exc:
            try:
                ctx.close()
            except Exception:
                pass
            return {"platform": plat, "authenticated": False, "error": str(exc)}


if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="External Browser Login & Session Verifier")
    parser.add_argument("platform", choices=list(PLATFORM_AUTH_MAP.keys()))
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    print(json.dumps(ensure_logged_in(args.platform, check_only=args.check_only, timeout_sec=args.timeout), indent=2))
