# DIAZAI SuperplaneALU v0.4

This release promotes the superplane from a routing table into a typed arithmetic/spectral execution model.

## Core machine

A state is

`(family, r, c, u_h, u_v, cover, color, mask8, scope, block_depth)`.

The geometric cell is

`C = r(u_v Λ) + c(u_h h_family) mod 9`.

### Arithmetic ISA

- horizontal `ADDH / SUBH`
- row translation `ADDR / SUBR`
- unit multiplication/division `MULV / DIVV`, `MULH / DIVH`
- generator exponentiation `POWV / POWH`
- Pontryagin character observation `DUAL`
- Lambda 3-step exchange `LAMBDA_FWD / LAMBDA_REV`
- structural whole-kernel recursion `LIFT / LOWER`

### Division boundary

`DIV*` rejects 0,3,6. Only `U9={1,2,4,8,7,5}` has multiplicative inverses.

### Exponentiation / duality

For `u=2^e ∈ U9 ≅ C6`, `u -> u^n` corresponds on exponent coordinates to `e -> ne mod6`.

The machine also emits the plane-local character

`K(r,c)=exp(2πi(u_v r+u_h c)/9)`.

### Routing codon

The existing 32-bit codon remains unchanged:

`[ scope2 | addr729:10 | family12 | mask8 ]`

The ALU opcode is kept in the receipt, not hidden in the spectral mask.

## New coprime-lane theorem

Exhausting all `3×6×6=108` principal generator gauges:

- exactly 36 have a complete nine-cell pairwise-coprime `y` lane;
- all 36 are Z-family gauges;
- every horizontal unit `u_h` is allowed;
- the unique row is `r = u_v^{-1} mod9`;
- there are no complete-y columns.

Canonical lane:

`111 129 138 147 156 165 174 183 192`

## Two exact 135s

`3*(1+2+...+9)=135`

and

`81+27+27=135`

for the principal-family Gram common mode. They remain separate typed invariants until an explicit natural intertwiner is proved.
