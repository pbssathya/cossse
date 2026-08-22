"""Prove a real Collector experience can flow into Memory and survive restart."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from collector.collect import collect

from cossse.adapters.collector import CollectorAdapter
from cossse.adapters.memory import MemoryAdapter
from cossse.flow import DispositionStatus, Flow, Meaning
from cossse.memory import Memory


def run(domain_path: str, source: str) -> int:
    need = Meaning(
        body={
            "need": "collect",
            "domain_path": domain_path,
            "source": source,
            "store": False,
        }
    )
    collected = Flow().encounter(need, adapters=(CollectorAdapter(collect),))
    if collected.status is not DispositionStatus.CLAIMED or not collected.feedback:
        return 2

    experience = collected.feedback[0]
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_path = Path(temp_dir) / "memory.db"

        with Memory(memory_path) as memory:
            preserved = Flow().encounter(experience, adapters=(MemoryAdapter(memory),))
            if preserved.status is not DispositionStatus.CLAIMED or not preserved.feedback:
                return 3
            receipt_meaning = preserved.feedback[0]
            memory_id = str(receipt_meaning.body["memory_id"])

        # New Memory instance: proves persistence across a restart boundary.
        with Memory(memory_path) as memory:
            recalled = memory.recall(memory_id)

    same_experience = (
        recalled["meaning_id"] == experience.meaning_id
        and recalled["caused_by"] == experience.caused_by
        and recalled["body"] == experience.body
    )
    report = experience.body.get("outcome") or {}
    execution = report.get("execution") or {}
    data = report.get("data") or {}
    raw = data.get("raw")

    print(
        json.dumps(
            {
                "collection_disposition": collected.status.value,
                "memory_disposition": preserved.status.value,
                "memory_id": memory_id,
                "collector_status": execution.get("status"),
                "raw_bytes": len(raw) if isinstance(raw, bytes) else None,
                "faithful_after_restart": same_experience,
            },
            indent=2,
        )
    )
    return 0 if same_experience else 4


if __name__ == "__main__":
    raise SystemExit(run("games/chance/lottery/kerala", "75352"))
