"""Stable-looking boundaries for the first Flow experiment.

These contracts intentionally avoid application names and receiver identities.
Meaning carries content. Capability adapters decide whether that content aligns
with what they can bridge to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class Meaning:
    """A unit of meaning moving through Flow.

    ``body`` is intentionally opaque to Flow. Flow does not interpret it.
    ``caused_by`` links newly produced meaning to an earlier meaning without
    naming a sender or receiver.
    """

    body: Mapping[str, Any]
    meaning_id: str = field(default_factory=lambda: f"meaning_{uuid4().hex}")
    created_at: datetime = field(default_factory=utcnow)
    relevant_until: datetime | None = None
    caused_by: str | None = None

    def is_relevant(self, at: datetime | None = None) -> bool:
        if self.relevant_until is None:
            return True
        instant = at or utcnow()
        return instant <= self.relevant_until


@dataclass(frozen=True, slots=True)
class Match:
    """An adapter's assessment of alignment with a Meaning."""

    aligned: bool
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityResult:
    """What returns from a temporary capability coupling."""

    feedback: tuple[Meaning, ...] = ()
    details: Mapping[str, Any] = field(default_factory=dict)


class DispositionStatus(str, Enum):
    CLAIMED = "claimed"
    UNCLAIMED = "unclaimed"
    CONTESTED = "contested"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class Disposition:
    """What happened to one Meaning during one Flow encounter."""

    meaning_id: str
    status: DispositionStatus
    observed_at: datetime = field(default_factory=utcnow)
    aligned_count: int = 0
    feedback: tuple[Meaning, ...] = ()
    notes: tuple[str, ...] = ()


@runtime_checkable
class CapabilityAdapter(Protocol):
    """Temporary boundary between Flow meaning and a native capability.

    The adapter is not the capability and Flow does not route by adapter name.
    """

    def recognize(self, meaning: Meaning) -> Match:
        """Return whether this adapter can safely bridge the meaning."""

    def act(self, meaning: Meaning) -> CapabilityResult:
        """Temporarily couple, invoke the capability, return feedback, detach."""
