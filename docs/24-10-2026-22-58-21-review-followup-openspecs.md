# Review follow-up OpenSpecs 14–15

Created: 24-10-2026-22-58-21 (Asia/Qyzylorda).
Reviewed baseline: `0566bc76abfd76341d674c6d5c480dd1d5cdfb40`.

## Scope

- [14: selection/artifact provenance](../openspec/changes/14-separate-selection-and-artifact-provenance/proposal.md): preserve neural selection history while checking each frozen model against its own execution role; cover direct S wins, veto fallbacks, F/H winners, real synthetic receipts and both release modes.
- [15: active runtime dependencies](../openspec/changes/15-validate-active-runtime-dependencies/proposal.md): parse markers/extras, enforce all active version constraints and validate deterministic installed closure before optional execution; cover cycles, conflicting parents, inactive dependencies and offline failure boundaries.
- Each package includes spec-driven metadata, proposal, design, falsifiable requirements and unchecked tasks. Updated the OpenSpec index, runbook, repository guidance and earlier task lists to identify these as pending corrections rather than completed fixes.

## Evidence and limits

Local structural, task/scenario, relative-link and whitespace checks are recorded in [review-followup-openspecs.txt](validation/review-followup-openspecs.txt). These checks validate documentation only. No source/runtime implementation changed; Pyright and model tests were not rerun for this documentation change. The preceding review ran 32 passing tests and clean Pyright, but reproduced failures outside their coverage.

The OpenSpec CLI was not retried. Earlier automatic approval review rejected completion verification because the validator contacted an untrusted third-party host and transmitted data was not established. Local offline document checks do not claim full CLI validation. A permitted offline OpenSpec validation remains an explicit implementation handoff task.

No source data was changed or read for this specification work. No model training, real G5 reservation/consumption, gate advancement, external submission or push occurred. All new implementation and real-target acceptance tasks remain pending; old evidence and ledger state must be preserved.
