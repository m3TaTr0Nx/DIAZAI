# OASIS / STAR ODK <-> DIAZAI Adapter Specification

## Source architecture

The reviewed OASIS architecture separates game-specific hooks, OGLib, STARAPIClient and hosted Web4/Web5 APIs. OGLib handles shared configuration/session/cross-game concerns. STARAPIClient is the game-agnostic C# NativeAOT HTTP, JWT, cache, queue, inventory, quest and NFT client exposed through a C ABI.

Source snapshot reviewed: `NextGenSoftwareUK/OASIS@221fbc5126cca5ab3e3ae6fc627494e0a07960f4`, especially `OASIS Omniverse/ARCHITECTURE.md` and `OASIS Omniverse/STARAPIClient/star_api.h`.

## Non-invasive seam

```text
Game callback
   -> OGLib / star_api_* operation
   -> authoritative STARAPIClient completion
   -> bounded non-blocking DIAZAI sidecar
   -> redaction and normalization
   -> deterministic 729-state address
   -> receipt chain
   -> replay, divergence and conformance
```

DIAZAI must not duplicate STARAPIClient HTTP calls, become another source of inventory/quest truth, store JWTs or refresh tokens, call provider databases around OASIS managers, or blindly reverse an external effect.

## Forward translation

`oasis_to_diazai(event)` performs operation normalization, stable pseudonymous identifiers, secret redaction, optional PII tokenization, effect classification, deterministic semantic hashing, deterministic 0-728 state addressing, and a redacted raw-event fingerprint.

The 729 state is a deterministic control-plane address. It is not a claim that a hash-derived state possesses intrinsic semantic meaning.

## Reverse translation

`diazai_to_oasis(envelope)` returns a **command proposal**, not an execution bypass. It supplies target component, suggested named STAR method or OASIS MCP tool, idempotency key, causal parent, effect class, approval requirement and payload. Read-only observations may be emitted directly. Mutations require policy approval and continue through OASIS managers.

## Initial STAR mappings

| DIAZAI operation | STAR method | Effect |
|---|---|---|
| `profile_loaded` | `star_api_restore_session` / operation callback 0 | read-only |
| `get_inventory` | background inventory request / callback 3 | read-only |
| `add_item` | `star_api_queue_add_item` | compensating |
| `pickup_with_mint` | `star_api_queue_pickup_with_mint` | nonreversible external |
| `quest_progress_from_pickup` | `star_api_queue_quest_progress_from_pickup` | compensating |
| `use_item` | `star_api_queue_use_item` | compensating |
| `start_quest` | `star_api_start_quest_then_set_active_objective` | compensating |
| `complete_quest_objective` | `star_api_complete_quest_objective` | compensating |
| `complete_quest` | `star_api_complete_quest` | compensating |
| `monster_kill` | `star_api_queue_monster_kill` | compensating |
| `send_item` | avatar/clan send methods | nonreversible external |
| `mint_nft` | `star_api_mint_inventory_nft` | nonreversible external |

## Binding pattern

The recommended C# integration is a bounded `Channel<T>` worker inside or adjacent to STARAPIClient. A post-success callback constructs a compact event and attempts `TryWrite`; it never blocks the game thread. A circuit breaker and bounded local spool handle sidecar unavailability.

Game integrations emit only facts available at the callback boundary. The C adapter writes JSONL to a local queue or invokes the C# sidecar export. It must not reimplement authentication, inventory, quests or cross-game mapping.

## Web6 and MCP

For Web6, capture exact named tools such as `web6_fahrn_solve`, `web6_memory_record` and `web6_orchestrator_invoke`: tool name, redacted arguments, response fingerprint, selected model/provider, policy decision and timing. Do not replace OASIS's typed MCP surface with an unrestricted HTTP passthrough.

## Conformance

Provider/model/version comparison contracts declare canonical fields, ignored volatile fields, numeric/timing tolerances, side-effect equivalence, compensation policy and pass/fail severity.
