"""Small deterministic codec for Memory v0.1.

The codec preserves the value shapes needed by real Collector reports without
using pickle. Unsupported values fail loudly instead of being silently coerced.
"""

from __future__ import annotations

import base64
import json
from datetime import date, datetime
from typing import Any, Mapping

_TAG = "__cossse_type__"


def _encode(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return {_TAG: "bytes", "data": base64.b64encode(value).decode("ascii")}
    if isinstance(value, bytearray):
        return {_TAG: "bytearray", "data": base64.b64encode(bytes(value)).decode("ascii")}
    if isinstance(value, datetime):
        return {_TAG: "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {_TAG: "date", "value": value.isoformat()}
    if isinstance(value, tuple):
        return {_TAG: "tuple", "items": [_encode(item) for item in value]}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, Mapping):
        return {
            _TAG: "mapping",
            "items": [[_encode(key), _encode(item)] for key, item in value.items()],
        }
    raise TypeError(f"Memory v0.1 cannot preserve value of type {type(value).__name__}")


def _decode(value: Any) -> Any:
    if not isinstance(value, (dict, list)):
        return value
    if isinstance(value, list):
        return [_decode(item) for item in value]

    kind = value.get(_TAG)
    if kind == "bytes":
        return base64.b64decode(value["data"])
    if kind == "bytearray":
        return bytearray(base64.b64decode(value["data"]))
    if kind == "datetime":
        return datetime.fromisoformat(value["value"])
    if kind == "date":
        return date.fromisoformat(value["value"])
    if kind == "tuple":
        return tuple(_decode(item) for item in value["items"])
    if kind == "mapping":
        return {_decode(key): _decode(item) for key, item in value["items"]}
    raise ValueError("Memory payload contains an unknown encoded type")


def dumps(value: Any) -> str:
    """Encode a supported value into deterministic JSON text."""

    return json.dumps(_encode(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def loads(payload: str) -> Any:
    """Restore a value previously encoded by :func:`dumps`."""

    return _decode(json.loads(payload))
