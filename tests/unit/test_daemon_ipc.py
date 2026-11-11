"""Unit tests for IVA Daemon IPC Server & Client."""

import tempfile
import time
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.process_supervision.daemon_ipc import (
    DaemonIpcClient,
    DaemonIpcServer,
    IpcRequest,
    IpcResponse,
)


class TestDaemonIpc(unittest.TestCase):
    """Tests zero-broker loopback IPC between background worker and chat UI."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="iva_ipc_test_")
        self.workspace_root = Path(self.temp_dir)
        # Spin up IPC server on ephemeral port (port 0)
        self.server = DaemonIpcServer(host="127.0.0.1", port=0, workspace_root=self.workspace_root)
        self.server.start()
        # Initialize client pointing to same workspace
        self.client = DaemonIpcClient(workspace_root=self.workspace_root)

    def tearDown(self):
        self.server.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ipc_ping_pong_and_uptime(self):
        """Verifies ping/pong and daemon liveness."""
        alive = self.client.is_daemon_alive()
        self.assertTrue(alive)

        resp = self.client.send_request("PING")
        self.assertIsNotNone(resp)
        self.assertEqual(resp.status, "OK")
        self.assertEqual(resp.data.get("status"), "PONG")
        self.assertGreaterEqual(resp.data.get("uptime_sec", 0), 0)

    def test_task_state_and_status_query(self):
        """Verifies live task state reporting."""
        self.server.set_task_state(
            task_id="task_999",
            name="Alpha_Hawkes_Calibration",
            phase="CALIBRATING_EXPONENTS",
            progress_pct=65.5,
            details={"samples": 1000},
        )

        status = self.client.get_status()
        self.assertIsNotNone(status)
        task = status.get("active_task", {})
        self.assertEqual(task.get("task_id"), "task_999")
        self.assertEqual(task.get("name"), "Alpha_Hawkes_Calibration")
        self.assertEqual(task.get("phase"), "CALIBRATING_EXPONENTS")
        self.assertEqual(task.get("progress_pct"), 65.5)

    def test_in_memory_log_ring_buffer_and_tail(self):
        """Verifies recent log streaming without touching disk."""
        for i in range(10):
            self.server.record_log(f"Test log message #{i}", level="INFO", category="TEST")

        logs = self.client.tail_logs(limit=5)
        self.assertEqual(len(logs), 5)
        self.assertEqual(logs[-1]["message"], "Test log message #9")
        self.assertEqual(logs[0]["message"], "Test log message #5")

    def test_custom_command_registration(self):
        """Verifies custom command handlers can be dynamically registered on the daemon."""
        def echo_handler(payload):
            return {"echo": payload.get("text", "").upper()}

        self.server.register_command("ECHO", echo_handler)

        resp = self.client.send_request("ECHO", {"text": "hello iva"})
        self.assertIsNotNone(resp)
        self.assertEqual(resp.status, "OK")
        self.assertEqual(resp.data.get("echo"), "HELLO IVA")


if __name__ == "__main__":
    unittest.main()
