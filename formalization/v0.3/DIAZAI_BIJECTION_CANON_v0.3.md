# DIAZAI Bijection / Involution / Mixed-Radix Canon v0.3

## Core primitive
For a canonical finite carrier X, reversible chart beta, and invertible state operator O, define the transported operator

O_beta = beta O beta^{-1}.

This preserves bijectivity, inverse existence, operator order, cycle type, orbit cardinalities, fixed-point counts, and conjugacy invariants.

## Master ternary state words
W_K = F3^K, |W_K| = 3^K.

For every d|K, let A_d={0,...,3^d-1}. The block codec

beta_{K,d}: F3^K -> A_d^(K/d)

groups d trits into one radix-3^d symbol and is bijective.

Thus for K=180:
3^180 = 9^90 = 27^60 = 81^45 = 243^36 = 729^30.

For K=360:
3^360 = 9^180 = 27^120 = 81^90 = 243^72 = 729^60.

These are reversible block views of the same K-trit word. A_d is an alphabet / codec for F3^d; it is not automatically the additive ring Z/(3^d)Z.

## Chart transition groupoid
C_{d->e}=beta_e beta_d^{-1}.

C_{d->d}=I,
C_{d->e}^{-1}=C_{e->d},
C_{e->f} C_{d->e}=C_{d->f}.

Any bijection O on W_K has chart realizations
O_d=beta_d O beta_d^{-1}
and
O_e=C_{d->e} O_d C_{d->e}^{-1}.

## Macro rotor
Let sigma_K be one-trit cyclic rotation. Then sigma_K^K=I.
Under width-d chart, beta_d sigma_K^d beta_d^{-1} is one block rotation of order K/d.

At K=360 the aligned macro-rotor orders are 360,180,120,90,72,60 for radix alphabets 3,9,27,81,243,729.

## 180-degree involution in the 360 clock
W_360 is set-bijective to W_180 x W_180 and 3^360=(3^180)^2.
Define H=sigma_360^180. Then H^2=I and under contiguous half-word splitting H(A,B)=(B,A).

## Character / sign bridge
For C_K=Z/KZ, chi_m(n)=exp(2*pi*i*m*n/K).
Index inversion n->-n maps chi to its conjugate / inverse.
For even K, chi_m(K/2)=(-1)^m.
Thus at K=360, index 180 is the exact half-turn sign operator in character space.

The positive integer 3^180 is not numerically -1. The rigorous bridge is: exponent/index 180 is the half-turn of the K=360 phase clock, while the master state count factors as 3^360=(3^180)^2.

## Exact non-floating phase clock
Use p=58321, primitive generator g=11.
Because 360|(p-1), omega_360=g^((p-1)/360) has exact order 360 and omega_360^180=-1 mod p.
The same field also supports primitive 180th and 60th roots.

## Local 729 nesting
A six-trit block has 3^6=729 states, so
W_180 ~= A_6^30 and W_360 ~= A_6^60.
The local DIAZAI carrier Z9^3 also has 729 states. Therefore an explicit set bijection gamma:F3^6 <-> Z9^3 may be defined, and operators transported as gamma O gamma^{-1}. This preserves invertibility without claiming the native additive laws are the same.

## Patent-facing computational method
Potentially protectable implementation components, subject to prior art and benchmark validation:
1. radix regrouping bijections beta_d;
2. conjugate operator realization O_d=beta_d O beta_d^{-1};
3. logical rotor/address transport instead of bulk data motion;
4. finite-field root-of-unity implementation without floating point;
5. reversible half-turn/sign-parity channel;
6. nested local 729 blocks inside 180/360-trit macro words;
7. deterministic inverse receipts and address recovery.

The mathematical cardinality identities are not themselves the patent target; the computational methodology and hardware/software realization are.