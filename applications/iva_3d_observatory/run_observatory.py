"""Launcher script for IVA 3D Neural Observatory."""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    print("=" * 70)
    print("   🚀 LAUNCHING IVA 3D NEURAL OBSERVATORY")
    print("=" * 70)
    server_script = BASE_DIR / "server.py"

    # Start server as subprocess
    proc = subprocess.Popen([sys.executable, str(server_script), "8090"])
    time.sleep(1.0)

    url = "http://localhost:8090"
    print(f"Opening browser at: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping Observatory Server...")
        proc.terminate()

if __name__ == "__main__":
    main()
