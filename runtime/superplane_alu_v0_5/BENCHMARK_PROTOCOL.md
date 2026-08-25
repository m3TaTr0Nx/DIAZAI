# DIAZAI Runtime v0.5 — GPT-OSS / vLLM Benchmark Protocol

## Goal

Test whether the exact superplane/spectral routing layer adds measurable value beyond ordinary cache-locality, load-balancing, and thermal/fabric telemetry.

## Target

First concrete model: `openai/gpt-oss-20b`, while keeping the trace schema model-agnostic.

The sidecar does not modify the model's logical top-k expert choices in phases 0–3.

## Phase 0 — exact/offline correctness

Completed locally in the v0.5 release:

- SuperplaneALU arithmetic/inverse tests
- exact spectral–physical intertwiner audit
- descent group closure/inverse audit
- coprime-lane theorem audit
- deterministic min-cost matching
- receipt-chain/store tests
- synthetic replay plumbing

## Phase 1 — single-node shadow capture

Capture, without changing model execution:

- per token/layer expert IDs and router weights
- request/token/layer identity
- KV block/cache events
- physical engine/rank
- DCGM/NVML GPU resource samples

Exit gate:

- zero model-output change
- target <1% serving-throughput overhead for telemetry
- >99.99% receipt completeness

## Phase 2 — identical-trace replay

Replay the same captured workload through:

1. round-robin / linear placement
2. matched-random finite lanes
3. cache-locality only
4. load only
5. vLLM default EPLB where reconstructible
6. cross-layer cache/load/thermal/fabric cost without DIAZAI spectral features
7. full DIAZAI

Metrics:

- expert balancedness
- expert remaps/migration bytes
- KV hit rate
- KV recompute and transfer bytes
- cross-node traffic
- predicted queue time
- thermal/power exposure
- sidecar decision latency

The spectral layer qualifies only if it adds lift after the ordinary physical signals are controlled.

## Phase 3 — live advisor

Use vLLM/LMCache/DCGM as the authoritative serving/storage/telemetry systems. DIAZAI proposes:

- cache source
- physical rank/queue
- generator lane
- Lambda exchange choice
- rebalance timing

The serving stack remains authoritative.

## Phase 4 — expert-placement A/B

Integrate a controlled DIAZAI EPLB policy and compare against vLLM default EPLB.

Measure real P50/P95/P99 TTFT and inter-token latency, throughput, balancedness, migration traffic, GPU memory overhead, NVLink/RDMA traffic, and energy/token.

## Phase 5 — closed-loop governor

Enable only after replay and advisor results reproduce online.

Hard constraints:

- logical expert IDs remain immutable unless a separate model-training experiment explicitly changes semantics
- bounded decision budget
- fail-open watchdog
- shadow comparator
- deterministic receipts

## No-go criteria

Demote the spectral-control layer if matched-random partitions perform the same, gains vanish after ordinary cache/load/thermal features are controlled, decision overhead consumes the gain, or closed-loop behavior oscillates.

In that case preserve any independently valuable observability, replay, receipt, cache-governance, or placement components.
