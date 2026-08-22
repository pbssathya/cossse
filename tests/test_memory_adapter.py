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
