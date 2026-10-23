# Proposal: Bind stage evidence to the evaluated implementation

## Why

G4 accepts G2/G3 evidence based on data identity and file hashes without requiring the same modeling implementation. A synthetic check accepted OLD_IMPLEMENTATION evaluation with NEW_IMPLEMENTATION freeze. Topic reports are accepted without a manifest binding their scores to predictions, assets and implementation.

## What Changes

- Introduce a versioned execution identity for relevant implementation, configuration, dependencies, assets and data/splits.
- Bind every stage to exact upstream evidence and enforce compatible identities before fitting, freezing or confirming.
- Give topic diagnostics a hashed evidence manifest and validate its prediction-derived metrics before applying vetoes.

## Capabilities

### New Capabilities

- `cross-stage-provenance`: corrective requirements in [spec.md](specs/cross-stage-provenance/spec.md).

### Modified Capabilities

None in the canonical spec tree, which is currently empty. This additive corrective capability supplements the existing unarchived changes; it does not replace their requirements.

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G0–G6, especially G2–G5; P03, P08–P11, P14–P19.
- **Dependencies:** Uses asset identity from 09 and conditional runtime identity from 13; sparse provenance may be implemented independently. Integrates with 11 release publication and 12 versioned diagnostic views.
- **Affected files:** src/ntl/common.py, gates.py, runner.py, diagnostics.py, decision.py, locked_eval.py, release.py and provenance tests.
- **Status:** implemented with local regression coverage; real target/campaign acceptance remains pending.

## Non-Goals

No new candidate family, hyperparameter search, source-data modification, split reseeding, automatic holdout reset or external submission. Text-only prediction, the canonical 18 labels and prompt-group isolation remain mandatory. Synthetic validation does not pass real target gates.
