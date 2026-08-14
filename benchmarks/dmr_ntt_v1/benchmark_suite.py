#!/usr/bin/env python3
"""DIAZAI DMR-NTT comparator v1.

Purpose
-------
Test the *specific* performance hypothesis that a fixed 3^6=729 radix-3
exact transform, with precomputed roots/twiddles and structural addressing,
can outperform less-specialized exact implementations while providing
bit-exact integer convolution for quantized AI workloads.

This benchmark deliberately distinguishes:
  * algorithmic complexity,
  * Python/runtime implementation effects,
  * floating FFT speed,
  * exact modular semantics,
  * RNS/CRT reconstruction cost,
  * 1-D 729 and 2-D 27x27 structured mixers.

It does NOT claim state-of-the-art NTT performance. Hosted Python results are
screening evidence for what deserves a C/CUDA/RTL implementation.
"""

from __future__ import annotations

import json
import math
import os
import platform
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import numpy as np
try:
    import scipy
    import scipy.fft as spfft
except Exception:
    scipy = None
    spfft = None

SEED = 0xD1A2A1
RNG = random.Random(SEED)
NP_RNG = np.random.default_rng(SEED)
STRUCTURAL_LENGTHS = (3, 9, 27, 81, 243, 729)
N = 729
UNIFIED_P = 58321
SMALL_729_P = 1459


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def factor_distinct(n: int) -> List[int]:
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def primitive_root_prime(p: int) -> int:
    assert is_prime(p)
    phi = p - 1
    fs = factor_distinct(phi)
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in fs):
            return g
    raise RuntimeError("no primitive root found")


