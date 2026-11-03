"""IVA Multi-Session Tracking Manager for Stateless Terminals.
================================================================================
Enables persistent multi-session tracking, context restoration, and session diffs
inside a pure standard terminal CLI:
1. Creates, lists, and switches between isolated work sessions.
2. Tracks modified files, prompt history, token usage, and active models.
3. Exports session reports and transcripts into structured Markdown or JSONL.
4. Requires ZERO external PyPI dependencies (100% Python standard library).
================================================================================
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SessionManager")


@dataclass
class SessionTurn:
    turn_index: int
    timestamp: float
    prompt: str
    response: str
    model: str
    modified_files: List[str] = field(default_factory=list)


@dataclass
class Session:
    session_id: str
    name: str
    created_at: float
    updated_at: float
    turns: List[SessionTurn] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    is_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "modified_files": self.modified_files,
            "turns": [asdict(t) for t in self.turns],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Session:
        turns_data = data.get("turns", [])
        turns = [
            SessionTurn(
                turn_index=t.get("turn_index", 0),
                timestamp=t.get("timestamp", 0.0),
                prompt=t.get("prompt", ""),
                response=t.get("response", ""),
                model=t.get("model", ""),
                modified_files=t.get("modified_files", []),
            )
            for t in turns_data
        ]
        return cls(
            session_id=data.get("session_id", ""),
            name=data.get("name", "unnamed_session"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            turns=turns,
            modified_files=data.get("modified_files", []),
            is_active=data.get("is_active", False),
        )


class SessionManager:
    """Manages persistent sessions across stateless terminal invocations."""

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        if storage_dir is not None:
            self.storage_dir = Path(storage_dir)
        else:
            repo_root = Path(__file__).resolve().parents[5] if len(Path(__file__).resolve().parents) >= 6 else Path.cwd()
            self.storage_dir = repo_root / "scratch" / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._active_session: Optional[Session] = None
        self._ensure_initial_session()

    def _get_session_path(self, session_id: str) -> Path:
        clean_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in session_id)
        return self.storage_dir / f"{clean_id}.json"

    def _ensure_initial_session(self) -> Session:
        sessions = self.list_sessions()
        for s in sessions:
            if s.is_active:
                self._active_session = s
                return s
        # Create default session if none exists
        return self.create_session("default_session")

    def create_session(self, name: Optional[str] = None) -> Session:
        now = time.time()
        sid = f"sess_{int(now)}_{os.urandom(2).hex()}"
        s_name = name.strip() if name and name.strip() else f"Session_{time.strftime('%Y%m%d_%H%M%S')}"

        # Deactivate any previous active session
        if self._active_session:
            self._active_session.is_active = False
            self.save_session(self._active_session)

        new_sess = Session(
            session_id=sid,
            name=s_name,
            created_at=now,
            updated_at=now,
            is_active=True,
        )
        self._active_session = new_sess
        self.save_session(new_sess)
        return new_sess

    def save_session(self, session: Session) -> None:
        path = self._get_session_path(session.session_id)
        path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")

    def get_active_session(self) -> Session:
        if self._active_session is None:
            return self._ensure_initial_session()
        return self._active_session

    def list_sessions(self) -> List[Session]:
        sessions: List[Session] = []
        for file in sorted(self.storage_dir.glob("sess_*.json"), key=os.path.getmtime, reverse=True):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                sessions.append(Session.from_dict(data))
            except Exception as e:
                logger.debug("Failed loading session file %s: %e", file, e)
        return sessions

    def switch_session(self, target_id_or_name: str) -> Optional[Session]:
        clean = target_id_or_name.strip().lower()
        sessions = self.list_sessions()
        matched: Optional[Session] = None

        for s in sessions:
            if s.session_id.lower() == clean or s.name.lower() == clean or s.session_id.lower().endswith(clean):
                matched = s
                break

        if not matched:
            return None

        # Deactivate current
        if self._active_session:
            self._active_session.is_active = False
            self.save_session(self._active_session)

        matched.is_active = True
        matched.updated_at = time.time()
        self.save_session(matched)
        self._active_session = matched
        return matched

    def record_turn(
        self,
        prompt: str,
        response: str,
        model: str,
        modified_files: Optional[List[str]] = None,
    ) -> SessionTurn:
        sess = self.get_active_session()
        turn_idx = len(sess.turns) + 1
        mods = list(modified_files or [])

        turn = SessionTurn(
            turn_index=turn_idx,
            timestamp=time.time(),
            prompt=prompt,
            response=response,
            model=model,
            modified_files=mods,
        )
        sess.turns.append(turn)
        sess.updated_at = time.time()

        for mf in mods:
            if mf not in sess.modified_files:
                sess.modified_files.append(mf)

        self.save_session(sess)
        return turn

    def record_file_change(self, filepath: str) -> None:
        sess = self.get_active_session()
        if filepath not in sess.modified_files:
            sess.modified_files.append(filepath)
            sess.updated_at = time.time()
            self.save_session(sess)

    def export_session_markdown(self, session_id: Optional[str] = None) -> str:
        sess = self.get_active_session() if not session_id else None
        if session_id:
            for s in self.list_sessions():
                if s.session_id == session_id:
                    sess = s
                    break
        if not sess:
            return "# Session Not Found\n"

        lines = [
            f"# IVA Session Transcript: {sess.name}",
            f"- **Session ID**: `{sess.session_id}`",
            f"- **Created At**: {time.ctime(sess.created_at)}",
            f"- **Last Updated**: {time.ctime(sess.updated_at)}",
            f"- **Total Turns**: {len(sess.turns)}",
            f"- **Modified Files ({len(sess.modified_files)})**:",
        ]
        for mf in sess.modified_files:
            lines.append(f"  - `{mf}`")

        lines.append("\n---\n## Conversation History\n")
        for t in sess.turns:
            lines.append(f"### Turn {t.turn_index} [{time.ctime(t.timestamp)} | Model: {t.model}]")
            lines.append(f"**User**:\n```text\n{t.prompt}\n```\n")
            lines.append(f"**Iva**:\n{t.response}\n")
            if t.modified_files:
                lines.append(f"*Files touched in this turn*: {', '.join(f'`{f}`' for f in t.modified_files)}\n")
            lines.append("---\n")

        return "\n".join(lines)
