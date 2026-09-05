# Enterprise Architecture

## Bounded contexts

1. **Mathematical kernel** — pure deterministic functions for the zero-suppressed display lift, address bijections, generators, superplanes, S3 actions, classifications, and predicates.
2. **Worldstate runtime** — maps external actions to one of 729 finite addresses and emits action-only state transitions.
3. **Control plane** — compiles requests, enforces connector and reversibility policies, issues approvals, executes adapters, and records receipts.
4. **Evidence plane** — independent event and receipt hash chains, before/after state hashes, checksums, benchmarks, and exportable artifacts.
5. **Experience plane** — Conjugate Atlas, Action-Metric Flight Deck, 4D Hypermatrix Flight Deck, and OpenAPI served from one backend contract.
6. **Model plane** — optional embeddings, retrieval, and inference adapters. Model output is evidence-bearing payload, never the source of mathematical truth.

## Production topology

```text
Browser / Agent / SDK
        │ HTTPS + OIDC
        ▼
API gateway / WAF / rate limits
        │
        ▼
DIAZAI stateless API replicas ───────► Model gateway / HF endpoint
        │                 │
        │                 └──────────► Connector workers / MCP / HTTP
        ▼
PostgreSQL (worldstate, receipts, policy, tenancy)
        │
        ├────────► object storage (artifacts, checkpoints, evidence)
        ├────────► Redis/NATS/Kafka (commands, SSE fanout, workflows)
        └────────► OpenTelemetry collector (traces, metrics, logs)
```

## Reversibility semantics

- **Exact:** captured before-image can restore the local authoritative state.
- **Compensating:** a new business action attempts to offset the first action; both remain in the ledger.
- **Read-only:** no state mutation occurred.
- **Nonreversible:** blocked by default or requires explicit approval.

A reverse operation creates a new receipt linked through `reversal_of`; history is never deleted.

## Extension ports

`StateStore`, `ReceiptStore`, `EventBus`, `ApprovalStore`, `ConnectorAdapter`, `ModelAdapter`, `ArtifactStore`, `CheckpointCodec`, `IdentityProvider`, `PolicyEngine`, `TelemetrySink`, and `SignatureProvider` are the migration seams from the executable reference to managed enterprise deployment.
