from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import struct
from typing import Sequence

BALANCED_DIGITS = (-1, 0, 1)


def int_to_balanced_ternary(value: int) -> list[int]:
    n = int(value)
    if n == 0:
        return [0]
    out: list[int] = []
    while n:
        n, r = divmod(n, 3)
        if r == 2:
            r = -1
            n += 1
        out.append(r)
    return out[::-1]


def balanced_ternary_to_int(digits: Sequence[int]) -> int:
    total = 0
    for d in digits:
        if int(d) not in BALANCED_DIGITS:
            raise ValueError("balanced ternary digits must be -1,0,1")
        total = total * 3 + int(d)
    return total


def packed_trits_encode(digits: Sequence[int]) -> int:
    value = 0
    for d in digits:
        if int(d) not in BALANCED_DIGITS:
            raise ValueError("balanced trit must be -1,0,1")
        value = value * 3 + (int(d) + 1)
    return value


def packed_trits_decode(value: int, width: int) -> list[int]:
    n = int(value)
    if n < 0 or n >= 3 ** int(width):
        raise ValueError("packed value outside width")
    out = [0] * int(width)
    for i in range(int(width) - 1, -1, -1):
        n, r = divmod(n, 3)
        out[i] = r - 1
    return out


@dataclass(frozen=True)
class MixedRadixRational:
    """Exact p/(2^a 3^b) bridge between dyadic and triadic rational grids."""

    numerator: int
    two_exponent: int = 0
    three_exponent: int = 0

    def __post_init__(self) -> None:
        if self.two_exponent < 0 or self.three_exponent < 0:
            raise ValueError("exponents must be nonnegative")

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, (2 ** self.two_exponent) * (3 ** self.three_exponent))

    def normalize(self) -> "MixedRadixRational":
        n, a, b = self.numerator, self.two_exponent, self.three_exponent
        while a and n % 2 == 0:
            n //= 2
            a -= 1
        while b and n % 3 == 0:
            n //= 3
            b -= 1
        return MixedRadixRational(n, a, b)

    def add(self, other: "MixedRadixRational") -> "MixedRadixRational":
        a = max(self.two_exponent, other.two_exponent)
        b = max(self.three_exponent, other.three_exponent)
        n1 = self.numerator * (2 ** (a - self.two_exponent)) * (3 ** (b - self.three_exponent))
        n2 = other.numerator * (2 ** (a - other.two_exponent)) * (3 ** (b - other.three_exponent))
        return MixedRadixRational(n1 + n2, a, b).normalize()

    def mul(self, other: "MixedRadixRational") -> "MixedRadixRational":
        return MixedRadixRational(self.numerator * other.numerator, self.two_exponent + other.two_exponent, self.three_exponent + other.three_exponent).normalize()

    def as_dict(self) -> dict[str, object]:
        n = self.normalize()
        return {"numerator": n.numerator, "two_exponent": n.two_exponent, "three_exponent": n.three_exponent, "denominator": 2 ** n.two_exponent * 3 ** n.three_exponent, "fraction": f"{n.fraction.numerator}/{n.fraction.denominator}", "float": float(n.fraction)}

    @staticmethod
    def from_fraction(value: Fraction, max_two: int = 32, max_three: int = 32) -> "MixedRadixRational":
        den = value.denominator
        a = b = 0
        while den % 2 == 0 and a < max_two:
            den //= 2
            a += 1
        while den % 3 == 0 and b < max_three:
            den //= 3
            b += 1
        if den != 1:
            raise ValueError("fraction has prime factors other than 2 and 3")
        return MixedRadixRational(value.numerator, a, b).normalize()


# BTMR32 layout:
# [31] orientation; [30] domain; [29:28] kind; [27:22] signed ternary exponent;
# [21:2] twelve packed balanced trits; [1:0] checksum.
BTMR32_TRITS = 12
BTMR32_EXP_BIAS = 32


