# OASIS MNDA Data Request and Benchmark Schedule

This schedule is designed to protect DIAZAI and OASIS. Counsel should place it inside the MNDA or a signed data-processing addendum.

## Minimum requested export

A de-identified JSONL or CSV extract for 5-20 representative sessions containing:

- correlation/session/trace ID;
- event/request ID;
- sequence and timestamps;
- source component and operation;
- provider, retry, and failover result;
- normalized request/response status;
- quest/inventory before-and-after summaries where available;
- error class, retry count, and compensation result;
- game/frame timing only where already logged.

## Exclude or tokenize

- passwords, refresh tokens, JWTs, API keys, wallet seeds/private keys;
- real names, emails, IP addresses, and exact personal coordinates;
- chat bodies, payment data, and unrelated proprietary content;
- raw avatar, holon, item, provider, quest, and session IDs when stable tokens preserve causality.

## Benchmark questions

1. How many events occur per workflow and at peak?
2. How often do retries or provider failovers occur?
3. How long does current incident localization take?
4. Which operations are exact, compensating, or nonreversible?
5. Which fields define business-equivalent provider responses?
6. What is the tolerated game-loop and STARAPIClient overhead?

## Return and deletion

DIAZAI returns derived benchmark reports, schema mappings, redacted divergence examples, and agreed code changes. Raw protected data is deleted or returned according to the signed schedule.
