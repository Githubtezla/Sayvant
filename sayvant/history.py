"""Verlauf der Diktate in SQLite (%APPDATA%\\Sayvant\\history.db)."""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    seconds REAL,
    engine TEXT,
    raw TEXT,
    final TEXT,
    cleanup TEXT,
    window TEXT
);
CREATE INDEX IF NOT EXISTS entries_ts ON entries(ts);
"""


class History:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, seconds: float, engine: str, raw: str, final: str, cleanup: str, window: str) -> None:
        with self._lock, self._conn() as c:
            c.execute(
                "INSERT INTO entries (ts, seconds, engine, raw, final, cleanup, window) VALUES (?,?,?,?,?,?,?)",
                (time.time(), seconds, engine, raw, final, cleanup, window),
            )

    def search(self, query: str = "", limit: int = 300) -> list[sqlite3.Row]:
        with self._lock, self._conn() as c:
            if query:
                like = f"%{query}%"
                return c.execute(
                    "SELECT * FROM entries WHERE final LIKE ? OR raw LIKE ? OR window LIKE ? ORDER BY ts DESC LIMIT ?",
                    (like, like, like, limit),
                ).fetchall()
            return c.execute("SELECT * FROM entries ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()

    def get(self, entry_id: int) -> sqlite3.Row | None:
        with self._lock, self._conn() as c:
            return c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()

    def delete(self, entry_id: int) -> None:
        with self._lock, self._conn() as c:
            c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))

    def last(self) -> sqlite3.Row | None:
        rows = self.search(limit=1)
        return rows[0] if rows else None

    def prune(self, keep_days: int) -> None:
        if keep_days <= 0:
            return
        with self._lock, self._conn() as c:
            c.execute("DELETE FROM entries WHERE ts < ?", (time.time() - keep_days * 86400,))

    def clear(self) -> None:
        with self._lock, self._conn() as c:
            c.execute("DELETE FROM entries")
