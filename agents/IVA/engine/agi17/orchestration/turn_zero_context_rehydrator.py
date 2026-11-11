"""IVA Turn-0 Context Rehydration Engine.
================================================================================
Eliminates amnesia and disconnected turns when restarting Antigravity, switching
devices, or pulling code updates.

Key Architectural Responsibilities:
1. Turn-Zero Memory & Task Discovery:
   - Queries DaemonIpcClient to retrieve live running task info, progress, and recent logs.
   - Audits OS process state via AntigravityPreflightGuardian.
   - Inspects persistent SQLite WAL memory nodes for recent decisions and active goals.
2. Context Synthesis:
   - Synthesizes an authoritative RehydratedContext object before the model generates
     its response, so the agent speaks with immediate total situational recall.
3. Zero-Interruption Resume:
   - Distinguishes between:
     * System running smoothly in background (UI can simply monitor).
     * System was interrupted by OS/App restart (needs automatic task resurrection).
     * System was idle or finished (ready for new instructions).
================================================================================
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..process_supervision.daemon_ipc import DaemonIpcClient
from .antigravity_preflight_guardian import AntigravityPreflightGuardian, PreflightReport

logger = logging.getLogger("iva.orchestration.turn_zero_context_rehydrator")

PROJECT_ROOT = Path(__file__).resolve().parents[5]


@dataclass
class RehydratedContext:
    timestamp_epoch: float
    is_daemon_alive: bool
    active_pids: List[int]
    task_name: str
    execution_phase: str
    progress_pct: float
    recent_logs: List[str]
    git_commit: str
    code_updated: bool
    surgical_experiment_passed: bool
    unresolved_goals: List[str] = field(default_factory=list)
    rehydration_prompt_block: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TurnZeroContextRehydrator:
    """Orchestrates total situational rehydration across IPC, OS PIDs, and SQLite WAL."""

    def __init__(
        self,
        workspace_root: Optional[Path | str] = None,
        memory_db_path: Optional[Path | str] = None,
    ) -> None:
        self.workspace_root = Path(workspace_root) if workspace_root else PROJECT_ROOT
        self.guardian = AntigravityPreflightGuardian(self.workspace_root)
        self.ipc_client = DaemonIpcClient(workspace_root=self.workspace_root)

        if memory_db_path:
            self.memory_db_path = Path(memory_db_path)
        else:
            d_path = Path(r"D:\AGI_Storage\AGI_1_7\memory\omega_memory.db")
            local_path = self.workspace_root / "agents" / "IVA" / "memory" / "omega_memory.db"
            mac_path = Path.home() / "Library" / "Application Support" / "IVA" / "memory" / "omega_memory.db"
            if sys.platform == "darwin" and mac_path.exists():
                self.memory_db_path = mac_path
            elif d_path.exists():
                self.memory_db_path = d_path
            elif local_path.exists():
                self.memory_db_path = local_path
            elif sys.platform == "darwin":
                self.memory_db_path = mac_path
            else:
                self.memory_db_path = Path.home() / ".iva" / "memory" / "omega_memory.db"

    def query_recent_unresolved_goals(self, limit: int = 3) -> List[str]:
        """Queries persistent SQLite storage for unfinished goals or open loops."""
        goals: List[str] = []
        if not self.memory_db_path.exists():
            return goals

        try:
            conn = sqlite3.connect(str(self.memory_db_path), timeout=0.1)
            cursor = conn.cursor()

            # Check for goals table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='autonomous_goals'")
            if cursor.fetchone():
                cursor.execute(
                    "SELECT title FROM autonomous_goals WHERE status IN ('ACTIVE', 'IN_PROGRESS', 'PENDING') ORDER BY priority DESC LIMIT ?",
                    (limit,)
                )
                for row in cursor.fetchall():
                    goals.append(row[0])

            # If empty, check memory nodes
            if not goals:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_nodes'")
                if cursor.fetchone():
                    cursor.execute(
                        "SELECT content FROM memory_nodes WHERE category IN ('OPEN_LOOP', 'DECISION') ORDER BY id DESC LIMIT ?",
                        (limit,)
                    )
                    for row in cursor.fetchall():
                        goals.append(row[0][:150])

            conn.close()
        except Exception as e:
            logger.debug("Failed querying goals from memory: %s", e)

        return goals

    def rehydrate(self) -> RehydratedContext:
        """Executes full rehydration across IPC daemon, preflight audit, and SQLite memory."""
        now = time.time()

        # 1. Evaluate Preflight Audit (PID liveness, git commit drift, surgical AST)
        preflight: PreflightReport = self.guardian.evaluate_preflight_on_chat()

        # 2. Query Daemon IPC Server for live execution status & ring-buffered logs
        ipc_status = self.ipc_client.get_status()
        is_ipc_alive = ipc_status is not None

        task_name = "IDLE"
        phase = "STANDBY"
        progress_pct = 0.0
        active_pids = list(preflight.active_pids)
        recent_logs: List[str] = []

        if ipc_status:
            daemon_pid = ipc_status.get("pid")
            if daemon_pid and daemon_pid not in active_pids:
                active_pids.append(daemon_pid)

            active_task = ipc_status.get("active_task", {})
            task_name = active_task.get("name", "IDLE")
            phase = active_task.get("phase", "STANDBY")
            progress_pct = active_task.get("progress_pct", 0.0)

            # Get last 5 log lines from memory ring buffer
            logs_raw = self.ipc_client.tail_logs(limit=5)
            for entry in logs_raw:
                msg = entry.get("message", "")
                cat = entry.get("category", "")
                recent_logs.append(f"[{cat}] {msg}")
        else:
            # Fallback to preflight status
            if preflight.task_status == "HEALTHY_ACTIVE":
                task_name = "BACKGROUND_DAEMON"
                phase = "EXECUTING"
            elif preflight.task_status == "RESTART_RECOVERED_IDLE":
                task_name = "INTERRUPTED_BY_RESTART"
                phase = "RESURRECTION_READY"

        # 3. Query unresolved goals from persistent memory
        unresolved_goals = self.query_recent_unresolved_goals(limit=3)

        # 4. Synthesize authoritative prompt rehydration block
        log_snippet = "\n".join([f"    • {l}" for l in recent_logs]) if recent_logs else "    • (No active log stream)"
        goals_snippet = "\n".join([f"    • {g}" for g in unresolved_goals]) if unresolved_goals else "    • (None pending)"

        prompt_block = (
            "================================================================================\n"
            "IVA TURN-0 REHYDRATED CONTEXT (AUTOMATIC TOTAL RECALL):\n"
            f"- Background Daemon: {'ALIVE & CONNECTED' if is_ipc_alive else preflight.task_status} (PIDs: {active_pids or 'None'})\n"
            f"- Active Task: {task_name} | Phase: [{phase}] ({progress_pct:.1f}%)\n"
            f"- Git State: Commit {preflight.current_git_commit} (Update Detected: {preflight.code_update_detected})\n"
            f"- Surgical AST Verification: {'PASSED (Zero Destructive Overwrite)' if preflight.surgical_experiment_passed else 'CHECK NEEDED'}\n"
            "- Recent Live Logs:\n"
            f"{log_snippet}\n"
            "- Active Goals / Open Loops:\n"
            f"{goals_snippet}\n"
            "================================================================================"
        )

        return RehydratedContext(
            timestamp_epoch=now,
            is_daemon_alive=is_ipc_alive or preflight.background_task_running,
            active_pids=active_pids,
            task_name=task_name,
            execution_phase=phase,
            progress_pct=progress_pct,
            recent_logs=recent_logs,
            git_commit=preflight.current_git_commit,
            code_updated=preflight.code_update_detected,
            surgical_experiment_passed=preflight.surgical_experiment_passed,
            unresolved_goals=unresolved_goals,
            rehydration_prompt_block=prompt_block,
        )


if __name__ == "__main__":
    rehydrator = TurnZeroContextRehydrator()
    ctx = rehydrator.rehydrate()
    print(ctx.rehydration_prompt_block)
