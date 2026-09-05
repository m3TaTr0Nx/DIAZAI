# DIAZAI DMR-NTT 729 Deep Comparator

Status: **benchmark / engineering hypothesis**, not a state-of-the-art speed claim.

## Question under test

Does a fixed `N = 729 = 3^6` radix-3 exact NTT, aligned with DIAZAI's six-trit address structure, provide a useful computational advantage over generic exact transforms, direct exact cyclic convolution, floating FFTs, and dense/circulant AI layers?

## Local benchmark environment

- Linux x86_64
- Python 3.13.5
- NumPy 2.3.5
- Numba 0.65.1
- PyTorch 2.10 CPU
- 5 logical CPUs visible to the container
- Primary field: `p = 58321`, primitive 729th root `12723`
- Second RNS field: `p = 1459`, primitive 729th root `9`
- Test coefficients: signed int8 range `[-127,127]`

## Verified correctness

- `INTT(NTT(x)) == x` at `N=729`
- fixed NTT == generic exact Python radix-3 NTT
- two-prime RNS/CRT cyclic convolution == direct signed integer cyclic convolution
- NumPy float64 FFT convolution rounded exactly to the same integer result on the benchmark vectors

## Key measured results

| Comparator | Median |
|---|---:|
| Fixed exact 729 NTT, Numba | 0.068933 ms |
| Generic exact 729 radix-3 NTT, Python | 1.302333 ms |
| Exact single-prime 729 cyclic convolution | 0.204864 ms |
| Exact two-prime RNS/CRT 729 convolution | 0.411956 ms |
| Direct exact O(N^2) cyclic convolution | 0.976374 ms |
| NumPy float64 FFT, 729 | 0.009695 ms |
| NumPy float64 FFT convolution | 0.030606 ms |
| NumPy dense 729 circulant matvec | 0.011927 ms |

Derived:

- fixed specialization vs generic Python exact NTT: **18.89x faster**
- exact two-prime NTT convolution vs direct exact convolution: **2.37x faster**
- fixed exact NTT vs optimized NumPy float FFT: **7.11x slower** in this CPU software implementation

A second benchmark with pretransformed weights measured:

- exact two-prime pretransformed-weight inference: **0.373199 ms**
- full two-prime convolution including weight transform: **0.612049 ms**
- direct exact convolution: **0.984582 ms**
- NumPy FFT convolution: **0.030745 ms**

So pretransforming learned weights provides a **1.64x** reduction relative to transforming weights every inference, and the exact pretransformed path is **2.64x faster** than direct exact convolution, but remains **12.14x slower** than the optimized floating FFT reference on this CPU.

## Hardware hypothesis

The current evidence does **not** establish that DIAZAI is faster than state-of-the-art NTT accelerators. The interesting hardware hypothesis is narrower:

1. Native 729 avoids padding a 729-state layer to 1024.
2. `729 = 3^6` gives exactly six radix-3 stages that can align with the six-trit address codec.
3. A fixed transform can hard-wire or precompute root schedules and routing.
4. Learned convolution kernels can be stored already transformed.
5. X/Y/Z, S3, Lambda and C/F actions may be implemented as address/bank permutations rather than physical tensor movement.
6. Multi-small-prime RNS lanes can preserve exact wider integer dynamic range.
7. The C60 macro-rotor should be tested as a logical address-phase permutation, not assumed to be a free 120-bit combinational barrel shift.

Approximate operation model for a fixed radix-3 729 transform:

- 6 stages
- 1458 radix-3 butterflies
- approximately 4374 general modular multiplies under a specialized 3-point DFT model
- padded radix-2 1024 comparison: 5120 butterflies/twiddle multiplies
- approximate general-multiply ratio: 0.8543
- storage-point ratio: 729/1024 = 0.7119

These are architectural counts, **not FPGA latency measurements**. Synthesis, place-and-route, BRAM banking, timing closure and energy measurements are required.

## AI benchmark targets

The next comparator should train/evaluate the same task with:

- dense `729 x 729` layer
- floating FFT circulant layer
- exact NTT/RNS circulant layer
- block-circulant multi-head DIAZAI layer
- separable `27 x 27` NTT layer

Measure task quality, parameter count, latency, memory traffic, deterministic exactness and eventually FPGA energy.

## Patent-oriented engineering wedge

The potentially protectable subject matter is the **computational method**, not the NTT mathematics:

- six-trit address-to-radix-3 stage scheduler
- address-preserving exact structured inference
- pretransformed learned-weight storage and adaptive RNS lane selection
- zero-copy/bank-permutation implementation of DIAZAI structural operators
- shared C60/729 root schedule and logical phase controller
- residue sidecar verification and deterministic execution receipts

Generic NTT, CRT/RNS, roots of unity, and the identities `729=3^6=27^2` are prior mathematical tools and should not be claimed as inventions.

## Files

- `diazai_deep_benchmark.py` - baseline deep comparator
- `diazai_deep_benchmark_v2.py` - pretransformed-weight / 27x27 / operation-model extensions
- `results_v1.json`
- `results_v2.json`

All timing claims are machine-specific and should be rerun on the target CPU/GPU/FPGA before external performance claims are made.
