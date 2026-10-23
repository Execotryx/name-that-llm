# Tasks: Bind frozen encoder loads to complete verified assets

**Status:** implementation and local checks complete; real campaign/target acceptance remains pending where unchecked.

**Traceability:** G1b, G3–G6; P04–P06, P08, P15–P19.

## 1. Inventory and loading

- [x] 1.1 Define and validate complete supported asset layouts, required roles, shard references and canonical manifest identity.
- [x] 1.2 Add load-time verification after deserialization and a verified relocation/rebinding interface; prevent stale in-memory state after rebinding.
- [x] 1.3 Integrate preflight checks before G5 reservation and verify both source and destination during refit packaging.

## 2. Regression verification

- [x] 2.1 Add marker-only, omitted tokenizer/config, altered weights, missing shard, unlisted alternative weights and escaping-path tests.
- [x] 2.2 Serialize, mutate and restore a fake encoder; spy on loaders to prove rejection precedes loading. Add valid relocated bundle tests.
- [ ] 2.3 Exercise unchanged real pinned assets offline when available; retain separate G1b evidence and never infer real feasibility from mocked tests.
- [x] 2.4 Run Pyright and the full unittest suite, including checks that S imports no optional neural packages.

## 3. Handoff

- [x] 3.1 Update AGENTS.md where lifecycle rules change, the runbook and dated change log.
- [x] 3.2 Record which caches and neural evidence need regeneration before any untouched G5; preserve all prior attempts and consumption state.


## Acceptance evidence and limits

Implementation and synthetic checks: `tests/test_contracts.py`, `tests/test_corrections.py`, [unittest output](../../../docs/validation/corrections-unittest.txt) and [Pyright output](../../../docs/validation/corrections-pyright.txt). The registered original files additionally passed disposable G0 verification: [registered-inputs-corrections.txt](../../../docs/validation/registered-inputs-corrections.txt). No real holdout was consumed and no target deployment gate was advanced.

Unchecked tasks include real neural/target execution or real diagnostic regeneration. Their local software-check portions are complete; the external evidence portions remain pending. Preserve prior evidence and consumption state.
