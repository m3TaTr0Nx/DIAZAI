from __future__ import annotations
import hashlib
import json
from typing import Any

ZERO_HASH = "0" * 64


def canonical_bytes(value: Any) -> bytes:
    """Deterministic JSON shared by Python, Node, receipts, and conformance.

    Business schemas should use integers or normalized strings for non-integral
    quantities to avoid language-specific floating-point render differences.
    """
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, (bytes, bytearray)) else canonical_bytes(value)
    return hashlib.sha256(raw).hexdigest()


def state_index(value: Any) -> int:
    return int(sha256_hex(value)[:16], 16) % 729


def state_digits(index: int) -> tuple[int, int, int]:
    if not 0 <= index < 729:
        raise ValueError("state index must be in [0, 728]")
    return (index // 81 + 1, (index // 9) % 9 + 1, index % 9 + 1)


def index_from_digits(i: int, j: int, k: int) -> int:
    if not all(1 <= d <= 9 for d in (i, j, k)):
        raise ValueError("digits must be in [1, 9]")
    return (i - 1) * 81 + (j - 1) * 9 + (k - 1)


def semantic_projection(event: dict[str, Any]) -> dict[str, Any]:
    """Business-comparison projection excluding run identity and clock fields."""
    return {
        key: event[key]
        for key in sorted(event)
        if key not in {"trace_id", "event_id", "timestamp"}
    }
