# Profile representative and comparable G1 workloads

## Why

P06 calls for fixed development texts plus synthetic variations at 4,000 and 8,000 rows. The current G1a instead repeats one sentence (`smoke.py:37–42`), while G1b times seven rows (the first five development responses, empty text and a repeated-word string) and extrapolates to 4,000 (`smoke.py:83–92`). No 8,000-row neural workload is executed. G1a's measured cost and G1b's extrapolated cost enter `runner.eligibility` and the registered selection tie-break as if they were comparable.

The sparse fixture stresses raw input length but does not establish representative vocabulary/feature density. The neural fixture exercises at most seven simultaneous texts at default encoder batch size eight and cannot establish the resource peak of a full inference batch of real long responses. Later G6 capacity tests cannot replace the early feasibility check required before neural experiments.

Mandatory for trustworthy G1a capacity evidence; neural workload acceptance is conditional on F/H activation. Maps to G1a/G1b/G2/G3/G4, P05–P06 and P09. G6 should reuse the workload policy where its existing full-data profiling remains applicable.

## What Changes

- Define a deterministic label-independent development workload manifest shared by S and F.
- Run actual 0/1/3/4,000/8,000-row workloads with fresh IDs, representative texts and explicit long-input/full-batch stress.
- Measure comparable inference cost boundaries and bind workload identity, batch sizes and cache policy to the evidence used by selection.
- Preserve the existing H cost rule (sum of S and F) and all statistical/search policy.

## Capabilities

### New Capabilities
- `representative-feasibility-workloads`: real measured capacity and comparable selection costs on a bound, development-only workload.

### Modified Capabilities
- None; supplements changes 02, 04 and 10 and the original P06 requirement.

## Impact

Affected: smoke workload construction, evidence schema, `runner.eligibility`, provenance, tests, runbook and potentially shared G6 workload construction. Dependencies: change 16 packaging and change 17 consistent resource checks. Reuse small shared functions rather than introduce a benchmarking framework.

Non-goals: using locked/test labels, fitting on the holdout, selecting workloads by model accuracy, changing batch/representation policy silently, upgrading architectures, or opening confirmation during readiness review.
