"""Minimal Flow runtime for the first COSsse experiment."""

from __future__ import annotations

from collections.abc import Iterable

from .contracts import (
    CapabilityAdapter,
    Disposition,
    DispositionStatus,
    Meaning,
)


class Flow:
    """Present meaning to independent capability boundaries.

    Flow does not understand the meaning, choose by identity, or interpret a
    capability's outcome. In this first experiment, exactly one alignment is
    required for automatic action. Multiple alignments are surfaced rather
    than silently resolved by a hidden dispatcher.
    """

    def encounter(
        self,
        meaning: Meaning,
        adapters: Iterable[CapabilityAdapter],
    ) -> Disposition:
        if not meaning.is_relevant():
            return Disposition(
                meaning_id=meaning.meaning_id,
                status=DispositionStatus.EXPIRED,
                notes=("Meaning was no longer relevant when encountered.",),
            )

        aligned: list[CapabilityAdapter] = []
        notes: list[str] = []

        for adapter in adapters:
            match = adapter.recognize(meaning)
            if match.aligned:
                aligned.append(adapter)
                if match.reason:
                    notes.append(match.reason)

        if not aligned:
            return Disposition(
                meaning_id=meaning.meaning_id,
                status=DispositionStatus.UNCLAIMED,
                aligned_count=0,
                notes=tuple(notes),
            )

        if len(aligned) > 1:
            return Disposition(
                meaning_id=meaning.meaning_id,
                status=DispositionStatus.CONTESTED,
                aligned_count=len(aligned),
                notes=tuple(notes),
            )

        result = aligned[0].act(meaning)
        return Disposition(
            meaning_id=meaning.meaning_id,
            status=DispositionStatus.CLAIMED,
            aligned_count=1,
            feedback=result.feedback,
            notes=tuple(notes),
        )
