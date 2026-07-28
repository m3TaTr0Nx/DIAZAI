# DIAZAI × OASIS StateTrace V1

A production-oriented reference pilot for attaching DIAZAI deterministic state, replay, canon, conformance, and edge reconciliation to the public OASIS/STAR stack.

## Implemented

- versioned OASIS/STAR event envelope;
- deterministic `OASIS event -> 729-state` addressing;
- append-only CINDERS-style receipts;
- exact replay and first-divergence localization;
- exact, compensating, and nonreversible action classes;
- provider conformance comparisons for HyperDrive/COSMIC adapters;
- offline edge queue with exactly-once ingestion;
- append-only canon entries;
- C# STARAPIClient sidecar adapter;
- interactive 27×27 control UI;
- Hugging Face Static Space preview.

## Run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest
python -m diazai_oasis.cli serve --port 8765
```

Open `http://127.0.0.1:8765` and `http://127.0.0.1:8765/docs`.

## OASIS integration seam

StateTrace does not replace STARAPIClient. OASIS deliberately keeps game hooks small while STARAPIClient owns HTTP, caching, queues, minting, and background workers. StateTrace subscribes only after a successful STAR operation and writes evidence to a separate non-blocking sidecar.

Recommended first joint pilot: one ODOOM/OQuake/Our World cross-world quest with deterministic replay and an injected divergence.

## Status

Tested reference pilot, not a completed OASIS production integration or certification. Live endpoints, credentials, game binaries, and provider-specific compensation policies must be supplied by the partnership team.
