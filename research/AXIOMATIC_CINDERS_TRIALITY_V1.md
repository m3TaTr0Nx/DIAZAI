# DIAZAI / OPUS / CINDERS - Axiomatic Triality Benchmark v1

This research pass formalizes the construction order **arithmetic triality -> permutation triality -> superplane embedding** and evaluates its consequences for the production CINDERS reversible kernel.

## Validated OPUS structure

- Native atlas: `9^3 = 729` states.
- Partition: 9 diagonal + 216 exactly-two-equal + 504 all-distinct.
- OPUS corpus: 108 right-handed + 108 left-handed = 216 variants.
- Across each handed bank: 972 ordinary all-distinct orbit instances exhibit exact `2/2/2` X/Y/Z covering; 108 shared arithmetic-coset orbit instances exhibit `6/6/6` covering.
- Mod-3 backbone checks and permutation-cover checks produced zero failures across the supplied corpus.
- A deliberately simplistic rule that numerically sorts a triple and assigns fixed permutation pairs to X/Y/Z mismatched 504/972 ordinary orbit instances per handed bank. This is treated as a diagnostic supporting the original arithmetic-first construction, not as an OPUS failure.

## Core CINDERS algebra

For one retained scalar control `v`, production CINDERS is affine over `Z9`:

```
x' = A x + v * 1
A = [[1,0,0],
     [1,1,0],
     [1,1,1]]
```

with `det(A)=1 (mod 9)` and exact matrix order `A^9 = I`.

One current OPUS cell supplies three scalar controls. Consequently C9/C27/C81 cell-layer blocks use 27/81/243 scalar steps, all divisible by 9. With a fixed triangular orientation the boundary linear component is therefore identity; the block can only differ by an additive translation, and in canonical row-major OPUS scheduling all tested C9/C27/C81 boundaries were exact identity transforms.

This explains why increasing vanilla CINDERS depth alone does **not** automatically increase boundary expressivity. It still increases receipt/checkpoint granularity and preserves every intermediate reversible trace.

## Triality-conjugated candidate

A reversible extension was tested in which the triangular CINDERS coupling is coordinate-conjugated according to arithmetic-triality coordinate order, with schedules grouped by permutation-pair sector. Each layer remains bijective because it is a coordinate conjugate of the production kernel.

Across the right-handed 108-variant bank using permutation-pair scheduling:

- C9: 67 unique affine transforms; 100/108 variants had nonidentity linear/spectral action.
- C27: 64 unique affine transforms; 105/108 variants had nonidentity linear/spectral action.
- C81: 26 unique transforms; the balanced full-superplane pass closes much of the linear action again.

A broader scan covers right/left banks, depths 9/27/81, four scheduling orders, and three coupling modes.

## Production-code parity and mutation tests

- 10,000 mixed trials comparing the fast affine formulation to the vendored production CINDERS code: **10,000/10,000 passed**, including exact inverse reconstruction.
- 5,000 one-control mutation trials on the selected triality-conjugated candidate: every mutation changed the final output. Output Hamming distances were 1:158, 2:1347, 3:3495. This is a sensitivity result, not a cryptographic claim.

## Spectral interpretation

For an affine block `T(x)=Mx+b` and finite character `chi_y`,

`chi_y(Tx) = omega^(y^T b) * chi_(M^T y)(x)`.

Thus:

- `M = I`: phase-only character transport.
- `M != I`: character-index transport/mixing.

This gives a direct finite-spectral benchmark for candidate reversible neural routing layers.

## Current architecture recommendation

- **C9**: short reversible mixer / local routing block.
- **C27**: strongest immediate triality-coupled reversible routing candidate.
- **C81**: full-superplane receipt/checkpoint/worldstate pass; do not assume depth alone increases expressivity.

Neural task accuracy, training convergence, hidden-weight causal explainability, and operational TRL-7 are deliberately left as open gates pending real model/deployment experiments.
