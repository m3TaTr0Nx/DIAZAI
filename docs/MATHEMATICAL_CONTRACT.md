# Mathematical Contract

## Carrier and display

The finite carrier is `H = Z9³`, with `|H| = 9³ = 3⁶ = 729`. Arithmetic uses residues `0..8`; display uses `1..9` with `9` as the zero-class representative. A separate boundary/chirality symbol may be rendered as `λ` or `λ′`, but it does not silently alter the ring operation.

`dr(n) = ((n - 1) mod 9) + 1` for displayed zero-suppressed digits.

## Exact addresses

For `(i,j,k) ∈ {1,…,9}³`:

`address(i,j,k) = 81(i-1) + 9(j-1) + (k-1)`.

For each digit, write `d-1 = 3h + l`, with `h,l ∈ Z3`. Then:

- atlas row: `9h_i + 3h_j + h_k`
- atlas column: `9l_i + 3l_j + l_k`

This gives a set bijection `Z9³ ↔ Z3⁶ ↔ {0,…,26}²`.

## Principal superplanes

For row anchor `r ∈ {1,…,9}`, column step `c ∈ {0,…,8}`, and slope `s`:

`P_s(r,c) = (r, dr(r+c), dr(r+s c))`.

- `X = P_2`, generator `(0,1,2)`
- `Y = P_5`, generator `(0,1,5)`
- `Z = P_8`, generator `(0,1,8)`
- vertical rotor `(1,1,1)`
- stator direction `(0,3,6)`

Each plane contains 81 unique triples and has Y/S/N inventory `39/24/18`.

## Verified finite counts

- all-distinct triples: `504`
- diagonal triples: `9`
- exactly-two-equal shell: `216`
- admissible all-distinct plus diagonal: `513`
- integer hinge `ik = j²`: `17` states

## Algebraic status

Scalar addition and multiplication inherited from `Z9` are commutative and associative. Division is not generally available because `Z9` has zero divisors. Ordered composition of permutations, generators, projections, lenses, connector actions, and reversals is generally noncommutative.

The system is therefore a commutative base ring with a noncommutative transformation/action layer—not one undifferentiated algebra.
