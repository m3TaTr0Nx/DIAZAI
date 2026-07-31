# DIAZAI StateTrace Enterprise V1

Deterministic replay, semantic first-divergence localization, provider/model conformance, and tamper-evident evidence for AI-agent and OASIS workflows.

This branch contains three independent runtime repositories:

- `python-service/` — FastAPI + SQLite WAL;
- `node-service/` — Node.js native HTTP + JSONL;
- `web-console/` — offline/connected HTML and JavaScript console.

It also contains OASIS C/C# adapters, shared schemas, MCP tools, benchmarks, CI, Docker, documentation, and the MNDA data schedule.

Local synthetic benchmark: 10,000 OASIS-shaped events per language plus a 2,000-event loopback HTTP batch. Real OASIS capacity and ROI remain evidence-gated on de-identified logs under MNDA.
