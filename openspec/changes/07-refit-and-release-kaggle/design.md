# Design: Refit frozen recipe and release a verified Kaggle notebook

## Context

The released classifier must be a faithful full-data refit of the evaluated recipe and must pass a cold, offline Kaggle replay on real test schema without introducing inference-time dependencies on prompt context.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Refit exactly the previously selected recipe using all 2,699 labeled rows, including the former locked 30 prompts, only after G5 is closed.
- Package sparse model and optionally preverified frozen encoder with hashed dependencies and an immutable artifact manifest.
- Provide a deterministic internet-disabled Kaggle notebook that reads runtime `id,text` and writes exact `id,model` Parquet.
- Test independence, schema, realistic runtime headroom and clean restart; report completion separately from actual Kaggle submission.

**Non-goals**

- Retuning on the former holdout or Kaggle leaderboard.
- Using hidden test labels, inferred prompt IDs or class distribution constraints.
- Claiming Kaggle submission or a passing notebook run without executed evidence.

## Decisions

### Decision 1: After G5 close, refit fixed S/F/H selection on all 2,699 original rows without synthetic augmentation, removal of length outliers, label correction, new hyperparameter search or use of the former holdout for early stopping

After G5 close, refit fixed S/F/H selection on all 2,699 original rows without synthetic augmentation, removal of length outliers, label correction, new hyperparameter search or use of the former holdout for early stopping.

### Decision 2: Preserve every preselected C, tokenizer/checkpoint revision, class order, blend weight, text transform, numerical dtype, seed and inference batch policy from `decision

Preserve every preselected C, tokenizer/checkpoint revision, class order, blend weight, text transform, numerical dtype, seed and inference batch policy from `decision.json`.

### Decision 3: If F/H selected, stage only the G1b-proven local encoder plus needed torch/transformers assets; if S selected, notebook must run with core dependencies and no neural imports

If F/H selected, stage only the G1b-proven local encoder plus needed torch/transformers assets; if S selected, notebook must run with core dependencies and no neural imports.

### Decision 4: Package fitted task model separately from base pretrained assets

Package fitted task model separately from base pretrained assets. Use joblib only on trusted locally authored artifacts with SHA-256 verification; never unpickle arbitrary remote files.

### Decision 5: If rules allow attached task-fitted artifacts, publish immutable Kaggle Dataset inputs; otherwise run the fixed full-data refit inside the notebook and profile its time

If rules allow attached task-fitted artifacts, publish immutable Kaggle Dataset inputs; otherwise run the fixed full-data refit inside the notebook and profile its time. Do not train a new model based on test distribution.

### Decision 6: Notebook validates local assets and versions, resolves actual test file, sends only `text` into predictor, predicts bounded batches, restores original order after any length sort and writes `/kaggle/working/submission

Notebook validates local assets and versions, resolves actual test file, sends only `text` into predictor, predicts bounded batches, restores original order after any length sort and writes `/kaggle/working/submission.parquet` with ordered columns.

### Decision 7: Check arbitrary test sizes including 0,1,3,4000,8000 where appropriate

Check arbitrary test sizes including 0,1,3,4000,8000 where appropriate. Never hard-code the 3-row fixture, a 4,000-row hidden-test estimate, class proportions or sample placeholder labels.

### Decision 8: Cold-replay on real Kaggle kernel with internet disabled and attached inputs only; measure memory/time with target under 80% available resource and below 70% confirmed time

Cold-replay on real Kaggle kernel with internet disabled and attached inputs only; measure memory/time with target under 80% available resource and below 70% confirmed time. Record hashes, package versions and source code revision.

## Interfaces and durable artifacts

- `notebooks/submission.ipynb` final thin inference notebook
- `artifacts/manifests/release_manifest.json` with all source/model/asset/environment/output hashes
- Trusted fitted artifacts and optional packaged encoder assets as permitted by competition
- `tests/test_release_replay.py`, offline execution logs, Parquet round-trip evidence and resource profiles

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** 06-run-one-time-locked-confirmation must have completed or explicitly closed with an integrity limitation.

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/kaggle-release/spec.md` using the same immutable split manifests and recorded environment. Do not use the Kaggle leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- A cold notebook failure, hidden network fetch, wrong test rows/ID order or missing asset blocks release.
- Mismatch in final recipe vs frozen decision requires investigation, not a silent optimization.
- The full-data-refit score is not an independent re-evaluation; only the pre-refit development-trained recipe was confirmed by G5.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G6 / P17–P19](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/kaggle-release/spec.md)
- [Implementation tasks](tasks.md)
