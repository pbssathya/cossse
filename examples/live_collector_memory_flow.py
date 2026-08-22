"""Prove a real Collector experience can be discovered from Memory after restart.

The restart side is intentionally not handed the memory_id produced during
preservation. It first discovers Memory receipts through Flow, then recalls the
candidate experiences through Flow. Relevance is decided by the consumer, not
by Memory.
"""

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
    report = experience.body.get("outcome") or {}
    execution = report.get("execution") or {}
    data = report.get("data") or {}
    raw = data.get("raw")

    with tempfile.TemporaryDirectory() as temp_dir:
        memory_path = Path(temp_dir) / "memory.db"

        with Memory(memory_path) as memory:
            preserved = Flow().encounter(experience, adapters=(MemoryAdapter(memory),))
            if preserved.status is not DispositionStatus.CLAIMED or not preserved.feedback:
                return 3
            preservation_status = preserved.status.value

        # Restart boundary. The memory_id from preservation is deliberately not
        # carried across. Discovery begins only from the preserved Memory itself.
        with Memory(memory_path) as memory:
            adapter = MemoryAdapter(memory)
            discovered = Flow().encounter(
                Meaning(body={"need": "discover_preserved_experiences"}),
                adapters=(adapter,),
            )
            if discovered.status is not DispositionStatus.CLAIMED or not discovered.feedback:
                return 4

            receipts = discovered.feedback[0].body.get("receipts") or ()
            relevant = None
            discovered_memory_id = None

            for receipt in receipts:
                candidate_id = str(receipt["memory_id"])
                recalled = Flow().encounter(
                    Meaning(
                        body={
                            "need": "recall_preserved_experience",
                            "memory_id": candidate_id,
                        }
                    ),
                    adapters=(adapter,),
                )
                if recalled.status is not DispositionStatus.CLAIMED or not recalled.feedback:
                    continue

                value = recalled.feedback[0].body.get("value") or {}
                body = value.get("body") or {}
                candidate_report = body.get("outcome") or {}
                request = candidate_report.get("request") or {}
                if (
                    request.get("domain_path") == domain_path
                    and str(request.get("source")) == str(source)
                ):
                    relevant = value
                    discovered_memory_id = candidate_id
                    break

    if relevant is None:
        return 5

    same_experience = (
        relevant["meaning_id"] == experience.meaning_id
        and relevant["caused_by"] == experience.caused_by
        and relevant["body"] == experience.body
    )

    print(
        json.dumps(
            {
                "collection_disposition": collected.status.value,
                "memory_disposition": preservation_status,
                "discovery_disposition": discovered.status.value,
                "discovered_receipts": len(receipts),
                "discovered_memory_id": discovered_memory_id,
                "collector_status": execution.get("status"),
                "raw_bytes": len(raw) if isinstance(raw, bytes) else None,
                "relevant_experience_found": True,
                "faithful_after_restart": same_experience,
                "prior_memory_id_required": False,
            },
            indent=2,
        )
    )
    return 0 if same_experience else 6


if __name__ == "__main__":
    raise SystemExit(run("games/chance/lottery/kerala", "75356"))
