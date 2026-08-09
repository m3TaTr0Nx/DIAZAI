# OPUS + CINDERS-81 Validation

This branch formalizes and validates the OPUS superplane combinatorics and an executable CINDERS-81 schedule.

## Source-derived facts

- OPUS archive version: `1.3.0-DOUBLED-CLOSED`
- 108 right-handed variants + 108 left-handed variants = 216 total
- Canonical horizontal generator families GX/GY/GZ and vertical rotor family GV are preserved from the OPUS archive
- Cross-language parity is recorded in the archive for 108/108 right-handed variants

## Newly validated structure

Across every matched X/Y/Z generator triplet and both handedness banks:

- 27 ordinary unordered all-distinct permutation orbits per triplet
- each ordinary orbit splits exactly `2 X + 2 Y + 2 Z`
- the two positions within each plane occupy opposite symmetry columns under zero-based indexing, `c1 + c2 = 9`
- the three mod-3 coset orbits `{1,4,7}`, `{2,5,8}`, `{3,6,9}` are shared invariants with all six permutations appearing in every plane
- every OPUS cell in columns 0, 3, and 6 satisfies `i ≡ j ≡ k (mod 3)`
- zero structural failures across all 216 variants

## CINDERS-81 schedule

The executable scheduling convention assigns one real CINDERS layer to each ordered cell of a 9x9 OPUS superplane, row-major. The displayed `(i,j,k)` digits of the OPUS cell form the retained three-control stream for that layer.

Validation campaign:

- 108 right-handed OPUS variants
- 81 randomized initial states per variant
- 8,748 complete CINDERS-81 networks
- 708,588 actual CINDERS layer executions
- 8,748/8,748 exact inverse reconstructions
- 0 failures

## Claim boundary

The CINDERS-81 schedule above is an executable and validated convention, not yet asserted to be the unique mathematical or neural interpretation of the OPUS geometry. Relaxed-generator families and stator-driven reduced-cycle schedules remain experimental targets.

## Next experiments

1. Stator-vertical schedules using GVS `(3,3,3)`, `(6,6,6)`, `(9,9,9)`.
2. Reduced 3-step superplanes and unitary/fixed-blade behavior.
3. Relaxed equality-shell dynamics for `i=j≠k`, `i=k≠j`, `j=k≠i`.
4. Nodal decomposition of `n^3-n=(n-1)n(n+1)` at `n=9`, separating the 9-point diagonal spine from the 720 off-diagonal cells.
5. Branch-causal receipt topology over immutable parent/child state transitions.
6. Live-provider operational validation and cross-runtime browser replay.
