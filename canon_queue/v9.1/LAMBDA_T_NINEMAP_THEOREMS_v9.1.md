# CANON QUEUE v9.1 — Lambda/T Nine-Map + 513/216 Shell

Status: **PROPOSED FOR CANON APPROVAL**

This queue item separates exact finite theorems from chosen codecs and open interpretations.

## A. Nine-map theorem for the principal superplanes

Let

\[
P_f=\{r\Lambda+c h_f:r,c\in Z_9\},\qquad \Lambda=(1,1,1),
\]

with canonical generators

\[
h_X=(0,1,2),\quad h_Y=(0,1,5),\quad h_Z=(0,1,8).
\]

For fixed column coordinate \(c\), define

\[
C_{f,c}=\{r\Lambda+c h_f:r\in Z_9\}.
\]

### THM A1 — 9-column orthogonal support decomposition

Each principal plane is a disjoint union of nine 9-cell columns:

\[
P_f=\bigsqcup_{c\in Z_9}C_{f,c},\qquad |C_{f,c}|=9.
\]

If \(Q_{f,c}\) is the cell-support projector onto \(C_{f,c}\) in \(\ell^2(P_f)\), then

\[
Q_{f,c}Q_{f,d}=\delta_{cd}Q_{f,c},\qquad \sum_c Q_{f,c}=I_{81}.
\]

Thus the nine columns are orthogonal **selection subspaces**. This does not assert that the raw numeric 9×3 digit arrays are mutually orthogonal under the ordinary Frobenius dot product.

### THM A2 — each column is a 27-character / 9×3 scalar raster

Writing \(h_f=(0,a,b)\),

\[
C_{f,c}(r)=(r,r+ac,r+bc).
\]

The 9 triples in one column contain 27 scalar characters and form a 9×3 raster. It may be cut into three contiguous 3×3 row-band squares. More importantly, each of its three coordinate tracks is a complete permutation of \(Z_9\):

\[
r,\quad r+ac,\quad r+bc,\qquad r\in Z_9.
\]

Hence one column contains three complete 9-stride coordinate multisets.

### THM A3 — exact 1-or-3 equality rule inside X/Y/Z

For \(c=0\),

\[
C_{f,0}=\{(r,r,r):r\in Z_9\}=\Lambda.
\]

For every \(c\neq0\), every triple in \(C_{f,c}\) has three pairwise-distinct coordinates. There are no exactly-two-equal cells in a principal X/Y/Z plane.

Therefore

\[
81=9_{AAA}+72_{ABC}.
\]

### THM A4 — common skeletal columns and the T degeneration

The three columns \(c=0,3,6\) are shared by X, Y, and Z:

\[
3h_X=3h_Y=3h_Z=(0,3,6),
\]
\[
6h_X=6h_Y=6h_Z=(0,6,3).
\]

Hence every principal plane decomposes as

\[
81=9_{\Lambda}+18_T+54_R,
\]

where

- \(c=0\): Lambda column,
- \(c=3,6\): two nonzero stator/T skeletal columns,
- \(c\in U_9=\{1,2,4,8,7,5\}\): six rotor columns.

This is the exact nine-map version of the Lambda/T coverage structure.

### THM A5 — character-dual column tracks

Under the standard finite character pairing

\[
\chi_m(r)=e^{2\pi i mr/9},
\]

a translated coordinate track \(r\mapsto r+s\) differs in character space by the phase multiplier

\[
e^{2\pi i ms/9}.
\]

Reduction to \(F_3\) uses cube-root characters \(e^{2\pi i ma/3}\). This supplies an exact Pontryagin/Fourier dual codec. It is not a field embedding of \(F_3\) into \(\mathbb C\).

---

## B. Global 513/216 equality-shell theorem

Use display digits \(1,\ldots,9\) as the standard section of \(Z_9\), with 9 representing residue 0.

### THM B1 — strict/core states

\[
|AAA|=9,
\qquad
|ABC|=9\cdot8\cdot7=504,
\]

so

\[
\boxed{|AAA\cup ABC|=513.}
\]

### THM B2 — exactly-two-equal shell

There are three choices for the distinct coordinate, 9 choices for the repeated value, and 8 choices for the distinct value:

\[
|AAB|=3\cdot9\cdot8=216=6^3.
\]

Thus

\[
\boxed{729=513+216.}
\]

Equivalently,

\[
216=72_{i=j\ne k}+72_{i=k\ne j}+72_{j=k\ne i}.
\]

This partition is \(S_3\)-invariant.

### DEF B3 — reversible 216↔U9^3 address codec

A chosen reversible codec is supplied in `EQUALITY_SHELL_216_TO_U9CUBE.json`.
Encode by equality pattern \(p\in\{0,1,2\}\), repeated residue \(a\in Z_9\), and nonzero relative difference \(\delta=b-a\in\{1,\ldots,8\}\), then rank

\[
R=((9p+a)8)+(\delta-1)\in\{0,\ldots,215\}.
\]

Write \(R\) in radix 6 and replace digits 0..5 by the rotor sequence \((1,2,4,8,7,5)\).
This is an exact reversible bijection with \(U_9^3\). It is a codec, not yet an algebra/group isomorphism and not automatically the same as the OPUS 24+144+48 structural decomposition.

---

## C. Cut-open 9→10 display lift

Let

\[
D_9=\{1,\ldots,9\},\qquad \widetilde D_9=\{0,1,\ldots,9\},
\]

with

\[
\pi(0)=\pi(9)=0\in Z_9.
\]

The exact endpoint/cardinality ratio is

\[
\eta=\frac{10}{9}=1.\overline1,
\qquad 9\eta=10,
\qquad 9.\overline9=10,
\qquad \log_{10}(10)=1.
\]

This is admitted as exact arithmetic/display structure. A special totient quotient, hyperinteger, physical-clock, or singularity interpretation remains **OPEN** until its source and target objects and maps are typed explicitly.

## Approval recommendation

### READY_FOR_CANON
A1–A5, B1–B2, and the cut-open endpoint map.

### READY_AS_CODEC_DEFINITION
B3, the explicit 216↔U9^3 mixed-radix bijection.

### HOLD / NEEDS FORMAL MAP
- “10-orthoplex” as intrinsic rather than visual geometry.
- privileged totient/hyperinteger interpretation of 10/9.
- physical endpoint singularity.
- magic-square status of the three 3×3 row bands without a declared scalar operation and verified invariant.
