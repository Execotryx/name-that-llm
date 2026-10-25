## 1. Define and implement the shared workload
- [x] 1.1 Register a deterministic development-only workload, text/source identities, scale list and explicit long-input/full-batch stress policy before scored comparisons.
- [x] 1.2 Replace the G1a repeated-sentence-only capacity fixture with the shared representative workloads, preserving separate edge-case contract tests.
- [x] 1.3 Execute actual G1b scale workloads without embedding/result-cache shortcuts; log token-length/truncation, batch and device measurements.
- [x] 1.4 Separate fit/cold-load/extraction, primary inference and total wall timers; use identical primary cost boundaries for S/F.

## 2. Bind costs and evidence
- [x] 2.1 Hash the workload and measurement records into G1 evidence; coordinate the schema with change 17.
- [x] 2.2 Reject mismatched or legacy workload/timing records before exposing costs to selection; retain H=S+F and all existing thresholds/budgets.
- [x] 2.3 Test deterministic workloads, allowlist enforcement, real row counts, cache bypass, full-batch stress, malformed output and incomplete evidence using inexpensive computation doubles.
- [x] 2.4 Reuse workload construction at G6 where appropriate without accessing full-data rows before G5 closes; retain G6 as a separate actual final replay.
- [x] 2.5 Update AGENTS.md and the runbook with implemented commands, measurements and explicit revalidation rules.

## 3. Real acceptance
- [x] 3.1 Run Pyright, full unittests and strict OpenSpec validation; retain outputs separately from target evidence.
- [ ] 3.2 Run mandatory actual cold target G1a on the registered inputs with the corrected runtime and record capacity/headroom at all required scales.
- [ ] 3.3 If neural eligibility is activated, pin and stage the checkpoint before target G0, run actual G1b with matching workloads, and verify the unchanged evidence is accepted before G3 fitting.
- [x] 3.4 Keep G2/G3 blocked until their applicable evidence exists; preserve source/splits and leave G5 untouched throughout feasibility work.

Software tasks above are verified by the [implementation log](../../../docs/25-10-2026-05-50-35-readiness-controls-implementation.md) and its linked validation records. Neural execution fixtures use computation doubles; actual cold target/checkpoint acceptance remains separately unchecked. No real holdout was consumed.
