# Design: Establish data governance and sealed evaluation protocol

## Context

A small benchmark containing 2,699 responses from 150 prompts can yield optimistic author-attribution scores when responses from the same prompt leak across validation boundaries or the final holdout is repeatedly consulted.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Validate competition constraints and input artifacts, including the 18 exact labels, 149 complete prompt blocks, and the missing `p002` / `claude-fable-5` pair.
- Record immutable input hashes and an audit; create a genuinely isolated 30-prompt lock and 120-prompt development partition, with grouped outer/inner folds.
- Register the finite S/F/H candidate policy, computational budget, diagnostics, seeds, and neural feasibility eligibility before interpreting new model scores.
- Make ordinary development commands incapable of reading holdout content; require an explicit one-time release mechanism later.

**Non-goals**

- Training or choosing a model.
- Treating exploratory analyses already performed as preregistered nested-CV results.
- Pretending that a directory alone provides security against a user who can read all files.

## Decisions

### Decision 1

Use the exact original train schema `id,prompt_id,text,model`; use `text` alone for modeling and `prompt_id` only for validation grouping; never rewrite original source bytes.

### Decision 2

Use pandas/NumPy and stdlib hashlib/json; save explicit membership manifests and a `configs/protocol.json` rather than requiring YAML at runtime.

### Decision 3

Recompute class counts, IDs, prompt/model uniqueness, missingness, exact/near duplicates, 36–274 word length range; preserve all observed rows and the missing pair without repair.

### Decision 4

Before deriving splits, audit near duplicates across prompts by a fixed label-independent rule. If they create connected components, partition components rather than allowing leakage.

### Decision 5

Sort 150 prompt IDs, shuffle using `numpy.random.default_rng(2027)`, and assign first 30 to lock unless component handling necessitates a versioned alternative.

### Decision 6

Create five outer grouped development folds, four inner folds per outer train and a separate four-fold full-development selection split; validate support for all 18 classes.

### Decision 7

Enforce separate development-only loader paths and an explicit sealed ledger; record every attempted access and any evidence of past holdout exposure.

### Decision 8

Register original S logistic and conditional F/H branches before scoring; no hidden new models, seed searches, hyperparameter grids or leaderboard-feedback tuning.

## Interfaces and durable artifacts

- `artifacts/manifests/source_audit.json`, source SHA-256 hashes and `configs/labels.json`
- `artifacts/manifests/split_roles.csv`, `outer_folds.csv`, `inner_folds.csv`, `final_selection_folds.csv`
- `configs/protocol.json` with content hash and `experiment_registry.csv`
- `sealed/` storage/access ledger, excluded from the normal development input path

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** None; must be completed before any registered model selection or deployment scoring.

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/dataset-governance/spec.md` using the same immutable split manifests and recorded environment. Do not use the Kaggle leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- Abort if labels/schema differ unexpectedly, or cross-boundary near duplicates are unresolved.
- If the holdout was previously exposed, record an integrity incident; do not assert it is untouched and do not reseed to bury the exposure.
- If a group split lacks class support, repair before scoring using a versioned deterministic plan; never choose based on metric performance.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G0 / P00–P03](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/dataset-governance/spec.md)
- [Implementation tasks](tasks.md)
