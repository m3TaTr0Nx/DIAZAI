# DIAZAI Hjelmslev Four-Tiling + ML Extension v9.0

This is a delta/overlay for the larger DIAZAI archive.

## New exact result
The 12 full Lambda-containing superplanes are not merely a list. Under reduction
P^1(Z9) -> P^1(F3), they split into exactly FOUR fibers of THREE planes.

The canonical XYZ family is exactly the fiber:
  [1:2], [1:5], [1:8].

The user's 27x27 handwritten/hardcoded XYZ matrix is regenerated exactly by a
macroblock codec:
- macro column = i
- macro row = j
- each 3x3 block stores the three triples (i,j,k) from the three lifts
- the three k values are sorted in display order.

The same construction gives two more affine fiber squares, and the fourth projective
fiber uses the natural rotated chart:
- macro column = i
- macro row = k
- the three j values vary.

## Shared diagonal
All four 27x27 matrices have the same scalar main diagonal:
111222333444555666777888999
(three copies of each digit), equivalently nine constant 3x3 Lambda macroblocks.

## GF9 bridge
GF9^x has eight nonzero oriented representatives. Quotient by +/- gives the four
P^1(F3) directions. The package includes all 256 binary masks over these eight
oriented labels as a separate 8-bit control space.
