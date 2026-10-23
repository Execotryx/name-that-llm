# Tasks: Record and enforce the conditional neural runtime

**Status:** implementation and local checks complete; real campaign/target acceptance remains pending where unchecked.

**Traceability:** G1a/G1b, G3–G6; P04–P06, P08, P15–P19.

## 1. Runtime capture

- [x] 1.1 Define versioned sparse/neural profiles and metadata-only optional-package discovery.
- [x] 1.2 Capture exact package/build/install-artifact identities and applicable accelerator/numerical settings, separating enforced fields from descriptive metadata.
- [x] 1.3 Implement explicit validated-profile comparison with field-level mismatch errors and no automatic downloads.

## 2. Pipeline integration

- [x] 2.1 Bind profiles to G1b, embedding caches, evaluation, decisions, pre-G5 checks and release; integrate with change 10.
- [x] 2.2 Stage and document the optional neural lock/wheel inventory independently of the core runtime; preserve S-only operation.

## 3. Regression verification

- [x] 3.1 Test missing optional neural packages do not affect S or import torch/transformers.
- [x] 3.2 With core versions fixed, change each required neural dependency and enforced numerical setting and require preflight rejection.
- [x] 3.3 Test cache invalidation, required tokenizer dependency failure and explicit compatible-profile acceptance; ensure no loader/download executes before rejection.
- [ ] 3.4 Run Pyright and full unittests. Retain real cold offline neural profile evidence when assets/hardware are available, separately from mocked tests.

## 4. Handoff

- [x] 4.1 Update AGENTS.md where runtime rules change, runbook and dated change log with migration/invalidation policy.
- [x] 4.2 Leave F/H eligibility blocked until the pinned checkpoint and recorded target profile pass G1b; do not reopen an exposed holdout to validate runtime changes.


## Acceptance evidence and limits

Implementation and synthetic checks: `tests/test_contracts.py`, `tests/test_corrections.py`, [unittest output](../../../docs/validation/corrections-unittest.txt) and [Pyright output](../../../docs/validation/corrections-pyright.txt). The registered original files additionally passed disposable G0 verification: [registered-inputs-corrections.txt](../../../docs/validation/registered-inputs-corrections.txt). No real holdout was consumed and no target deployment gate was advanced.

Unchecked tasks include real neural/target execution or real diagnostic regeneration. Their local software-check portions are complete; the external evidence portions remain pending. Preserve prior evidence and consumption state.
