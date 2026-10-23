# Tasks: Refit frozen recipe and release a verified offline notebook

**Gate:** G6 · **Plan packages:** P17–P19 · **Status:** code implemented; local synthetic verification available; real campaign acceptance pending.

## 1. Refit selected recipe

- [ ] 1.1 P17: verify G5 closed and selected `decision.json` unchanged, then train fixed recipe on all 2,699 labeled rows with all 18 labels, retaining missing pair as missing.
- [ ] 1.2 Refit training-only vocabulary/IDF and classifier on full data; for F/H, reuse pinned frozen encoder and regenerate full-training embeddings only now.
- [ ] 1.3 Save trusted artifact hashes, code and dependency/environment lock; test class order and reload equality.

## 2. Build offline submission notebook

- [ ] 2.1 P18: load only permitted local artifacts, resolve runtime `test.csv`, validate `id,text` and call text-only predictor; do not run CV or tune.
- [ ] 2.2 Predict with bounded batches and order restoration, then write exact UTF-8 `id,model` Parquet in the runtime working directory.
- [ ] 2.3 Reopen with pyarrow, assert row count, ID uniqueness/order, no extra columns or index, valid 18 labels and no nulls.

## 3. Verify release

- [ ] 3.1 P19: restart-and-run-all with target platform internet disabled; test supplied 3-row fixture plus 1-row, shuffled and scaled synthetic tests.
- [ ] 3.2 Benchmark 4k/8k workloads and cold-start/refit allowance, peak RAM/VRAM and budget reserve; ensure no hidden Hub/package/cache downloads.
- [ ] 3.3 Re-run independent-row, artifact-reload and submission tests on the exact final bundle.
- [ ] 3.4 Write durable `release_manifest.json` with source/model/asset hashes, runtime evidence and final Parquet hash; keep external submission separate from release artifact production.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`offline-release` specification](specs/offline-release/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
