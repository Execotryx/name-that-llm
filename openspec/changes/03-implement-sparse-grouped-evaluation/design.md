# Design: Implement sparse baseline and prompt-grouped nested evaluation

## Context

The release requires a competitive, reproducible CPU baseline and an evaluation runner that isolates prompt groups and prevents preprocessing and hyperparameter leakage.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Build a word-plus-character TF-IDF sparse logistic S model with the original fixed grid and valid 18-class probabilities.
- Implement nested prompt-grouped CV, out-of-fold (OOF) evidence, canonical class alignment, convergence monitoring and model-fit provenance.
- Keep char-only LinearSVC and handcrafted style variants strictly diagnostic unless a pre-holdout amended protocol registers additional selection candidates.
- Deliver credible sparse-only performance and the inputs required for later F/H comparison.

**Non-goals**

- Treating exploratory three-fold baseline results as formal nested evidence.
- Adding arbitrary architectures, calibrators or further `C` sweeps.
- Allowing `LinearSVC` margins to masquerade as calibrated probabilities.

## Decisions

### Decision 1: Preserve S from the implementation plan: word `(1,2)` TF-IDF (`min_df=2`, `max_df=

Preserve S from the implementation plan: word `(1,2)` TF-IDF (`min_df=2`, `max_df=.995`, cap 150k) and char `(3,5)` TF-IDF (`min_df=2`, cap 250k); lowercase false, sublinear TF, float32 sparse storage; concatenate with unit branch weights.

### Decision 2: Use scikit-learn L2 multiclass-capable `LogisticRegression` with the pinned `saga`-compatible configuration, maximum 2,500 iterations, seed 2027, no class weighting; register `C in {0

Use scikit-learn L2 multiclass-capable `LogisticRegression` with the pinned `saga`-compatible configuration, maximum 2,500 iterations, seed 2027, no class weighting; register `C in {0.5,1,2,4}`. Verify the pinned solver/multiclass API.

### Decision 3: Fit vectorizers/IDF/scaler/classifier only on each training portion

Fit vectorizers/IDF/scaler/classifier only on each training portion. Persist training ID lists; test that a validation-only sentinel token cannot enter fitted vocabulary.

### Decision 4: Use five outer grouped folds with four inner grouped folds on outer-training rows; select sparse C by pooled inner OOF balanced accuracy, then refit once and emit outer OOF predictions for each development row

Use five outer grouped folds with four inner grouped folds on outer-training rows; select sparse C by pooled inner OOF balanced accuracy, then refit once and emit outer OOF predictions for each development row.

### Decision 5: Reindex every fitted estimator's `classes_` into the 18 lexicographically sorted exact strings before emitting probabilities

Reindex every fitted estimator's `classes_` into the 18 lexicographically sorted exact strings before emitting probabilities. Require 18 finite probabilities summing to one and deterministic tie policy.

### Decision 6: Maintain strict labels: `Per-candidate nested OOF` and `Complete-selector outer OOF` are not interchangeable

Maintain strict labels: `Per-candidate nested OOF` and `Complete-selector outer OOF` are not interchangeable. For S-only eligibility the complete selector chooses among S C values inside inner folds.

### Decision 7: Keep word-only, char-only `LinearSVC(C=1

Keep word-only, char-only `LinearSVC(C=1.0)` and stylometry experiments as fixed-setting diagnostics with their own registry entries, not candidates in the registered S/F/H decision family.

### Decision 8: Record convergence warnings, vocabulary sizes, sparse RAM usage, runtime, fold and training hashes; define one consistent convergence remedy before comparing scores

Record convergence warnings, vocabulary sizes, sparse RAM usage, runtime, fold and training hashes; define one consistent convergence remedy before comparing scores.

## Interfaces and durable artifacts

- `src/ntl/features.py`, `models.py`, `splits.py`, `selection.py`, `evaluation.py`
- `tests/test_no_fold_leakage.py`, `tests/test_class_alignment.py`, `tests/test_grouped_oof.py`, `tests/test_metric.py`
- `artifacts/runs/<run_id>/sparse_oof.csv` or Parquet with ID/fold/class columns, plus `fold_metrics.json`, fit registry, convergence and environment logs

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** 01-establish-data-protocol and 02-prove-offline-cpu-inference.

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/sparse-evaluation/spec.md` using the same immutable split manifests and recorded environment. Do not use the Kaggle leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- Any prompt overlap or validation-fitted transform invalidates the affected OOF run.
- Solver nonconvergence must be handled by the registered uniform remedy; no selective favorable-fold retries.
- An 18-class score is invalid when a true class has no support in the evaluation partition.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G2 / P07, P09–P10 (sparse component), P11 metric basics](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/sparse-evaluation/spec.md)
- [Implementation tasks](tasks.md)
