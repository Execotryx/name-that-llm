# Name That LLM — implementation OpenSpecs

This directory contains **seven spec-driven OpenSpec changes** for [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) v1.1. Executable code now lives in `src/ntl/`, with local synthetic contract tests and a [runbook](../docs/runbook.md). Real-data gate acceptance remains pending; no benchmark model, sealed campaign or target platform execution is claimed.

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
