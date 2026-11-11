"""IVA Daemon IPC Server & Client Architecture.
================================================================================
Provides zero-dependency, ultra-reliable inter-process communication (IPC) between
the detached background supervisor/worker and the Antigravity interactive chat UI.

Key Architectural Capabilities:
1. Local Loopback Socket Protocol:
   - High-throughput JSON protocol bound strictly to 127.0.0.1 (Windows, macOS, Linux).
   - Zero external broker (no Redis, no RabbitMQ, no mandatory external daemons).
2. Live Log Streaming & In-Memory Ring Buffer:
   - Maintains a thread-safe ring buffer of recent logs (default: 500 events).
   - Allows newly opened Antigravity chat sessions or reconnected clients to
     instantly tail the last N logs without reading slow disk files.
3. Live Task Query & Control:
   - Query: PING, STATUS, TAIL_LOGS, GET_METRICS.
   - Control: SUBMIT_TASK, PAUSE_TASK, RESUME_TASK, STOP_TASK.
4. Auto-Port Discovery:
   - Discovers active port from scratch/daemon_ipc.port or falls back to standard 9444.
================================================================================
"""

from __future__ import annotations

import collections
import json
import logging
import os
import socket
import socketserver
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

logger = logging.getLogger("iva.process_supervision.daemon_ipc")

DEFAULT_IPC_PORT = 9444
MAX_RING_BUFFER_SIZE = 500


