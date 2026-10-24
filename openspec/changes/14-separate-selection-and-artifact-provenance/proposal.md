# Proposal: Separate selection history from artifact execution identity

## Why

Review of `0566bc76abfd76341d674c6d5c480dd1d5cdfb40` found a **P1** regression. `freeze()` captures `execution(encoder)` for the neural-enabled selection run and writes it into the decision/G4 even when S wins directly or replaces a challenger after a veto. S artifacts contain no encoder. `verify_decision()` derives `execution(model_encoder(selected))`, rejects the otherwise valid decision as changed, and prevents G5/refit. The existing end-to-end test exercises only S-only eligibility.

## What Changes

- Give selection history and each frozen artifact distinct, explicitly versioned provenance roles.
- Keep exact G1a/G1b, evaluation, diagnostic, topic and cost bindings at freeze; carry the verified selection history forward unchanged.
- Check each artifact against its own architecture, recipe, hash and execution identity at confirmation and refit; replay checks the selected recipe's applicable identity.
- Exercise direct S wins, veto fallbacks, and retained F/H with real synthetic Git receipts and one-use ledgers.

## Capabilities

### New Capabilities

- `selection-artifact-provenance`: [requirements and acceptance scenarios](specs/selection-artifact-provenance/spec.md).

### Modified Capabilities

None in the canonical tree, which is absent. This additive correction supplements unarchived changes 10 and 13, specifying the identity roles required by their existing guarantees.

## Impact

- **Traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G2/G3 evidence through G4–G6; P09–P19.
- **Dependencies:** changes 05–07, 09–11 and 13. Coordinate the runtime profile format with change 15; do not weaken execution equality to repair the mismatch.
- **Affected files:** `src/ntl/provenance.py`, `decision.py`, `gates.py`, `locked_eval.py`, `release.py`, inference helpers, synthetic integration tests and runbook.
- **Applicability:** schema/consumer correction is mandatory; neural-selection cases apply when F/H are eligible. S-only behavior remains supported.
- **Status:** implemented with local synthetic verification; real target acceptance remains pending.

## Non-Goals

No candidate, tuning budget, promotion threshold, veto, data row, canonical label, split or inference-input change. No real holdout access, automatic ledger reset, historical evidence relabeling or external submission. Synthetic passes do not establish neural performance or target feasibility.
