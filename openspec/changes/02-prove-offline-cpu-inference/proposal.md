# Proposal: Prove offline CPU inference and submission contract

## Why

A valid attribution model is unusable unless a clean internet-disabled deployment environment can load its dependencies and process arbitrary independent test rows into a correct Parquet submission.

## What Changes

- Implement the minimum direct dependencies `pandas`, `scikit-learn`, `pyarrow` and capture the resolved runtime versions.
- Build a text-only classifier interface and a slim notebook adapter that preserves the test ID sequence without ever passing IDs or prompt IDs into the predictor.
- Run a CPU-only offline smoke test, a Parquet write/read round trip, independent-row invariance tests and realistic synthetic capacity profiles.
- Separate deployment proof from accuracy measurement and from the optional neural feasibility gate.

## Capabilities

- **ADDED** `offline-inference` — implementation requirements in [specs/offline-inference/spec.md](specs/offline-inference/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G1a, P04–P06 (mandatory CPU path); section 4 inference contract; version 1.1 governs in case of ambiguity.
- **Depends on:** 01-establish-data-protocol (G0).
- **Implementation scope:** `src/ntl/inference.py and a small reusable model/sparse pipeline factory`; `notebooks/submission.ipynb smoke/deployment adapter (evolves into final notebook at G6)`; `tests/test_inference_contract.py and tests/test_submission.py`; `artifacts/runs/<run_id>/offline_smoke.json, environment-lock.json, contract_tests.json and output schema checks`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Selecting a winning architecture on the three-row sample.
- Downloading packages or pretrained assets during scoring.
- Needing a GPU, Docker, model service, experiment tracker or the optional neural Python stack.
