# Proposal: Publish submissions only after a passing release gate

## Why

replay() writes submission.parquet before computing G6 status and returns normally when blocked. The notebook only prints the result. A simulated target run with one byte of allowed memory left a submission and completed successfully despite a blocked gate.

## What Changes

- Stage candidate output under a non-submission filename and validate all release conditions before publication.
- Make target notebook and CLI execution fail explicitly when G6 is blocked while preserving diagnostic evidence.
- Define safe handling of stale output, publication failures and interrupted replay without overwriting prior evidence.

## Capabilities

### New Capabilities

- `release-publication-control`: corrective requirements in [spec.md](specs/release-publication-control/spec.md).

### Modified Capabilities

None in the canonical spec tree, which is currently empty. This additive corrective capability supplements the existing unarchived changes; it does not replace their requirements.

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G6; P18–P19, with G5/P17 prerequisites unchanged.
- **Dependencies:** Existing 07; consumes schema contract from 08 and provenance/runtime controls from 10 and 13.
- **Affected files:** src/ntl/release.py, src/ntl/cli.py, notebooks/submission.ipynb and release failure-path tests.
- **Status:** implemented with local regression coverage; real target/campaign acceptance remains pending.

## Non-Goals

No new candidate family, hyperparameter search, source-data modification, split reseeding, automatic holdout reset or external submission. Text-only prediction, the canonical 18 labels and prompt-group isolation remain mandatory. Synthetic validation does not pass real target gates.
