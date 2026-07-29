from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import gcd


class Relation(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"
    ADD = "ADD"
    HINGE = "HINGE"


RELATIONS = tuple(Relation)
SLOPES = {Relation.X: 2, Relation.Y: 5, Relation.Z: 8}


def mod(v: int, m: int) -> int:
    if m < 2:
        raise ValueError("modulus must be >= 2")
    return int(v) % int(m)


def toric_distance(v: int, m: int) -> int:
    r = mod(v, m)
    return min(r, m - r)


def residual(relation: Relation | str, i: int, j: int, k: int, m: int) -> int:
    relation = Relation(relation)
    if relation in SLOPES:
        s = SLOPES[relation]
        return mod((s - 1) * i - s * j + k, m)
    if relation is Relation.ADD:
        return mod(i + k - 2 * j, m)
    if relation is Relation.HINGE:
        return mod(i * k - j * j, m)
    raise ValueError(relation)


def holds(relation: Relation | str, i: int, j: int, k: int, m: int) -> bool:
    return residual(relation, i, j, k, m) == 0


def relation_vector(i: int, j: int, k: int, m: int) -> tuple[int, ...]:
    return tuple(residual(r, i, j, k, m) for r in RELATIONS)


def relation_distance_vector(i: int, j: int, k: int, m: int) -> tuple[int, ...]:
    return tuple(toric_distance(residual(r, i, j, k, m), m) for r in RELATIONS)


def ring_type(x: int, m: int) -> str:
    r = mod(x, m)
    if r == 0:
        return "zero"
    return "unit" if gcd(r, m) == 1 else "zero_divisor"


@dataclass(frozen=True)
class RelationSpec:
    relation: Relation
    family: str
    expression: str
    exact: bool
    general_modulus: bool


SPECS = {
    Relation.X: RelationSpec(Relation.X, "linear_superplane", "i - 2j + k = 0 (mod m)", True, True),
    Relation.Y: RelationSpec(Relation.Y, "linear_superplane", "4i - 5j + k = 0 (mod m)", True, True),
    Relation.Z: RelationSpec(Relation.Z, "linear_superplane", "7i - 8j + k = 0 (mod m)", True, True),
    Relation.ADD: RelationSpec(Relation.ADD, "additive_midpoint", "i + k - 2j = 0 (mod m)", True, True),
    Relation.HINGE: RelationSpec(Relation.HINGE, "multiplicative_hinge", "ik - j^2 = 0 (mod m)", True, True),
}
