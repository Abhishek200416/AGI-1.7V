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

    def test_05_oracle_fallback_on_network_error(self) -> None:
        """Verifies graceful fallback response when API call fails or times out."""
        with patch("urllib.request.urlopen", side_effect=OSError("Network unreachable")):
            reply = query_nemotron_oracle("Tell me of the cosmos", "Cosmic Core")
            self.assertIsInstance(reply, str)
            self.assertGreater(len(reply), 10)


if __name__ == "__main__":
    unittest.main()
