# DIAZAI 12 Full Superplane Atlas v1.0

This branch adds the canonical 12 full Lambda-containing superplanes of `P^1(Z/9Z)` in `i=r` locked form.

## Canonical principal seeds

- `X = (0,1,2)`
- `Y = (0,1,5)`
- `Z = (0,1,8)`
- `Lambda = (1,1,1)`

The twelve full 81-state planes are indexed by the projective representatives

`[1:t]` for `t=0..8`, plus `[0:1]`, `[3:1]`, `[6:1]`.

Each plane is generated as

`P(h) = { r Lambda + c h : r,c in Z/9Z }`

with `h=(0,a,b)`, so the first coordinate is exactly `i=r`.

Each plane has six unit-associated horizontal generators and the common six vertical rotor generators `(1,1,1),(2,2,2),(4,4,4),(8,8,8),(7,7,7),(5,5,5)`.

Therefore each plane has `6 x 6 = 36` primitive horizontal/vertical coordinate gauges, and the 12-plane atlas has `432` such parameterizations.

## Exact cover

The 12 full planes cover all 729 ambient triples with multiplicities:

- 648 triples on exactly 1 plane
- 72 triples on exactly 3 planes
- 9 Lambda-axis triples on all 12 planes

Weighted incidence count: `648 + 72*3 + 9*12 = 972 = 12*81`.

## XYZ 729-scalar unfolding

A separate `27 x 27` scalar tiling is formed by taking the 243 X/Y/Z plane-cell triple occurrences once and unfolding each triple into its three scalar coordinates: `3 planes x 81 triples x 3 coordinates = 729 scalar cells`.

The rendered PDF/DOCX/XLSX/PPTX/SQLite package is generated from the same canon and stored with the DIAZAI archive.