# DIAZAI DMR-NTT Comparator v1

This benchmark asks a narrow question:

> Does a fixed `3^6 = 729` radix-3 exact transform gain measurable performance from structural specialization, and where is that useful for quantized AI?

It does **not** assume that the DIAZAI transform is faster than current optimized NTTs. The suite measures the proposition.

## Exact comparators

At N=729 the suite compares:

- direct finite-field DFT (`O(N^2)`) as a correctness/performance floor;
- generic recursive radix-3 NTT with twiddles recomputed during execution;
- fixed-plan radix-3 NTT with roots/twiddles precomputed once;
- the unified `p=58321` profile;
- a narrow `p=1459` 729-only profile;
- direct exact integer cyclic convolution;
- dense int64 circulant matrix-vector execution;
- exact single-prime NTT convolution modulo p;
- exact signed RNS/CRT NTT convolution;
- float64 NumPy FFT convolution;
- float32 SciPy FFT convolution;
- exact 27x27 separable NTT versus 2-D floating FFT.

Every exact path is checked against a reference before its timing is accepted.

## Why 729 might be special in implementation

The differentiator is **not** that NTT itself is novel. The engineering hypothesis is that `729=3^6` permits:

- six uniform radix-3 stages;
- a static stage/address schedule;
- reusable twiddle tables;
- narrow 729-friendly prime fields;
- parallel narrow RNS lanes for exact signed reconstruction;
- a native `27 x 27` separable alternative;
- direct correspondence with the six-trit / `Z9^3` structural address without using 729 as the coefficient modulus.

A fixed 729-only field such as `F_1459` uses 11-bit residues, whereas the unified `F_58321` profile uses 16-bit residues. Hardware implications must be established by synthesis rather than inferred from Python timing.

## AI comparator

The main AI-like workload is a 729-token circulant mixer:

`y = x *_cyclic h`

with int8 activations and int8 learned kernel weights.

The exact transform path computes the same integer layer through NTT/RNS/CRT. The floating path computes the same structured layer through FFT. This makes the arithmetic comparison much fairer than comparing an NTT mixer to an unrelated dense matrix.

A separate 27x27 benchmark evaluates the same 729-state count as a separable 2-D cyclic mixer.

## Floating exactness envelope

The suite increases integer coefficient magnitude and checks when rounded float32/float64 FFT convolution stops reproducing the exact integer reference. This is relevant because exact arithmetic is useful only if the application actually benefits from determinism or a dynamic range for which floating FFT rounding is material.

## Macro-rotor algebra correction

The circular 60-trit rotor is modeled as `C60` acting on `F3^60`, equivalently multiplication by `x` in

`F3[x] / (x^60 - 1)`.

That is distinct from ordinary multiplication in `Z/(3^60)Z`. The latter is still a valid 60-trit 3-adic/radix representation, but cyclic coordinate rotation is a permutation action.

## Interpreting results

A result can support one of four different conclusions:

1. **Planned > generic exact NTT**: evidence that structural specialization matters in software.
2. **Small-prime > unified-prime**: evidence that narrow residue width matters in the current implementation.
3. **Exact NTT > direct/dense exact integer methods**: expected algorithmic evidence, useful but not a state-of-the-art claim.
4. **Floating FFT remains much faster**: indicates the commercial case depends on exactness, determinism, RNS compatibility, or future C/CUDA/FPGA/ASIC optimization rather than raw CPU software latency.

The decisive hardware claim requires a common RTL benchmark with equal dynamic range and comparable I/O assumptions.
