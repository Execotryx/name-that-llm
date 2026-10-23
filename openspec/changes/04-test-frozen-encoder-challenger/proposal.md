# Proposal: Optionally enable frozen DeBERTa and bounded hybrid selector

## Why

A frozen contextual encoder may capture attribution cues complementary to sparse stylistic fingerprints, but neural experimentation cannot proceed without demonstrated offline load, resource budget and a bounded selection procedure.

## What Changes

- Prove one pinned `microsoft/deberta-v3-small` checkpoint can load and extract offline on available target platform hardware.
- Train only a logistic linear probe over frozen, cached, development-only embeddings; preserve deterministic extraction settings and cache provenance.
- Run the original finite S/F/H nested architecture selector with the fixed C and blend grids if G1b passes.
- Record F/H as feasibility-ineligible if G1b fails, and continue the honest S-only path without claiming neural performance.

## Capabilities

- **ADDED** `frozen-challenger` — implementation requirements in [specs/frozen-challenger/spec.md](specs/frozen-challenger/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G1b + G3 (conditional), P04–P06 neural path, P08–P10; version 1.1 governs in case of ambiguity.
- **Depends on:** 01-establish-data-protocol and 02-prove-offline-cpu-inference; compare against the G2 S baseline (03). Activate only if the registered G0 protocol permits the branch.
- **Implementation scope:** `src/ntl/encoder.py, cache identity/validation code and isolated optional imports`; `artifacts/runs/<run_id>/neural_feasibility.json, resource logs, pinned asset manifest and local replay evidence`; `artifacts/runs/<run_id>/frozen_probe_oof.*, hybrid_selector_oof.* and aligned 18-class matrices if eligible`; `artifacts/manifests/neural_eligibility.json even when blocked`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Fine-tuning transformer weights in v1.
- Testing multiple checkpoints based on validation scores or requiring a 4 GB laptop GPU.
- Serving any generative LLM or adding decision-model architectures.
