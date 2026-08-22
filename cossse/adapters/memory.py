"""Flow boundary for the native Memory capability.

Memory itself remains unaware of Flow. This adapter recognizes preservation,
discovery, and recall meanings, temporarily couples them to Memory, and detaches
after the action completes.
"""

from __future__ import annotations

from cossse.flow import CapabilityResult, Match, Meaning
from cossse.memory import Memory


_DISCOVER_NEED = "discover_preserved_experiences"
_RECALL_NEED = "recall_preserved_experience"


class MemoryAdapter:
    """Temporary bridge between Flow meaning and native Memory."""

    def __init__(self, memory: Memory):
        self._memory = memory

    def recognize(self, meaning: Meaning) -> Match:
        body = meaning.body

        if "experience" in body:
            return Match(True, "Meaning represents preservable experience.")

        if body.get("need") == _DISCOVER_NEED:
            return Match(True, "Meaning asks which preserved experiences exist.")

        if body.get("need") == _RECALL_NEED:
            if not body.get("memory_id"):
                return Match(False, "Recall meaning is missing memory_id.")
            return Match(True, "Meaning asks to recall one preserved experience.")

        return Match(False)

    def act(self, meaning: Meaning) -> CapabilityResult:
        body = meaning.body

        if "experience" in body:
            return self._preserve(meaning)

        if body.get("need") == _DISCOVER_NEED:
            return self._discover(meaning)

        if body.get("need") == _RECALL_NEED:
            return self._recall(meaning)

        return CapabilityResult()

    def _preserve(self, meaning: Meaning) -> CapabilityResult:
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

    def _discover(self, meaning: Meaning) -> CapabilityResult:
        receipts = tuple(
            {
                "memory_id": receipt.memory_id,
                "stored_at": receipt.stored_at,
                "sha256": receipt.sha256,
            }
            for receipt in self._memory.receipts()
        )
        feedback = Meaning(
            body={
                "memory_event": "discovered",
                "receipts": receipts,
            },
            caused_by=meaning.meaning_id,
        )
        return CapabilityResult(feedback=(feedback,))

    def _recall(self, meaning: Meaning) -> CapabilityResult:
        memory_id = str(meaning.body["memory_id"])
        value = self._memory.recall(memory_id)
        feedback = Meaning(
            body={
                "memory_event": "recalled",
                "memory_id": memory_id,
                "value": value,
            },
            caused_by=meaning.meaning_id,
        )
        return CapabilityResult(feedback=(feedback,))
