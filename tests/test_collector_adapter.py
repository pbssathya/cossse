from cossse.adapters import CollectorAdapter
from cossse.flow import DispositionStatus, Flow, Meaning


def test_collector_adapter_uses_native_collector_contract_unchanged():
    calls = []

    def existing_collector(domain_path, source, store=True, requester=None):
        calls.append((domain_path, source, store, requester))
        return {
            "report_version": "1.0.0",
            "execution": {"status": "success", "events": []},
            "data": {"parsed": {"value": 42}},
        }

    meaning = Meaning(
        body={
            "need": "collect",
            "domain_path": "games/chance/lottery/kerala",
            "source": "75356",
            "store": False,
            "requester": "lakshmi",
        }
    )

    disposition = Flow().encounter(meaning, [CollectorAdapter(existing_collector)])

    assert disposition.status is DispositionStatus.CLAIMED
    assert calls == [
        ("games/chance/lottery/kerala", "75356", False, "lakshmi")
    ]
    feedback = disposition.feedback[0]
    assert feedback.caused_by == meaning.meaning_id
    assert feedback.body["experience"] == "capability_attempt"
    assert feedback.body["capability"] == "collect"
    assert feedback.body["outcome"]["report_version"] == "1.0.0"


def test_collector_adapter_ignores_non_collection_meaning():
    called = False

    def existing_collector(*args, **kwargs):
        nonlocal called
        called = True
        return {}

    meaning = Meaning(body={"need": "write-caption", "text": "hello"})
    disposition = Flow().encounter(meaning, [CollectorAdapter(existing_collector)])

    assert disposition.status is DispositionStatus.UNCLAIMED
    assert called is False
