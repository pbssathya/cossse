"""Run one real Flow encounter against an installed Collector capability.

This script is intentionally domain-agnostic. It receives a Collector domain path
and source from the command line, expresses the need as Meaning, and lets Flow
encounter a CollectorAdapter. Collector itself remains unaware of Flow.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from collector.collect import collect

from cossse.adapters.collector import CollectorAdapter
from cossse.flow import DispositionStatus, Flow, Meaning


def _report_summary(report: dict[str, Any] | None) -> dict[str, Any]:
    if report is None:
        return {"report": None}

    execution = report.get("execution") or {}
    metadata = report.get("metadata") or {}
    provenance = report.get("provenance") or {}
    return {
        "report_version": report.get("report_version"),
        "status": execution.get("status"),
        "events": execution.get("events", []),
        "connector_used": execution.get("connector_used"),
        "collected_at": metadata.get("collected_at"),
        "source_url": metadata.get("source_url"),
        "run_id": provenance.get("run_id"),
        "collector_version": provenance.get("collector_version"),
    }


def run(domain_path: str, source: str, *, store: bool = False) -> int:
    meaning = Meaning(
        body={
            "need": "collect",
            "domain_path": domain_path,
            "source": source,
            "store": store,
        }
    )

    disposition = Flow().encounter(
        meaning,
        adapters=(CollectorAdapter(collect),),
    )

    print(
        json.dumps(
            {
                "meaning_id": meaning.meaning_id,
                "disposition": disposition.status.value,
                "aligned_count": disposition.aligned_count,
                "notes": disposition.notes,
            },
            indent=2,
            default=str,
        )
    )

    if disposition.status is not DispositionStatus.CLAIMED:
        return 2

    if not disposition.feedback:
        print("Flow was claimed but produced no feedback.")
        return 3

    feedback = disposition.feedback[0]
    report = feedback.body.get("outcome")
    print(json.dumps(_report_summary(report), indent=2, default=str))

    if not isinstance(report, dict):
        return 4

    status = (report.get("execution") or {}).get("status")
    return 0 if status in {"success", "partial"} else 5


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a real collection meaning through COSsse Flow."
    )
    parser.add_argument("domain_path", help="Collector domain path")
    parser.add_argument("source", help="Collector source identifier")
    parser.add_argument(
        "--store",
        action="store_true",
        help="Allow Collector to persist the collected result",
    )
    args = parser.parse_args()
    return run(args.domain_path, args.source, store=args.store)


if __name__ == "__main__":
    raise SystemExit(main())
