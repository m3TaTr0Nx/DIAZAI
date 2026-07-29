# DJINN Ultracode v2 - Authentic Rebenchmark

Measured in-container on 2026-07-29. Protocol: stratified 70/30 transductive node classification, seeds 1/2/3, weighted focal loss for binary tasks, and exact target booleans excluded from learned inputs.

## Audit findings

1. The legacy hinge input included `1.0 if i*k == j*j else 0.0`.
2. Only 17 of 729 states are positive hinges, so an always-negative model scores 97.668% accuracy.
3. Reproducing the legacy DJINN yielded TP=0, FP=0, FN=6, TN=214 for every seed: positive recall 0.0.
4. The legacy int8 function dequantized to float and evaluated sigmoid through `np.exp`.
5. Dense fixed attention-mask memory was omitted from the old 2.1 KB edge claim.

## Hinge result

| Model | Accuracy | Balanced accuracy | Precision | Recall | Positive F1 | MCC |
|---|---:|---:|---:|---:|---:|---:|
| Always negative | 0.9727 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Legacy DJINN reproduced | 0.9727 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| DJINN raw | 0.9621 | 0.8185 | 0.4028 | 0.6667 | 0.4818 | 0.4907 |
| MLP algebra | 0.9939 | 0.9969 | 0.8667 | 1.0000 | 0.9167 | 0.9224 |
| **DJINN Fusion** | **0.9955** | **0.9977** | **0.8889** | **1.0000** | **0.9333** | **0.9369** |
| Int8-weight Fusion | 0.9955 | 0.9977 | 0.8889 | 1.0000 | 0.9333 | 0.9369 |
| Exact symbolic | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The user hypothesis was correct: product/quotient, additive, coset and P/S/C structure materially improves the learned hinge detector. The remaining learned error is false-positive, not missed-hinge error.

## Other measured results

- coset accuracy: 0.9924, versus legacy reported 0.7489;
- additive positive recall: 1.0000;
- four-way archetype macro F1: 0.9235;
- plane accuracy: 0.9216;
- DR accuracy: 0.6578 without passing the DR answer as an input.

## Deployment profile

- 1,473 learnable parameters;
- 1,473 raw int8 weight bytes;
- 20,427 bytes including sparse relation keys and neighbor topology;
- 1.356 ms median full-lattice float inference;
- 1.380 ms median int8-weight round-trip inference.

The Python reference is int8-weight mixed precision, not end-to-end integer MCU execution. Exact-integer claims apply to the lattice, symbolic predicates, relation keys and topology indices.
