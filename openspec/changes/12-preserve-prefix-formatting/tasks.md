# Tasks: Preserve formatting in prefix-length diagnostics

**Status:** implementation and local checks complete; real campaign/target acceptance remains pending where unchecked.

**Traceability:** G4; P13–P15 and the unchanged diagnostic fit budget.

## 1. Transform and identity

- [x] 1.1 Implement the exact original-string slice semantics, retaining registered 40/80/120 limits and existing word-count eligibility.
- [x] 1.2 Bump view identity and propagate it to cache/diagnostic manifests; define which artifacts are superseded.
- [x] 1.3 Keep frozen perturbation and refit controls separate with matched subset IDs and an explicit semantic-information caveat.

## 2. Regression verification

- [x] 2.1 Test exactly-n and fewer-than-n inputs remain identical, including trailing spaces, indentation, tabs, blank lines and Unicode whitespace.
- [x] 2.2 Test more-than-n inputs equal the expected source slice and every result is a literal source prefix.
- [x] 2.3 Test paired row identity, class support, refit flags and stale-view rejection without expanding fit budgets.
- [ ] 2.4 Run Pyright and full unittests; regenerate only eligible pre-exposure diagnostics under recorded amendment/version history.

## 3. Handoff

- [x] 3.1 Update the runbook, interpretation notes and dated change log; retain prior reports as superseded.
- [x] 3.2 Require fresh diagnostic evidence for acceptance without changing frozen holdout membership or claiming a second independent confirmation.


## Acceptance evidence and limits

Implementation and synthetic checks: `tests/test_contracts.py`, `tests/test_corrections.py`, [unittest output](../../../docs/validation/corrections-unittest.txt) and [Pyright output](../../../docs/validation/corrections-pyright.txt). The registered original files additionally passed disposable G0 verification: [registered-inputs-corrections.txt](../../../docs/validation/registered-inputs-corrections.txt). No real holdout was consumed and no target deployment gate was advanced.

Unchecked tasks include real neural/target execution or real diagnostic regeneration. Their local software-check portions are complete; the external evidence portions remain pending. Preserve prior evidence and consumption state.
