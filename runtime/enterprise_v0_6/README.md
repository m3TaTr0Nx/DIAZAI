# DIAZAI Enterprise Runtime v0.6 — Public SDK Boundary

This branch is the **public-safe integration surface** for the DIAZAI inference sidecar. The full enterprise archive contains additional private IP, benchmark material, and deployment controls that are intentionally not committed to this public repository.

## Public components

- model-agnostic MoE router-event schema
- reference model profiles for gpt-oss-20b, Qwen3-30B-A3B, Mixtral-8x7B, and OLMoE-1B-7B
- shadow/replay benchmark protocol
- exact finite-state self-test boundary inherited from v0.5
- strict rule that physical routing must not alter the model's logical expert identity
- matched-random and shuffled-label controls for causal evaluation

## Release authority

`shadow` and `replay` are the default modes. `advisor` requires integration validation. Closed-loop scheduling is not production-qualified in v0.6.

## IP boundary

This public branch is **not** the complete proprietary product and does not grant a license to unpublished/private DIAZAI components. Production policy calibration, customer traces, private telemetry quantizers, unpublished hardware mappings, and invention-disclosure material remain outside this repository.

## Current scientific boundary

The exact superplane/intertwiner mathematics is separately verified. The present spectral/generator-lane preference has **not yet demonstrated causal performance lift** over the same physical cache/load/thermal/fabric optimizer under matched synthetic controls. Real MoE traces are the next evidence gate.
