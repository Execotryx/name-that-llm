# Design: Publish submissions only after a passing release gate

## Context and scope

replay() writes submission.parquet before computing G6 status and returns normally when blocked. The notebook only prints the result. A simulated target run with one byte of allowed memory left a submission and completed successfully despite a blocked gate.

Reviewed baseline: `a4499c73d8bdc6db89679cdffa36995a2128c0a6`. These controls now have implementation and local regression coverage; see tasks.md for remaining real execution evidence.

## Decisions and failure paths

### 1. Publication sequence

Preflight bundle, runtime and output directory; predict to an attempt-specific candidate Parquet name that is not submission.parquet. Validate its schema, ID order, labels, independent-row contract, offline/cold target evidence and resource headroom. Only a successful target replay may atomically publish the final filename on the same filesystem.

### 2. Blocked behavior

Preserve blocked/failed attempt evidence with reason and candidate hash when available. Local diagnostic replay may return a blocked report and a non-final candidate, but must never publish the submission filename. Target CLI/notebook must raise or exit nonzero on blocked status. Do not merely print a warning.

### 3. Stale and interrupted output

Refuse a pre-existing final submission or release manifest before starting; preserve it and explain that it belongs to a prior attempt, rather than deleting or overwriting it. Bind completion to an attempt ID and output hash. If publication or final evidence persistence fails, record failure and remove/quarantine only the current attempt's newly published output when possible; never report a passing completed release. On restart, unmatched final output/evidence must be detected and explicitly reconciled, not silently accepted. Filesystem crashes cannot be made transactional across two files, so test and document this limitation.

### 4. No experimental expansion

Keep the chosen recipe and all runtime checks unchanged; do not tune a new model after failed replay. Continue to require closed G5, fixed full-data refit, exact output identity and real cold target evidence. Synthetic platform mocks prove control flow only.

## Dependencies and evidence

Existing 07; consumes schema contract from 08 and provenance/runtime controls from 10 and 13.

Implement [tasks.md](tasks.md) and verify every [acceptance scenario](specs/release-publication-control/spec.md). Retain commands, environment, failure logs and artifact identities. No test may inspect real locked labels or reserve a real G5 attempt merely to validate software behavior. Use temporary synthetic campaigns for destructive/failure-path checks.
