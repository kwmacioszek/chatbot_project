from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

_DB_PATH = Path("sessions.db")

_ASK_CACHE_TTL_SECONDS = 300
_ask_cache: dict[str, tuple[str, float]] = {}


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            messages TEXT NOT NULL
        )
        """
    )
    return conn


def get_session(session_id: str) -> list[ModelMessage]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT messages FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
    if row is None:
        return []
    return ModelMessagesTypeAdapter.validate_json(row[0])


def save_session(session_id: str, messages: list[ModelMessage]) -> None:
    payload = ModelMessagesTypeAdapter.dump_json(messages).decode("utf-8")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, messages) VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET messages = excluded.messages
            """,
            (session_id, payload),
        )


def end_session(session_id: str) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM sessions WHERE session_id = ?", (session_id,)
        )
        return cursor.rowcount > 0


def _cache_key(question: str) -> str:
    return question.strip().lower()


def cache_get(question: str) -> str | None:
    entry = _ask_cache.get(_cache_key(question))
    print(f"Cache entry for '{_cache_key(question)}': {entry}")
    if entry is None:
        return None
    answer, expires_at = entry
    if time.monotonic() > expires_at:
        del _ask_cache[_cache_key(question)]
        return None
    return answer


def cache_set(question: str, answer: str) -> None:
    _ask_cache[_cache_key(question)] = (
        answer,
        time.monotonic() + _ASK_CACHE_TTL_SECONDS,
    )

def cache_clear() -> int:
    cleared = len(_ask_cache)
    _ask_cache.clear()
    return cleared