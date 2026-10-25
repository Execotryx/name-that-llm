# OpenSpecs 16–18: runtime and feasibility implementation

Created 25 October 2026, 05:50:35 Asia/Qyzylorda.
Based on the review of `8fdf97a323c9b3169cacee73bce22593d2c3b1d0`.

## Result

Implemented all software changes in OpenSpecs 16–18. The sparse runtime export contains its missing `packaging` dependency and is checked against the unchanged lock. A fresh local-wheel-only environment proves imports and a synthetic text-only fit/Parquet contract through the bundled source layout. The export is included in source/bundle execution identity.

G1a, G1b and G6 share finite-budget validation and strict 80% memory/70% time reserves through `ntl.resources`. Total stage wall time, primary inference and every capacity/stress time are checked consistently. Neural measurements use the actual encoder device and record allocated/reserved peaks; resetting peaks retains memory already occupied by loaded weights. Invalid budgets fail before expensive execution or release reservation. Incomplete/OOM smoke attempts preserve blocked records, partial outputs and incident logs without replacing an earlier accepted G1a.

`ntl.capacity` registers deterministic ID-sorted input cycles, source/text hashes and a fixed timing/cache policy. Both component paths execute actual 0/1/3/4,000/8,000-row workloads plus full-batch long-input stress. Primary cost covers direct uncached prediction and Parquet write/read; generation of fixtures occurs outside that timer. Optional encoder token-length/truncation summaries prove the stress fills the 512-token window. Gate validation binds workload, scales, output files and actual runtime batch; joint eligibility rejects different S/F workloads before scored experiments. H retains the existing S+F cost rule and statistical thresholds.

G6 uses the same profiling code with all original ID/text profile rows, available only after confirmation closes, and verifies their membership against the full-data refit manifest. Capacity outputs join the candidate/final submission hashes in the release record. Publication and one-use holdout controls remain intact.

## Simplicity critique and revisions

| Round | Concrete critique | Resolution |
|---|---|---|
| 1 | The shared smoke evidence helper retained an unused model argument; its wall timer ended before evidence-file hashing. | Removed the argument and measured wall time after execution metadata, resource capture and hashing. G6 follows the same timing boundary. |
| 2 | Profiling accepted both a model and a separately supplied encoder, allowing metadata and the measured predictor to disagree. | Derive the encoder from the model through the existing shared accessor; verify its recorded batch against execution identity. |
| 3 | A new neural smoke reload could keep two encoder copies resident and overstate deployment memory. Failure reporting also risked diverging between the two smoke functions. | Removed the unnecessary neural probe serialization/reload; pinned cold loading and dedicated restored-encoder regressions remain. Added one small attempt context for both smoke failure records. CPU sparse reload remains part of its required vertical slice. |
| 4 | Reviewed resource predicates, workload generation, aliases, stage consumers, package validation and failure paths again. No further actionable simplification was found within this scope. | Retained the explicit versioned dictionaries and existing scalar cost aliases, whose equality is checked at consumption. No gate framework, resolver or benchmark orchestration layer was added. |

The review stopped after four rounds, below the requested maximum of ten. This is a scoped engineering judgment, not a claim that future critique is impossible.

## Validation

- [Pyright](validation/readiness-pyright.txt): zero errors and warnings.
- [Unittests](validation/readiness-unittest.txt): 44 tests passed in 55.377 seconds, including the prior receipt, provenance, single-consumption, refit and release regressions.
- [Strict OpenSpec validation](validation/readiness-openspec.txt): all 18 change packages pass with OpenSpec 1.15.0, telemetry and update checks disabled.
- [Isolated runtime proof](validation/readiness-runtime.json): a fresh unseeded environment installed only the pinned runtime requirements from staged wheels with `--no-index`. Bundled-layout CLI/help, release import, dependency profile capture and a two-row synthetic fit/Parquet check passed under a socket network guard, with no torch/transformers import. The report records local wheel hashes and execution identity.
- New readiness regressions execute actual workload row counts using inexpensive computation doubles, verify cache bypass and full-batch stress, and reject missing scales, stale workload hashes, batch drift, inconsistent costs, unbound outputs and incomplete token profiles. They cover producer/consumer time disagreement, exact reserve boundaries, invalid numeric values, nondefault-device allocated/reserved memory, failed neural attempts and continued valid S-only eligibility.
- Export tests reject missing, added, changed-version and changed-marker requirements. Dedicated encoder token-summary tests exercise the real summary method without importing optional execution packages.
- [Final real-input local verification](validation/readiness-registered-local-smoke.txt): disposable G0 reproduced the exact registered source, `large_string` sample schema, 2,159 development rows and 30 locked prompts. An unscored development-only sparse fit took 49.012 seconds; the complete smoke took 66.072 seconds. Actual 4,000/8,000-row prediction-and-Parquet workloads took 4.797/9.502 seconds. Process peak RAM was 417,644,544 bytes against the measured 8,589,934,592-byte local allowance. All local contracts completed, and the gate correctly stayed **blocked** for missing Kaggle/cold-restart evidence. No consumption ledger existed; the disposable checkout and model were removed after the check. These are host diagnostics, not a Kaggle runtime guarantee.

## Migration and remaining target acceptance

The export changes execution identity, and new resource/capacity evidence is version 1. Preserve historical artifacts and explicitly regenerate affected upstream/downstream evidence under the existing source/split/search policy; do not fill new fields into old records or silently rehash results. Preserve every reserved/exposed/closed G5 ledger. No holdout reset or renewed independent confirmation is authorized by these software changes.

The original three data files, canonical 18 labels, source hashes, prompt split seed/allocation, model families and fitting/search thresholds were not changed. No registered nested model selection, real holdout predictions, confirmation or competition submission was performed. Real cold Kaggle G1a, optional pinned-checkpoint/GPU G1b and final G6 target acceptance remain pending. The corresponding OpenSpec tasks stay unchecked. Optional neural execution is not activated by synthetic tests; the committed protocol still has an unpinned optional checkpoint.
