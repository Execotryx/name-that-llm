# Name That LLM

Methodologically controlled source-model attribution for the **Name That LLM** benchmark (18 exact labels). The Python package implements the staged protocol, grouped model selection, diagnostics, single-use confirmation and offline submission adapter. Real benchmark execution and offline release remain gated on external inputs and target evidence.

## Start here

**[Runbook](docs/runbook.md)** — installation, commands, evidence requirements and recovery rules.

**[Implementation OpenSpecs](openspec/README.md)** — seven staged requirements. Their campaign acceptance remains pending real execution.

**[Full implementation plan (v1.1)](IMPLEMENTATION_PLAN.md)** — G0–G6 execution gates, P00–P19 tasks, canonical label controls, reproducible evaluation design, offline feasibility, acceptance criteria and the minimal technology stack (section 16).

## Corrective controls

[OpenSpec changes 08–13](openspec/README.md#corrective-backlog-from-the-implementation-review) add sample-compatible Arrow schemas, verified encoder/runtime locks, cross-stage execution identity, matched prefix diagnostics and release publication only after G6 passes. Existing evidence without these identities requires explicit migration; real target gates remain pending. See the runbook for preparation and recovery.

## Chosen stack

- **Core:** Python, pandas, scikit-learn, NumPy/SciPy (compatible dependencies), pyarrow. JSON manifests and stdlib tests avoid extra infrastructure.
- **Production sparse anchor (S):** word + character TF-IDF with logistic regression; emits canonical 18-class probabilities for the original nested model-selection protocol. Character TF-IDF + LinearSVC is an *exploratory/diagnostic* comparison only.
- **Conditional neural challenger (F):** a single pinned `microsoft/deberta-v3-small` checkpoint, PyTorch, Transformers and tokenizer dependencies, executed offline on target GPU only after the neural feasibility gate. The fixed S/F probability blend (H) is considered only when F is feasible.
- **Deployment:** internet-disabled offline notebook, exact `id,model` Parquet schema, independent prediction from `text` alone. Remote compute is allowed; local 4 GB GPU use is optional.
- **Out of scope for v1:** System One decision models, fine-tuning, serving frameworks, MLOps orchestrators and unregistered candidate sweeps.

## Execution order

1. **G0** audit data, register exact split/group manifest, seal the 30-prompt holdout *before* formal modeling, and freeze the candidate/budget protocol.
2. **G1a** prove CPU-only end-to-end offline inference and Parquet production. **G1b** separately establishes neural feasibility if that optional path is activated.
3. **G2/G3** run grouped nested sparse evaluation, then frozen challenger and hybrid only if G1b passes.
4. **G4** complete predeclared diagnostics and freeze `decision.json` before any holdout access.
5. **G5** consume the locked holdout once for confirmation, with no post-hoc selection.
6. **G6** refit the frozen recipe on the full eligible training set and replay an internet-disabled submission notebook.

**Scientific and release invariants:** the test file provides `id,text` only; `prompt_id` must never be a predictor feature. Do not tune to leaderboard feedback, assume the holdout is sealed without a persisted manifest, or declare an execution gate passed without logged evidence.

Run `uv sync --locked`, `uv run pyright` and `uv run python -m unittest discover -s tests -v`. Use `uv run ntl --help` for separate stage commands. No real trained model, benchmark score, consumed holdout or offline release is claimed by local synthetic tests.

[Readiness corrections 16–18](openspec/README.md#training-readiness-corrections-from-review-of-8fdf97a) add a verified offline runtime export, shared resource checks and actual representative capacity workloads. Run `uv run python scripts/verify_runtime.py` to detect export drift; add `--wheelhouse PATH` for an isolated local-wheel runtime proof. Real cold target G1a/G1b acceptance remains separate from implementation and local verification.
