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


# 7-Scale Universal Hierarchy (Planet -> Solar System -> Stellar Neighborhood -> Milky Way -> Superclusters -> Cosmic Web -> Multiverse Hypercube Matrix)
COSMIC_SCALES: Dict[str, Dict[str, Any]] = {
    "planetary": {
        "id": "planetary",
        "name": "Terrestrial Planetary Scale",
        "order": 1,
        "metrics": "10^7 m (7,000 km)",
        "camera_dist": 6.5,
        "fov": 48,
        "chronicle": "A living sapphire jewel, cradled in stellar grace, where liquid oceans and delicate atmospheres cradle consciousness.",
        "badge": "🌍 Terrestrial",
        "particle_density": 6000
    },
    "solar_system": {
        "id": "solar_system",
        "name": "Heliosphere Solar System",
        "order": 2,
        "metrics": "10^13 m (100 AU)",
        "camera_dist": 130,
        "fov": 58,
        "chronicle": "A radiant stellar furnace carrying eight worlds and rocky belts in harmonious Keplerian choreography.",
        "badge": "☀️ Heliosphere",
        "particle_density": 18000
    },
    "stellar_neighborhood": {
        "id": "stellar_neighborhood",
        "name": "Stellar Neighborhood & Multi-Star Systems",
        "order": 3,
        "metrics": "10^17 m (10 Light Years)",
        "camera_dist": 650,
        "fov": 62,
        "chronicle": "Our Sun travels through the Orion Spur beside Alpha Centauri, radiant Sirius, pulsating Betelgeuse, and the Pleiades.",
        "badge": "✨ Star Cluster",
        "particle_density": 28000
    },
    "milky_way": {
        "id": "milky_way",
        "name": "Milky Way Galactic Spiral & Sagittarius A*",
        "order": 4,
        "metrics": "10^21 m (100,000 Light Years)",
        "camera_dist": 3500,
        "fov": 65,
        "chronicle": "A grand design spiral arm of starlight swirling around Sagittarius A*, where billions of suns keep their ancient vigil.",
        "badge": "🌌 Galactic",
        "particle_density": 45000
    },
    "supercluster": {
        "id": "supercluster",
        "name": "Laniakea Mega-Cluster & Great Attractor",
        "order": 5,
        "metrics": "10^24 m (520 Million Light Years)",
        "camera_dist": 18000,
        "fov": 70,
        "chronicle": "Thousands of galaxies flowing along gravitational rivers of starlight toward the mysterious Great Attractor.",
        "badge": "🌀 Supercluster",
        "particle_density": 55000
    },
    "cosmic_web": {
        "id": "cosmic_web",
        "name": "Observable Cosmic Web & Boötes Voids",
        "order": 6,
        "metrics": "10^26 m (93 Billion Light Years)",
        "camera_dist": 65000,
        "fov": 75,
        "chronicle": "A cosmic sponge of dark matter filaments linking superclusters across light-years of silence.",
        "badge": "🕸️ Cosmic Web",
        "particle_density": 65000
    },
    "multiverse_matrix": {
        "id": "multiverse_matrix",
        "name": "Bubble Multiverse & Cosmic Voids",
        "order": 7,
        "metrics": "10^29 m (Macro-Cosmic Bulk)",
        "camera_dist": 220000,
        "fov": 78,
        "chronicle": "Vast hyperspherical bubble universes nucleating within the quantum inflationary void, each with distinct physical constants and cosmic structures.",
        "badge": "🫧 Bubble Multiverse",
        "particle_density": 85000
    }
}

# Solar System Astronomical Bodies
SOLAR_SYSTEM_PLANETS: List[Dict[str, Any]] = [
    {"name": "Sun", "type": "star", "radius": 5.5, "color": "#ffa200", "orbit_radius": 0, "orbit_speed": 0, "lore": "The life-giving fusion furnace at the center of the heliosphere."},
    {"name": "Mercury", "type": "planet", "radius": 0.55, "color": "#a8a8a8", "orbit_radius": 12, "orbit_speed": 0.038, "lore": "Sun-scorched iron world in rapid tidal resonance."},
    {"name": "Venus", "type": "planet", "radius": 1.1, "color": "#e8c37d", "orbit_radius": 18, "orbit_speed": 0.028, "lore": "Shrouded in dense carbon dioxide with runaway greenhouse fury."},
    {"name": "Earth", "type": "planet", "radius": 1.25, "color": "#2878d6", "orbit_radius": 26, "orbit_speed": 0.022, "has_moon": True, "moon_radius": 0.35, "moon_dist": 2.8, "lore": "The living oasis of liquid water, nitrogen atmosphere, and conscious life."},
    {"name": "Mars", "type": "planet", "radius": 0.75, "color": "#d64527", "orbit_radius": 34, "orbit_speed": 0.018, "lore": "Rust-red dunes, ancient dry river valleys, and dormant volcanic giants."},
    {"name": "Jupiter", "type": "planet", "radius": 3.4, "color": "#c98f4b", "orbit_radius": 52, "orbit_speed": 0.010, "has_bands": True, "lore": "The gas colossus whose gravity shields the inner worlds from cometary impacts."},
    {"name": "Saturn", "type": "planet", "radius": 2.8, "color": "#e8cb8d", "orbit_radius": 74, "orbit_speed": 0.007, "has_rings": True, "ring_inner": 3.6, "ring_outer": 6.8, "lore": "Crowned by shimmering rings of crystalline water ice and silicates."},
    {"name": "Uranus", "type": "planet", "radius": 1.9, "color": "#5297d4", "orbit_radius": 96, "orbit_speed": 0.005, "lore": "Tilted on its side, an icy world bathed in methane turquoise."},
    {"name": "Neptune", "type": "planet", "radius": 1.85, "color": "#284db0", "orbit_radius": 118, "orbit_speed": 0.004, "lore": "Deep azure ice giant swept by supersonic storm winds."}
]