def root_for_length(p: int, n: int) -> int:
    if (p - 1) % n:
        raise ValueError(f"{n} does not divide p-1={p-1}")
    g = primitive_root_prime(p)
    w = pow(g, (p - 1) // n, p)
    if pow(w, n, p) != 1:
        raise AssertionError("root does not close")
    # All structural lengths are powers of 3.
    if n > 1 and pow(w, n // 3, p) == 1:
        raise AssertionError("root order is too small")
    return w


@dataclass(frozen=True)
class StagePlan:
    n: int
    root: int
    twiddle_1: Tuple[int, ...]
    twiddle_2: Tuple[int, ...]
    zeta: int
    zeta2: int


class Radix3Plan:
    """Reusable fixed radix-3 plan. Twiddles are generated once per stage size."""

    def __init__(self, n: int, p: int):
        if n not in STRUCTURAL_LENGTHS:
            raise ValueError("benchmark plan expects n in 3^1..3^6")
        self.n = n
        self.p = p
        self.root = root_for_length(p, n)
        self.inv_root = pow(self.root, -1, p)
        self.forward = self._make_stages(self.root)
        self.inverse = self._make_stages(self.inv_root)
        self.inv_n = pow(n, -1, p)

    def _make_stages(self, root: int) -> Dict[int, StagePlan]:
        stages = {}
        size = self.n
        r = root
        while size > 1:
            m = size // 3
            zeta = pow(r, m, self.p)
            tw1 = tuple(pow(r, k, self.p) for k in range(m))
            tw2 = tuple((x * x) % self.p for x in tw1)
            stages[size] = StagePlan(size, r, tw1, tw2, zeta, (zeta * zeta) % self.p)
            r = pow(r, 3, self.p)
            size = m
        return stages

    @property
    def stored_twiddles_per_direction(self) -> int:
        return sum(len(s.twiddle_1) for s in self.forward.values())

    def transform(self, values: Sequence[int], inverse: bool = False) -> List[int]:
        p = self.p
        stages = self.inverse if inverse else self.forward

        def rec(a: Sequence[int], size: int) -> List[int]:
            if size == 1:
                return [int(a[0]) % p]
            m = size // 3
            A0 = rec(a[0::3], m)
            A1 = rec(a[1::3], m)
            A2 = rec(a[2::3], m)
            st = stages[size]
            out = [0] * size
            z, z2 = st.zeta, st.zeta2
            for k in range(m):
                b0 = A0[k]
                b1 = (st.twiddle_1[k] * A1[k]) % p
                b2 = (st.twiddle_2[k] * A2[k]) % p
                out[k] = (b0 + b1 + b2) % p
                out[k + m] = (b0 + z * b1 + z2 * b2) % p
                out[k + 2 * m] = (b0 + z2 * b1 + z * b2) % p
            return out

        out = rec(values, self.n)
        if inverse:
            inv_n = self.inv_n
            out = [(v * inv_n) % p for v in out]
        return out


# Generic recursive radix-3 baseline. Same mathematics, deliberately recomputes
# powers in each call to quantify the benefit of a fixed transform plan.
def ntt_generic(values: Sequence[int], p: int, root: int, inverse: bool = False) -> List[int]:
    n = len(values)
    r = pow(root, -1, p) if inverse else root

    def rec(a: Sequence[int], size: int, w: int) -> List[int]:
        if size == 1:
            return [int(a[0]) % p]
        m = size // 3
        subw = pow(w, 3, p)
        A0 = rec(a[0::3], m, subw)
        A1 = rec(a[1::3], m, subw)
        A2 = rec(a[2::3], m, subw)
        z = pow(w, m, p)
        z2 = (z * z) % p
        out = [0] * size
        for k in range(m):
            wk = pow(w, k, p)
            wk2 = (wk * wk) % p
            b0 = A0[k]
            b1 = (wk * A1[k]) % p
            b2 = (wk2 * A2[k]) % p
            out[k] = (b0 + b1 + b2) % p
            out[k + m] = (b0 + z * b1 + z2 * b2) % p
            out[k + 2*m] = (b0 + z2 * b1 + z * b2) % p
        return out

    out = rec(values, n, r)
    if inverse:
        inv_n = pow(n, -1, p)
        out = [(v * inv_n) % p for v in out]
    return out


def ntt_direct(values: Sequence[int], p: int, root: int) -> List[int]:
    n = len(values)
    powers = [1] * n
    for i in range(1, n):
        powers[i] = (powers[i-1] * root) % p
    out = [0] * n
    for k in range(n):
        s = 0
        for j, x in enumerate(values):
            s += int(x) * powers[(j * k) % n]
        out[k] = s % p
    return out


def direct_cyclic_conv(x: Sequence[int], h: Sequence[int]) -> List[int]:
    n = len(x)
    out = [0] * n
    for k in range(n):
        s = 0
        for j in range(n):
            s += int(x[j]) * int(h[(k-j) % n])
        out[k] = s
    return out


def ntt_conv_mod(x: Sequence[int], h: Sequence[int], plan: Radix3Plan) -> List[int]:
    X = plan.transform(x)
    H = plan.transform(h)
    Y = [(a*b) % plan.p for a, b in zip(X, H)]
    return plan.transform(Y, inverse=True)


def find_ntt_primes(n: int, min_product: int, start_k: int = 2, max_prime: int = 65535) -> List[int]:
    primes = []
    M = 1
    k = start_k
    # n is odd; even k produces odd candidates.
    if k % 2:
        k += 1
    while M <= min_product:
        p = k*n + 1
        if p > max_prime:
            raise RuntimeError("not enough small NTT primes within requested bound")
        if is_prime(p):
            primes.append(p)
            M *= p
        k += 2
    return primes


def crt_signed_vectors(residue_vectors: Sequence[Sequence[int]], primes: Sequence[int]) -> List[int]:
    M = math.prod(primes)
    coeffs = []
    for p in primes:
        Mi = M // p
        coeffs.append(Mi * pow(Mi, -1, p))
    out = []
    half = M // 2
    for vals in zip(*residue_vectors):
        z = sum(int(a)*c for a, c in zip(vals, coeffs)) % M
        if z > half:
            z -= M
        out.append(z)
    return out


def rns_exact_conv(x: Sequence[int], h: Sequence[int]) -> Tuple[List[int], List[int]]:
    n = len(x)
    B = n * max(abs(int(v)) for v in x) * max(abs(int(v)) for v in h)
    primes = find_ntt_primes(n, min_product=2*B)
    residues = []
    for p in primes:
        plan = Radix3Plan(n, p)
        residues.append(ntt_conv_mod(x, h, plan))
    return crt_signed_vectors(residues, primes), primes


def fft_cyclic_conv64(x: Sequence[int], h: Sequence[int]) -> np.ndarray:
    xa = np.asarray(x, dtype=np.float64)
    ha = np.asarray(h, dtype=np.float64)
    y = np.fft.ifft(np.fft.fft(xa) * np.fft.fft(ha)).real
    return np.rint(y).astype(np.int64)


def fft_cyclic_conv32(x: Sequence[int], h: Sequence[int]) -> np.ndarray:
    if spfft is None:
        raise RuntimeError("SciPy unavailable")
    xa = np.asarray(x, dtype=np.float32)
    ha = np.asarray(h, dtype=np.float32)
    y = spfft.ifft(spfft.fft(xa) * spfft.fft(ha)).real
    return np.rint(y).astype(np.int64)


def circulant_dense_conv(x: Sequence[int], h: Sequence[int]) -> np.ndarray:
    xarr = np.asarray(x, dtype=np.int64)
    harr = np.asarray(h, dtype=np.int64)
    n = len(x)
    rows = np.arange(n)[:, None]
    cols = np.arange(n)[None, :]
    C = harr[(rows - cols) % n]
    return C @ xarr


def ntt2d_conv_mod(a: np.ndarray, b: np.ndarray, plan27: Radix3Plan) -> np.ndarray:
    assert a.shape == (27, 27) and b.shape == (27, 27)

    def fwd(mat: np.ndarray) -> List[List[int]]:
        rows = [plan27.transform([int(v) for v in row]) for row in mat]
        cols = [[rows[r][c] for r in range(27)] for c in range(27)]
        cols = [plan27.transform(col) for col in cols]
        return [[cols[c][r] for c in range(27)] for r in range(27)]

    def inv(mat: List[List[int]]) -> np.ndarray:
        cols = [[mat[r][c] for r in range(27)] for c in range(27)]
        cols = [plan27.transform(col, inverse=True) for col in cols]
        tmp = [[cols[c][r] for c in range(27)] for r in range(27)]
        rows = [plan27.transform(row, inverse=True) for row in tmp]
        return np.asarray(rows, dtype=np.int64)

    A = fwd(a)
    B = fwd(b)
    C = [[(A[r][c]*B[r][c]) % plan27.p for c in range(27)] for r in range(27)]
    return inv(C)


def fft2d_conv64(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    y = np.fft.ifft2(np.fft.fft2(a.astype(np.float64)) * np.fft.fft2(b.astype(np.float64))).real
    return np.rint(y).astype(np.int64)


def direct2d_cyclic(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Vectorized exact int64 reference by summing 729 rolled copies.
    out = np.zeros((27,27), dtype=np.int64)
    for i in range(27):
        for j in range(27):
            out += int(a[i,j]) * np.roll(np.roll(b, i, axis=0), j, axis=1)
    return out


def bench(fn: Callable[[], object], warmup: int = 2, repeats: int = 9) -> Dict[str, float]:
    for _ in range(warmup):
        fn()
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter_ns()
        fn()
        ts.append((time.perf_counter_ns() - t0) / 1e6)
    ts_sorted = sorted(ts)
    p95_index = min(len(ts_sorted)-1, math.ceil(0.95*len(ts_sorted))-1)
    med = statistics.median(ts)
    return {
        "median_ms": med,
        "p95_ms": ts_sorted[p95_index],
        "min_ms": min(ts),
        "max_ms": max(ts),
        "repeats": repeats,
        "throughput_per_s": 1000.0/med if med else float("inf"),
    }


def exactness_sweep() -> List[Dict[str, object]]:
    # Float32 should fail much earlier than float64. We keep exact reference in Python ints.
    magnitudes = [1, 8, 32, 128, 512, 2048, 8192, 32768, 131072, 524288, 2_000_000, 8_000_000, 32_000_000]
    out = []
    for mag in magnitudes:
        x = [RNG.randint(-mag, mag) for _ in range(N)]
        h = [RNG.randint(-mag, mag) for _ in range(N)]
        ref = direct_cyclic_conv(x, h)
        row = {"magnitude": mag, "max_abs_reference": max(abs(v) for v in ref)}
        y64 = fft_cyclic_conv64(x, h)
        e64 = [abs(int(a)-int(b)) for a,b in zip(y64, ref)]
        row.update({"float64_exact": max(e64)==0, "float64_max_abs_error": max(e64)})
        if spfft is not None:
            y32 = fft_cyclic_conv32(x, h)
            e32 = [abs(int(a)-int(b)) for a,b in zip(y32, ref)]
            row.update({"float32_exact": max(e32)==0, "float32_max_abs_error": max(e32)})
        out.append(row)
    return out


def system_info() -> Dict[str, object]:
    info = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "numpy": np.__version__,
        "scipy": getattr(scipy, "__version__", None),
        "seed": SEED,
    }
    try:
        info["cpu_model"] = next(
            line.split(":",1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
            if line.lower().startswith("model name")
        )
    except Exception:
        pass
    return info


def main() -> None:
    result: Dict[str, object] = {"system": system_info(), "validation": {}, "benchmarks": {}, "analysis": {}}

    # ---------- Root and round-trip validation ----------
    roots = {}
    for n in STRUCTURAL_LENGTHS:
        p = UNIFIED_P
        plan = Radix3Plan(n, p)
        x = [RNG.randrange(p) for _ in range(n)]
        rt = plan.transform(plan.transform(x), inverse=True)
        assert rt == [v % p for v in x]
        roots[str(n)] = plan.root
    result["validation"]["roots_mod_58321"] = roots
    result["validation"]["all_roundtrips"] = True

    # Compare direct DFT, generic radix-3, planned radix-3 at representative sizes.
    exact_compare = {}
    for n in (27, 81, 729):
        p = UNIFIED_P
        plan = Radix3Plan(n, p)
        x = [RNG.randrange(p) for _ in range(n)]
        generic = ntt_generic(x, p, plan.root)
        planned = plan.transform(x)
        direct = ntt_direct(x, p, plan.root)
        assert generic == planned == direct
        exact_compare[str(n)] = True
    result["validation"]["direct_generic_planned_agree"] = exact_compare

    # ---------- Single-transform benchmark ----------
    for p in (SMALL_729_P, UNIFIED_P):
        plan = Radix3Plan(N, p)
        x = [RNG.randrange(p) for _ in range(N)]
        key = f"N729_mod{p}"
        result["benchmarks"][key] = {
            "modulus_bits": p.bit_length(),
            "product_bits": (p*p).bit_length(),
            "stored_twiddles_per_direction": plan.stored_twiddles_per_direction,
            "planned_radix3": bench(lambda: plan.transform(x), warmup=2, repeats=13),
            "generic_radix3": bench(lambda: ntt_generic(x, p, plan.root), warmup=1, repeats=7),
        }
    # Direct finite DFT is intentionally fewer repeats.
    p = UNIFIED_P
    plan = Radix3Plan(N, p)
    x = [RNG.randrange(p) for _ in range(N)]
    result["benchmarks"]["N729_mod58321"]["direct_finite_dft"] = bench(
        lambda: ntt_direct(x, p, plan.root), warmup=0, repeats=3
    )

    # ---------- Exact int8 convolution / AI mixer benchmark ----------
    x8 = [RNG.randint(-127,127) for _ in range(N)]
    h8 = [RNG.randint(-127,127) for _ in range(N)]
    ref = direct_cyclic_conv(x8, h8)

    # NTT modulo 58321 validation.
    plan = Radix3Plan(N, UNIFIED_P)
    ymod = ntt_conv_mod(x8, h8, plan)
    assert ymod == [v % UNIFIED_P for v in ref]

    # Exact RNS/CRT validation.
    yrns, rns_primes = rns_exact_conv(x8, h8)
    assert yrns == ref

    yfft64 = fft_cyclic_conv64(x8, h8)
    assert [int(v) for v in yfft64] == ref
    if spfft is not None:
        yfft32 = fft_cyclic_conv32(x8, h8)
        assert [int(v) for v in yfft32] == ref

    ydense = circulant_dense_conv(x8, h8)
    assert [int(v) for v in ydense] == ref

    mix = {
        "parameters_structured_kernel": N,
        "dense_unstructured_parameter_equivalent": N*N,
        "rns_primes": rns_primes,
        "rns_modulus_product_bits": math.prod(rns_primes).bit_length(),
        "direct_exact_O_N2": bench(lambda: direct_cyclic_conv(x8,h8), warmup=0, repeats=5),
        "dense_circulant_int64_matvec": bench(lambda: circulant_dense_conv(x8,h8), warmup=1, repeats=7),
        "float64_fft_circulant": bench(lambda: fft_cyclic_conv64(x8,h8), warmup=3, repeats=21),
        "planned_single_prime_ntt_mod58321": bench(lambda: ntt_conv_mod(x8,h8,plan), warmup=2, repeats=11),
        "exact_rns_ntt_signed": bench(lambda: rns_exact_conv(x8,h8), warmup=1, repeats=7),
    }
    if spfft is not None:
        mix["float32_fft_circulant"] = bench(lambda: fft_cyclic_conv32(x8,h8), warmup=3, repeats=21)
    result["benchmarks"]["AI_729_circulant_int8"] = mix

    # ---------- 27x27 exact separable mixer ----------
    A = NP_RNG.integers(-31,32,size=(27,27),dtype=np.int64)
    B = NP_RNG.integers(-31,32,size=(27,27),dtype=np.int64)
    ref2 = direct2d_cyclic(A,B)
    p = UNIFIED_P
    plan27 = Radix3Plan(27,p)
    y2 = ntt2d_conv_mod(A,B,plan27)
    assert np.array_equal(y2 % p, ref2 % p)
    y2f = fft2d_conv64(A,B)
    assert np.array_equal(y2f,ref2)
    result["benchmarks"]["AI_27x27_separable"] = {
        "float64_fft2": bench(lambda: fft2d_conv64(A,B), warmup=3, repeats=21),
        "exact_ntt2_mod58321": bench(lambda: ntt2d_conv_mod(A,B,plan27), warmup=2, repeats=9),
        "direct_exact_reference": bench(lambda: direct2d_cyclic(A,B), warmup=0, repeats=3),
    }

    # ---------- Floating exactness envelope ----------
    result["benchmarks"]["floating_exactness_sweep"] = exactness_sweep()

    # ---------- Static operation/architecture counts ----------
    stages = int(round(math.log(N,3)))
    butterflies = (N//3) * stages
    # This implementation has ~6 nontrivial modular multiplies per radix-3 butterfly
    # (2 input twiddles + 4 cube-root products); exact optimized hardware can reduce this.
    approx_mults_transform = butterflies * 6
    result["analysis"] = {
        "radix3_stages_N729": stages,
        "butterflies_N729": butterflies,
        "approx_modular_multiplies_per_transform": approx_mults_transform,
        "direct_DFT_mulacc_pairs": N*N,
        "approx_arithmetic_ratio_direct_to_radix3": (N*N)/approx_mults_transform,
        "planned_twiddles_per_direction": Radix3Plan(N,UNIFIED_P).stored_twiddles_per_direction,
        "mod1459_operand_bits": SMALL_729_P.bit_length(),
        "mod58321_operand_bits": UNIFIED_P.bit_length(),
        "hardware_hypothesis": [
            "N=729 is six uniform radix-3 stages: no mixed-radix dispatch is required.",
            "A fixed plan can hardwire address permutations and store/reuse stage twiddles.",
            "A 729-only profile can use very small NTT-friendly primes such as 1459; RNS can recover dynamic range with parallel narrow lanes.",
            "Software Python timing does not predict FPGA/ASIC throughput; RTL must measure Fmax, II, LUT/DSP/BRAM, power, and memory traffic.",
        ],
        "macro_rotor_correction": "Model the 60-trit circular rotor as C60 acting on F3^60, equivalently multiplication by x in F3[x]/(x^60-1). A dynamic barrel shift is a mux network, not free wiring.",
    }

    outdir = Path("results")
    outdir.mkdir(exist_ok=True)
    outfile = outdir / "benchmark.json"
    outfile.write_text(json.dumps(result, indent=2))

    print("\n=== DIAZAI DMR-NTT BENCHMARK SUMMARY ===")
    print(json.dumps({
        "system": result["system"],
        "N729_mod1459": result["benchmarks"]["N729_mod1459"],
        "N729_mod58321": result["benchmarks"]["N729_mod58321"],
        "AI_729_circulant_int8": result["benchmarks"]["AI_729_circulant_int8"],
        "AI_27x27_separable": result["benchmarks"]["AI_27x27_separable"],
        "analysis": result["analysis"],
    }, indent=2))
    print("BENCHMARK_JSON_BEGIN")
    print(outfile.read_text())
    print("BENCHMARK_JSON_END")


if __name__ == "__main__":
    main()
