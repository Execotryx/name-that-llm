# Proposal: Record and enforce the conditional neural runtime

## Why

environment() records only core packages. Torch, Transformers and tokenizer dependencies are omitted, so release environment checks cannot detect changes to the neural stack even when F/H is selected.

## What Changes

- Define separate sparse and neural runtime profiles with exact package and relevant execution-setting identities.
- Bind the neural profile to G1b, embeddings, evaluation, freeze, confirmation and release.
- Reject missing or changed required neural dependencies before model loading while retaining a neural-free S path.

## Capabilities

### New Capabilities

- `conditional-runtime-identity`: corrective requirements in [spec.md](specs/conditional-runtime-identity/spec.md).

### Modified Capabilities

None in the canonical spec tree, which is currently empty. This additive corrective capability supplements the existing unarchived changes; it does not replace their requirements.

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G1a/G1b, G3–G6; P04–P06, P08, P15–P19.
- **Dependencies:** Existing 02, 04 and 07; coordinates with asset identity 09 and evidence lineage 10. Neural obligations are conditional on F/H.
- **Affected files:** src/ntl/common.py, encoder.py, smoke.py, runner.py, decision.py, locked_eval.py, release.py, dependency artifacts and runtime tests.
- **Status:** implemented with local regression coverage; real target/campaign acceptance remains pending.

## Non-Goals

No new candidate family, hyperparameter search, source-data modification, split reseeding, automatic holdout reset or external submission. Text-only prediction, the canonical 18 labels and prompt-group isolation remain mandatory. Synthetic validation does not pass real target gates.