# Comprehensive Multiverse Stellar & Galactic Systems Catalog
STELLAR_SYSTEMS: List[Dict[str, Any]] = [
    {
        "id": "cygnus_blue_hypergiant",
        "name": "Cygnus Leviathan (Blue Hypergiant)",
        "type": "blue_hypergiant",
        "sector": "Orion-Cygnus Molecular Arm",
        "distance": "10x Solar Radius • 40,000 K",
        "lore": "A colossal blue hypergiant star ten times larger than our solar system, blazing with incandescent cyan thermonuclear fire and carrying multiple solar systems in massive elliptical orbits.",
        "color": "#00f3ff",
        "frequency": "741.00 Hz"
    },
    {
        "id": "alcyone",
        "name": "Alcyone Major (Cluster Primary)",
        "type": "cluster_star",
        "sector": "Local Cluster Barycenter",
        "distance": "0 LY (Center)",
        "lore": "The supermassive golden anchor star around which our Sun and neighboring solar systems complete their grand orbital dance.",
        "color": "#ffd166",
        "frequency": "432.08 Hz"
    },
    {
        "id": "sol",
        "name": "Helios Prime (Our Sun)",
        "type": "star_system",
        "sector": "Orion Spur • Sector 00",
        "distance": "350 AU from Primary",
        "lore": "The radiant yellow dwarf carrying Earth, Mars, Jupiter, and 5 other worlds in harmonic Keplerian flight.",
        "color": "#ffa200",
        "frequency": "528.00 Hz"
    },
    {
        "id": "alpha_centauri",
        "name": "Alpha Centauri & Proxima b",
        "type": "star_system",
        "sector": "Orion Spur • Sector 01",
        "distance": "4.37 Light Years",
        "lore": "A trinary stellar system hosting the red dwarf Proxima Centauri and its potentially habitable terrestrial world Proxima b.",
        "color": "#ffbe0b",
        "frequency": "639.12 Hz"
    },
    {
        "id": "kepler_452",
        "name": "Kepler-452 ('Earth's Cousin')",
        "type": "star_system",
        "sector": "Cygnus Arm • Sector 12",
        "distance": "1,400 Light Years",
        "lore": "A G2-type solar twin orbited by a super-Earth in its circumstellar habitable zone.",
        "color": "#00f3ff",
        "frequency": "741.00 Hz"
    },
    {
        "id": "trappist_1",
        "name": "TRAPPIST-1 Seven Worlds",
        "type": "star_system",
        "sector": "Aquarius Arm • Sector 08",
        "distance": "39.6 Light Years",
        "lore": "An ultra-cool red dwarf encircled by seven Earth-sized terrestrial planets in tight resonant orbits.",
        "color": "#ff007f",
        "frequency": "417.00 Hz"
    },
    {
        "id": "sirius",
        "name": "Sirius A & White Dwarf Sirius B",
        "type": "star_system",
        "sector": "Canis Major • Sector 03",
        "distance": "8.6 Light Years",
        "lore": "The brightest diamond-white star in Earth's skies, orbited by the dense exotic white dwarf Sirius B.",
        "color": "#e0f2fe",
        "frequency": "852.00 Hz"
    },
    {
        "id": "vega",
        "name": "Vega & Circumstellar Debris Disc",
        "type": "star_system",
        "sector": "Lyra Constellation • Sector 05",
        "distance": "25.0 Light Years",
        "lore": "A rapidly spinning sapphire-white star flattened at its poles, wrapped in a radiant ring of nascent planetesimals.",
        "color": "#38bdf8",
        "frequency": "963.00 Hz"
    },
    {
        "id": "betelgeuse",
        "name": "Betelgeuse (Crimson Supergiant)",
        "type": "supergiant",
        "sector": "Orion Molecular Cloud",
        "distance": "642.5 Light Years",
        "lore": "A colossal pulsating red supergiant over 700 times larger than the Sun, destined for a supernova burst.",
        "color": "#ef4444",
        "frequency": "174.00 Hz"
    },
    {
        "id": "sagittarius_a",
        "name": "Sagittarius A* (Galactic Core)",
        "type": "supermassive_black_hole",
        "sector": "Milky Way Nucleus",
        "distance": "26,000 Light Years",
        "lore": "The 4-million solar mass supermassive black hole around which the entire Milky Way galaxy and 400 billion stars revolve.",
        "color": "#9d4edd",
        "frequency": "108.50 Hz"
    },
    {
        "id": "andromeda",
        "name": "Andromeda Galaxy Core (M31)",
        "type": "galaxy",
        "sector": "Local Group Barycenter",
        "distance": "2.537 Million Light Years",
        "lore": "A majestic spiral galaxy containing 1 trillion stars, approaching the Milky Way in a cosmic gravitational rendezvous.",
        "color": "#00d4ff",
        "frequency": "285.00 Hz"
    },
    {
        "id": "great_attractor",
        "name": "The Great Attractor",
        "type": "cosmic_nexus",
        "sector": "Laniakea Zone of Avoidance",
        "distance": "250 Million Light Years",
        "lore": "A colossal gravitational anomaly drawing millions of galaxies and superclusters along luminous velocity streamlines.",
        "color": "#ff0055",
        "frequency": "396.00 Hz"
    },
    {
        "id": "multiverse_prime",
        "name": "Universe Prime 4D Cosmic Hypercube",
        "type": "multiverse_tesseract",
        "sector": "Omniverse 125-Cell Dimensional Matrix",
        "distance": "Macro-Dimensional Bulk",
        "lore": "The 4-dimensional tesseract housing our observable cosmos, nestled within an infinite lattice of parallel bubble universes.",
        "color": "#38ef7d",
        "frequency": "963.00 Hz"
    }
]


