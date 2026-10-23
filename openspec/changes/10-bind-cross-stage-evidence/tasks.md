# Tasks: Bind stage evidence to the evaluated implementation

**Status:** implementation and local checks complete; real campaign/target acceptance remains pending where unchecked.

**Traceability:** G0–G6, especially G2–G5; P03, P08–P11, P14–P19.

## 1. Identity and lineage

- [x] 1.1 Define versioned canonical execution identities and stage-specific compatibility rules; hash source from a verified root.
- [x] 1.2 Record and check upstream identities in evaluation, diagnostics, freeze, confirmation and refit/replay, including G1b and costs for F/H.
- [x] 1.3 Persist topic evidence manifests with row alignment and prediction-derived metric validation.
- [x] 1.4 Reject legacy incomplete identities with actionable migration errors; preserve prior evidence and lock state.

## 2. Regression verification

- [x] 2.1 Run synthetic OLD/NEW implementation cases and require rejection before freeze fitting; allow a docs-only commit.
- [x] 2.2 Test changed encoder, cost profile, runtime, data manifest and topic view plus edited report metrics and missing topic evidence.
- [x] 2.3 Use a temporary real Git repository and committed receipt to exercise verify_decision without mocking it; test both valid and drifted provenance before reservation.
- [x] 2.4 Test an exposed ledger cannot be reset by migration; run Pyright and the full unittest suite.

## 3. Handoff

- [x] 3.1 Document evidence schema, invalidation boundaries and incident handling in runbook/AGENTS.md plus a dated change log.
- [x] 3.2 Publish validation evidence separately from scientific gate results; do not reuse reviewed synthetic passes as real campaign acceptance.


## Acceptance evidence and limits

Implementation and synthetic checks: `tests/test_contracts.py`, `tests/test_corrections.py`, [unittest output](../../../docs/validation/corrections-unittest.txt) and [Pyright output](../../../docs/validation/corrections-pyright.txt). The registered original files additionally passed disposable G0 verification: [registered-inputs-corrections.txt](../../../docs/validation/registered-inputs-corrections.txt). No real holdout was consumed and no target deployment gate was advanced.
