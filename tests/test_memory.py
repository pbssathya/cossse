from __future__ import annotations

from datetime import datetime, timezone

from cossse.memory import Memory


def test_memory_survives_restart_and_preserves_binary(tmp_path):
    path = tmp_path / "memory.db"
    original = {
        "raw": b"\x00\x01collector-bytes\xff",
        "when": datetime(2026, 8, 22, 7, 43, tzinfo=timezone.utc),
        "nested": {"values": [1, 2, 3], "tuple": ("a", b"b")},
    }

    with Memory(path) as memory:
        receipt = memory.remember(original)

    with Memory(path) as memory:
        recalled = memory.recall(receipt.memory_id)

    assert recalled == original
