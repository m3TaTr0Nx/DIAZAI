# DIAZAI v0.6 Public Benchmark Policy

A DIAZAI performance claim must use identical captured workloads across baselines and include matched controls.

Required comparisons:

1. serving-engine default;
2. locality-only routing;
3. load-only routing;
4. cross-layer physical cost without DIAZAI spectral labels;
5. full DIAZAI;
6. DIAZAI with spectral labels shuffled;
7. matched-random route labels;
8. no-Lambda-exchange ablation.

Primary measurements: TTFT, TPOT/inter-token latency, throughput, KV hit rate, KV bytes moved, expert imbalance, migration bytes, NVLink/RDMA/PCIe traffic, power, temperature, GPU memory, and policy overhead.

No claim that the spectral/superplane layer improves performance is allowed unless its incremental effect survives these controls. Synthetic tests are proof-of-mechanism only and must not be presented as production inference benchmarks.
