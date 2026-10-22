# Design: Measure robustness, quantify uncertainty and freeze the development decision

## Context

Grouped nested CV alone does not remove bias from repeated model and diagnostic comparisons. Claims of source attribution also require uncertainty, artifact sensitivity and a complete decision frozen before holdout access.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Compute exact 18-class balanced accuracy, class recalls, provider diagnostics and confusion tables.
- Use prompt-clustered paired uncertainty and preregistered style, format, prefix and topic-proxy stress diagnostics.
- Apply only preregistered vetoes and complexity rules to development OOF; never tune weights or architectures on diagnostics or lock.
- Persist a fully specified, hashed `decision.json` and fitted development-only artifacts.

**Non-goals**

- Assuming the overlapping CV folds or individual responses are independent trials.
- Proving causal fingerprints intrinsic to base LLMs.
- Using diagnostic results to invent replacement architectures or alter thresholds post hoc.

## Decisions

### Decision 1

Compute BA as `(1/18) * sum_k(correct_k/support_k)` over all exact labels; require all classes present. Pooled outer OOF BA is primary; fold averages are descriptive.

### Decision 2

Report per-class support and recall, 18×18 true-normalized confusion matrix, class-to-provider mappings and provider BA; do not drop cross-provider errors from sibling analysis.

### Decision 3

Bootstrap 10,000 prompt groups with replacement keeping all their member responses and multiplicities; compute paired candidate differences and percentile intervals.

### Decision 4

Run 100,000 paired prompt-vector label-swaps with `(extreme+1)/(B+1)` and the same BA statistic (not mean per-prompt accuracy); Holm-adjust planned F-vs-S/H-vs-S comparisons if both eligible.

### Decision 5

Implement the nine fixed diagnostics: word-only, stylometry, length-only, format-only, no-explicit-length, format-stripped, lexical-only, openings kept/removed, and prefixes 40/80/120 words; explicitly say whether each is refit or perturbation.

### Decision 6

Build six development-only topic-proxy clusters from fixed format-stripped frozen embeddings averaged per prompt, `KMeans(n_clusters=6,n_init=50,random_state=2027)` and leave-cluster-out stress. If the required representation is unavailable, record blocked evidence; do not claim topic robustness passed.

### Decision 7

Predeclared neural vetoes: pooled topic BA at most .02 below S, no class recall >.10 worse than S, nonnegative improvement after deleting each provider in turn. These vetoes can only reject a challenger in favor of S.

### Decision 8

Use the separate full-development grouped four-fold selection and the original 0.03 promotion margin, plus per-candidate outer OOF +0.03 and vetoes. If neural blocked, choose the eligible S without pretending other candidates were compared.

### Decision 9

Seal `decision.json` with code/input/split/environment hashes, exact assets, class order, C/weight/seed/batch/precision, rationale, model artifacts, and holdout access protocol; freeze before G5.

## Interfaces and durable artifacts

- `src/ntl/diagnostics.py`, `evaluation.py`, `selection.py` and fixed diagnostic transformations
- `artifacts/runs/<run_id>/robustness_report.json`, candidate/selector score distinctions, cluster/support tables and uncertainty results
- `decision.json` with immutable hash and development-only fitted candidate/comparator artifacts
- `artifacts/manifests/g4_acceptance.json` including any blocked diagnostic and reason

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** 03-implement-sparse-grouped-evaluation; 04 only if neural G1b passed (otherwise use its recorded ineligibility).

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/robustness-and-decision/spec.md` using the same immutable split manifests and recorded environment. Do not use the Kaggle leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- If support incomplete, do not print a misleading 18-class BA.
- If neural representation is missing, topic diagnostic is blocked with scoped limitations; cannot be treated as passing robustness.
- Any post-decision candidate modification revokes confirmation eligibility and requires explicit protocol breach handling.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G4 / P11–P15](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/robustness-and-decision/spec.md)
- [Implementation tasks](tasks.md)
