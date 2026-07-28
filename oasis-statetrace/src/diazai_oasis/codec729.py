from __future__ import annotations

import hashlib
from typing import Iterable

from .models import AtlasAddress, OasisAction, OasisDomain, OasisEvent

DOMAIN_DIGIT = {
    OasisDomain.AVATAR: 1,
    OasisDomain.INVENTORY: 2,
    OasisDomain.QUEST: 3,
    OasisDomain.KARMA: 4,
    OasisDomain.GEO: 5,
    OasisDomain.NFT: 6,
    OasisDomain.PROVIDER: 7,
    OasisDomain.AGENT: 8,
    OasisDomain.SYSTEM: 9,
}

ACTION_DIGIT = {
    OasisAction.START: 1,
    OasisAction.READ: 2,
    OasisAction.UPDATE: 3,
    OasisAction.COMPLETE: 4,
    OasisAction.ADD: 5,
    OasisAction.USE: 6,
    OasisAction.TRANSFER: 7,
    OasisAction.COMPENSATE: 8,
    OasisAction.VERIFY: 9,
}


def _pair(n: int) -> tuple[int, int]:
    return divmod(n, 3)


def triple_to_index(i: int, j: int, k: int) -> int:
    if not all(1 <= d <= 9 for d in (i, j, k)):
        raise ValueError("digits must be in 1..9")
    return 81 * (i - 1) + 9 * (j - 1) + (k - 1)


def index_to_triple(index: int) -> tuple[int, int, int]:
    if not 0 <= index < 729:
        raise ValueError("index must be in 0..728")
    return index // 81 + 1, (index // 9) % 9 + 1, index % 9 + 1


def triple_to_trits(i: int, j: int, k: int) -> list[int]:
    out: list[int] = []
    for d in (i, j, k):
        out.extend(_pair(d - 1))
    return out


def trits_to_triple(trits: Iterable[int]) -> tuple[int, int, int]:
    ds = list(trits)
    if len(ds) != 6 or any(d not in (0, 1, 2) for d in ds):
        raise ValueError("expected six trits")
    return tuple(1 + 3 * ds[p] + ds[p + 1] for p in (0, 2, 4))  # type: ignore[return-value]


def entity_shard(entity_id: str, avatar_id: str = "anonymous") -> int:
    digest = hashlib.sha256(f"{avatar_id}|{entity_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 9 + 1


def _bank(i: int, j: int, k: int) -> str:
    if i == j == k:
        return "OMEGA_999" if i == 9 else "CORE_DIAGONAL"
    if i != j and j != k and i != k:
        return "CORE_DISTINCT"
    if i == j:
        return "SHELL_IJ"
    if j == k:
        return "SHELL_JK"
    return "SHELL_KI"


def address_for_digits(i: int, j: int, k: int) -> AtlasAddress:
    index = triple_to_index(i, j, k)
    ih, il = _pair(i - 1)
    jh, jl = _pair(j - 1)
    kh, kl = _pair(k - 1)
    row = 9 * ih + 3 * jh + kh
    col = 9 * il + 3 * jl + kl
    return AtlasAddress(
        i=i,
        j=j,
        k=k,
        scalar=100 * i + 10 * j + k,
        index729=index,
        trits6=[ih, il, jh, jl, kh, kl],
        row27=row,
        col27=col,
        bank=_bank(i, j, k),
    )


def address_for_event(event: OasisEvent) -> AtlasAddress:
    return address_for_digits(
        DOMAIN_DIGIT[event.domain],
        ACTION_DIGIT[event.action],
        entity_shard(event.entity_id, event.avatar_id),
    )
