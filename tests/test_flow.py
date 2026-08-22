from datetime import timedelta

from cossse.flow import (
    CapabilityResult,
    DispositionStatus,
    Flow,
    Match,
    Meaning,
)
from cossse.flow.contracts import utcnow


class MatchingAdapter:
    def __init__(self):
        self.calls = 0

    def recognize(self, meaning: Meaning) -> Match:
        return Match(meaning.body.get("need") == "demo")

    def act(self, meaning: Meaning) -> CapabilityResult:
        self.calls += 1
        return CapabilityResult(
            feedback=(Meaning(body={"result": "done"}, caused_by=meaning.meaning_id),)
        )


class AlsoMatchingAdapter(MatchingAdapter):
    pass


def test_one_alignment_claims_and_returns_feedback():
    adapter = MatchingAdapter()
    meaning = Meaning(body={"need": "demo"})

    disposition = Flow().encounter(meaning, [adapter])

    assert disposition.status is DispositionStatus.CLAIMED
    assert disposition.aligned_count == 1
    assert adapter.calls == 1
    assert disposition.feedback[0].caused_by == meaning.meaning_id


def test_unrelated_meaning_passes_unclaimed():
    adapter = MatchingAdapter()
    meaning = Meaning(body={"need": "something-else"})

    disposition = Flow().encounter(meaning, [adapter])

    assert disposition.status is DispositionStatus.UNCLAIMED
    assert adapter.calls == 0


def test_multiple_alignments_are_surfaced_not_secretly_selected():
    first = MatchingAdapter()
    second = AlsoMatchingAdapter()
    meaning = Meaning(body={"need": "demo"})

    disposition = Flow().encounter(meaning, [first, second])

    assert disposition.status is DispositionStatus.CONTESTED
    assert disposition.aligned_count == 2
    assert first.calls == 0
    assert second.calls == 0


def test_expired_meaning_is_not_acted_on():
    adapter = MatchingAdapter()
    meaning = Meaning(
        body={"need": "demo"},
        relevant_until=utcnow() - timedelta(seconds=1),
    )

    disposition = Flow().encounter(meaning, [adapter])

    assert disposition.status is DispositionStatus.EXPIRED
    assert adapter.calls == 0
