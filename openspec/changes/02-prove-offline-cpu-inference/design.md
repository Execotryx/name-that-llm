# Design: Prove offline CPU inference and submission contract

## Context

A valid attribution model is unusable unless a clean internet-disabled deployment environment can load its dependencies and process arbitrary independent test rows into a correct Parquet submission.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Implement the minimum direct dependencies `pandas`, `scikit-learn`, `pyarrow` and capture the resolved runtime versions.
- Build a text-only classifier interface and a slim notebook adapter that preserves the test ID sequence without ever passing IDs or prompt IDs into the predictor.
- Run a CPU-only offline smoke test, a Parquet write/read round trip, independent-row invariance tests and realistic synthetic capacity profiles.
- Separate deployment proof from accuracy measurement and from the optional neural feasibility gate.

**Non-goals**

- Selecting a winning architecture on the three-row sample.
- Downloading packages or pretrained assets during scoring.
- Needing a GPU, Docker, model service, experiment tracker or the optional neural Python stack.

## Decisions

### Decision 1

Keep `pandas`, `scikit-learn`, `pyarrow` as declared direct core dependencies; capture tested scikit-learn, NumPy, SciPy, joblib, threadpoolctl and Python versions in an environment lock.

### Decision 2

Expose `fit_model(texts, labels, config)`, `TextClassifier.predict(texts)` and `predict_proba(texts)`, and `build_submission(test_frame,predictor,schema)`; grouping is the evaluation adapter's concern.

### Decision 3

For the initial vertical slice use a fixed unscored logistic TF-IDF pipeline with canonical class ordering; no pretrained encoder is needed in G1a.

### Decision 4

Keep preprocessing fitted on training partition only, preserve text exactly, accept empty strings, reject null/non-string values with an informative error, and produce correctly typed zero-row output for an empty test table.

### Decision 5

Reject duplicate/empty IDs in the submission adapter; never use IDs as predictive features. Assert independence under reorder, reverse, repetition, additional unrelated rows, ID replacements and chunk sizes 1/2/production.

### Decision 6

Use PyArrow to create `submission.parquet` with ordered UTF-8 string fields `id,model`, no extra index, original IDs and labels from the 18-class manifest.

### Decision 7

Exercise the supplied three-row `test.csv` solely as a schema fixture. Synthesize 4,000/8,000 development-derived test loads without depending on repeated-text cache hits for performance.

### Decision 8

Perform the final proof in a restarted target CPU kernel with internet disabled; benchmark time and RAM and retain at least target 70% time / 80% memory resource thresholds from the plan.

## Interfaces and durable artifacts

- `src/ntl/inference.py` and a small reusable model/sparse pipeline factory
- `notebooks/submission.ipynb` smoke/deployment adapter (evolves into final notebook at G6)
- `tests/test_inference_contract.py` and `tests/test_submission.py`
- `artifacts/runs/<run_id>/offline_smoke.json`, `environment-lock.json`, `contract_tests.json` and output schema checks

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** 01-establish-data-protocol (G0).

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/offline-inference/spec.md` using the same immutable split manifests and recorded environment. Do not use the public leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- Any runtime attempt to fetch packages, models or internet assets blocks G1a.
- A clean smoke run that writes Parquet but fails re-opening or exact ID order cannot pass.
- Numerically unstable label predictions across batching/reordering block release; report failure rather than relaxing acceptance.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G1a / P04–P06 (mandatory CPU path); section 4 inference contract](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/offline-inference/spec.md)
- [Implementation tasks](tasks.md)
