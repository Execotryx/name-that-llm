# Repository instructions

- Run `uv run pyright` after Python changes and `uv run python -m unittest discover -s tests -v` for changes to model, data, split, lock or release controls.
- Core inference must remain text-only and import no torch/transformers. Optional neural dependencies are loaded only by `ntl.encoder` after a pinned local asset inventory and G1b evidence.
- Preserve source rows and the canonical 18 labels. Fit vocabularies and classifiers inside training folds. Use the persisted prompt-disjoint splits.
- Registered execution requires a clean committed checkout. Do not regenerate split seeds, silently expand S/F/H or treat diagnostic variants as release candidates.
- `prepare`, `smoke`, `evaluate`, `diagnose`, `topic`, `freeze`, `confirm`, `refit` and `replay` are separate entry points. Never make normal evaluation read sealed content.
- Commit the generated decision receipt before `confirm`. Never reset a holdout ledger automatically, including after crashes. Record mechanical failures and obtain custodian incident review before any pre-exposure recovery.
- Keep Kaggle gates blocked until actual cold offline target execution and resource evidence exist. Synthetic tests establish software behavior only.
- Add a dated Markdown change log under `docs/` for every change. Creation timestamps use `dd-MM-yyyy-HH-mm-ss` in Asia/Qyzylorda.
- For new features, update this file and the runbook. Run `cargo check` for Rust changes if any Rust code is introduced.

## Corrective execution controls (08–13)

- Passing evidence uses execution identity v2: hash the executing package and bundled notebook/config/lock from their verified roots. Bind exact upstream gates, measured selection costs, runtime profile and optional asset identity. Documentation and receipt commits may differ; relevant code/runtime changes invalidate dependent evidence. Reject legacy missing identities rather than silently rehashing them.
- Persist `submission_schema.json` from the registered sample. Accept logical UTF-8 `string`/`large_string`, preserve the recorded physical field types through smoke/refit/replay, and retain exact ordered IDs and canonical predicted labels.
- Neural assets require a complete single-layout inventory, all indexed shards/config/tokenizer files, and `runtime-lock.json` with installed build and staged-wheel identities. Reverify before every cold load, after restoration and after verified rebind/copy. G5 preflights assets before reservation; later failures never reset a ledger.
- Optional runtime packages/settings are captured by the encoder after asset verification; sparse metadata capture must not import optional neural packages. Runtime/asset/view identities enter cache keys. Cross-platform/device changes require fresh validated evidence rather than implicit compatibility exceptions.
- Prefix diagnostics use original-string slices and `views-v2-preserved-prefix`; retain internal whitespace and return inputs at/below the word limit unchanged. Supersede old prefix evidence explicitly; do not change fit budgets or candidate families.
- Replay reserves an output attempt, writes only a candidate until G6 passes, then publishes the final submission. CLI/notebook must fail on blocked release. Never overwrite prior final output/evidence or automatically reconcile interrupted publication; preserve incidents and attempt history.

## Selection provenance and validated dependencies (14–15)

- Decisions/G4 use provenance envelope v3: immutable `selection_execution`, per-model `artifact_execution` roles, and `execution` as the checked selected-role alias for generic gates. Preserve receipt-bound selection evidence snapshots; do not require unused neural metadata/assets after S is frozen.
- Runtime profiles/locks use version 2 and validate the installed dependency closure with parsed markers, explicit extras and every active version constraint before optional imports. Reject legacy ambiguous provenance/unchecked locks explicitly; no silent rehash or holdout reset.
- Keep the closure traversal and prediction-model checks shared across consumers. Synthetic tests verify software control flow; real cold neural/target acceptance remains pending.
