# Proposal: Run one-time locked holdout confirmation

## Why

The only genuinely independent confirmation is a single evaluation of the previously frozen development choice. Repeated holdout comparisons would destroy the methodological safeguard.

## What Changes

- Verify sealed membership and hashes, unchanged decision artifacts and no prior holdout consumption.
- Run pre-frozen predictions, hash them before revealing labels/results, then compute selected candidate and (if distinct) registered S comparator metrics.
- Record uncertainty, per-class recalls, prespecified contradiction rules and a consumed-state ledger.
- Never reselect architecture or repair performance based on holdout results.

## Capabilities

- **ADDED** `locked-confirmation` — implementation requirements in [specs/locked-confirmation/spec.md](specs/locked-confirmation/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G5, P16; version 1.1 governs in case of ambiguity.
- **Depends on:** 05-diagnose-and-freeze-selection; a durable G0 lock must exist and G4 decision must already be immutable.
- **Implementation scope:** `src/ntl/locked_eval.py with sealed data access and state machine`; `sealed/consumption_ledger.json plus hashes of decision, inputs, artifacts, prediction matrices and source version`; `artifacts/runs/<run_id>/holdout_confirmation.json with scores, paired intervals, per-class recalls, interpretation and caveats`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Promoting a different model based on holdout ranking.
- Resetting or repartitioning a viewed holdout.
- Interpreting a negative or inconclusive 30-prompt result as proof of equivalence.
