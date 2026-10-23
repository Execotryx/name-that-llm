# Implementation and simplicity review

Created: 24-10-2026-01-55-22 (Asia/Qyzylorda)

## Scope and implementation

Implemented the seven OpenSpec capabilities as a small `ntl` Python package. Added immutable source auditing, canonical labels/provider mapping, development allowlists and persisted nested grouped folds; sparse S, optional local frozen F and H; conditional uncertainty, diagnostics and topic-proxy stress; decision freezing with a committed Git receipt; single-use confirmation; exact post-confirmation full-data refit and a thin offline notebook.

Core runtime dependencies remain pandas, scikit-learn and pyarrow with their resolved transitive packages. `uv.lock` and `requirements-runtime.txt` record locally resolved versions, not a validated deployment environment. Added Pyright as required by repository instructions. No orchestration service, API, model-family expansion, neural fine-tuning, Docker requirement or Ollama dependency was introduced.

Registered execution requires a clean committed checkout. Original benchmark inputs, fitted artifacts and holdout material are absent. Synthetic tests use temporary directories and explicitly synthetic gate fixtures; they create no real G0–G6 passing evidence.

## Simplicity review cycle 1

Critique: duplicating integrity/persistence code across stages would make provenance checks diverge. Addressed with shared JSON/hash/file-verification primitives and a narrow evidence validator. Separate entry points retain the methodological boundaries without an orchestration framework.

Critique: repeated sparse and probe component refits for selector/candidate outputs would inflate computation. Addressed by deduplicating component configurations per outer fold, and reusing outer sparse artifacts for prefix perturbations. Diagnostic controls remain outside selection.

## Simplicity review cycle 2

Critique: recomputing externally pretrained embeddings in each inner fit adds cost without new information. Addressed with development-only identity-keyed caches and evaluator-owned aligned embedding arrays. The deployed classifier retains only the frozen encoder/probe, never a response lookup cache.

Critique: pickling the pretrained encoder repeatedly and storing absolute asset paths would complicate release portability. Addressed by excluding loaded model/tokenizer state from serialization and resolving packaged local encoder assets at replay.

Critique: separate hand-maintained class orderings risk silent probability mistakes. Addressed with one canonical module, generated JSON manifest and explicit column reindexing.

## Simplicity review cycle 3

Critique: extra reference fits in prefix diagnostics violate the fixed budget. Addressed by reusing G2 outer S models; the primary perturbation and fixed-C refit sensitivity analysis remain explicitly distinguished.

Critique: format-stripped and lexical-only views initially duplicated behavior. Addressed with separate deterministic formatting removal and lexical extraction.

Critique: all-empty/pruned diagnostic vocabularies could drop or reject valid rows. Addressed with a TF-IDF subclass that contributes a zero column when no terms survive, yielding an intercept-only classifier if both branches are empty. It preserves every row and adds no signal.

Critique: assuming attached fitted artifacts were permitted would leave a deployment gap. Addressed with one bundle manifest supporting attached-model and fixed-refit notebook modes; both use the identical frozen recipe.

## Final review

No further actionable simplification was identified without weakening gate, isolation, independent-inference or provenance requirements. This is a bounded review conclusion, not a claim that code is perfect. Frozen membership/recipe changes require explicit versioned amendments rather than implicit convenience flags.

## Validation and blockers

Validation commands: `uv run pyright`; `uv run python -m unittest discover -s tests -v`; `openspec validate --all`. Durable outputs are in `docs/validation/`. Integration tests cover the full synthetic sparse nested evaluation, artifact diagnostics, blocked topic disclosure, final development selection/freeze, sealed prediction-before-label ordering, one-use consumption, and full-data-shaped refit/replay. Parquet/independence tests include empty/Unicode/code/long strings and varied row counts.

An initial CSV fixture failure came from Windows newline translation in the test writer; the lossless parser was correct and the fixture now writes exact newlines. A synthetic constant-feature diagnostic initially failed the prescribed convergence gate; the test fixture was improved to exercise nondegenerate length variation while unresolved real convergence still aborts. Missing synthetic provenance fields and a test-local variable placement were fixed before final validation.

Real campaign gates remain blocked: missing source CSV/Parquet inputs; no real sealed split; no verified deployment environment/restart/profile; no optional checkpoint revision/assets/license evidence; no real OOF/diagnostics/frozen decision/confirmation/refit. Topic diagnostics are explicitly blocked without a proven representation. Public competition overview confirms output/metric/offline nine-hour limits; detailed rules remain reCAPTCHA-blocked and attached-task-artifact permission is unverified. The receipt binds a decision to Git history; it is not an independent custodian signature. Separate paths/allowlists are accident controls, not an OS access boundary. Cold-restart flags remain operator assertions alongside target logs. No external upload or submission was performed.

Sources checked for implementation compatibility: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html ; https://huggingface.co/docs/transformers/main/en/installation .

Final recorded results: 16 unittest cases passed (71.230 seconds); Pyright reported zero errors and warnings; all seven OpenSpec changes validated; notebook code cells parsed successfully; git diff --check passed. The Windows native peak-memory handle ABI was corrected and exercised by the release replay integration test. A final focused nested/diagnostic/freeze check covers the explicit G3 eligibility evidence handoff.
