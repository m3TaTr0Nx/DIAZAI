# DIAZAI v9.0 ML integration plan

## Layer 0 - deterministic codec
Map token/event/voxel indices to:
- Z9^3 address
- six trits
- four projective-fiber memberships
- Lambda / equality class
- rotor/stator coordinate counts
- optional 8-bit GF9-oriented control mask

## Layer 1 - observability
Attach forward hooks to open-weight Transformers and aggregate activation statistics by DIAZAI addresses/fibers.
Do not claim explanation merely because a pattern is visible.

Target reference models:
- openai/gpt-oss-20b
- Qwen/Qwen3-8B
- google/gemma-3-4b-it

## Layer 2 - feature augmentation
Concatenate or add learned embeddings of six trits / fiber IDs to hidden states.
Run ablations against ordinary positional encodings and random matched features.

## Layer 3 - structured mixer
Replace a small MLP/mixing block with an explicitly reversible or exact finite-transform module.
Measure quality, latency, parameter count, and stability.

## Layer 4 - training experiments
Train adapters first. Do not train a foundation model from scratch until an ablation demonstrates value.

## Required falsification controls
1. random permutation of all 729 addresses;
2. random four-way partition matched in size;
3. random six-trit labels;
4. ordinary base-3 positional encoding;
5. no-DIAZAI baseline.
