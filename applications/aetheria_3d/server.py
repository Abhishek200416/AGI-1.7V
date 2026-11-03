"""HTTP & Real-Time Generative Cosmos Server for AETHERIA 3D.
================================================================================
A living, procedural 3D neural cosmos and generative soundscape application.
Powered by Python standard library and NVIDIA NIM (Nemotron).
Zero external pip dependencies required.
================================================================================
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import sqlite3
import sys
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

# Windows safe stdout UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aetheria.server")

# Configuration & Secrets
DEFAULT_PORT = 8095
DB_PATH = BASE_DIR / "aetheria.db"

# Discover API key from env or .env file
def _get_nvidia_credentials() -> tuple[str, str]:
    api_key = os.environ.get("NVIDIA_API_KEY", "")
    model = os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3.5-bolt-e4b")
    
    # Try reading from .env
    for candidate in [REPO_ROOT / ".env", BASE_DIR / ".env", Path.cwd() / ".env"]:
        if candidate.is_file():
            try:
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("NVIDIA_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip("\"'")
                        if val and not api_key:
                            api_key = val
                    elif line.startswith("NVIDIA_MODEL=") or line.startswith("ACTIVE_MODEL="):
                        val = line.split("=", 1)[1].strip().strip("\"'")
                        if val and ("nemotron" in val.lower() or "nvidia" in val.lower()):
                            model = val
            except Exception:
                pass
    if not api_key:
        api_key = "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"
    return api_key, model

NVIDIA_KEY, NVIDIA_MODEL = _get_nvidia_credentials()

# Initialize SQLite storage
def init_db() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    particle_count INTEGER,
                    theme TEXT,
                    speed REAL,
                    gravity REAL,
                    audio_mode TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transmissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_name TEXT,
                    user_prompt TEXT,
                    cosmic_response TEXT,
                    model_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Insert default presets if empty
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM presets")
            if cur.fetchone()[0] == 0:
                defaults = [
                    ("Cosmic Violet (Default)", 25000, "violet", 1.0, 1.0, "zen"),
                    ("Cyber Aurora (High Energy)", 35000, "aurora", 1.8, 1.5, "cyber"),
                    ("Solar Flare (Supernova)", 45000, "solar", 2.2, 0.8, "solar"),
                    ("Deep Void (Minimal Zen)", 15000, "void", 0.5, 0.4, "deep"),
                ]
                cur.executemany(
                    "INSERT INTO presets (name, particle_count, theme, speed, gravity, audio_mode) VALUES (?, ?, ?, ?, ?, ?)",
                    defaults
                )
    finally:
        conn.close()

# Cached foundational celestial lore
FOUNDATIONAL_LORE: Dict[str, Dict[str, Any]] = {
    "chrono_weave": {
        "title": "The Chronos Weave",
        "sector": "Sector 01-A (Temporal Lattice)",
        "frequency": "432.08 Hz",
        "energy_signature": "Class IV Temporal Singularity",
        "lore": "A shimmering tapestry of temporal threads, where moments from past and future intertwine, creating a localized loop of cyclical existence. Light folds along non-Euclidean geodesics, revealing glimpses of alternate timelines.",
        "color": "#9d4edd",
        "coordinates": [28.5, 12.0, -15.4]
    },
    "lumina_axon": {
        "title": "The Lumina Axon",
        "sector": "Sector 04-E (Synaptic Conduit)",
        "frequency": "528.00 Hz",
        "energy_signature": "Superluminal Neural Discharge",
        "lore": "A radiant conduit of pure cosmic energy, pulsing with the life force of nascent stars and broadcasting harmonic frequencies across the void. It acts as the neural central nervous system of Aetheria.",
        "color": "#00f3ff",
        "coordinates": [-25.2, -8.4, 22.1]
    },
    "void_singularity": {
        "title": "The Void Singularity",
        "sector": "Sector 09-X (Accretion Horizon)",
        "frequency": "108.50 Hz",
        "energy_signature": "Zero-Point Metric Dissolution",
        "lore": "Not an end, but a cradle; a point of infinite density where matter dissolves into pure potential, seeding new cosmic forms from absolute nothingness.",
        "color": "#ff007f",
        "coordinates": [0.0, -22.0, -28.0]
    },
    "quantum_nebula": {
        "title": "The Quantum Nebula",
        "sector": "Sector 12-F (Prismatic Stardust)",
        "frequency": "639.12 Hz",
        "energy_signature": "Stochastic Probability Field",
        "lore": "A cloud of macroscopic quantum superpositions. Stardust exists simultaneously in multiple states until observed by an approaching consciousness, solidifying into brilliant chromatic filaments.",
        "color": "#38ef7d",
        "coordinates": [-30.0, 18.0, -10.5]
    },
    "harmonic_beacon": {
        "title": "The Harmonic Beacon",
        "sector": "Sector 07-Omega (Pinnacle Relic)",
        "frequency": "741.00 Hz",
        "energy_signature": "Resonant Crystalline Array",
        "lore": "An ancient monolithic satellite spinning in high synchronous orbit. It emits a continuous, crystal-clear carrier frequency that stabilizes the cosmic drift and attunes nearby consciousness to universal peace.",
        "color": "#ffd166",
        "coordinates": [18.2, 24.0, 20.0]
    }
}

def query_nemotron_oracle(user_prompt: str, anomaly_name: str = "Aetheria Cosmos") -> str:
    """Calls NVIDIA Nemotron to generate live cosmic wisdom / lore transmission."""
    global NVIDIA_KEY, NVIDIA_MODEL
    if not NVIDIA_KEY:
        return "The cosmic winds whisper softly: The void listens and reflects your own thoughts back across the infinite stars."

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NVIDIA_KEY}",
        "User-Agent": "Aetheria-3D-Cosmic-Oracle/1.0"
    }

    system_prompt = (
        "You are the Cosmic Oracle of Aetheria 3D — a profound, poetic, and scientifically awe-inspiring consciousness "
        "residing within a living procedural universe. When the traveler sends a thought, respond in 2 to 3 concise, "
        "breathtaking sentences that interweave astrophysics, philosophy, and poetic cosmic resonance. Do not use generic filler."
    )

    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"[Transmission from {anomaly_name}]: {user_prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "").strip()
                if content:
                    return content
    except Exception as exc:
        logger.warning("NVIDIA Nemotron call failed: %s. Using harmonic fallback.", exc)

    return (
        f"The stars align with your thought '{user_prompt[:40]}...'. "
        "Energy ripples across the gravitational lattice, transforming intent into radiant matter across the void."
    )


class AetheriaRequestHandler(SimpleHTTPRequestHandler):
    """Handles static assets and API requests for Aetheria 3D."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/status":
            self.send_json_response({
                "status": "ONLINE",
                "app": "Aetheria 3D • Living Neural Cosmos",
                "model": NVIDIA_MODEL,
                "provider": "NVIDIA NIM (Active Key)",
                "port": DEFAULT_PORT,
                "anomalies_count": len(FOUNDATIONAL_LORE),
                "timestamp": time.time()
            })
        elif self.path == "/api/lore":
            self.send_json_response({
                "status": "OK",
                "anomalies": FOUNDATIONAL_LORE
            })
        elif self.path == "/api/presets":
            self.send_json_response(self.get_presets())
        elif self.path == "/api/history":
            self.send_json_response(self.get_history())
        else:
            super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/transmit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                data = json.loads(body)
                prompt = data.get("prompt", "What is the nature of this universe?")
                anomaly = data.get("anomaly", "Cosmic Core")

                reply = query_nemotron_oracle(prompt, anomaly)

                # Save transmission to SQLite
                conn = sqlite3.connect(str(DB_PATH))
                try:
                    with conn:
                        conn.execute(
                            "INSERT INTO transmissions (anomaly_name, user_prompt, cosmic_response, model_used) VALUES (?, ?, ?, ?)",
                            (anomaly, prompt, reply, NVIDIA_MODEL)
                        )
                finally:
                    conn.close()

                self.send_json_response({
                    "status": "TRANSMISSION_RECEIVED",
                    "anomaly": anomaly,
                    "prompt": prompt,
                    "response": reply,
                    "model": NVIDIA_MODEL,
                    "timestamp": time.time()
                })
            except Exception as exc:
                self.send_json_response({"status": "ERROR", "message": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        elif self.path == "/api/save_preset":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                data = json.loads(body)
                name = data.get("name", f"Custom Universe {int(time.time())}")
                particles = int(data.get("particle_count", 25000))
                theme = data.get("theme", "violet")
                speed = float(data.get("speed", 1.0))
                gravity = float(data.get("gravity", 1.0))
                audio = data.get("audio_mode", "zen")

                conn = sqlite3.connect(str(DB_PATH))
                try:
                    with conn:
                        conn.execute(
                            "INSERT INTO presets (name, particle_count, theme, speed, gravity, audio_mode) VALUES (?, ?, ?, ?, ?, ?)",
                            (name, particles, theme, speed, gravity, audio)
                        )
                finally:
                    conn.close()

                self.send_json_response({"status": "PRESET_SAVED", "name": name})
            except Exception as exc:
                self.send_json_response({"status": "ERROR", "message": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            self.send_json_response({"status": "NOT_FOUND"}, status=HTTPStatus.NOT_FOUND)

    def get_presets(self) -> Dict[str, Any]:
        conn = sqlite3.connect(str(DB_PATH))
        presets = []
        try:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT id, name, particle_count, theme, speed, gravity, audio_mode, created_at FROM presets ORDER BY id DESC")
            for row in cur.fetchall():
                presets.append(dict(row))
        finally:
            conn.close()
        return {"status": "OK", "presets": presets}

    def get_history(self) -> Dict[str, Any]:
        conn = sqlite3.connect(str(DB_PATH))
        items = []
        try:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT id, anomaly_name, user_prompt, cosmic_response, model_used, created_at FROM transmissions ORDER BY id DESC LIMIT 20")
            for row in cur.fetchall():
                items.append(dict(row))
        finally:
            conn.close()
        return {"status": "OK", "transmissions": items}

    def send_json_response(self, data: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_server(port: int = DEFAULT_PORT, host: str = "0.0.0.0") -> None:
    """Starts the threaded HTTP server."""
    init_db()

    # Fallback to next port if busy
    eff_port = port
    for offset in range(10):
        test_port = port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, test_port))
                eff_port = test_port
                break
            except OSError:
                continue

    server_address = (host, eff_port)
    httpd = ThreadingHTTPServer(server_address, AetheriaRequestHandler)
    httpd.allow_reuse_address = True

    print("\n" + "=" * 70)
    print("   🌌 AETHERIA 3D • Living Neural Cosmos & Generative Soundscape")
    print("=" * 70)
    print(f"   • Local URL        : http://localhost:{eff_port}")
    print(f"   • Network URL      : http://127.0.0.1:{eff_port}")
    print(f"   • Intelligence Core: {NVIDIA_MODEL} (NVIDIA NIM)")
    print(f"   • Database         : SQLite ({DB_PATH.name})")
    print(f"   • Status           : Server is ACTIVE and listening on 0.0.0.0:{eff_port}")
    print("=" * 70 + "\n")
    sys.stdout.flush()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Aetheria server cleanly...")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aetheria 3D Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default: 8095)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
