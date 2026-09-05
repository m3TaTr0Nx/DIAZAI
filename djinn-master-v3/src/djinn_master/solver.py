from __future__ import annotations
from dataclasses import asdict, dataclass
from math import gcd
from time import perf_counter_ns
import hashlib
import json

from .relations import Relation, SLOPES, holds, mod, residual


def solve_linear_congruence(a: int, b: int, m: int) -> tuple[int, ...]:
    """Solve a*x = b (mod m), returning every residue in canonical order."""
    a, b, m = mod(a, m), mod(b, m), int(m)
    g = gcd(a, m)
    if b % g:
        return ()
    ar, br, mr = a // g, b // g, m // g
    x0 = 0 if mr == 1 else (pow(ar, -1, mr) * br) % mr
    return tuple(sorted((x0 + t * mr) % m for t in range(g)))


def _linear_coefficients(relation: Relation) -> tuple[int, int, int]:
    if relation in SLOPES:
        s = SLOPES[relation]
        return (s - 1, -s, 1)
    if relation is Relation.ADD:
        return (1, -2, 1)
    raise ValueError(f"{relation} is not linear")


def complete_exact(relation: Relation | str, values: tuple[int | None, int | None, int | None], m: int) -> tuple[int, ...]:
    relation = Relation(relation)
    if sum(v is None for v in values) != 1:
        raise ValueError("exactly one coordinate must be None")
    mask = values.index(None)
    known = [0 if v is None else mod(int(v), m) for v in values]
    i, j, k = known
    if relation is Relation.HINGE:
        if mask == 0:
            return solve_linear_congruence(k, j * j, m)
        if mask == 2:
            return solve_linear_congruence(i, j * j, m)
        target = mod(i * k, m)
        return tuple(x for x in range(m) if mod(x * x, m) == target)
    coeffs = _linear_coefficients(relation)
    rhs = -sum(coeffs[q] * known[q] for q in range(3) if q != mask)
    return solve_linear_congruence(coeffs[mask], rhs, m)


def complete_bruteforce(relation: Relation | str, values: tuple[int | None, int | None, int | None], m: int) -> tuple[int, ...]:
    relation = Relation(relation)
    if sum(v is None for v in values) != 1:
        raise ValueError("exactly one coordinate must be None")
    mask = values.index(None)
    out: list[int] = []
    for candidate in range(m):
        row = list(values)
        row[mask] = candidate
        if holds(relation, int(row[0]), int(row[1]), int(row[2]), m):
            out.append(candidate)
    return tuple(out)


@dataclass(frozen=True)
class CompletionCertificate:
    schema: str
    relation: str
    modulus: int
    values: tuple[int | None, int | None, int | None]
    masked_axis: int
    candidates: tuple[int, ...]
    ambiguous: bool
    verified: bool
    residuals: tuple[int, ...]
    solver: str
    elapsed_ns: int
    digest: str

    def to_dict(self) -> dict:
        return asdict(self)


def complete(relation: Relation | str, values: tuple[int | None, int | None, int | None], m: int) -> CompletionCertificate:
    relation = Relation(relation)
    start = perf_counter_ns()
    candidates = complete_exact(relation, values, m)
    elapsed = perf_counter_ns() - start
    mask = values.index(None)
    residuals = []
    verified = True
    for candidate in candidates:
        row = list(values)
        row[mask] = candidate
        r = residual(relation, int(row[0]), int(row[1]), int(row[2]), m)
        residuals.append(r)
        verified &= r == 0
    payload = {
        "relation": relation.value,
        "modulus": m,
        "values": values,
        "masked_axis": mask,
        "candidates": candidates,
        "verified": verified,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=list).encode()).hexdigest()
    return CompletionCertificate(
        schema="diazai.djinn-completion-certificate.v1",
        relation=relation.value,
        modulus=int(m),
        values=values,
        masked_axis=mask,
        candidates=candidates,
        ambiguous=len(candidates) != 1,
        verified=bool(verified),
        residuals=tuple(residuals),
        solver="closed_form_linear_congruence+exact_quadratic_fiber",
        elapsed_ns=elapsed,
        digest=digest,
    )
