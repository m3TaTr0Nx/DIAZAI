# DIAZAI DMR-NTT Hardware Audit v1

## Purpose

This note separates mathematically exact structure from hardware claims that still require synthesis.

## 1. Correct carrier for the 60-trit rotor

A circular rotation of a 60-trit word is most naturally modeled as the action of `C60` on `F3^60`, or equivalently as multiplication by `x` in the cyclic polynomial module/ring

`F3[x] / (x^60 - 1)`.

It is **not** ordinary multiplication in `Z/(3^60)Z`. The latter remains a useful 3-adic integer/radix chart, but its arithmetic multiplication is not the same operation as a cyclic coordinate rotation.

## 2. Dynamic barrel shift is not free wiring

A constant circular shift can be implemented as wiring. A runtime-selectable shift `sigma in 0..59` requires a permutation/multiplexer network (or an equivalent staged routing fabric). A synthesis tool may infer a barrel shifter from behavioral code, but area, delay, fanout, and routing must be measured.

Claims such as “all 60 trits rotate in one cycle” are architectural throughput targets, not yet measured results. A pipelined barrel network may have initiation interval 1 while still having multiple cycles of latency.

## 3. Six-trit codec correction

A six-trit block contains exactly three two-trit `Z9` coordinates:

- coordinate `i`: `(r_i, q_i)`
- coordinate `j`: `(r_j, q_j)`
- coordinate `k`: `(r_k, q_k)`

with

`x = r + 3 q (mod 9)`, `r,q in F3`.

Therefore a six-trit block should decode directly to one `(i,j,k)` address. It should **not** be decoded as two three-trit base-27 digits followed by a synthesized “dummy” third coordinate. That construction changes the state space and invalidates comparisons with the canonical 729 carrier.

## 4. Fixed 729 NTT hardware hypothesis

The potentially differentiating hardware properties are:

1. `729 = 3^6`: six uniform radix-3 stages.
2. Fixed address permutations: no general mixed-radix planner in the datapath.
3. Fixed roots/twiddles: stage tables can be ROM, distributed constants, or generated from a compact recurrence.
4. Small NTT-friendly primes for a 729-only profile: e.g. `1459 = 2*729 + 1` supports an order-729 root while using only 11-bit residues.
5. Parallel RNS lanes can recover exact signed dynamic range while keeping each modular multiplier narrow.
6. The `27 x 27` view permits a separable two-dimensional implementation with two banks of 27-point transforms.
7. The structural `Z9^3` address codec can be retained as sideband metadata without forcing the NTT coefficient modulus to equal 729.

None of these alone proves a speed advantage. The claim must be benchmarked against optimized software and synthesized RTL.

## 5. Required RTL comparators

At minimum compare:

- generic configurable NTT core at N=729;
- fixed six-stage radix-3 NTT at N=729;
- 27x27 separable NTT;
- floating FFT IP at comparable precision/dynamic range;
- direct/dense integer baseline where applicable.

Measure:

- clock frequency (Fmax);
- initiation interval (II);
- latency;
- transforms/s;
- exact convolutions/s;
- LUTs / ALMs;
- DSP blocks;
- BRAM / SRAM bits;
- twiddle storage;
- external memory traffic;
- power and energy/transform;
- exact reconstruction range per RNS profile.

## 6. Patent-relevant implementation hooks

Potential implementation claims should be tied to measured computer improvements, such as:

- a fixed ternary address schedule eliminating a generic permutation planner;
- reusing one radix-3 butterfly fabric across N=3,9,27,81,243,729;
- dynamic selection of narrow RNS lanes based on an input-bound certificate;
- deterministic reconstruction receipts carried with a Z9^3 structural address;
- transform-domain tensor routing that preserves reversible/permutation metadata;
- one memory-banking scheme shared by 729-vector and 27x27 atlas execution.

The mathematics (NTT, CRT, roots of unity, 3^6=729) should be treated as prior mathematical infrastructure; protect the engineered processor, scheduler, codec, memory routing, verification, and application pipeline.
