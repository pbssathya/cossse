"""Flow boundary for the native Memory capability.

Memory itself remains unaware of Flow. This adapter recognizes preservable
experience meaning, temporarily couples it to Memory, and detaches after the
preservation action completes.
"""

from __future__ import annotations

from cossse.flow import CapabilityResult, Match, Meaning
from cossse.memory import Memory


class MemoryAdapter:
    """Temporary bridge from experience Meaning to Memory."""

    def __init__(self, memory: Memory):
        self._memory = memory

    def recognize(self, meaning: Meaning) -> Match:
        if "experience" not in meaning.body:
            return Match(False)
        return Match(True, "Meaning represents preservable experience.")

    def act(self, meaning: Meaning) -> CapabilityResult:
        preserved = {
            "meaning_id": meaning.meaning_id,
            "created_at": meaning.created_at,
            "relevant_until": meaning.relevant_until,
            "caused_by": meaning.caused_by,
            "body": meaning.body,
        }
        receipt = self._memory.remember(preserved)
        feedback = Meaning(
            body={
                "memory_event": "preserved",
                "memory_id": receipt.memory_id,
                "stored_at": receipt.stored_at,
                "sha256": receipt.sha256,
            },
            caused_by=meaning.meaning_id,
        )
        return CapabilityResult(feedback=(feedback,))
