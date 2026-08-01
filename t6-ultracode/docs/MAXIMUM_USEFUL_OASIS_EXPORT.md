# Maximum Useful OASIS / STAR Export

## Executive answer

The maximum useful export is not a raw server dump. It is a **protected, causally complete, versioned event corpus** that lets a second team reconstruct what happened without receiving credentials or unnecessary personal information.

The preferred gold-standard package contains:

1. A 30-day event stream or 1-10 million events, whichever is smaller enough for a first controlled transfer.
2. Complete traces from normal, retry/failover, partial-failure and known-incident classes.
3. Stable pseudonymous trace, event and actor identifiers.
4. Wall-clock and monotonic timing, queue wait, network and operation duration.
5. Source component, named operation, deployed binary/package version and source commit.
6. Provider route, attempt order, retry count, failover reason and cache status.
7. Redacted payloads plus before/after state or canonical diffs.
8. Effect classification and idempotency/compensation outcome.
9. Error class and fingerprint with secrets removed.
10. A field dictionary, schema files, privacy manifest and benchmark baseline.

## Three useful levels

### Level 1 - adapter minimum

Use 5-20 complete traces. This is enough to validate field mapping, causality, secret redaction, idempotency, translation, replay and first-divergence tests. It is not enough to establish production capacity or ROI.

### Level 2 - benchmark useful

Use 10,000-100,000 events distributed across ordinary successful sessions, cache paths, retries, provider failover, duplicate delivery, known errors and cross-game handoffs. This supports throughput, latency, queue, divergence and duplicate-action benchmarks.

### Level 3 - maximum useful safe

Use a 30-day export or 1-10 million events plus selected snapshots and known-incident annotations. This supports capacity and retention sizing, provider/version drift, incident distributions, retry amplification, replay success, mean time to explain and commercial ROI estimates.

## Required files

```text
OASIS_PROTECTED_EXPORT/
├── export_manifest.json
├── events.jsonl
├── field_dictionary.csv
├── event.schema.json
├── privacy_manifest.json
├── source_versions.json
├── known_incidents.json
├── baseline_metrics.json
├── snapshots/                 # optional, redacted
└── checksums.sha256
```

## Do not export

- passwords;
- JWTs or refresh tokens;
- API keys;
- private keys, seeds or mnemonic phrases;
- raw authorization headers or cookies;
- unneeded names, email addresses or phone numbers;
- precise personal location without a separately agreed consent, retention and access policy;
- unrelated proprietary payloads.

## Recommended transfer control

Under the MNDA, use a data schedule that states permitted benchmark purposes, prohibited re-identification, allowed personnel, encryption controls, retention/deletion dates, incident notification, derived-result ownership, publication approval, and background/foreground IP treatment.
