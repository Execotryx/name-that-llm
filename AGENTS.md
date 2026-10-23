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
