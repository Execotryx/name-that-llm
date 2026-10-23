# Name That LLM — implementation OpenSpecs

This directory contains **seven original implementation changes and six corrective changes** for [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) v1.1. Executable code now lives in `src/ntl/`, with local synthetic contract tests and a [runbook](../docs/runbook.md). Corrective changes 08–13 have implementation and local regression coverage; real target acceptance remains pending. Real-data gate acceptance remains pending; no benchmark model, sealed campaign or target platform execution is claimed.

Every change contains a proposal (`proposal.md`), design (`design.md`), delta spec (`specs/<capability>/spec.md`) and task list (`tasks.md`). Unchecked campaign tasks still require actual inputs and execution evidence. Keep changes unarchived until their gate evidence is complete.

| Order | Change | Gates | Plan tasks | Required? |
|---|---|---|---|---|
| 1 | [Establish data protocol](changes/01-establish-data-protocol/proposal.md) | G0 | P00–P03 | Mandatory |
| 2 | [Prove offline CPU inference](changes/02-prove-offline-cpu-inference/proposal.md) | G1a | P04–P06 CPU slice | Mandatory |
| 3 | [Implement sparse grouped evaluation](changes/03-implement-sparse-grouped-evaluation/proposal.md) | G2 | P07, P09–P11 sparse parts | Mandatory |
| 4 | [Test frozen encoder challenger](changes/04-test-frozen-encoder-challenger/proposal.md) | G1b, G3 | P04–P10 neural and blend parts | **Conditional** |
| 5 | [Diagnose and freeze](changes/05-diagnose-and-freeze-selection/proposal.md) | G4 | P11–P15 | Mandatory; neural tests conditional |
| 6 | [One-time locked confirmation](changes/06-run-one-time-locked-confirmation/proposal.md) | G5 | P16 | Mandatory after frozen decision |
| 7 | [Refit and release target platform](changes/07-refit-and-release-offline/proposal.md) | G6 | P17–P19 | Mandatory |

## Corrective backlog from the implementation review

These changes address the six findings against commit `a4499c7`. Task lists distinguish completed implementation/local checks from remaining real neural/target evidence. New additive capabilities supplement the existing unarchived specifications because there is no canonical `openspec/specs/` tree yet; they do not replace or relax the original methodological requirements.

| Change | Review priority | Acceptance focus | Applies to |
|---|---|---|---|
| [08 — Parquet string contract](changes/08-fix-parquet-string-contract/proposal.md) | P1 | Registered `large_string` sample passes G0; shared persisted output schema | All paths |
| [09 — Frozen encoder assets](changes/09-bind-frozen-encoder-assets/proposal.md) | P1 | Complete inventory; restored encoders reject changed assets before loading | F/H |
| [10 — Cross-stage evidence](changes/10-bind-cross-stage-evidence/proposal.md) | P1 | Changed implementation cannot reuse old evaluation/topic evidence; real receipt verifier tested | All paths |
| [11 — Fail-closed release](changes/11-fail-closed-release/proposal.md) | P1 | Blocked target replay fails execution and publishes no new final submission | All paths |
| [12 — Prefix formatting](changes/12-preserve-prefix-formatting/proposal.md) | P2 | Prefix truncation preserves original whitespace and matched diagnostic subsets | Prefix diagnostics |
| [13 — Neural runtime lock](changes/13-lock-neural-runtime/proposal.md) | P2 | Neural dependency/settings drift invalidates eligibility and dependent artifacts | F/H; S isolation also tested |

Implementation order: resolve **08** first; define **09/13** asset and runtime identities before completing neural lineage in **10**; integrate **11** with the schema and provenance contracts. Complete **12** before producing corrected prefix evidence. Sparse-only provenance work does not depend on acquiring a neural checkpoint. All applicable corrections and their required real execution evidence must be verified before dependent formal stages proceed.

Use synthetic temporary campaigns and temporary Git repositories for ledger, receipt and failure-path tests. Do not consume a real holdout to validate these controls. Preserve prior evidence; changed implementation or diagnostic views require explicit invalidation/version history, never silent rehashing or lock resets. Spec validation establishes document structure only, not passing scientific or deployment gates.

## Execution policy

1. Finish **G0 before new registered modeling**. Persist split roles and a real sealed holdout manifest. Do not mistake prior exploratory grouped metrics for preregistered evidence.
2. Pass **G1a** on an internet-disabled target CPU environment before declaring the submission route feasible.
3. Run **G2** using sparse S; investigate **G1b/G3** only if a one-checkpoint frozen encoder fits remote hardware. If G1b fails, document F/H as *not evaluated*, and continue with S-only eligibility.
4. Complete G4 robustness (record unavailable diagnostics as blocked), freeze `decision.json` and only then run the G5 lock once.
5. Refit after the lock is closed and demonstrate a clean offline G6 replay. External upload/submission is separate from release readiness.

## Technology boundaries

- Core: Python, pandas, scikit-learn, pyarrow; stdlib JSON, unittest and SHA-256. CPU deployment must not import torch.
- Optional neural: pinned `microsoft/deberta-v3-small` with torch/transformers/tokenizer dependencies; local assets only, GPU remote execution permitted.
- S is **word + character TF-IDF logistic regression**, not a silent substitution with exploratory LinearSVC. F is a frozen encoder + logistic probe; H is the registered probability blend.
- Do not add System One or any other model family to this implementation backlog. New candidate families require a separate, explicitly approved experiment protocol and untouched confirmation.
- No extra orchestration framework, serving API, tracker, Docker runtime, calibration/stacking or neural fine-tuning is required in v1.

## OpenSpec usage

The default OpenSpec workflow supports `proposal.md`, `specs/<capability>/spec.md`, `design.md` and `tasks.md`. Run `openspec validate --all`, verify the implemented controls against real gate evidence, and archive only when complete. Local synthetic verification is described in the runbook and dated change log.

Do not treat the 30-prompt sealed partition as a secure boundary merely because it is in a directory; use loader allowlists, access ledgers and recorded operator controls as described in the plan.