class AetheriaRequestHandler(SimpleHTTPRequestHandler):
    """Handles static assets and API requests for Aetheria 3D."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        elif self.path == "/api/status":
            self.send_json_response({
                "status": "ONLINE",
                "app": "Aetheria 3D • Living Neural Cosmos",
                "model": NVIDIA_MODEL,
                "provider": "NVIDIA NIM (Active Key)",
                "port": DEFAULT_PORT,
                "anomalies_count": len(FOUNDATIONAL_LORE),
                "systems_count": len(STELLAR_SYSTEMS),
                "timestamp": time.time()
            })
        elif self.path == "/api/lore":
            self.send_json_response({
                "status": "OK",
                "anomalies": FOUNDATIONAL_LORE
            })
        elif self.path == "/api/scales":
            self.send_json_response({
                "status": "OK",
                "scales": COSMIC_SCALES
            })
        elif self.path == "/api/planets":
            self.send_json_response({
                "status": "OK",
                "planets": SOLAR_SYSTEM_PLANETS
            })
        elif self.path == "/api/systems":
            self.send_json_response({
                "status": "OK",
                "systems": STELLAR_SYSTEMS
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


class DualStackThreadingServer(ThreadingHTTPServer):
    """Threading HTTP server supporting dual-stack IPv4 and IPv6."""
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        try:
            self.address_family = socket.AF_INET6
            super().__init__(server_address, RequestHandlerClass, bind_and_activate=False)
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (AttributeError, OSError):
                pass
            if bind_and_activate:
                self.server_bind()
                self.server_activate()
        except Exception:
            self.address_family = socket.AF_INET
            super().__init__(("0.0.0.0", server_address[1]), RequestHandlerClass, bind_and_activate=bind_and_activate)


def run_server(port: int = DEFAULT_PORT, host: str = "") -> None:
    """Starts the dual-stack threaded HTTP server."""
    init_db()

    httpd = None
    for attempt in range(12):
        try:
            bind_host = "::" if socket.has_ipv6 else "0.0.0.0"
            httpd = DualStackThreadingServer((bind_host, port), AetheriaRequestHandler)
            break
        except OSError as err:
            if attempt < 11:
                time.sleep(0.35)
            else:
                try:
                    httpd = ThreadingHTTPServer(("0.0.0.0", port), AetheriaRequestHandler)
                    httpd.allow_reuse_address = True
                    break
                except OSError:
                    logger.error("Port %d is busy after retries: %s", port, err)
                    sys.exit(1)

    print("\n" + "=" * 70)
    print("   🌌 AETHERIA 3D • Living Neural Cosmos & Generative Soundscape")
    print("=" * 70)
    print(f"   • Local URL        : http://localhost:{port}")
    print(f"   • Network URL      : http://127.0.0.1:{port}")
    print(f"   • IPv6 URL         : http://[::1]:{port}")
    print(f"   • Intelligence Core: {NVIDIA_MODEL} (NVIDIA NIM)")
    print(f"   • Database         : SQLite ({DB_PATH.name})")
    print(f"   • Dual-Stack Status: ACTIVE on [::]:{port} + 0.0.0.0:{port} (Zero Refusal)")
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
    parser.add_argument("--host", type=str, default="", help="Host interface")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
