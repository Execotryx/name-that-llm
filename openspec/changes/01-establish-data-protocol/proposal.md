# Proposal: Establish data governance and sealed evaluation protocol

## Why

A small benchmark containing 2,699 responses from 150 prompts can yield optimistic author-attribution scores when responses from the same prompt leak across validation boundaries or the final holdout is repeatedly consulted.

## What Changes

- Validate competition constraints and input artifacts, including the 18 exact labels, 149 complete prompt blocks, and the missing `p002` / `claude-fable-5` pair.
- Record immutable input hashes and an audit; create a genuinely isolated 30-prompt lock and 120-prompt development partition, with grouped outer/inner folds.
- Register the finite S/F/H candidate policy, computational budget, diagnostics, seeds, and neural feasibility eligibility before interpreting new model scores.
- Make ordinary development commands incapable of reading holdout content; require an explicit one-time release mechanism later.

## Capabilities

- **ADDED** `dataset-governance` — implementation requirements in [specs/dataset-governance/spec.md](specs/dataset-governance/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G0, P00–P03; version 1.1 governs in case of ambiguity.
- **Depends on:** None; must be completed before any registered model selection or deployment scoring.
- **Implementation scope:** `artifacts/manifests/source_audit.json, source SHA-256 hashes and configs/labels.json`; `artifacts/manifests/split_roles.csv, outer_folds.csv, inner_folds.csv, final_selection_folds.csv`; `configs/protocol.json with content hash and experiment_registry.csv`; `sealed/ storage/access ledger, excluded from the normal development input path`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Training or choosing a model.
- Treating exploratory analyses already performed as preregistered nested-CV results.
- Pretending that a directory alone provides security against a user who can read all files.
