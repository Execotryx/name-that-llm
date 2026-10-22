# Design: Run one-time locked holdout confirmation

## Context

The only genuinely independent confirmation is a single evaluation of the previously frozen development choice. Repeated holdout comparisons would destroy the methodological safeguard.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Verify sealed membership and hashes, unchanged decision artifacts and no prior holdout consumption.
- Run pre-frozen predictions, hash them before revealing labels/results, then compute selected candidate and (if distinct) registered S comparator metrics.
- Record uncertainty, per-class recalls, prespecified contradiction rules and a consumed-state ledger.
- Never reselect architecture or repair performance based on holdout results.

**Non-goals**

- Promoting a different model based on holdout ranking.
- Resetting or repartitioning a viewed holdout.
- Interpreting a negative or inconclusive 30-prompt result as proof of equivalence.

## Decisions

### Decision 1

Require `decision.json` immutable hash; development-trained selected artifact and, when applicable, baseline comparator; G1 contract tests and class mapping; sealed source/split hashes and zero prior score exposure.

### Decision 2

Prevent routine G2/G4 modules from loading sealed samples; implement one explicit `src/ntl/locked_eval.py` access path that checks eligibility, writes a consumption ledger and never runs hyperparameter selection.

### Decision 3

Predict each locked text independently with frozen development artifacts; serialize and hash prediction arrays before exposing ground-truth holdout labels to scoring/report code.

### Decision 4

Score exactly the selected candidate and at most one predeclared S comparator. Report exact 18-class BA, per-class recall, paired prompt bootstrap confidence intervals and conditional interpretation.

### Decision 5

If selected challenger beats S with paired interval above zero, report directional support; if interval spans zero without material reversal, report inconclusive; if challenger at least .03 BA below S or paired interval wholly below zero, report material contradiction.

### Decision 6

Always report even small negative point estimates. Contradiction categories constrain **claims**, not model choice. G6 still refits the frozen candidate unless the experiment is explicitly closed as failed.

### Decision 7

Only a mechanical crash before exposure may be retried with an incident record; after any prediction/score exposure, a rerun is a reproducibility check on a consumed lock, not independent confirmation.

### Decision 8

If earlier work exposed the lock, close with an integrity report and do not manufacture a clean confirmation by recreating a new split.

## Interfaces and durable artifacts

- `src/ntl/locked_eval.py` with sealed data access and state machine
- `sealed/consumption_ledger.json` plus hashes of decision, inputs, artifacts, prediction matrices and source version
- `artifacts/runs/<run_id>/holdout_confirmation.json` with scores, paired intervals, per-class recalls, interpretation and caveats

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** 05-diagnose-and-freeze-selection; a durable G0 lock must exist and G4 decision must already be immutable.

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/locked-confirmation/spec.md` using the same immutable split manifests and recorded environment. Do not use the Kaggle leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- Prior exposure or mismatch blocks calling results independent confirmation.
- Any holdout-driven refit/weight decision is a methodological breach; report it and retain the score as exploratory only.
- Re-running after scores have been shown never restores independence.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G5 / P16](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/locked-confirmation/spec.md)
- [Implementation tasks](tasks.md)
