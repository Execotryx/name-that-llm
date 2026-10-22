# Proposal: Measure robustness, quantify uncertainty and freeze the development decision

## Why

Grouped nested CV alone does not remove bias from repeated model and diagnostic comparisons. Claims of source attribution also require uncertainty, artifact sensitivity and a complete decision frozen before holdout access.

## What Changes

- Compute exact 18-class balanced accuracy, class recalls, provider diagnostics and confusion tables.
- Use prompt-clustered paired uncertainty and preregistered style, format, prefix and topic-proxy stress diagnostics.
- Apply only preregistered vetoes and complexity rules to development OOF; never tune weights or architectures on diagnostics or lock.
- Persist a fully specified, hashed `decision.json` and fitted development-only artifacts.

## Capabilities

- **ADDED** `robustness-and-decision` — implementation requirements in [specs/robustness-and-decision/spec.md](specs/robustness-and-decision/spec.md).

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G4, P11–P15; version 1.1 governs in case of ambiguity.
- **Depends on:** 03-implement-sparse-grouped-evaluation; 04 only if neural G1b passed (otherwise use its recorded ineligibility).
- **Implementation scope:** `src/ntl/diagnostics.py, evaluation.py, selection.py and fixed diagnostic transformations`; `artifacts/runs/<run_id>/robustness_report.json, candidate/selector score distinctions, cluster/support tables and uncertainty results`; `decision.json with immutable hash and development-only fitted candidate/comparator artifacts`; `artifacts/manifests/g4_acceptance.json including any blocked diagnostic and reason`.
- **Exit evidence:** all requirements' acceptance scenarios pass and the gate record exists. No implementation gate is assumed complete just because these specifications have been committed.

## Out of Scope

- Assuming the overlapping CV folds or individual responses are independent trials.
- Proving causal fingerprints intrinsic to base LLMs.
- Using diagnostic results to invent replacement architectures or alter thresholds post hoc.
