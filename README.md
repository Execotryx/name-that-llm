# Name That LLM

Methodologically controlled source-model attribution for the Kaggle **Name That LLM** benchmark (18 exact labels). This repository currently contains the **implementation specification**, not a completed training system.

## Start here

**[Implementation OpenSpecs](openspec/README.md)** — seven staged, testable changes for implementing the plan. These are pending specifications, not completed work.


**[Full implementation plan (v1.1)](IMPLEMENTATION_PLAN.md)** — G0–G6 execution gates, P00–P19 tasks, canonical label controls, reproducible evaluation design, offline feasibility, acceptance criteria and the minimal technology stack (section 16).

## Chosen stack

- **Core:** Python, pandas, scikit-learn, NumPy/SciPy (compatible dependencies), pyarrow. JSON manifests and stdlib tests avoid extra infrastructure.
- **Production sparse anchor (S):** word + character TF-IDF with logistic regression; emits canonical 18-class probabilities for the original nested model-selection protocol. Character TF-IDF + LinearSVC is an *exploratory/diagnostic* comparison only.
- **Conditional neural challenger (F):** a single pinned `microsoft/deberta-v3-small` checkpoint, PyTorch, Transformers and tokenizer dependencies, executed offline on Kaggle GPU only after the neural feasibility gate. The fixed S/F probability blend (H) is considered only when F is feasible.
- **Deployment:** internet-disabled Kaggle notebook, exact `id,model` Parquet schema, independent prediction from `text` alone. Remote compute is allowed; local 4 GB GPU use is optional.
- **Out of scope for v1:** System One decision models, fine-tuning, serving frameworks, MLOps orchestrators and unregistered candidate sweeps.

## Execution order

1. **G0** audit data, register exact split/group manifest, seal the 30-prompt holdout *before* formal modeling, and freeze the candidate/budget protocol.
2. **G1a** prove CPU-only end-to-end offline inference and Parquet production. **G1b** separately establishes neural feasibility if that optional path is activated.
3. **G2/G3** run grouped nested sparse evaluation, then frozen challenger and hybrid only if G1b passes.
4. **G4** complete predeclared diagnostics and freeze `decision.json` before any holdout access.
5. **G5** consume the locked holdout once for confirmation, with no post-hoc selection.
6. **G6** refit the frozen recipe on the full eligible training set and replay an internet-disabled submission notebook.

**Scientific and release invariants:** the test file provides `id,text` only; `prompt_id` must never be a predictor feature. Do not tune to leaderboard feedback, assume the holdout is sealed without a persisted manifest, or declare an execution gate passed without logged evidence.

*Documentation-only initial commit. No claimed trained model, validation score, completed holdout, or Kaggle release.*