@dataclass(frozen=True)
class BTMR32:
    orientation: int
    domain: int
    kind: int
    exponent: int
    trits: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.orientation not in (0, 1) or self.domain not in (0, 1):
            raise ValueError("orientation and domain must be bits")
        if self.kind not in (0, 1, 2, 3):
            raise ValueError("kind must be 0..3")
        if not -32 <= self.exponent <= 31:
            raise ValueError("exponent must be -32..31")
        if len(self.trits) != BTMR32_TRITS or any(t not in BALANCED_DIGITS for t in self.trits):
            raise ValueError("BTMR32 requires twelve balanced trits")

    def pack(self) -> int:
        exp_raw = self.exponent + BTMR32_EXP_BIAS
        mantissa = packed_trits_encode(self.trits)
        checksum = (sum(t + 1 for t in self.trits) + self.orientation + self.domain + exp_raw) % 4
        return (self.orientation << 31) | (self.domain << 30) | (self.kind << 28) | (exp_raw << 22) | (mantissa << 2) | checksum

    def to_bytes(self) -> bytes:
        return struct.pack(">I", self.pack())

    @staticmethod
    def unpack(word: int, verify: bool = True) -> "BTMR32":
        w = int(word) & 0xFFFFFFFF
        orientation = (w >> 31) & 1
        domain = (w >> 30) & 1
        kind = (w >> 28) & 0b11
        exp_raw = (w >> 22) & 0b111111
        mantissa = (w >> 2) & ((1 << 20) - 1)
        if mantissa >= 3 ** BTMR32_TRITS:
            raise ValueError("invalid packed mantissa")
        trits = tuple(packed_trits_decode(mantissa, BTMR32_TRITS))
        obj = BTMR32(orientation, domain, kind, exp_raw - BTMR32_EXP_BIAS, trits)
        if verify:
            expected = (sum(t + 1 for t in trits) + orientation + domain + exp_raw) % 4
            if expected != (w & 0b11):
                raise ValueError("checksum mismatch")
        return obj

    @staticmethod
    def from_bytes(blob: bytes) -> "BTMR32":
        if len(blob) != 4:
            raise ValueError("BTMR32 requires four bytes")
        return BTMR32.unpack(struct.unpack(">I", blob)[0])

    def numeric_fraction(self) -> Fraction | None:
        if self.kind == 1:
            return Fraction(0, 1)
        if self.kind != 0:
            return None
        value = Fraction(0, 1)
        for index, digit in enumerate(self.trits):
            value += Fraction(digit, 3 ** index)
        scale = 3 ** self.exponent if self.exponent >= 0 else Fraction(1, 3 ** (-self.exponent))
        return value * scale

    def as_dict(self) -> dict[str, object]:
        word = self.pack()
        fraction = self.numeric_fraction()
        return {"word_uint32": word, "hex": f"0x{word:08X}", "binary": f"{word:032b}", "orientation": "RTL" if self.orientation else "LTR", "domain": "cardinal_display" if self.domain else "modular_residue", "kind": ("finite", "zero", "infinity", "reserved_nan")[self.kind], "exponent": self.exponent, "balanced_trits": self.trits, "fraction": None if fraction is None else f"{fraction.numerator}/{fraction.denominator}", "float": None if fraction is None else float(fraction)}


def quantize_btmr32(value: float | Fraction, orientation: int = 0, domain: int = 0) -> BTMR32:
    f = Fraction(value).limit_denominator(3 ** 20) if not isinstance(value, Fraction) else value
    if f == 0:
        return BTMR32(orientation, domain, 1, 0, (0,) * BTMR32_TRITS)
    exponent = 0
    scaled = f
    while abs(scaled) >= 3 and exponent < 31:
        scaled /= 3
        exponent += 1
    while abs(scaled) < Fraction(1, 3) and exponent > -32:
        scaled *= 3
        exponent -= 1
    trits: list[int] = []
    remainder = scaled
    for index in range(BTMR32_TRITS):
        weight = Fraction(1, 3 ** index)
        _, digit = min((abs(remainder - d * weight), d) for d in BALANCED_DIGITS)
        trits.append(digit)
        remainder -= digit * weight
    return BTMR32(orientation, domain, 0, exponent, tuple(trits))


def orientation_action(value: int, orientation: int) -> int:
    x = int(value) % 3
    return x if int(orientation) % 2 == 0 else (-x) % 3


def s3_semidirect_compose(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    r1, s1 = a[0] % 3, a[1] % 2
    r2, s2 = b[0] % 3, b[1] % 2
    return ((r1 + (r2 if s1 == 0 else -r2)) % 3, (s1 + s2) % 2)


def s3_semidirect_inverse(a: tuple[int, int]) -> tuple[int, int]:
    r, s = a[0] % 3, a[1] % 2
    return ((-r if s == 0 else r) % 3, s)


def unit_group_mod3() -> dict[str, object]:
    return {"units": [1, 2], "order": 2, "identification": {"1": "+1", "2": "-1"}, "group": "C2", "note": "phi(3)=2 counts units; it does not identify binary and ternary. The C2 unit group supplies an orientation/reflection action on Z3."}
