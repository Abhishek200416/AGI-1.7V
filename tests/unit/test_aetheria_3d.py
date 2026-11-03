"""Unit Tests for AETHERIA 3D • Living Neural Cosmos & Generative Soundscape."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from applications.aetheria_3d.server import (
    AetheriaRequestHandler,
    FOUNDATIONAL_LORE,
    init_db,
    query_nemotron_oracle,
    DB_PATH,
    BASE_DIR
)


class TestAetheria3D(unittest.TestCase):
    """Verifies backend logic, API endpoints, SQLite persistence, and asset integrity for Aetheria 3D."""

    def setUp(self) -> None:
        init_db()

    def test_01_assets_exist(self) -> None:
        """Verifies all required static assets exist in the application bundle."""
        self.assertTrue((BASE_DIR / "index.html").is_file(), "index.html must exist")
        self.assertTrue((BASE_DIR / "css" / "aetheria.css").is_file(), "aetheria.css must exist")
        self.assertTrue((BASE_DIR / "js" / "aetheria_audio.js").is_file(), "aetheria_audio.js must exist")
        self.assertTrue((BASE_DIR / "js" / "aetheria_scene.js").is_file(), "aetheria_scene.js must exist")
        self.assertTrue((BASE_DIR / "js" / "three.min.js").is_file(), "three.min.js must exist")
        self.assertTrue((BASE_DIR / "js" / "OrbitControls.js").is_file(), "OrbitControls.js must exist")

    def test_02_database_initialized_with_presets(self) -> None:
        """Verifies that SQLite table and default universe presets are initialized correctly."""
        conn = sqlite3.connect(str(DB_PATH))
        try:
            cur = conn.cursor()
            cur.execute("SELECT name, particle_count, theme FROM presets")
            rows = cur.fetchall()
            self.assertGreaterEqual(len(rows), 4, "Should have at least 4 default presets")
            names = [r[0] for r in rows]
            self.assertTrue(any("Cosmic Violet" in n for n in names))
            self.assertTrue(any("Cyber Aurora" in n for n in names))
        finally:
            conn.close()

    def test_03_foundational_lore_structure(self) -> None:
        """Verifies that foundational celestial anomalies contain required astrophysics and lore keys."""
        required_keys = {"title", "sector", "frequency", "energy_signature", "lore", "color", "coordinates"}
        self.assertGreaterEqual(len(FOUNDATIONAL_LORE), 5)
        for anomaly_id, data in FOUNDATIONAL_LORE.items():
            for key in required_keys:
                self.assertIn(key, data, f"Anomaly '{anomaly_id}' missing key '{key}'")
            self.assertEqual(len(data["coordinates"]), 3, f"Anomaly '{anomaly_id}' coordinates must be 3D vector")

    @patch("urllib.request.urlopen")
    def test_04_query_nemotron_oracle_success(self, mock_urlopen: MagicMock) -> None:
        """Verifies oracle response parsing from mocked NVIDIA NIM completion."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [
                {
                    "message": {
                        "content": "The universe reflects your awareness like starlight off a black hole accretion disk."
                    }
                }
            ]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        reply = query_nemotron_oracle("What is time?", "The Chronos Weave")
        self.assertIn("black hole accretion disk", reply)

    def test_06_cosmic_scales_structure(self) -> None:
        """Verifies that all 5 universal scales exist with chronicles and metrics."""
        from applications.aetheria_3d.server import COSMIC_SCALES
        self.assertEqual(len(COSMIC_SCALES), 5)
        expected = ["planetary", "solar_system", "milky_way", "supercluster", "cosmic_web"]
        for key in expected:
            self.assertIn(key, COSMIC_SCALES)
            scale = COSMIC_SCALES[key]
            self.assertIn("name", scale)
            self.assertIn("metrics", scale)
            self.assertIn("camera_dist", scale)
            self.assertIn("chronicle", scale)
            self.assertGreater(len(scale["chronicle"]), 10)

    def test_07_solar_system_planets(self) -> None:
        """Verifies solar system planets array contains Sun and all 8 major planets."""
        from applications.aetheria_3d.server import SOLAR_SYSTEM_PLANETS
        self.assertGreaterEqual(len(SOLAR_SYSTEM_PLANETS), 9)
        names = [p["name"] for p in SOLAR_SYSTEM_PLANETS]
        for expected_planet in ["Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]:
            self.assertIn(expected_planet, names)


if __name__ == "__main__":
    unittest.main()

