# Design: a fixed measured workload contract

## Workload construction

Build workloads from the verified development allowlist only, in a deterministic order registered before scored comparisons. Bind source row IDs/text hashes, development manifest, workload version and exact synthetic transformation rules. Cover normal development diversity and a separately identified upper-length/full-batch stress case. A simple deterministic cycle through the development corpus plus a fixed long-text subset is sufficient; no clustering, adaptive sampler or new research parameter is needed.

Generate fresh unique adapter IDs at each requested scale. Use the same primary 4,000-row text sequence for S and F, including the same end-to-end adapter/Parquet timing boundary. Keep cold-load, fit/extraction, primary inference, stress workload and total wall measurements separate. Workload generation occurs outside the primary inference timer consistently. Do not use the three supplied test rows as a hidden-test throughput estimate.

Run the actual 4,000/8,000 rows; a seven-row extrapolation may remain informational but cannot serve as the accepted primary measurement. Disable embedding/text-result caches during throughput measurement. Preserve the configured adapter and encoder batch sizes and force at least one full encoder batch of maximum-token-length inputs in the stress test. Tokenization/truncation settings and actual token-length/truncation summaries should be logged for the optional encoder. If batch size changes for feasibility, capture a new runtime lock and new evidence using the established identity policy, without changing the representation or pretending prior timings remain valid.

## Cost integration

Record explicit measured cost units and workload identity with G1a/G1b. `eligibility` verifies matching primary workload identity, scale and timing boundary before exposing S/F costs to `choose`. H remains the registered sum of comparable component costs. Do not change promotion/tie thresholds, fit counts or architecture sets. Different hardware is represented by each verified runtime identity; it is not silently normalized into a different cost definition.

Coordinate evidence schema validation with change 17. Bind the workload records and measurement outputs through existing file hashes/upstream lineage. Reject older or mismatched profiles with explicit revalidation instructions. No silent reinterpretation of old `inference_seconds` values.

## Failure and acceptance

OOM, timeout, malformed output, cache shortcuts or missing required scales block the relevant feasibility branch. Keep partial diagnostics in a fresh attempt directory and retain prior attempts. Tests can use a counting predictor/encoder and small fixtures to prove actual invocation counts, batch coverage, identity matching and cache disabling without running thousands of expensive neural calls in every unit test. The real target acceptance must still execute the requested scales, satisfy reserves and preserve text-only independence and physical Parquet types.

An actual cold Kaggle G1a remains required before registered G2. G1b is optional, and a blocked F/H branch must not prevent a verified S-only campaign. Preserve all G5 ledgers; never use the holdout to validate workloads or grant independent confirmation again after an implementation change.
