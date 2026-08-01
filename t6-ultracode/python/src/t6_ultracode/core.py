from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import cmath
import itertools
import json
import math
from typing import Any, Sequence

DIGITS = tuple(range(1, 10))
PERMUTATIONS = tuple(itertools.permutations((0, 1, 2)))
SLOPES = {"X": 2, "Y": 5, "Z": 8}


def residue(d: int) -> int:
    if d not in DIGITS:
        raise ValueError("display digit must be 1..9")
    return d % 9


def display(r: int) -> int:
    return 9 if r % 9 == 0 else r % 9


def validate_triple(triple: Sequence[int]) -> tuple[int, int, int]:
    if len(triple) != 3:
        raise ValueError("triple must contain exactly three digits")
    out = tuple(int(x) for x in triple)
    if any(x not in DIGITS for x in out):
        raise ValueError("triple digits must be in 1..9")
    return out  # type: ignore[return-value]


def z9_add(a: int, b: int) -> int:
    return display(residue(a) + residue(b))


def z9_sub(a: int, b: int) -> int:
    return display(residue(a) - residue(b))


def z9_neg(a: int) -> int:
    return display(-residue(a))


def z9_mul(a: int, b: int) -> int:
    return display(residue(a) * residue(b))


def z9_unit_inverse(a: int) -> int:
    r = residue(a)
    if math.gcd(r, 9) != 1:
        raise ValueError(f"{a} is not a unit in Z9")
    return display(pow(r, -1, 9))


def toric_add(triple: Sequence[int], vector: Sequence[int]) -> tuple[int, int, int]:
    t = validate_triple(triple)
    if len(vector) != 3:
        raise ValueError("vector must have length 3")
    return tuple(display(residue(t[i]) + int(vector[i])) for i in range(3))  # type: ignore[return-value]


def complement(triple: Sequence[int]) -> tuple[int, int, int]:
    return tuple(z9_neg(x) for x in validate_triple(triple))  # type: ignore[return-value]


def permute(triple: Sequence[int], permutation: Sequence[int]) -> tuple[int, int, int]:
    t = validate_triple(triple)
    p = tuple(int(x) for x in permutation)
    if p not in PERMUTATIONS:
        raise ValueError("permutation must be one of the six permutations of 0,1,2")
    return (t[p[0]], t[p[1]], t[p[2]])


def encode_index(triple: Sequence[int]) -> int:
    i, j, k = validate_triple(triple)
    return (i - 1) * 81 + (j - 1) * 9 + (k - 1)


