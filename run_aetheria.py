#!/usr/bin/env python3
"""Run script for AETHERIA 3D • Living Neural Cosmos.

Starts the server on port 8095 (or first available port) and optionally opens browser.
"""

from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Windows UTF-8 stdout fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from applications.aetheria_3d.server import run_server, DEFAULT_PORT
except ImportError:
    from server import run_server, DEFAULT_PORT

def main() -> None:
    port = DEFAULT_PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    # Open browser automatically after half a second
    import threading
    def _open_browser() -> None:
        import time
        time.sleep(0.8)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    threading.Thread(target=_open_browser, daemon=True).start()
    run_server(port=port)


if __name__ == "__main__":
    main()
