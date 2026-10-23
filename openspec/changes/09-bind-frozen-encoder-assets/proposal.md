# Proposal: Bind frozen encoder loads to complete verified assets

## Why

Asset hashes are verified only by FrozenEncoder.__init__(). Joblib restoration skips that constructor; load() then reads external files without verifying them. A nonempty inventory can also omit every inference asset. The frozen probe artifact can therefore survive while the representation used at confirmation changes.

## What Changes

- Require a complete inference-relevant weights/config/tokenizer inventory for the one pinned encoder.
- Reverify assets on every cold load, including restored encoders, and bind the asset identity to cache, gate, decision and release evidence.
- Verify both sides of encoder packaging and support relocation without weakening identity checks.

## Capabilities

### New Capabilities

- `encoder-asset-integrity`: corrective requirements in [spec.md](specs/encoder-asset-integrity/spec.md).

### Modified Capabilities

None in the canonical spec tree, which is currently empty. This additive corrective capability supplements the existing unarchived changes; it does not replace their requirements.

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G1b, G3–G6; P04–P06, P08, P15–P19.
- **Dependencies:** Conditional on F/H use; the S-only path remains available. Coordinate identity fields with changes 10 and 13.
- **Affected files:** src/ntl/encoder.py, src/ntl/decision.py, src/ntl/locked_eval.py, src/ntl/release.py, encoder integrity tests and runbook.
- **Status:** implemented with local regression coverage; real target/campaign acceptance remains pending.

## Non-Goals

No new candidate family, hyperparameter search, source-data modification, split reseeding, automatic holdout reset or external submission. Text-only prediction, the canonical 18 labels and prompt-group isolation remain mandatory. Synthetic validation does not pass real target gates.
