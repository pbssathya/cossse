"""Flow boundary for an existing Collector-style callable.

Collector itself remains unaware of Flow. This adapter translates a collection
meaning into Collector's existing native call and places the report back into
Flow as new meaning.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from cossse.flow import CapabilityResult, Match, Meaning


CollectorCallable = Callable[..., dict[str, Any] | None]


class CollectorAdapter:
    """Temporary bridge to a Collector-compatible callable.

    Recognized meaning shape for this experiment::

        {
            "need": "collect",
            "domain_path": "games/chance/lottery/kerala",
            "source": "75356",
            "store": true,              # optional
            "requester": "lakshmi"     # optional provenance only
        }

    ``need`` expresses required capability; it is not a receiver identity.
    """

    def __init__(self, collect: CollectorCallable):
        self._collect = collect

    def recognize(self, meaning: Meaning) -> Match:
        body = meaning.body
        if body.get("need") != "collect":
            return Match(False)

        missing = [name for name in ("domain_path", "source") if not body.get(name)]
        if missing:
            return Match(False, f"Collection meaning missing: {', '.join(missing)}")

        return Match(True, "Meaning requires collection and contains a usable collection request.")

    def act(self, meaning: Meaning) -> CapabilityResult:
        body = meaning.body
        report = self._collect(
            str(body["domain_path"]),
            str(body["source"]),
            bool(body.get("store", True)),
            body.get("requester"),
        )

        feedback = Meaning(
            body={
                "experience": "capability_attempt",
                "capability": "collect",
                "outcome": report,
            },
            caused_by=meaning.meaning_id,
        )

        return CapabilityResult(feedback=(feedback,))
