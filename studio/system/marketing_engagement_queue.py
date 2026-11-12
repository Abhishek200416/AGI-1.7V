#!/usr/bin/env python3
"""
IVA Marketing Studio — Organized Multi-Platform Engagement & Inbox Queue
Manages comments and chat/DM threads across YouTube, Instagram, and LinkedIn in a
local SQLite WAL database (`marketing_inbox.db`). Supports thread ingestion,
priority triage, diligent contextual reply drafting, and organized status tracking
(`PENDING` -> `DRAFTED` -> `APPROVED` -> `SENT`).
"""

import contextlib
import json
import os
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_DB = os.path.join(BASE_DIR, "system", "marketing_inbox.db")

PLATFORMS = ("youtube", "instagram", "linkedin", "reddit")
CHANNEL_KINDS = ("comment", "chat_dm")


@contextlib.contextmanager
def _db_conn(db_path: str = INBOX_DB):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS engagement_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                channel_kind TEXT NOT NULL,
                author TEXT NOT NULL,
                post_or_campaign TEXT DEFAULT '',
                incoming_text TEXT NOT NULL,
                priority INTEGER DEFAULT 2,
                draft_reply TEXT DEFAULT '',
                status TEXT DEFAULT 'PENDING',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        yield conn
        conn.commit()
    finally:
        conn.close()


def add_thread(
    platform: str,
    channel_kind: str,
    author: str,
    incoming_text: str,
    post_or_campaign: str = "",
    priority: int = 2,
    db_path: str = INBOX_DB,
) -> int:
    plat = platform.strip().lower()
    kind = channel_kind.strip().lower()
    if plat not in PLATFORMS:
        raise ValueError(f"Unsupported platform '{platform}'. Choose from {PLATFORMS}.")
    if kind not in CHANNEL_KINDS:
        raise ValueError(f"Unsupported channel_kind '{channel_kind}'. Choose from {CHANNEL_KINDS}.")

    now = datetime.now(timezone.utc).isoformat()
    with _db_conn(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO engagement_threads
            (platform, channel_kind, author, post_or_campaign, incoming_text, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
            """,
            (plat, kind, author.strip(), post_or_campaign.strip(), incoming_text.strip(), priority, now, now),
        )
        return int(cur.lastrowid)


def draft_diligent_reply(
    thread_id: int,
    app_name: str,
    app_url: str,
    custom_reply: str | None = None,
    db_path: str = INBOX_DB,
) -> dict:
    """Draft an organized, polite, helpful reply tailored to the thread question."""
    with _db_conn(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM engagement_threads WHERE id = ?", (thread_id,)).fetchone()
        if not row:
            raise ValueError(f"Thread {thread_id} not found.")

        if custom_reply:
            reply = custom_reply.strip()
        else:
            msg_low = row["incoming_text"].lower()
            author = row["author"].lstrip("@")
            if any(k in msg_low for k in ("link", "where", "find", "download", "url", "install")):
                reply = (
                    f"Hi {author}, thanks for reaching out! You can find {app_name} directly at {app_url}. "
                    f"Let us know once you try it — happy to help you get set up."
                )
            elif any(k in msg_low for k in ("how", "use", "work", "start", "setup", "guide")):
                reply = (
                    f"Hi {author}! To get started with {app_name}, head to {app_url} and run the quickstart command shown on the page. "
                    f"Reply here anytime if you'd like a walkthrough for your setup."
                )
            else:
                reply = (
                    f"Appreciate your message, {author}! Thanks for checking out {app_name} ({app_url}) — "
                    f"feel free to ask any questions or share feedback."
                )

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "UPDATE engagement_threads SET draft_reply = ?, status = 'DRAFTED', updated_at = ? WHERE id = ?",
            (reply, now, thread_id),
        )
        return {"thread_id": thread_id, "platform": row["platform"], "channel_kind": row["channel_kind"], "draft_reply": reply, "status": "DRAFTED"}


def mark_sent(thread_id: int, db_path: str = INBOX_DB) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    with _db_conn(db_path) as conn:
        conn.execute("UPDATE engagement_threads SET status = 'SENT', updated_at = ? WHERE id = ?", (now, thread_id))
    return {"thread_id": thread_id, "status": "SENT"}


def list_queue(platform: str | None = None, status: str | None = None, db_path: str = INBOX_DB) -> list[dict]:
    sql = "SELECT * FROM engagement_threads WHERE 1=1"
    params: list = []
    if platform:
        sql += " AND platform = ?"
        params.append(platform.strip().lower())
    if status:
        sql += " AND status = ?"
        params.append(status.strip().upper())
    sql += " ORDER BY priority ASC, id ASC"
    with _db_conn(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def _self_check():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        tmp_db = tf.name
    try:
        tid1 = add_thread("youtube", "comment", "@dev_alex", "Where can I find the link to try this?", "Launch Short", priority=1, db_path=tmp_db)
        tid2 = add_thread("linkedin", "chat_dm", "Priya Sharma", "How do we set this up for our team?", "Product Post", priority=1, db_path=tmp_db)
        tid3 = add_thread("instagram", "chat_dm", "rohan_ui", "Looks clean, congrats!", "Reel 01", priority=2, db_path=tmp_db)
        draft_diligent_reply(tid1, "IVA", "https://github.com/Abhishek200416/IVA", db_path=tmp_db)
        draft_diligent_reply(tid2, "IVA", "https://github.com/Abhishek200416/IVA", db_path=tmp_db)
        mark_sent(tid1, db_path=tmp_db)
        q = list_queue(db_path=tmp_db)
        assert len(q) == 3
        assert q[0]["status"] == "SENT" and "github.com/Abhishek200416/IVA" in q[0]["draft_reply"]
        assert q[1]["status"] == "DRAFTED" and q[2]["status"] == "PENDING"
        print("[PASS] marketing_engagement_queue organized inbox self-check verified (3 threads across YT/LI/IG).")
    finally:
        for ext in ("", "-wal", "-shm"):
            p = tmp_db + ext
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    _self_check()
