# StateTrace Benchmark Report

Generated: 2026-07-31T19:09:24Z

Workload: 10,000 synthetic OASIS-shaped events per language plus a 2,000-event loopback HTTP batch.

## Results

| Runtime | Metric | Value |
|---|---|---:|
| Python | canonicalize events/s | 87,335 |
| Python | SQLite WAL batch append/s | 14,304 |
| Python | replay events/s | 43,688 |
| Python | divergence p50 | 1.30 ms |
| Python | conformance comparisons/s | 100,026 |
| Node.js | canonicalize events/s | 128,700 |
| Node.js | JSONL append/s | 10,765 |
| Node.js | replay events/s | 148,971 |
| Node.js | divergence p50 | 0.12 ms |
| Node.js | conformance comparisons/s | 130,797 |

## Loopback HTTP

| Runtime | Batch ingest events/s | Verify latency | Integrity |
|---|---:|---:|---|
| Python FastAPI | 11,767 | 58.9 ms | PASS |
| Node HTTP | 14,589 | 81.0 ms | PASS |

## Cross-language contract

- Canonical SHA-256: `e4ac52c5a3f6eec7694c5ec1261e5a6d86331c5ceaf9f606429a1bccdef9069b`
- 729 state index: `622`
- Python/Node equality: **PASS**
- Injected semantic mutation localized at position `6000` in both runtimes.

## Interpretation

This establishes deterministic cross-language behavior, verified receipt chains, replay, semantic first-divergence, conformance, durable reference persistence, and runnable APIs.

It does not establish OASIS production capacity or ROI. No OASIS production/incident logs, provider endpoints, STARAPIClient callback, or game loop were available. Those measurements are the MNDA benchmark gate.
