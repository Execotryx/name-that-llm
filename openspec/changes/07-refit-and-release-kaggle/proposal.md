# Proposal: Refit frozen recipe and release a verified Kaggle notebook

## Why

The released classifier must be a faithful full-data refit of the evaluated recipe and must pass a cold, offline Kaggle replay on real test schema without introducing inference-time dependencies on prompt context.

## What Changes

- Refit exactly the previously selected recipe using all 2,699 labeled rows, including the former locked 30 prompts, only after G5 is closed.
- Package sparse model and optionally preverified frozen encoder with hashed dependencies and an immutable artifact manifest.
- Provide a deterministic internet-disabled Kaggle notebook that reads runtime `id,text` and writes exact `id,model` Parquet.
- Test independence, schema, realistic runtime headroom and clean restart; report completion separately from actual Kaggle submission.

## Capabilities

- **ADDED** `kaggle-release` — implementation requirements in [specs/kaggle-release/spec.md](specs/kaggle-release/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G6, P17–P19; version 1.1 governs in case of ambiguity.
- **Depends on:** 06-run-one-time-locked-confirmation must have completed or explicitly closed with an integrity limitation.
- **Implementation scope:** `notebooks/submission.ipynb final thin inference notebook`; `artifacts/manifests/release_manifest.json with all source/model/asset/environment/output hashes`; `Trusted fitted artifacts and optional packaged encoder assets as permitted by competition`; `tests/test_release_replay.py, offline execution logs, Parquet round-trip evidence and resource profiles`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Retuning on the former holdout or Kaggle leaderboard.
- Using hidden test labels, inferred prompt IDs or class distribution constraints.
- Claiming Kaggle submission or a passing notebook run without executed evidence.