def decode_index(index: int) -> tuple[int, int, int]:
    idx = int(index)
    if not 0 <= idx < 729:
        raise ValueError("index must be in 0..728")
    return (idx // 81 + 1, (idx // 9) % 9 + 1, idx % 9 + 1)


def split_six_trits(triple: Sequence[int]) -> tuple[int, int, int, int, int, int]:
    out: list[int] = []
    for d in validate_triple(triple):
        # Positional chart codec uses d-1 and is distinct from Z9 arithmetic where 9->0.
        out.extend(divmod(d - 1, 3))
    return tuple(out)  # type: ignore[return-value]


def join_six_trits(trits: Sequence[int]) -> tuple[int, int, int]:
    if len(trits) != 6 or any(int(x) not in (0, 1, 2) for x in trits):
        raise ValueError("six trits must each be 0,1,2")
    return tuple(3 * int(trits[n]) + int(trits[n + 1]) + 1 for n in (0, 2, 4))  # type: ignore[return-value]


def equality_class(triple: Sequence[int]) -> str:
    unique = len(set(validate_triple(triple)))
    return {1: "diagonal", 2: "exactly_two_equal", 3: "all_distinct"}[unique]


def fixed_i_atlas(triple: Sequence[int]) -> tuple[int, int]:
    i, j, k = validate_triple(triple)
    i1, i0 = divmod(i - 1, 3)
    j1, j0 = divmod(j - 1, 3)
    k1, k0 = divmod(k - 1, 3)
    return 9 * i1 + 3 * i0 + j1, 9 * j0 + 3 * k1 + k0


def high_low_atlas(triple: Sequence[int]) -> tuple[int, int]:
    trits = split_six_trits(triple)
    return 9 * trits[0] + 3 * trits[2] + trits[4], 9 * trits[1] + 3 * trits[3] + trits[5]


def arithmetic_atlas(triple: Sequence[int]) -> tuple[int, int]:
    return divmod(encode_index(triple), 27)


def atlas_inverse(row: int, col: int, chart: str = "fixed_i") -> tuple[int, int, int]:
    r, c = int(row), int(col)
    if not (0 <= r < 27 and 0 <= c < 27):
        raise ValueError("row and col must be 0..26")
    if chart == "arithmetic":
        return decode_index(r * 27 + c)
    if chart == "high_low":
        h0, rem = divmod(r, 9)
        h1, h2 = divmod(rem, 3)
        l0, rem2 = divmod(c, 9)
        l1, l2 = divmod(rem2, 3)
        return join_six_trits((h0, l0, h1, l1, h2, l2))
    if chart == "fixed_i":
        i1, rem = divmod(r, 9)
        i0, j1 = divmod(rem, 3)
        j0, rem2 = divmod(c, 9)
        k1, k0 = divmod(rem2, 3)
        return join_six_trits((i1, i0, j1, j0, k1, k0))
    raise ValueError("chart must be fixed_i, high_low, or arithmetic")


def superplane_phase(triple: Sequence[int], family: str) -> int:
    i, j, k = [residue(x) for x in validate_triple(triple)]
    m = SLOPES[family.upper()]
    return (k - i - m * (j - i)) % 9


def superplane_member(triple: Sequence[int], family: str, phase: int = 0) -> bool:
    return superplane_phase(triple, family) == int(phase) % 9


def superplane_generate(family: str, phase: int = 0) -> list[tuple[int, int, int]]:
    m = SLOPES[family.upper()]
    q = int(phase) % 9
    return [(display(i), display(i + t), display(i + m * t + q)) for i in range(9) for t in range(9)]


def strict_union_180() -> list[tuple[int, int, int]]:
    union: set[tuple[int, int, int]] = set()
    for family in SLOPES:
        union.update(superplane_generate(family, 0))
    return sorted(x for x in union if len(set(x)) == 3)


def orbit(triple: Sequence[int], vector: Sequence[int], steps: int = 9) -> list[tuple[int, int, int]]:
    current = validate_triple(triple)
    result = [current]
    for _ in range(int(steps)):
        current = toric_add(current, vector)
        result.append(current)
    return result


def torus_angles(triple: Sequence[int]) -> tuple[float, float, float]:
    return tuple(2.0 * math.pi * residue(x) / 9.0 for x in validate_triple(triple))  # type: ignore[return-value]


def torus_embed(triple: Sequence[int]) -> list[tuple[float, float]]:
    return [(math.cos(a), math.sin(a)) for a in torus_angles(triple)]


def character(triple: Sequence[int], frequency: Sequence[int]) -> complex:
    t = [residue(x) for x in validate_triple(triple)]
    if len(frequency) != 3:
        raise ValueError("frequency must have length 3")
    exponent = sum(t[i] * int(frequency[i]) for i in range(3)) % 9
    return cmath.exp(2j * math.pi * exponent / 9)


def dft9(values: Sequence[complex]) -> list[complex]:
    if len(values) != 9:
        raise ValueError("DFT input must have length 9")
    omega = cmath.exp(-2j * math.pi / 9)
    return [sum(values[n] * omega ** (k * n) for n in range(9)) for k in range(9)]


def digitwise_fold(triple: Sequence[int]) -> dict[str, Any]:
    t = validate_triple(triple)
    c = complement(t)
    return {"original": t, "complement": c, "paired": "".join(map(str, t)) + ":" + "".join(map(str, c)), "residue_sums": [(residue(t[i]) + residue(c[i])) % 9 for i in range(3)]}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_hash(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def verify_all_charts() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for chart, fn in {"fixed_i": fixed_i_atlas, "high_low": high_low_atlas, "arithmetic": arithmetic_atlas}.items():
        cells = {fn(decode_index(i)) for i in range(729)}
        result[chart] = {"count": len(cells), "bijective": len(cells) == 729, "center_555": fn((5, 5, 5))}
    return result


@dataclass(frozen=True)
class T6State:
    triple: tuple[int, int, int]

    @property
    def index(self) -> int:
        return encode_index(self.triple)

    @property
    def trits(self) -> tuple[int, int, int, int, int, int]:
        return split_six_trits(self.triple)

    def as_dict(self) -> dict[str, Any]:
        return {"triple": self.triple, "index": self.index, "six_trits": self.trits, "equality_class": equality_class(self.triple), "charts": {"fixed_i": fixed_i_atlas(self.triple), "high_low": high_low_atlas(self.triple), "arithmetic": arithmetic_atlas(self.triple)}, "phases": {f: superplane_phase(self.triple, f) for f in SLOPES}, "angles": torus_angles(self.triple)}
