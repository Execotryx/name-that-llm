# Corrective controls implementation (OpenSpec 08–13)

Created: 24-10-2026-04-31-14 (Asia/Qyzylorda).

## Changes

| Change | Implemented behavior | Verification |
|---|---|---|
| 08 | A shared persisted schema accepts string/large_string and preserves sample physical types through smoke, refit and replay. Preparation rejects invalid types/nulls/IDs before completed manifests. | Direct preparation and Unicode/empty Parquet cases; registered originals through a disposable committed source snapshot. |
| 09 | One complete weights/config/tokenizer inventory, indexed shards and runtime lock; cold loads verify after deserialization, rebind and copy. G5 preflights before reservation. | Mutated restored weights rejected before loader import; incomplete/escaping/alternative layouts rejected; valid local restored load and relocation exercised with synthetic loader fixtures. |
| 10 | Execution identity v2 resolves the actual package root and binds code/notebook/config/lock, runtime, optional assets and upstream gates/costs. Topic evidence includes exact rows/clusters/inner folds/selections/predictions and recomputed metrics. | Stale code/cost/asset/runtime/view/report checks; actual temporary Git receipt; docs-only commit accepted; code drift denied; synthetic one-use confirmation stays consumed. |
| 11 | Replay reserves a fresh attempt, stages candidate output, publishes final output only on passing G6, and records blocked/failure/incident evidence. Notebook and CLI raise on blocked status. | Resource/cold/target/contract failures, successful publication, stale output, rename and evidence-write failures; both refit routes remain covered. |
| 12 | Prefixes are literal original-string slices; whitespace is preserved and at/below-limit texts are unchanged. View version is bumped and subsets carry exact IDs. | Empty/whitespace/Unicode/code/newline/tab cases, exact boundaries, matched synthetic diagnostic pipeline and stale-view rejection. |
| 13 | Metadata-only core runtime and conditional neural package/build/settings identity; new local asset-lock helper records staged wheel hashes without downloads. Runtime identity enters caches, gates and bundles. | Sparse import isolation, package/settings drift, missing dependency before optional import, runtime cache identity, and complete local wheel-lock checks. |

## Validation

- `uv run pyright`: output in [corrections-pyright.txt](validation/corrections-pyright.txt).
- `uv run python -m unittest discover -s tests -v`: output in [corrections-unittest.txt](validation/corrections-unittest.txt).
- `uv run python tests/verify_registered_inputs.py ../project_sources`: output in [registered-inputs-corrections.txt](validation/registered-inputs-corrections.txt). It uses a disposable committed source snapshot, runs preparation only and deletes its temporary artifacts.
- Local OpenSpec package/task/scenario/link/whitespace checks and notebook code parsing are recorded in [corrections-structure.txt](validation/corrections-structure.txt).

Final local results: 32 tests passed in 36.283 seconds; Pyright reported zero errors/warnings. Registered-input G0 verification accepted the unchanged source hash and `large_string` fields, produced 2,159 development rows and 30 locked prompts, and created no consumption ledger. Local document checks passed with 53 completed tasks, four pending external-evidence tasks and 43 acceptance scenarios. `git diff --check` passed.

## Evidence boundaries and migration

The canonical source CSV/Parquet bytes, 18-label manifest, split seed/allocation policy, model families and search/diagnostic budgets are preserved. New artifact identities deliberately reject legacy incomplete evidence; no automatic manifest rehash, compatibility exception or holdout reset is provided. A new tested platform/device profile requires fresh bound evidence before use.

Real checkpoint acquisition/license verification, real neural numerical equivalence and hardware feasibility, real prefix diagnostics, and cold offline Kaggle replay remain pending. Checkboxes for tasks requiring that evidence remain unchecked. No real training/selection, holdout confirmation or external submission was performed. Synthetic target flags validate control flow only.

The OpenSpec CLI was not retried: earlier automatic approval review rejected completion verification because it contacted an untrusted third-party host and the transmitted data was not established. Local document checks are used for this change; the earlier printed CLI result is not represented as a fresh validation run.
