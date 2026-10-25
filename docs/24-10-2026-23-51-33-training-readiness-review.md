# Training readiness review and proposed OpenSpecs

Created 24 October 2026, 23:51:33 Asia/Qyzylorda.
Reviewed `Execotryx/name-that-llm` main at `8fdf97a323c9b3169cacee73bce22593d2c3b1d0`.

## Verdict

**The sparse training implementation runs, but the full registered training campaign is not ready to start.** The current pinned development environment successfully fits the actual development partition. The exported offline runtime is incomplete, early capacity evidence is inadequate, and no actual cold target G1a was established in this review. The optional neural branch also has a reproducible producer/consumer resource-gate inconsistency and still lacks its pinned checkpoint/real target proof.

Do not confuse these findings with a failure to fit S or a reason to redesign its architecture. The next work is packaging and feasibility correction, followed by actual target evidence. No accuracy result is claimed.

## Findings

### P1 — The exported offline environment cannot import the execution path

Locations: `requirements-runtime.txt:3–31`, `src/ntl/environment.py:13–16`, `pyproject.toml:9` and the notebook's `from ntl.release import replay, require_release`.

`packaging` was added to the project and lock but omitted from the generated runtime requirements. An unseeded environment containing only `requirements-runtime.txt` fails while importing `ntl.release`:

```text
ModuleNotFoundError: No module named 'packaging'
```

The traceback reaches `from packaging.requirements import Requirement` through release → locked_eval → gates → provenance → environment. A current `uv export --locked --no-dev --no-hashes --no-emit-project --format requirements-txt` includes `packaging==26.3`; the checked-in export does not. This is reproducible without Kaggle. A notebook image with ambient packaging could conceal the defect; the successful locked developer environment does not validate this deployment recipe.

Correction: [change 16](../openspec/changes/16-sync-offline-runtime-export/proposal.md), including export-drift and isolated offline runtime checks. Do not upgrade packages merely to repair the missing entry.

### P1 — Early capacity profiles do not establish representative scale or comparable selection costs

Locations: `src/ntl/smoke.py:37–42,83–92`, `src/ntl/runner.py:100–124`, and `IMPLEMENTATION_PLAN.md` P05–P06/P09.

G1a profiles 4,000/8,000 copies of one repeated sentence. With the actual development-fitted feature extractor, that row has 54 nonzero features; the development median is 1,799, p95 approximately 3,483 and maximum 4,385. This is evidence of a feature-density mismatch, **not** a claim of a proportional runtime difference. The fixture still exercises raw text length, but does not establish representative sparse inference capacity.

G1b profiles only seven texts, multiplies their timing by 4,000/7 and never executes an 8,000-row neural workload. At the default encoder batch size eight, those seven rows also cannot establish full-batch long-input peak memory. S's measured repeated-sentence cost and F's extrapolated seven-row cost feed the registered cost tie-break despite different workloads.

Correction: [change 18](../openspec/changes/18-profile-representative-g1-workloads/proposal.md). Use deterministic development-only workloads, real scale runs, explicit full-batch stress and matching timing definitions before exposing costs to selection. Preserve the existing S/F/H family, cost rule and thresholds. G6 remains a separate final replay.

### P2 — G1b can announce success that its consumer immediately rejects

Locations: `src/ntl/smoke.py:93–102` and `src/ntl/gates.py:22–29`.

The producer checks inferred inference time but not total stage wall time. The consumer checks total wall time. A deterministic synthetic reproduction through the actual producer and consumer produced:

```json
{
  "producer_status": "passed",
  "wall_seconds": 100,
  "limit_seconds": 100,
  "inference_seconds": 5.71428571428572,
  "consumer_result": "Insufficient time reserve"
}
```

The registered 70% reserve permits less than 70 seconds here. The consumer correctly refuses the record; therefore this is a contradictory readiness signal and a possible late neural-training admission failure, not evidence that the downstream guard is bypassed. The reproduction used synthetic data, a clock and computation doubles; it did not run a real encoder or forge real campaign evidence.

Correction: [change 17](../openspec/changes/17-unify-feasibility-resource-checks/proposal.md). Share a small validation helper, retain strict reserves, distinguish stage and workload time, and validate explicit device-specific measurements. Neural failure must still leave an independently verified S-only route available.

## Verification performed

