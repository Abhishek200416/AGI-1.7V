"""Meetup 3D Application — Production HTTP REST API Server.
================================================================================
Zero third-party dependencies (100% Python standard library http.server).
Serves REST API endpoints (/api/meetups, /api/rsvp, /api/health) and static frontend.
================================================================================
"""

from __future__ import annotations

import json
import logging
import mimetypes
import os
import re
import socketserver
import sys
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from .database import MeetupRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Meetup3DServer")

REPO_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


class MeetupAPIHandler(SimpleHTTPRequestHandler):
    """Handles REST API queries and serves static 3D WebGL assets."""

    repo = MeetupRepository()

    def end_headers(self) -> None:
        # Inject enterprise CORS and security headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def _send_json(self, status_code: int, data: Any) -> None:
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # 1. API: Health Check
        if path == "/api/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "status": "UP",
                    "service": "Meetup-3D-Enterprise-API",
                    "version": "1.0.0",
                    "timestamp": time.time(),
                },
            )
            return

        # 2. API: List All Meetups
        elif path == "/api/meetups":
            events = self.repo.get_all_events()
            self._send_json(
                HTTPStatus.OK,
                {
                    "success": True,
                    "count": len(events),
                    "events": [e.to_dict() for e in events],
                },
            )
            return

        # 3. API: Single Meetup
        elif path.startswith("/api/meetups/"):
            event_id = path[len("/api/meetups/") :].rstrip("/")
            if event_id and not event_id.endswith("/rsvp"):
                event = self.repo.get_event_by_id(event_id)
                if event:
                    self._send_json(HTTPStatus.OK, {"success": True, "event": event.to_dict()})
                else:
                    self._send_json(HTTPStatus.NOT_FOUND, {"success": False, "error": f"Event '{event_id}' not found"})
                return

        # 4. API: System Statistics
        elif path == "/api/stats":
            events = self.repo.get_all_events()
            total_rsvps = sum(e.rsvp_count for e in events)
            categories = list({e.category for e in events})
            self._send_json(
                HTTPStatus.OK,
                {
                    "success": True,
                    "total_events": len(events),
                    "total_rsvps": total_rsvps,
                    "categories": categories,
                },
            )
            return

        # 5. Static Frontend Asset Routing
        self._serve_static_file(path)

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # API: RSVP Registration
        match = re.match(r"^/api/meetups/([^/]+)/rsvp/?$", path)
        if match:
            event_id = match.group(1)
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)

            try:
                payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
            except Exception:
                self._send_json(HTTPStatus.BAD_REQUEST, {"success": False, "error": "Malformed JSON payload"})
                return

            name = payload.get("name", "")
            email = payload.get("email", "")
            success, message, attendee = self.repo.register_rsvp(event_id, name, email)

            if success:
                self._send_json(
                    HTTPStatus.CREATED,
                    {
                        "success": True,
                        "message": message,
                        "attendee": attendee.__dict__ if attendee else None,
                    },
                )
            else:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "success": False,
                        "error": message,
                    },
                )
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"success": False, "error": "Endpoint not found"})

    def _serve_static_file(self, path: str) -> None:
        clean_path = path.lstrip("/") or "index.html"
        target_file = (FRONTEND_DIR / clean_path).resolve()

        # Prevent directory traversal outside frontend
        if not str(target_file).startswith(str(FRONTEND_DIR.resolve())):
            self.send_error(HTTPStatus.FORBIDDEN, "Access Denied")
            return

        if target_file.is_dir():
            target_file = target_file / "index.html"

        if not target_file.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, f"File Not Found: {clean_path}")
            return

        content_type, _ = mimetypes.guess_type(str(target_file))
        content_type = content_type or "application/octet-stream"

        try:
            content_bytes = target_file.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content_bytes)))
            self.end_headers()
            self.wfile.write(content_bytes)
        except Exception as exc:
            logger.error("Failed serving %s: %s", target_file, exc)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_server(host: str = "127.0.0.1", port: int = 8095) -> socketserver.TCPServer:
    """Launches the Meetup 3D REST API server on specified port."""
    server = ThreadedHTTPServer((host, port), MeetupAPIHandler)
    logger.info("Meetup 3D REST Server listening on http://%s:%d", host, port)
    return server


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8095
    srv = start_server(port=port)
    print(f"🚀 Meetup 3D Enterprise Application live at: http://127.0.0.1:{port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly...")
        srv.shutdown()