@dataclass
class IpcRequest:
    msg_id: str
    command: str  # "PING", "STATUS", "TAIL_LOGS", "SUBMIT_TASK", "STOP_TASK", "SET_STATE"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data_str: str) -> IpcRequest:
        data = json.loads(data_str)
        return cls(
            msg_id=data.get("msg_id", ""),
            command=data.get("command", "PING"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class IpcResponse:
    msg_id: str
    status: str  # "OK", "ERROR"
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data_str: str) -> IpcResponse:
        data = json.loads(data_str)
        return cls(
            msg_id=data.get("msg_id", ""),
            status=data.get("status", "OK"),
            data=data.get("data", {}),
            error_message=data.get("error_message"),
            timestamp=data.get("timestamp", time.time()),
        )


class _ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Handles individual incoming IPC connections from Antigravity or local CLI."""

    def handle(self) -> None:
        server: DaemonIpcServer = self.server  # type: ignore
        self.request.settimeout(1.5)
        buffer = ""
        while not server.stop_event.is_set():
            try:
                data = self.request.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        req = IpcRequest.from_json(line)
                        resp = server.dispatch_request(req)
                        resp_bytes = (resp.to_json() + "\n").encode("utf-8")
                        self.request.sendall(resp_bytes)
                    except Exception as exc:
                        err_resp = IpcResponse(
                            msg_id="err",
                            status="ERROR",
                            error_message=f"Invalid IPC payload: {exc}",
                        )
                        self.request.sendall((err_resp.to_json() + "\n").encode("utf-8"))
            except (ConnectionResetError, BrokenPipeError, socket.timeout):
                break
            except Exception as e:
                logger.debug("IPC client handler error: %s", e)
                break


class DaemonIpcServer(socketserver.ThreadingTCPServer):
    """Threaded TCP IPC Server for detached background worker processes."""

    allow_reuse_address = True

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = DEFAULT_IPC_PORT,
        workspace_root: Optional[Path | str] = None,
    ) -> None:
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.scratch_dir = self.workspace_root / "scratch"
        self.port_file = self.scratch_dir / "daemon_ipc.port"
        self.stop_event = threading.Event()
        self.start_epoch = time.time()
        self.log_ring_buffer: Deque[Dict[str, Any]] = collections.deque(maxlen=MAX_RING_BUFFER_SIZE)
        self.buffer_lock = threading.Lock()

        # Dynamic state
        self.active_task_info: Dict[str, Any] = {
            "task_id": None,
            "name": "IDLE",
            "phase": "STANDBY",
            "progress_pct": 0.0,
            "started_epoch": None,
            "details": {},
        }
        self.command_handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

        # Bind to host and port (try requested, or bind to ephemeral port if busy)
        bind_port = port
        try:
            super().__init__((host, bind_port), _ThreadedTCPRequestHandler)
        except OSError:
            super().__init__((host, 0), _ThreadedTCPRequestHandler)

        self.actual_port = self.server_address[1]
        self._server_thread: Optional[threading.Thread] = None

    def record_log(self, message: str, level: str = "INFO", category: str = "GENERAL") -> None:
        """Appends a log line to the thread-safe in-memory ring buffer."""
        entry = {
            "timestamp": time.time(),
            "level": level,
            "category": category,
            "message": message.strip(),
        }
        with self.buffer_lock:
            self.log_ring_buffer.append(entry)

    def set_task_state(
        self,
        task_id: Optional[str],
        name: str,
        phase: str,
        progress_pct: float = 0.0,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Updates the live task execution state visible to connecting clients."""
        self.active_task_info = {
            "task_id": task_id,
            "name": name,
            "phase": phase,
            "progress_pct": progress_pct,
            "started_epoch": time.time() if task_id else None,
            "details": details or {},
        }
        self.record_log(f"Task '{name}' phase updated to [{phase}] ({progress_pct:.1f}%)", level="INFO", category="STATE")

    def register_command(self, command: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Registers a custom command handler."""
        self.command_handlers[command.upper()] = handler

    def dispatch_request(self, req: IpcRequest) -> IpcResponse:
        """Processes an incoming IPC request and formats the response."""
        cmd = req.command.upper()

        if cmd == "PING":
            return IpcResponse(
                msg_id=req.msg_id,
                status="OK",
                data={
                    "status": "PONG",
                    "pid": os.getpid(),
                    "uptime_sec": time.time() - self.start_epoch,
                    "active_task": self.active_task_info,
                },
            )

        elif cmd == "STATUS":
            return IpcResponse(
                msg_id=req.msg_id,
                status="OK",
                data={
                    "pid": os.getpid(),
                    "uptime_sec": time.time() - self.start_epoch,
                    "active_task": self.active_task_info,
                    "buffered_logs_count": len(self.log_ring_buffer),
                },
            )

        elif cmd == "TAIL_LOGS":
            limit = int(req.payload.get("limit", 50))
            with self.buffer_lock:
                logs = list(self.log_ring_buffer)[-limit:]
            return IpcResponse(
                msg_id=req.msg_id,
                status="OK",
                data={"logs": logs, "total_buffered": len(self.log_ring_buffer)},
            )

        elif cmd in self.command_handlers:
            try:
                result = self.command_handlers[cmd](req.payload)
                return IpcResponse(msg_id=req.msg_id, status="OK", data=result)
            except Exception as e:
                return IpcResponse(
                    msg_id=req.msg_id,
                    status="ERROR",
                    error_message=f"Handler error for {cmd}: {e}",
                )

        else:
            return IpcResponse(
                msg_id=req.msg_id,
                status="ERROR",
                error_message=f"Unknown command: {req.command}",
            )

    def start(self) -> None:
        """Starts the IPC server in a dedicated background daemon thread."""
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.port_file.write_text(json.dumps({
                "port": self.actual_port,
                "pid": os.getpid(),
                "started_epoch": self.start_epoch,
            }), encoding="utf-8")
        except Exception as e:
            logger.warning("Could not write port file: %s", e)

        self._server_thread = threading.Thread(
            target=self.serve_forever,
            name="IVA-DaemonIPCServer",
            daemon=True,
        )
        self._server_thread.start()
        self.record_log(f"Daemon IPC Server online on port {self.actual_port} (PID: {os.getpid()})")
        logger.info("Daemon IPC Server listening on 127.0.0.1:%s (PID: %s)", self.actual_port, os.getpid())

    def stop(self) -> None:
        """Gracefully shuts down the IPC server and cleans up the port file."""
        self.stop_event.set()
        self.shutdown()
        self.server_close()
        try:
            if self.port_file.exists():
                self.port_file.unlink()
        except Exception:
            pass


class DaemonIpcClient:
    """Client for Antigravity UI, chat turns, or CLI tools to communicate with the daemon."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: Optional[int] = None,
        workspace_root: Optional[Path | str] = None,
        timeout_sec: float = 1.0,
    ) -> None:
        self.host = host
        self.timeout_sec = timeout_sec
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.scratch_dir = self.workspace_root / "scratch"
        self.port_file = self.scratch_dir / "daemon_ipc.port"
        self._explicit_port = port

    def resolve_port(self) -> int:
        """Discovers port from scratch/daemon_ipc.port or defaults to standard port."""
        if self._explicit_port:
            return self._explicit_port
        if self.port_file.exists():
            try:
                data = json.loads(self.port_file.read_text(encoding="utf-8"))
                return int(data.get("port", DEFAULT_IPC_PORT))
            except Exception:
                pass
        return DEFAULT_IPC_PORT

    def send_request(self, command: str, payload: Optional[Dict[str, Any]] = None) -> Optional[IpcResponse]:
        """Sends a single request to the daemon IPC server and awaits structured response."""
        port = self.resolve_port()
        req = IpcRequest(
            msg_id=f"req_{int(time.time() * 1000)}",
            command=command,
            payload=payload or {},
        )
        try:
            with socket.create_connection((self.host, port), timeout=self.timeout_sec) as sock:
                sock.settimeout(self.timeout_sec)
                sock.sendall((req.to_json() + "\n").encode("utf-8"))

                resp_buffer = ""
                while "\n" not in resp_buffer:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    resp_buffer += chunk.decode("utf-8")

                if resp_buffer:
                    line = resp_buffer.split("\n", 1)[0].strip()
                    return IpcResponse.from_json(line)
        except (ConnectionRefusedError, socket.timeout, OSError):
            return None
        return None

    def is_daemon_alive(self) -> bool:
        """Fast check if the background daemon IPC server is responsive."""
        resp = self.send_request("PING")
        return resp is not None and resp.status == "OK"

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Retrieves active task status, uptime, and PID."""
        resp = self.send_request("STATUS")
        if resp and resp.status == "OK":
            return resp.data
        return None

    def tail_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent logs directly from daemon in-memory ring buffer."""
        resp = self.send_request("TAIL_LOGS", {"limit": limit})
        if resp and resp.status == "OK":
            return resp.data.get("logs", [])
        return []
