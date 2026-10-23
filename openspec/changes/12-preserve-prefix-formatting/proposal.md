# Proposal: Preserve formatting in prefix-length diagnostics

## Why

The prefix transform joins split words with spaces, changing newlines, tabs, indentation and repeated spaces. A 120-word text changes under prefix-120 despite retaining every word. Character TF-IDF can respond to these changes, confounding length and formatting effects.

## What Changes

- Define prefix extraction as a slice of the original string at a Unicode whitespace-delimited token boundary.
- Preserve original content and whitespace up to the cutoff and leave texts at or below the limit unchanged.
- Version diagnostic views and invalidate affected prefix artifacts without introducing new release candidates.

## Capabilities

### New Capabilities

- `prefix-intervention-isolation`: corrective requirements in [spec.md](specs/prefix-intervention-isolation/spec.md).

### Modified Capabilities

None in the canonical spec tree, which is currently empty. This additive corrective capability supplements the existing unarchived changes; it does not replace their requirements.

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G4; P13–P15 and the unchanged diagnostic fit budget.
- **Dependencies:** Existing 05; provenance integration with 10. Required before interpreting newly generated prefix diagnostics.
- **Affected files:** src/ntl/views.py, src/ntl/diagnostics.py, view identity/cache consumers, diagnostic regression tests and runbook.
- **Status:** implemented with local regression coverage; real target/campaign acceptance remains pending.

## Non-Goals

No new candidate family, hyperparameter search, source-data modification, split reseeding, automatic holdout reset or external submission. Text-only prediction, the canonical 18 labels and prompt-group isolation remain mandatory. Synthetic validation does not pass real target gates.
