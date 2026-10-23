# Tasks: Accept the registered Parquet string schema

**Status:** implementation and local checks complete; real campaign/target acceptance remains pending where unchecked.

**Traceability:** G0, G1a, G6; P00–P02, P05, P18–P19.

## 1. Contract and implementation

- [x] 1.1 Record both input Arrow string types and define the validated contract without changing source hashes, label set or split policy.
- [x] 1.2 Replace disconnected G0/writer checks with shared contract validation and pass the contract through smoke, bundles and replay.
- [x] 1.3 Validate nulls, ordered columns and ID identity before completing G0; keep runtime output label validation distinct from sample placeholders.

## 2. Regression verification

- [x] 2.1 Add direct prepare() tests covering string/large_string, mixed storage, invalid types, nulls, duplicate IDs and reordered IDs; exercise actual control flow rather than mocking prepare().
- [x] 2.2 Add empty/nonempty Unicode Parquet round trips and text-only inference tests using the persisted physical schema.
- [x] 2.3 Run uv run pyright and uv run python -m unittest discover -s tests -v; retain results. Run preparation with the registered originals in isolated review roots when available; do not train or consume a holdout.

## 3. Handoff

- [x] 3.1 Update runbook and dated change log with contract semantics and artifact migration policy.
- [x] 3.2 Record acceptance evidence for the fix separately from real G1a/G6 target execution; leave target gates blocked until executed.


## Acceptance evidence and limits

Implementation and synthetic checks: `tests/test_contracts.py`, `tests/test_corrections.py`, [unittest output](../../../docs/validation/corrections-unittest.txt) and [Pyright output](../../../docs/validation/corrections-pyright.txt). The registered original files additionally passed disposable G0 verification: [registered-inputs-corrections.txt](../../../docs/validation/registered-inputs-corrections.txt). No real holdout was consumed and no target deployment gate was advanced.
