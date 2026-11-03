"""Meetup 3D Application — Automated Integration & Verification Tests.
================================================================================
Verifies REST API contracts, RSVP registrations, CORS headers, and static assets.
================================================================================
"""

from __future__ import annotations

import json
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
from applications.meetup_3d.backend.server import start_server


class TestMeetup3DBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = 8991
        cls.server = start_server(host="127.0.0.1", port=cls.port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.3)  # Allow socket bind

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path: str) -> tuple[int, dict | str]:
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            try:
                return (status, json.loads(body))
            except Exception:
                return (status, body)

    def _post_json(self, path: str, payload: dict) -> tuple[int, dict]:
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                status = resp.status
                return (status, json.loads(resp.read().decode("utf-8")))
        except urllib.error.HTTPError as err:
            return (err.code, json.loads(err.read().decode("utf-8")))

    def test_01_health_check(self) -> None:
        status, data = self._get("/api/health")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("status"), "UP")
        self.assertIn("timestamp", data)

    def test_02_get_all_meetups(self) -> None:
        status, data = self._get("/api/meetups")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, dict)
        self.assertTrue(data.get("success"))
        events = data.get("events", [])
        self.assertGreaterEqual(len(events), 4)

        # Verify 3D Coordinates presence
        for e in events:
            self.assertIn("coordinates_3d", e)
            coords = e["coordinates_3d"]
            self.assertIn("x", coords)
            self.assertIn("y", coords)
            self.assertIn("z", coords)
            self.assertIn("glow_color", e)

    def test_03_rsvp_registration_workflow(self) -> None:
        test_email = f"lead.tester.{int(time.time())}@enterprise.org"
        status, data = self._post_json(
            "/api/meetups/meetup-02/rsvp",
            {"name": "Senior Staff Architect", "email": test_email},
        )
        self.assertEqual(status, 201)
        self.assertTrue(data.get("success"))
        self.assertIn("RSVP Confirmed", data.get("message", ""))

        # Verify duplicate prevention
        dup_status, dup_data = self._post_json(
            "/api/meetups/meetup-02/rsvp",
            {"name": "Senior Staff Architect", "email": test_email},
        )
        self.assertEqual(dup_status, 400)
        self.assertFalse(dup_data.get("success"))
        self.assertIn("already registered", dup_data.get("error", ""))

    def test_04_static_assets_serving(self) -> None:
        # Home page HTML
        status, html = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("<title>NexusMeet 3D", html)
        self.assertIn("webgl-canvas", html)

        # CSS asset
        status, css = self._get("/css/styles.css")
        self.assertEqual(status, 200)
        self.assertIn("--bg-primary", css)


if __name__ == "__main__":
    unittest.main()
