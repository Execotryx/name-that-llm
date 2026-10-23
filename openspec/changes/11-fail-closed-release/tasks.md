# Tasks: Publish submissions only after a passing release gate

**Status:** implementation and local checks complete; real campaign/target acceptance remains pending where unchecked.

**Traceability:** G6; P18–P19, with G5/P17 prerequisites unchanged.

## 1. Publication control

- [x] 1.1 Introduce attempt-specific candidate output and preflight checks for stale final files/evidence.
- [x] 1.2 Move final publication after successful schema/identity/runtime/provenance checks and use same-filesystem atomic rename.
- [x] 1.3 Add blocked/failed records and attempt-owned cleanup or quarantine on publication/evidence failure.
- [x] 1.4 Make target CLI and notebook fail on blocked outcomes while keeping a non-publishing local diagnostic route.

## 2. Regression verification

- [x] 2.1 Reproduce the one-byte memory-budget case and assert blocked evidence, no new final submission and unsuccessful target execution.
- [x] 2.2 Test time, environment, missing cold restart, schema and contract failures, plus a valid publication with exact output hash.
- [x] 2.3 Test existing final output remains unchanged; inject rename/write failures and restart with unmatched evidence.
- [x] 2.4 Execute notebook code cells against controlled replay outcomes, test CLI exit codes and both attached-model/fixed-refit routes; run Pyright and full unittests.

## 3. Handoff

- [x] 3.1 Update runbook/AGENTS.md and dated change log with publication/recovery behavior.
- [ ] 3.2 Run an actual cold offline target replay before marking G6 passed; keep synthetic control-flow verification separate.


## Acceptance evidence and limits

Implementation and synthetic checks: `tests/test_contracts.py`, `tests/test_corrections.py`, [unittest output](../../../docs/validation/corrections-unittest.txt) and [Pyright output](../../../docs/validation/corrections-pyright.txt). The registered original files additionally passed disposable G0 verification: [registered-inputs-corrections.txt](../../../docs/validation/registered-inputs-corrections.txt). No real holdout was consumed and no target deployment gate was advanced.

Unchecked tasks include real neural/target execution or real diagnostic regeneration. Their local software-check portions are complete; the external evidence portions remain pending. Preserve prior evidence and consumption state.
