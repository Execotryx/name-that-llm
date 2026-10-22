# Tasks: Establish data governance and sealed evaluation protocol

**Gate:** G0 · **Plan packages:** P00–P03 · **Status:** not started (documentation only).

## 1. Audit execution contract

- [ ] 1.1 P00: confirm current competition rules, allowed external checkpoints/artifacts, Kaggle internet-off scoring, CPU/GPU availability, run limit, and `id,model` Parquet contract; record evidence and unresolved assumptions.
- [ ] 1.2 Write `environment-target.json` with OS/Python/dependency versions, memory, GPU visibility and runtime target; do not import the laptop profile blindly.
- [ ] 1.3 P01: hash original CSV/Parquet bytes, audit all 2,699 rows, 18 canonical classes and 150 prompts; identify precisely the incomplete block and any duplicate/near-duplicate clusters.

## 2. Seal the data

- [ ] 2.1 P02: derive and persist deterministic 30-prompt lock / 120-prompt development role membership, with component-aware adjustment if justified before modeling.
- [ ] 2.2 Create outer 5-fold and inner 4-fold grouped split manifests plus full-development 4-fold selection splits; prove disjointness, all-class support, and complete coverage.
- [ ] 2.3 Implement development-only input adapters, a sealed content path with a one-time access ledger, and negative tests that development workers reject locked IDs.

## 3. Freeze policy and prove G0

- [ ] 3.1 P03: record fixed S/F/H candidates, conditional G1b handling, parameter grids, zero-leakage constraints, 10,000-bootstrap/100,000-permutation budgets, diagnostics, thresholds and resource ceilings.
- [ ] 3.2 Create versioned `experiment_registry.csv` and protocol hashes; flag earlier exploratory scores separately from registered evidence.
- [ ] 3.3 Run integrity/unit tests, review exposure risks, and write a G0 acceptance record. Do not mark G0 passed merely because documentation exists.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`dataset-governance` specification](specs/dataset-governance/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
