# DIAZAI DJINN Ultracode v2

A leak-audited neuro-symbolic hybrid for the 729-state zero-suppressed Z9 lattice.

The v2 release corrects four scientific problems in the uploaded v1 benchmark:

1. the legacy hinge input contained the exact hinge label;
2. 17 positive hinges among 729 states made ordinary accuracy misleading;
3. the claimed integer path dequantized to float and evaluated a sigmoid with `exp`;
4. dense 729x729 attention masks were excluded from the edge memory claim.

V2 separates exact symbolic predicates from learned features, adds multiplicative/quotient/additive archetypes, P/S/C and coset fusion, uses sparse group-key attention, reports balanced metrics and packages reproducible weights and reports.

```bash
pip install -e '.[dev]'
pytest -q
python -m djinn_ultracode.benchmark --output-dir artifacts/benchmarks
```
