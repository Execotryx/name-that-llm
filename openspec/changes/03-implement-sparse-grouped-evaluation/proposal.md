# Proposal: Implement sparse baseline and prompt-grouped nested evaluation

## Why

The release requires a competitive, reproducible CPU baseline and an evaluation runner that isolates prompt groups and prevents preprocessing and hyperparameter leakage.

## What Changes

- Build a word-plus-character TF-IDF sparse logistic S model with the original fixed grid and valid 18-class probabilities.
- Implement nested prompt-grouped CV, out-of-fold (OOF) evidence, canonical class alignment, convergence monitoring and model-fit provenance.
- Keep char-only LinearSVC and handcrafted style variants strictly diagnostic unless a pre-holdout amended protocol registers additional selection candidates.
- Deliver credible sparse-only performance and the inputs required for later F/H comparison.

## Capabilities

- **ADDED** `sparse-evaluation` — implementation requirements in [specs/sparse-evaluation/spec.md](specs/sparse-evaluation/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G2, P07, P09–P10 (sparse component), P11 metric basics; version 1.1 governs in case of ambiguity.
- **Depends on:** 01-establish-data-protocol and 02-prove-offline-cpu-inference.
- **Implementation scope:** `src/ntl/features.py, models.py, splits.py, selection.py, evaluation.py`; `tests/test_no_fold_leakage.py, tests/test_class_alignment.py, tests/test_grouped_oof.py, tests/test_metric.py`; `artifacts/runs/<run_id>/sparse_oof.csv or Parquet with ID/fold/class columns, plus fold_metrics.json, fit registry, convergence and environment logs`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Treating exploratory three-fold baseline results as formal nested evidence.
- Adding arbitrary architectures, calibrators or further `C` sweeps.
- Allowing `LinearSVC` margins to masquerade as calibrated probabilities.
