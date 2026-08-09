# DIAZAI State Machine Lab v0.1.0

Source-integrated experimental implementation of the DIAZAI state-machine architecture derived from the 2026-08-08 master workspace.

## Architecture lock

- Machine law: `M_D=(Q,Gamma,A,O,E,delta,F)`.
- Instantaneous configuration: `H_t=(a,m,p,l,r,tau,pi)`.
- Preserve the conventional Turing primitive: read one D9 symbol, write one D9 symbol, move `L/R/S`, change finite-control state.
- Project the signed unbounded tape through deterministic 729-cell pages into `(i,j,k)` and 27x27 views.
- Keep higher-order DIAZAI generator, permutation, toric, semantic, workflow and tool actions in an explicit policy/operator layer.
- Every committed transition should expose provenance and a human-readable reason.

## v0.1 contents

- Four versioned JSON contracts: hypervoxel state, port/edge, event, world transition.
- Python reference kernel and persistent 729-paged D9 Turing tape.
- Canonical-runtime discrete operators for A/B/C/Lambda, S3 permutation and toric neighbors.
- Provisional `q9(tanh)` Q/K/V projector kept explicitly non-canonical.
- Operational Artifact Forge demonstration.

The separately packaged State Machine Lab also contains the interactive HTML/CSS/JS simulator, FastAPI adapter, tests, architecture report, diagrams, PPTX and PDF artifacts. This branch is intentionally experimental pending Windows/Fabric integration validation.
