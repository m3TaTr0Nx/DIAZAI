# OASIS Integration Guide

## First integration target

Instrument one post-success callback in `STARAPIClient`, not every game and not every API at once. Recommended sequence:

1. `star_api_queue_add_item` completion;
2. `web5_quest_complete_objective` completion;
3. provider persistence result;
4. cross-game item consumption;
5. GeoHotSpot / Our World reward acceptance.

## Required adapter behavior

- generate a stable `trace_id` for the player/session/workflow;
- generate an idempotency-safe `event_id`;
- include sequence, UTC timestamp, operation, actor, target, payload, and effect class;
- emit only after the OASIS action result is known;
- never block the game loop;
- buffer locally during service outage;
- never store passwords, JWTs, wallet secrets, private keys, or unapproved personal location.

## Responsibility boundary

Game code keeps engine-specific hooks. OGLib keeps shared integration behavior. STARAPIClient remains the Web4/Web5 HTTP, authentication, retry, cache, queue, inventory, quest, and NFT client. StateTrace is a post-result evidence/control sidecar and must never execute a duplicate business mutation.

## Acceptance scenario

Run baseline and candidate traces. Inject one quantity, order, provider, duplicate, or missing-callback mutation. Pass when the chain verifies, the first material divergence is located, replay reconstructs the declared state, duplicate event IDs are ignored, and an evidence bundle is exportable.
