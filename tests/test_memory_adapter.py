from __future__ import annotations

from cossse.adapters.memory import MemoryAdapter
from cossse.flow import DispositionStatus, Flow, Meaning
from cossse.memory import Memory


def test_memory_adapter_claims_experience_and_ignores_other_meaning(tmp_path):
    path = tmp_path / "memory.db"
    experience = Meaning(
        body={
            "experience": "capability_attempt",
            "capability": "collect",
            "outcome": {"data": {"raw": b"abc"}},
        },
        caused_by="meaning_need",
    )
    unrelated = Meaning(body={"need": "compose", "text": "hello"})

    with Memory(path) as memory:
        adapter = MemoryAdapter(memory)
        claimed = Flow().encounter(experience, adapters=(adapter,))
        ignored = Flow().encounter(unrelated, adapters=(adapter,))
        memory_id = claimed.feedback[0].body["memory_id"]

    assert claimed.status is DispositionStatus.CLAIMED
    assert ignored.status is DispositionStatus.UNCLAIMED

    with Memory(path) as memory:
        recalled = memory.recall(memory_id)

    assert recalled["meaning_id"] == experience.meaning_id
    assert recalled["caused_by"] == "meaning_need"
    assert recalled["body"] == experience.body


def test_memory_adapter_discovers_then_recalls_after_restart(tmp_path):
    path = tmp_path / "memory.db"
    experience = Meaning(
        body={
            "experience": "capability_attempt",
            "capability": "collect",
            "outcome": {
                "request": {
                    "domain_path": "games/chance/lottery/kerala",
                    "source": "75356",
                },
                "data": {"raw": b"real-shape-bytes"},
            },
        }
    )

    with Memory(path) as memory:
        preserved = Flow().encounter(experience, adapters=(MemoryAdapter(memory),))
        original_id = preserved.feedback[0].body["memory_id"]

    # New process/lifetime: the caller intentionally does not retain original_id.
    with Memory(path) as memory:
        adapter = MemoryAdapter(memory)
        discovered = Flow().encounter(
            Meaning(body={"need": "discover_preserved_experiences"}),
            adapters=(adapter,),
        )

        receipts = discovered.feedback[0].body["receipts"]
        discovered_id = receipts[0]["memory_id"]

        recalled = Flow().encounter(
            Meaning(
                body={
                    "need": "recall_preserved_experience",
                    "memory_id": discovered_id,
                }
            ),
            adapters=(adapter,),
        )

    assert discovered.status is DispositionStatus.CLAIMED
    assert recalled.status is DispositionStatus.CLAIMED
    assert discovered_id == original_id
    value = recalled.feedback[0].body["value"]
    assert value["body"] == experience.body
