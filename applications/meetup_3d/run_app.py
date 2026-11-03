#!/usr/bin/env python3
"""Meetup 3D Application — Production Launcher.
================================================================================
Launches the REST API server and opens the interactive 3D WebGL experience in browser.
Usage:
  python run_app.py
  (or py -3 run_app.py on Windows)
================================================================================
"""

from __future__ import annotations

import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from applications.meetup_3d.backend.server import start_server


def main() -> None:
    port = 8095
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    url = f"http://127.0.0.1:{port}/"
    print("\n" + "=" * 74)
    print("  🌐 NEXUSMEET 3D — SPATIAL ENGINEERING MEETUPS APPLICATION")
    print("=" * 74)
    print(f"  • REST API & WebGL Server : {url}")
    print(f"  • API Endpoints           : {url}api/meetups, {url}api/stats, {url}api/health")
    print(f"  • Frontend Three.js Scene : {url}")
    print("=" * 74)

    server = start_server(host="127.0.0.1", port=port)

    # Verify server health
    time.sleep(0.4)
    try:
        with urllib.request.urlopen(f"{url}api/health", timeout=3.0) as resp:
            if resp.status == 200:
                print("  ✅ Server Health Check: HTTP 200 OK (Threaded Server Active)")
    except Exception as exc:
        print(f"  ⚠️ Health check note: {exc}")

    print(f"\n  🚀 Launching interactive 3D WebGL viewport in your default browser...")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print("  Press Ctrl+C to terminate server.\n" + "=" * 74 + "\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Meetup 3D Server cleanly...")
        server.shutdown()
        server.server_close()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()
