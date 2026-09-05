# DJINN Master Architect v3

## Executive design

DJINN v3 is a **neuro-symbolic modular reasoning system** rather than a conventional classifier with decorative algebraic features. It uses a two-lane execution contract:

1. **Exact Symbolic Route (ESR)** for clean, typed integer state. It compiles a relation into a closed-form modular solver, returns every valid completion, and emits a residual-verification certificate.
2. **Learned Residual Route (LRR)** for noisy, partial, corrupted, or uncertain state. A neural router chooses among algebraic families while fixed residual geometry prevents unconstrained predictions.

## Why this is a material evolution beyond v2

DJINN v2 established a leak-audited Z9 classifier with toric neighborhoods and sparse relation groups. V3 generalizes the carrier from a fixed 729-node classification problem to a compiler/runtime for arbitrary moduli, while preserving the specialized Z9 superplane implementation.

The critical design change is that **known equations are executed, not approximated**. Neural components are reserved for routing, denoising, tie resolution, and incomplete-state estimation.

## Mathematical carrier

For modulus `m >= 2`, the runtime uses

```text
state = (i, j, k) in Z_m^3
```

with relation families

```text
X:     i - 2j + k = 0 mod m
Y:    4i - 5j + k = 0 mod m
Z:    7i - 8j + k = 0 mod m
ADD:   i + k - 2j = 0 mod m
HINGE: i*k - j^2 = 0 mod m
```

The Z9 specialization retains zero-suppressed display, unit/stator typing, the 729-state atlas, X/Y/Z superplanes, the common kernel, the LCM-60 scalar ladder, and the F37 phase/scalar cover.

## Exact compiler

A relation and one masked coordinate are lowered to a congruence solver. For a linear relation `a*x = b (mod m)`, let `g = gcd(a,m)`. A solution exists iff `g` divides `b`; when it exists there are exactly `g` solutions. The runtime reduces to modulus `m/g`, uses a modular inverse there, and reconstructs the complete fiber.

For the hinge with masked `k`, the compiler solves `i*k = j^2 (mod m)` using the same linear-congruence theorem. When `j` is masked, the executor enumerates only the exact quadratic fiber. Every result is rechecked by the original residual and sealed in a deterministic certificate.

## Neural router

The learned path includes:

- RCE residue and character features;
- MARS residuals for all five relation families;
- harmonic coordinates over the active modulus;
- ring-type features for units, zero divisors, and zero;
- gcd and coset features;
- dual 36/60 phase features;
- five arithmetic experts;
- CAGE gating;
- reversible coupling blocks;
- TRAK fixed residual-prior routing.

The fixed prior restricts output to the algebraically nearest relation family. The neural network resolves ties and uncertainty inside that admissible set.

## Runtime pipeline

```text
ingest
  -> canonical typed state
  -> residue/character encoding
  -> exact residual bank
  -> route and policy decision
  -> relation IR
  -> exact candidate execution
  -> residual verification
  -> CINDERS receipt
  -> API, edge, or workflow adapter
```

## Enterprise boundary

DJINN is a sidecar and compiler layer. It does not replace general-purpose transformers, graph stores, workflow engines, or symbolic solvers. It adds a compact exact finite-algebra execution plane, a learned uncertainty route, and evidence suitable for audit and replay.

## Deployment strata

- Python reference: authoritative semantics and benchmarks.
- FastAPI service: completion, inspection, model metadata, and certificates.
- Hugging Face package: model card, dataset card, weights, benchmark JSON, and reproducibility commands.
- PyTorch export/torchao path: production quantization and graph capture.
- ONNX/ExecuTorch path: portable inference after operator compatibility validation.
- MLIR dialect path: future FCR-IR lowering to affine, arithmetic, LLVM, WASM, and accelerator targets.
- FPGA/ASIC path: one-hot address decoder, congruence unit, relation bank, and receipt hash engine.

## Scientific boundary

This release demonstrates exact completion and selected learned baselines on a generated finite-algebra benchmark. It does not prove universal neural superiority, language-model superiority, or superiority over every symbolic algebra system.
