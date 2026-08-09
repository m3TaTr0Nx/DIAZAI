# CINDERS-NL Open-Weight Inspector — private timestamp branch

Timestamp intent: 2026-08-09, pending founder approval before any merge/public promotion.

This branch records the next validation phase only. It does not claim trained-model benefit yet.

## Current validated local basis
- 729/729 canonical address round-trips.
- CINDERS exact reversible composition validated through C27/C81 campaigns.
- OPUS corpus: 108 right + 108 left variants.
- X self-reversal; Y/Z exchanged-sector relation validated on supplied generator families.
- 243 tagged incidences -> 189 unique support, with 27 common core + 162 exterior support.

## Open-weight inspector target
Use Apache-2.0 open-weight causal LMs such as HuggingFaceTB/SmolLM2-135M first, then SmolLM2-360M and Qwen/Qwen2.5-0.5B where compute permits.

Inspector protocol:
1. Load model weights without destructive modification.
2. Capture Q/K/V/O and MLP projection tensors per selected layer.
3. Partition compatible tensor axes into triads / 27 / 81 / 729 windows.
4. Apply candidate CINDERS operators as reversible sidecar transforms, initially on copied weights and/or activations.
5. Measure exact inverse reconstruction, Frobenius change, Gram preservation, singular spectrum, row/column cosine orthogonality, condition number, spectral entropy, triality/coset mixing, and multivector-grade aggregates.
6. Compare independent XYZ, X+(Y/Z) spinor, nonlinear-conjugated CINDERS-NL, random orthogonal/permutation controls, and identity.
7. Run forward grading: perplexity/logit KL/top-k agreement on a fixed prompt corpus before vs transformed vs restored.
8. Only after non-destructive inspection passes, consider LoRA/adapter or training experiments.

## Claim boundary
A basis rotation can preserve selected Gram/singular properties without preserving model function unless compensating transforms are applied consistently across connected layers. Therefore a weight-space inspector result is not itself evidence of improved model quality.

## HF execution status
Hugging Face account authentication was confirmed. Model metadata for SmolLM2-135M, SmolLM2-360M and Qwen2.5-0.5B was retrieved. Remote HF Jobs execution was attempted from ChatGPT, but the connector returned `Tool hf_jobs not found`; no remote weight benchmark result is claimed from that failed invocation.
