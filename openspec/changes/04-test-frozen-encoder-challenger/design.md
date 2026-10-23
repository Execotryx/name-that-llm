# Design: Optionally enable frozen DeBERTa and bounded hybrid selector

## Context

A frozen contextual encoder may capture attribution cues complementary to sparse stylistic fingerprints, but neural experimentation cannot proceed without demonstrated offline load, resource budget and a bounded selection procedure.

The development and deployment contracts come from [the implementation plan](../../../IMPLEMENTATION_PLAN.md), not from these specifications alone. All 18 labels and 2,699 source rows remain unchanged. The normal predictor operates on **text only**; `prompt_id` is evaluation metadata and the locked holdout is not available to routine development code.

## Goals and Non-Goals

**Goals**

- Prove one pinned `microsoft/deberta-v3-small` checkpoint can load and extract offline on available target platform hardware.
- Train only a logistic linear probe over frozen, cached, development-only embeddings; preserve deterministic extraction settings and cache provenance.
- Run the original finite S/F/H nested architecture selector with the fixed C and blend grids if G1b passes.
- Record F/H as feasibility-ineligible if G1b fails, and continue the honest S-only path without claiming neural performance.

**Non-goals**

- Fine-tuning transformer weights in v1.
- Testing multiple checkpoints based on validation scores or requiring a 4 GB laptop GPU.
- Serving any generative LLM or adding decision-model architectures.

## Decisions

### Decision 1

Select exactly `microsoft/deberta-v3-small` at a pinned revision, subject to upfront license/asset verification; this deliberately replaces the larger original DeBERTa-base proposal, not an additional architecture search.

### Decision 2

Stage torch, transformers and tokenizer dependencies (sentencepiece only if required) and complete checkpoint/config/tokenizer files as attached offline assets; set `HF_HUB_OFFLINE=1`, `local_files_only=True`, `trust_remote_code=False`.

### Decision 3

Run `eval()` and `inference_mode()` with max sequence length 512, attention-mask-aware final-layer mean pooling including non-padding special tokens, L2 normalization, stable dtype/seed and deterministic text tokenization.

### Decision 4

Profile GPU available on target platform rather than assuming a T4; on a 4 GB local GPU begin at batch=1. Measure memory allocated/reserved, CPU RAM, cold-load, truncation and passages/s; scale to 4k/8k synthetic texts.

### Decision 5

Cache only development embeddings under a key including input hash, ID, text-view version, encoder revision, tokenizer, max length, pooling/special-token policy, dtype and code revision. Validate row order after shuffle; no locked embeddings.

### Decision 6

Fit F using logistic regression `C in {0.5,1,2,4}` on the training side of each grouped fold; no PCA, learned whitening or fold-trained transformer reuse.

### Decision 7

Blend H from aligned 18-class probability matrices using `w*p_S+(1-w)*p_F`, `w in {0,.1,...,1}`. Endpoints collapse to S/F. Do not introduce probability calibration, stacking or third candidates.

### Decision 8

Five outer folds, four inner folds: 80 probe fits and up to 176 precomputed blend combinations per outer fold (4×4×11). Inner BA chooses architecture, C and w; complex promotion requires +0.03 vs S. Within 0.005 among qualifiers: lower measured cost, fewer components, lower C, higher sparse weight.

### Decision 9

Complete-selector outer OOF and per-candidate nested OOF have different meanings and are saved separately; no outer-label-tuned weights. If G1b fails, exclude F/H with a signed reason before any score comparison.

## Interfaces and durable artifacts

- `src/ntl/encoder.py`, cache identity/validation code and isolated optional imports
- `artifacts/runs/<run_id>/neural_feasibility.json`, resource logs, pinned asset manifest and local replay evidence
- `artifacts/runs/<run_id>/frozen_probe_oof.*`, `hybrid_selector_oof.*` and aligned 18-class matrices if eligible
- `artifacts/manifests/neural_eligibility.json` even when blocked

Persist provenance (source/code/split/asset/environment hashes and explicit row IDs) wherever the referenced plan requires it. No checkpoint, notebook execution or measurement is considered complete without saved evidence.

## Workflow and dependency ordering

**Prerequisites:** 01-establish-data-protocol and 02-prove-offline-cpu-inference; compare against the G2 S baseline (03). Activate only if the registered G0 protocol permits the branch.

Implement the ordered tasks in `tasks.md`. Run acceptance scenarios from `specs/frozen-challenger/spec.md` using the same immutable split manifests and recorded environment. Do not use the public leaderboard or the final holdout to resolve implementation model choices.

## Failure and recovery

- Missing offline checkpoint/config/tokenizer, network dependency, OOM or runtime deficit makes F/H ineligible.
- A cache keyed on row indices alone is rejected; all learned folds/normalizers remain separated.
- Outer-fold evidence must not guide selection weights or permit adding other checkpoints.

## Verification policy

Use stdlib `unittest`/assertion-based tests, plus actual environment/integration executions for gates that demand them. Negative-path tests are required where specified. Preserve logs of failed attempts and distinguish blocked prerequisites from passing results.

## References

- [Implementation plan v1.1 — G1b + G3 (conditional) / P04–P06 neural path, P08–P10](../../../IMPLEMENTATION_PLAN.md)
- [OpenSpec requirement scenarios](specs/frozen-challenger/spec.md)
- [Implementation tasks](tasks.md)
