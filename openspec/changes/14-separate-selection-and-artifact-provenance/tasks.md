# Tasks: Separate selection history from artifact execution identity

**Status:** implementation/local verification complete; offline CLI and real-target acceptance remain pending.
**Traceability:** review P1 at `0566bc7`; G2/G3 → G4–G6, P09–P19; changes 10/13 and coordinated change 15.

## 1. Provenance contract

- [x] 1.1 Introduce and document the versioned decision/G4 role envelope, strict role-set validation and explicit legacy rejection.
- [x] 1.2 Add architecture-aware identity derivation from actual restored S/F/H objects, including H branches and reference S; preserve exact code/runtime/asset checks.
- [x] 1.3 Define the refit/release envelope carrying original selection history, frozen artifact roles and the selected execution identity; coordinate runtime format with 15.

## 2. Stage integration

- [x] 2.1 Update freeze to retain all live evaluation/diagnostic/eligibility/cost checks and capture artifact identities after direct selection or veto fallback without changing the selector.
- [x] 2.2 Update G4 validation and committed-receipt verification to check both roles and immutable history without requiring unused neural runtime for S; leave other gate checks intact.
- [x] 2.3 Preflight every G5 prediction artifact against its own role before reservation, preserving prediction-before-label ordering and the one-use ledger.
- [x] 2.4 Update full-data refit and both replay modes to enforce selected execution identity and preserve exact decision/G5 lineage; keep publication fail-closed.

## 3. Regression verification

- [x] 3.1 Add synthetic freeze tests for S-only, neural direct-S, veto-to-S with blocked topic, and retained F/H; assert role maps, unchanged recipes/budgets and full selection provenance.
- [x] 3.2 Exercise real temporary Git receipts and unmocked verify/confirm for these outcomes; verify a valid first confirmation, prediction-before-label ordering and rejection of a repeat.
- [x] 3.3 Test post-freeze S with neural packages/assets unavailable in a subprocess, both refit modes and replay; verify no optional metadata access/import/load and unchanged ordered IDs/labels.
- [x] 3.4 Test changed selection lineage/costs/code, malformed or swapped roles, selected/reference recipe/bytes/runtime/assets, legacy envelopes and docs-only commits; assert failures occur at the required boundary.
- [x] 3.5 Verify migration/failure paths preserve reserved, exposed and closed synthetic ledgers and never silently rehash old evidence.
- [x] 3.6 Run `uv run pyright` and `uv run python -m unittest discover -s tests -v`; retain outputs and map tests to every acceptance scenario.

## 4. Handoff and external acceptance

- [x] 4.1 Update AGENTS.md, runbook, schema/migration guidance and a dated implementation log with actual results and remaining limitations.
- [ ] 4.2 Validate OpenSpec structure using a permitted offline validator and preserve its output separately from test and gate evidence.
- [ ] 4.3 When separately authorized real assets/target are available, retain genuine cold offline evidence for applicable S and F/H release paths under the corrected identities; keep target gates blocked until it exists and do not consume a real holdout merely to test software.

## Local evidence and acceptance boundaries

See `tests/test_followups.py`, the expanded contract/correction tests and `docs/validation/followups-*`. Synthetic neural computation is a deterministic test double; real Git receipts, the verifier, reservation/consumption logic and release controls execute normally. No real holdout was consumed. Local structural validation is not a replacement claim for full OpenSpec CLI validation. Real checkpoint/GPU/Kaggle evidence stays pending.
