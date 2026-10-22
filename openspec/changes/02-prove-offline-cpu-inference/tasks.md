# Tasks: Prove offline CPU inference and submission contract

**Gate:** G1a · **Plan packages:** P04–P06 (mandatory CPU path); section 4 inference contract · **Status:** not started (documentation only).

## 1. Build the minimal runtime

- [ ] 1.1 Create core runtime declarations for pandas, scikit-learn and pyarrow, resolve and pin actual tested Kaggle versions and dependency hashes.
- [ ] 1.2 Implement isolated class manifest loader, text-only prediction API and a CPU model fixture without a requirement for PyTorch/Transformers.
- [ ] 1.3 Implement a slim notebook that resolves its competition input paths through config and never reads `prompt_id` at inference.

## 2. Enforce inference and submission contracts

- [ ] 2.1 Add one-row, empty-table, shuffled, duplicate-ID, missing-ID, blank-text, Unicode/code/math/markup and long-text tests; reject null/non-string text.
- [ ] 2.2 Verify probabilities are finite, 18-wide, sum to one and use canonical class order; tests must compare singleton and mixed/shifted batches.
- [ ] 2.3 Write and reopen a PyArrow Parquet file with exact `id,model` string schema, same row count/order/unique IDs as runtime input, no nulls and 18-label membership.

## 3. Complete G1a resource proof

- [ ] 3.1 Restart/run an internet-disabled Kaggle CPU notebook with only declared inputs; save stdout/environment hashes and evidence of no hidden installs.
- [ ] 3.2 Profile 4,000 and 8,000 synthetic row workloads at realistic and worst-case lengths, disabling caching shortcuts; record cold load, peak RAM and wall time.
- [ ] 3.3 Mark G1a passed only with durable end-to-end output, test records and measured headroom. If blocked, document the precise blocker and keep G2/release blocked.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`offline-inference` specification](specs/offline-inference/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
