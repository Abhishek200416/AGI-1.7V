"""Launcher for IVA Sovereign Studio."""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    print("=" * 70)
    print("   🚀 LAUNCHING IVA SOVEREIGN STUDIO (NVIDIA NIM)")
    print("=" * 70)
    server_script = BASE_DIR / "server.py"

    proc = subprocess.Popen([sys.executable, str(server_script), "8095"])
    time.sleep(1.0)

    url = "http://localhost:8095"
    print(f"Opening browser at: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping Studio Server...")
        proc.terminate()

if __name__ == "__main__":
    main()
