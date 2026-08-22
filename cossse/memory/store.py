"""Native persistent Memory capability for the first real COSsse experiment."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .codec import dumps, loads


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryIntegrityError(RuntimeError):
    """Raised when preserved content no longer matches its recorded digest."""


@dataclass(frozen=True, slots=True)
class MemoryReceipt:
    memory_id: str
    stored_at: str
    sha256: str


class Memory:
    """Preserve opaque supported values and reproduce them faithfully later.

    Memory deliberately knows nothing about Flow or the source/meaning of a value.
    SQLite is an internal implementation detail and can be replaced behind this API.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._db = sqlite3.connect(self.path)
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                stored_at TEXT NOT NULL,
                payload TEXT NOT NULL,
                sha256 TEXT NOT NULL
            )
            """
        )
        self._db.commit()

    def remember(self, value: Any, *, memory_id: str | None = None) -> MemoryReceipt:
        payload = dumps(value)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        record_id = memory_id or f"memory_{uuid4().hex}"
        stored_at = _utcnow_iso()
        self._db.execute(
            "INSERT INTO memories(memory_id, stored_at, payload, sha256) VALUES (?, ?, ?, ?)",
            (record_id, stored_at, payload, digest),
        )
        self._db.commit()
        return MemoryReceipt(record_id, stored_at, digest)

    def receipts(self) -> tuple[MemoryReceipt, ...]:
        """Return receipts for preserved values without interpreting their payloads.

        This is intentionally enumeration, not search. It exposes only Memory's
        own housekeeping metadata so a consumer can discover what may be recalled
        without reaching into the storage implementation.
        """

        rows = self._db.execute(
            "SELECT memory_id, stored_at, sha256 FROM memories "
            "ORDER BY stored_at ASC, memory_id ASC"
        ).fetchall()
        return tuple(MemoryReceipt(*row) for row in rows)

    def recall(self, memory_id: str) -> Any:
        row = self._db.execute(
            "SELECT payload, sha256 FROM memories WHERE memory_id = ?",
            (memory_id,),
        ).fetchone()
        if row is None:
            raise KeyError(memory_id)

        payload, expected_digest = row
        actual_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if actual_digest != expected_digest:
            raise MemoryIntegrityError(f"Integrity check failed for {memory_id}")
        return loads(payload)

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "Memory":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
