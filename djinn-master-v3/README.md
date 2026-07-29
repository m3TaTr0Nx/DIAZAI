# DIAZAI DJINN Master Architect v3

DJINN is the **Deep Junctioned Involutional Neural Net**: a neuro-symbolic modular reasoning architecture that pairs exact finite-algebra execution with a learned residual router.

## Measured result

- 55,965 exact completion queries.
- Formula exact-set accuracy: 1.000.
- Formula throughput: 481,118 queries/s.
- Brute-force throughput: 85,774 queries/s.
- Lookup throughput: 2,629,327 queries/s.
- Unseen-modulus 43 exact-set accuracy: 1.000.
- DJINN OOD routing balanced accuracy: 0.5508, highest among the learned models included in this release.

The exact compiler is faster than brute force and far smaller/more general than the fixed lookup artifact; the lookup table remains faster. This is a narrow measured Pareto claim, not universal dominance.

## Architecture

DJINN v3 separates an authoritative Exact Symbolic Route from a Learned Residual Route for noisy, partial, or uncertain inputs. The generalized relation bank includes X/Y/Z linear superplanes, additive midpoint, and multiplicative hinge relations over arbitrary modulus. Every exact completion returns the full candidate fiber, verifies every residual, and emits a deterministic certificate digest.

Operational modules include RCE, MARS, TRAK, CAGE, MoAE, ACR, FCR-IR, FCCB, RVC, and DCC. The Z9/729 architecture remains a specialization of the generalized finite-relation runtime rather than an implicit substitute for other arithmetic domains.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[bench,dev]"
pytest -q
python -m djinn_master.benchmark --output-dir artifacts/benchmarks
uvicorn djinn_master.api:app --host 127.0.0.1 --port 8000
```

The complete release ZIP includes the Python SDK, CLI, FastAPI service, OpenAPI contract, offline/online HTML studio, generated datasets, float and int8-weight model artifacts, benchmark JSON, Hugging Face cards, diagrams, DOCX, and PDF.
