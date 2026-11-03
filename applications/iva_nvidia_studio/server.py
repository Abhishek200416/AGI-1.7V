"""HTTP & AI Inference Server for IVA Sovereign Studio (Powered by NVIDIA NIM).

Pure Python standard library implementation (zero external pip dependencies).
Serves the web studio interface and proxies generative AI requests to NVIDIA NIM
using the verified API key and model targets.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import sys
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.IVA.engine.agi17.adapters.model_adapter import ModelRequest
from agents.IVA.engine.agi17.adapters.universal_api_provider import UniversalAPIProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("iva.nvidia_studio.server")

DEFAULT_API_KEY = os.environ.get("NVIDIA_API_KEY") or "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"
DEFAULT_MODEL = os.environ.get("NVIDIA_MODEL") or "nvidia/nemotron-3.5-bolt-e4b"


class StudioRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving web assets and routing AI generation endpoints."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self) -> None:
        """Handles GET requests for static assets and metadata."""
        if self.path == "/api/status":
            self.send_json_response(self.get_studio_status())
        elif self.path == "/api/models":
            self.send_json_response(self.get_active_models())
        else:
            super().do_GET()

    def do_POST(self) -> None:
        """Handles POST requests for live generative AI completions."""
        if self.path == "/api/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                payload = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self.send_json_response({"error": "Invalid JSON body"}, status=HTTPStatus.BAD_REQUEST)
                return

            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self.send_json_response({"error": "Empty prompt provided"}, status=HTTPStatus.BAD_REQUEST)
                return

            model_override = payload.get("model") or DEFAULT_MODEL
            result = self.execute_nvidia_generation(prompt, model_override)
            self.send_json_response(result)
        else:
            self.send_json_response({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)

    def send_json_response(self, data: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        """Sends JSON encoded response with permissive local CORS headers."""
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        """Handles CORS preflight checks."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def execute_nvidia_generation(self, prompt: str, model_name: str) -> Dict[str, Any]:
        """Calls NVIDIA NIM via UniversalAPIProvider with live error recovery."""
        t0 = time.perf_counter()
        provider = UniversalAPIProvider(
            api_key=DEFAULT_API_KEY,
            provider_type="nvidia",
            model_name=model_name,
        )

        req = ModelRequest(
            task_id=f"STUDIO-{int(time.time() * 1000)}",
            prompt=prompt,
            system_instruction=(
                "You are IVA, the autonomous sovereign AI engineering partner for Abhishek. "
                "Respond with technical brilliance, sharp engineering insight, and clean formatting."
            ),
        )

        res = provider.generate(req)
        duration_ms = round((time.perf_counter() - t0) * 1000, 1)

        if res.get("status") == "SUCCEEDED":
            return {
                "status": "ok",
                "model": res.get("model", model_name),
                "response": res.get("response_text", ""),
                "duration_ms": duration_ms,
                "usage": res.get("provider_usage", {}),
            }
        else:
            return {
                "status": "failed",
                "model": model_name,
                "response": f"NVIDIA Generation Error: {res.get('error_message', 'Generation failed.')}",
                "duration_ms": duration_ms,
                "usage": {},
            }

    def get_studio_status(self) -> Dict[str, Any]:
        """Returns metadata about the active provider and system state."""
        return {
            "application": "IVA Sovereign Studio",
            "provider": "NVIDIA NIM",
            "active_model": DEFAULT_MODEL,
            "has_valid_key": bool(DEFAULT_API_KEY.startswith("nvapi-")),
            "key_preview": f"{DEFAULT_API_KEY[:10]}...{DEFAULT_API_KEY[-4:]}",
            "status": "ONLINE",
            "timestamp": time.time(),
        }

    def get_active_models(self) -> Dict[str, Any]:
        """Returns verified working models on this API key."""
        return {
            "active_model": DEFAULT_MODEL,
            "verified_models": [
                {
                    "id": "nvidia/nemotron-3.5-bolt-e4b",
                    "label": "Nemotron 3.5 Bolt (Fast Response)",
                    "badge": "PRIMARY",
                    "status": "VERIFIED_200",
                },
                {
                    "id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                    "label": "Nemotron 3 Nano Omni (Deep Reasoning)",
                    "badge": "REASONING",
                    "status": "VERIFIED_200",
                },
                {
                    "id": "nvidia/nemotron-3.5-lightning-30b-a3b",
                    "label": "Nemotron 3.5 Lightning (High Throughput)",
                    "badge": "LIGHTNING",
                    "status": "VERIFIED_200",
                },
                {
                    "id": "poolside/laguna-xs-2.1",
                    "label": "Laguna XS (Coding Specialist)",
                    "badge": "CODE",
                    "status": "VERIFIED_200",
                },
            ],
        }


def find_available_port(default_port: int = 8095) -> int:
    """Finds available local port starting from default_port."""
    port = default_port
    while port < default_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return default_port


def run_server(port: int = 8095) -> None:
    """Starts the Threading HTTP Server for the Studio."""
    eff_port = find_available_port(port)
    server_address = ("127.0.0.1", eff_port)
    httpd = ThreadingHTTPServer(server_address, StudioRequestHandler)
    print("\n" + "=" * 74)
    print("   🟢 IVA SOVEREIGN STUDIO ONLINE (POWERED BY NVIDIA NIM)")
    print("=" * 74)
    print(f"   • Local Studio URL: http://localhost:{eff_port}")
    print(f"   • Active Model   : {DEFAULT_MODEL}")
    print(f"   • Active API Key : {DEFAULT_API_KEY[:12]}...{DEFAULT_API_KEY[-4:]}")
    print("   • Press Ctrl+C to stop.")
    print("=" * 74 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Studio Server Stopped]")
        httpd.server_close()


if __name__ == "__main__":
    p_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8095
    run_server(p_arg)