| Check | Observed result | What it establishes |
|---|---|---|
| Remote main and local checkout | Exact reviewed SHA matches | Current source was reviewed |
| `uv sync --locked` | Success; Python 3.12.14 | The committed developer lock installs here |
| `uv run pyright` | 0 errors, 0 warnings | Static checks pass |
| `uv run python -m unittest discover -s tests -v` | 37 passed in 58.960 seconds | Existing synthetic regression suite passes |
| Registered original files | All three exact hashes match | No input amendment is needed for these copies |
| `uv run python tests/verify_registered_inputs.py ../project_sources` | Success in disposable committed snapshot | Actual G0 parsing/audit/splits/schema work locally |
| Real-data fixed-C sparse execution probe | Fit and contracts pass; no scoring | S can execute on the real development rows |
| Fresh exported-runtime import | Reproduced missing `packaging` | Deployment recipe defect is confirmed |
| Synthetic G1b producer/consumer reproduction | Producer passes, consumer rejects | Resource decision inconsistency is confirmed |
| OpenSpec 1.15.0 strict validation | All 18 changes pass | Existing and new specifications are structurally valid |

OpenSpec validation ran with `OPENSPEC_TELEMETRY=0`, `DO_NOT_TRACK=1` and update checks disabled by those privacy settings. It does not certify implementation or target feasibility. No Python implementation was changed by this review.

### Input identity and disposable G0

| File | SHA-256 |
|---|---|
| train.csv | `40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707` |
| test.csv | `4545aa3a3459f4c0724f97ad5bd06c4caa3506bdfea5fab905e8203184fc0c57` |
| sample_submission.parquet | `ccf86796b80fd7f83d8463664603fd1208e17559abcf416f198776b819646188` |

The originals contain 2,699 training rows, 150 prompts, 18 labels and three test rows. The sample uses `large_string` for both ordered fields `id,model`. Disposable preparation completed with 2,159 development rows and 30 locked prompts; no consumption ledger existed. Its temporary campaign was deleted by the repository's verifier. This is input/code verification, not a durable formal campaign or target-specific G0 receipt.

### Real-data sparse execution probe

The probe selected the development partition using the registered sorted prompt list and `default_rng(2027)` allocation, excluded the first 30 shuffled prompts, then fit only S at the predeclared smoke `C=2`. It ran under the offline socket guard, used no accuracy metric and performed no model comparison. It did not open sealed labels, invoke confirmation or produce holdout predictions.

- Development rows: 2,159; excluded prompt groups: 30.
- Fit: 55.603 seconds; whole probe: 59.985 seconds on this host.
- Convergence: 189 iterations, first 2,500-iteration allowance, no convergence warning/retry.
- Feature dimension: 156,391; process peak RAM: 481,660,928 bytes (about 459 MiB).
- Saved-model reload, independent-row checks and the three-row Parquet round trip passed.
- Output retained the sample's physical `large_string` field types.

These figures are diagnostic host measurements, not a Kaggle runtime guarantee or full nested-CV estimate. The local fitted probe model and diagnostic predictions are not release artifacts or accepted campaign evidence.

## Proposed work and execution order

1. Implement change 16 and verify the complete isolated runtime export.
2. Define changes 17/18's small shared resource/workload contracts, implement them and retain targeted negative regressions. Do not redesign the classifier.
3. Prepare the actual campaign in the intended compatible runtime, preserving source, split seed and any existing campaign/holdout history. Collect real cold internet-disabled target G1a with representative scale evidence.
4. Start registered G2 only after its actual gate is accepted. If remaining S-only, explicitly record F/H as not evaluated.
5. If activating F/H, register the exact checkpoint revision before actual campaign preparation, stage its verified assets/wheels and pass corrected real G1b before scored neural work. The current configuration has `encoder.revision=null`; this is an unmet optional prerequisite, not a reason to block S forever.

The repository already specifies real G0/G1 acceptance in changes 01/02/04. Those tasks remain pending; the new packages address concrete gaps rather than add a parallel approval process. No real Kaggle session, GPU checkpoint load, registered nested evaluation, final selection, confirmation, refit or submission was performed in this review.

## Change log

Prepared OpenSpec changes 16–18, updated the OpenSpec index and runbook with their proposed status, and recorded this review plus local verification evidence. Implementation tasks remain unchecked. Source modules, dependency exports, datasets, statistical settings and existing holdout state were not modified. The prepared review changes have not been committed or pushed.
