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


def test_memory_can_enumerate_receipts_without_exposing_payloads(tmp_path):
    path = tmp_path / "memory.db"

    with Memory(path) as memory:
        first = memory.remember({"kind": "one", "secret_payload": b"first"})
        second = memory.remember({"kind": "two", "secret_payload": b"second"})

    with Memory(path) as memory:
        receipts = memory.receipts()

    assert [receipt.memory_id for receipt in receipts] == [
        first.memory_id,
        second.memory_id,
    ]
    assert receipts[0].sha256 == first.sha256
    assert receipts[1].sha256 == second.sha256
    assert all(not hasattr(receipt, "payload") for receipt in receipts)
