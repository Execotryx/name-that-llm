# Running Name That LLM

## Runtime packaging and capacity controls (16–18)

Changes [16](../openspec/changes/16-sync-offline-runtime-export/proposal.md), [17](../openspec/changes/17-unify-feasibility-resource-checks/proposal.md) and [18](../openspec/changes/18-profile-representative-g1-workloads/proposal.md) implement the findings from the [readiness review](24-10-2026-23-51-33-training-readiness-review.md). `requirements-runtime.txt` now includes `packaging` and is part of execution identity and release copying. A source or bundled-layout import cannot borrow packages from the development environment in the isolated packaging check.

Verify the export routinely, then stage wheels for the intended Python/platform during acquisition. Verify those local wheels in an unseeded isolated environment before staging the actual target. The second command below is an acquisition download; it is never run by inference or the offline notebook.

```text
uv run python scripts/verify_runtime.py
python -m pip download --only-binary=:all: --dest PATH/wheels -r requirements-runtime.txt
uv run python scripts/verify_runtime.py --wheelhouse PATH/wheels --report PATH/new-runtime-check.json
```

The check compares normalized lock-derived requirements (including version/marker changes), installs with `--no-index` from the wheel directory, imports the bundled source layout, captures its execution profile and completes a tiny synthetic fit/Parquet contract. No optional neural packages are installed or imported. Reports are exclusive writes; retain prior results. This establishes local packaging behavior, not real target acceptance.

G1 producers, gate consumers and G6 publication now use resource evidence v1 and the same strict reserves: all required time measurements must be below 70% of the allowance and RAM/GPU peaks below 80%. Budgets must be positive and finite before work begins. GPU measurements use the encoder's actual device; peak resets retain current loaded allocation and reservation. Recorded phases distinguish fit/extraction/cold load from primary inference and total stage wall time. A producer cannot pass a record that its consumer rejects for a different resource definition.

Capacity evidence v1 binds the hashed `ntl.capacity.POLICY`, development manifest, ordered source IDs/text hashes, actual scale counts/timings, output hashes, adapter/encoder batches and optional token-length/truncation summaries. The policy is registered by committing the implementation before G0. Both S/F profile the same deterministic ID-sorted development-text cycles at 0/1/3/4000/8000 rows. Timers cover direct prediction plus Parquet write/read with no embedding/result-cache lookup; fixture construction occurs outside each primary timer. A separate long-text stress case fills at least one encoder batch and its 512-token window. The stress adapter batch can exceed the primary 64 rows when required by the recorded encoder batch; this is logged explicitly. Workload or timing-definition mismatches are rejected before selection; H keeps the existing additive component cost. Failed/OOM smoke attempts retain partial outputs, a blocked record and `incidents.jsonl`; accepted root G1a evidence is never replaced.

G6 reuses the same profiling implementation with `profile_inputs.csv`, containing all original IDs/texts only after the closed confirmation permits full-data refit. It verifies those IDs against the refit manifest before measuring or publishing. Capacity Parquet hashes join the candidate/final output hashes in the release record. A matching measured source inventory is required; legacy `profile_texts.json` bundles need explicit new evidence rather than an implicit fallback.

The supplied originals match registered hashes and pass disposable G0 verification (2,159 development rows, 30 locked prompts, no consumption ledger). Do not copy a local runtime identity to a different target: prepare the actual campaign under the intended compatible target runtime and unchanged split policy. Retain any existing campaign manifests/ledgers and follow their migration policy rather than replacing them. No real confirmation is needed for packaging or feasibility testing.

For an optional unscored local probe using the real originals, run `uv run python tests/verify_registered_inputs.py PATH --smoke --available-memory BYTES` with a measured local allowance. It creates a disposable committed source snapshot, prepares the unchanged split, fits development-only S and exercises all capacity workloads. Its local gate remains blocked, and no holdout predictions, scoring, confirmation or permanent campaign is created.

## Corrective controls

[Changes 08–13](../openspec/README.md#corrective-backlog-from-the-implementation-review) now have executable controls and synthetic regression checks. They add a persisted Arrow schema contract, verified restored encoder assets, execution identity v2 and upstream lineage, conditional runtime locks, formatting-preserving prefixes and gate-controlled submission publication. Real cold target acceptance remains a separate requirement. See the dated implementation log and `docs/validation/corrections-*` for local evidence.

**Review corrections 14–15:** selection history and saved-model execution now have separate roles. Decision/G4 provenance v3 retains the exact selection identity and evidence snapshots under `selection_evidence/`, while `artifact_execution` describes each selected/reference model. The `execution` field is a checked alias for the selected role so generic gates need no separate compatibility mode. A neural-selection-to-S result executes as sparse at G5/refit/replay, with unused neural packages/assets unnecessary. F/H still enforce their required assets/runtime, and every G5 prediction artifact is checked before reservation.

Runtime profile/lock v2 records parsed dependency closure, roots/extras, marker environment and active edges. Active missing/incompatible requirements fail with their parent, constraint and environment; false markers do not pull in ambient distributions. Explicit transitive extras are resolved to a fixed point, including cycles and conflicting parents. `packaging` is a direct core dependency. Unsupported active direct URLs and malformed metadata fail locally without installation. The recorded marker environment is compared exactly; moving platforms requires fresh evidence under the existing compatibility policy. Legacy role envelopes/profiles/locks require explicit migration and affected evidence regeneration; they are never rewritten automatically. Preserve any reserved/exposed/closed G5 state.

Local evidence and simplicity-review decisions are in the dated 14–15 implementation log and `docs/validation/followups-*`. Real cold neural/target evidence and permitted offline CLI validation remain separate pending tasks.

Existing artifacts without the new schema/execution/runtime identities are rejected. Preserve them as historical records. Before an untouched formal campaign, register an amendment and regenerate affected evidence under the same source and split policy; do not silently rehash old artifacts. An exposed or consumed G5 must remain consumed. New software checks do not authorize another independent confirmation.

Install the local development environment with `uv sync --locked`. The resolved `uv.lock` records the versions tested locally; it is not evidence of a deployment-compatible environment. The sparse runtime uses pandas, scikit-learn, pyarrow and their locked dependencies. Optional neural dependencies are intentionally absent from this environment.

Verify code with:

```powershell
uv run pyright
uv run python -m unittest discover -s tests -v
openspec validate --all
```

Commit the implementation before registered execution. All commands use configured paths and preserve previous run directories. No real data, pretrained assets, deployment credentials, benchmark scores or lock state are included in the repository.

## G0: prepare once

```powershell
uv run ntl prepare --train PATH/01-train.csv --test PATH/02-test.csv --sample PATH/03-sample_submission.parquet --root artifacts/protocol --sealed sealed
```

This checks the registered source hash, preserves literal `NA`, Unicode and empty strings, audits missing pairs and duplicates, checks label completeness, allocates exactly 30 prompts using NumPy default_rng(2027), and saves nested folds. A structural/source discrepancy aborts. Cross-prompt near-duplicate links abort pending a versioned component-aware amendment; they never silently change the allocation. The exhaustive fixed near-duplicate rule can take time on long responses.

`development.csv` is the only modeling input. `manifest.json` hashes its files and provides a row allowlist. The original source remains operator-accessible; separate paths and logs are accident controls, not a security boundary. Use a separate custodian/credentials if stronger assurance is needed. The sealed texts and labels are stored separately.

## G1: cold target smoke

In a fresh target CPU session with Internet disabled, stage the package and compatible wheels first. Supply the *measured* runtime memory allowance in bytes:

```text
ntl smoke --root artifacts/protocol --test PATH/test.csv --output artifacts/protocol/smoke-001 --available-memory BYTES --cold-restart
```

The accepted sample Arrow field types are persisted in `submission_schema.json`. Both `string` and `large_string` are logical UTF-8; output retains the recorded physical types, exact field order and runtime IDs. Placeholder sample model values are never used for inference or selection.

The command fits development-only S at fixed C=2, tests independent rows/reload, writes and reads Parquet, profiles native process peak RAM and the actual representative 0/1/3/4000/8000 workloads plus long-input stress, and records environment versions and source revision. The output directory must be a fresh child of the protocol root. A successful deployment run publishes `artifacts/protocol/G1a.json`. Local execution writes a blocked G1a record even if local contracts pass. `--cold-restart` is an operator assertion about notebook lifecycle, not automatic proof of a restart. The Python network guard rejects normal socket connections; platform Internet-disabled execution is still required. No runtime installer or downloader is used.

For neural eligibility, register an exact 40-character DeBERTa-small revision in `configs/protocol.json` **before preparing G0**. Stage a fresh local directory containing configuration, tokenizer files and exactly one supported weights layout (`model.safetensors`, `pytorch_model.bin`, or a corresponding shard index plus every referenced shard). Unlisted loader-relevant alternatives, missing roles and escaped paths are rejected. Optional documentation may remain alongside the assets.

Prepare the exact neural environment and a local wheel directory covering its required dependencies. Asset acquisition can author a new manifest/runtime lock using the following Python helper; it performs no downloads and refuses to replace an existing lock:

```python
from pathlib import Path
from ntl.encoder import prepare_assets
prepare_assets(Path("PATH/new-encoder-assets"), Path("PATH/pinned-wheels"),
               revision="EXACT_40_CHARACTER_REVISION", device="cuda:0", batch_size=8)
```

The helper captures installed package versions and METADATA/WHEEL/RECORD identities, applicable torch/CUDA/cuDNN/device/driver/TF32/determinism settings, numerical environment variables, and SHA-256 identities of local installation wheels. Set required numerical environment variables before capture. `runtime-lock.json` is included in `encoder.json`; all runtime consumers verify the current profile against it. Tokenizers using `spm.model` also require sentencepiece/protobuf. A failed acquisition retains staging files; inspect them and use a new directory rather than overwriting evidence.

Call `ntl.smoke.neural_smoke` in a fresh offline target session with a `FrozenEncoder`, measured resource allowances and `cold_restart=True`. Its G1b record binds the asset/runtime identities and upstream G1a. Loaders verify assets after restoration and relocation; missing packages/assets fail locally, never trigger installation. Device, build, numerical-policy or dependency changes require a fresh target profile and affected evidence. There is no implicit compatibility whitelist. S remains operational without the neural packages. No real checkpoint/license/GPU feasibility is established by synthetic tests.

## G2/G3: bounded nested evaluation

```powershell
uv run ntl evaluate --root artifacts/protocol --output artifacts/runs/nested-001
```

This requires passing G1a. Every stage checks execution identity v2 (relevant package/notebook/config/lock bytes, runtime and optional encoder), together with exact data/split and upstream gate hashes. Git revision is retained separately; docs-only and receipt commits do not change executable identity. Missing legacy identities are explicit migration errors. To activate verified F/H, add `--encoder-assets PATH --neural-gate PATH/G1b.json --device cuda:0`. S-only operation does not import neural packages. The registry includes starts, successes, failures, training IDs, settings and fit budget. Five outer folds each use four grouped inner folds. S/F component C choices are .5/1/2/4; H uses the registered grid, collapsing endpoints to S/F. Component refits are deduplicated. Pooled OOF results and complete-selector OOF are separate. F/H-vs-S paired intervals/randomization tests are conditional development diagnostics; Holm correction is limited to that registered family.

## G4: diagnostics and freeze

```powershell
uv run ntl diagnose --root artifacts/protocol --run artifacts/runs/nested-001 --output artifacts/runs/diagnostics-001
uv run ntl topic --root artifacts/protocol --output artifacts/runs/topic-001
uv run ntl freeze --root artifacts/protocol --run artifacts/runs/nested-001 --diagnostics artifacts/runs/diagnostics-001 --topic-report artifacts/runs/topic-001/topic_report.json --output artifacts/decision
```

Completed topic evidence contains a manifest binding views, assets/runtime, cluster/fold membership, row IDs, selections, OOF predictions and report. Freeze verifies hashes and recomputes pooled/per-cluster metrics before using veto scores. Artifact diagnostics bind the exact nested run and view version. Prefixes preserve all original whitespace up to the cutoff; at/below the word limit input remains identical. The diagnostic still removes semantic information with the suffix, so it is not a pure length-causality experiment.

The topic command records **blocked** without a verified encoder. With a verified encoder and gate arguments, it generates six fixed topic-proxy clusters and nested leave-cluster-out scores. Blocked topic evidence cannot pass a challenger veto. S can be frozen with the topic limitation disclosed. Artifact controls use fixed C=2; primary prefix perturbations reuse nested outer S models and compare raw/perturbed results on identical eligible/common subsets. They do not enter architecture selection.

Freeze uses separate full-development four-fold selection, outer improvement checks and fixed robustness vetoes. It saves fitted development artifacts, recipe, class order, source/code/split/environment hashes, rationale, contract checks and `configs/decision-receipt.json`. **Commit the receipt before continuing.** The receipt binds the exact G4/decision hashes to Git history; it is not a cryptographic external custodian signature.

## G5: one confirmation

```powershell
uv run ntl confirm --root artifacts/protocol --sealed sealed --decision artifacts/decision --operator OPERATOR_ID
```

After checking the real committed receipt, full execution identity, loaded recipes and encoder asset/runtime preflight, this atomically reserves the attempt, writes predictions and hashes, then opens the label file. It records fixed interpretation rules and closes the consumed ledger. A second call is denied. Mechanical errors leave an incident and reserved/exposed state; there is no automatic retry or reset. A pre-exposure recovery needs explicit custodian review. Once predictions/results are exposed, any reproduction uses a consumed lock and is not independent confirmation. The frozen candidate never changes because of the holdout ranking.

## G6: refit and release

After G5 closes, use the fixed-refit notebook route by default. Add the flag below only after confirming that attached task-fitted artifacts are permitted:

```powershell
uv run ntl refit --root artifacts/protocol --sealed sealed --decision artifacts/decision --train PATH/01-train.csv --output artifacts/release --task-artifacts-permitted
```

With `--task-artifacts-permitted`, the bundle contains the exact unchanged full-data model. Without the flag, it contains the eligible full training CSV and the fixed recipe; the notebook performs that refit and includes its cost in measured runtime. Both modes contain package source, optional local encoder, input identities and manifest. They account for all original rows. Only trusted locally authored joblib artifacts may be loaded; a hash supplied by an attacker does not make an untrusted pickle safe.

Attach the bundle and matching pinned dependencies to the target platform. Configure `NTL_BUNDLE`, `NTL_TEST`, `NTL_AVAILABLE_MEMORY_BYTES` and `NTL_COLD_RESTART=1`, then restart and run `notebooks/submission.ipynb` with Internet disabled. The default runtime test path comes from the competition overview. The thin notebook passes only text to inference. Replay first reserves `attempt.json` in a fresh output directory and writes an attempt-specific `candidate-*.parquet`. Only passing G6 publishes `submission.parquet`; its hash is recorded in `release_manifest.json`. Blocked local library replay may return diagnostic evidence and a candidate, but CLI/notebook call `require_release` and fail on blocked status. A pre-existing final file, release record or reservation is refused before inference. A failed publication records an incident and attempts to quarantine only the current attempt's final output; unmatched files after an interruption require explicit reconciliation. Prior files and G5 ledgers are never overwritten or reset. A local replay is available through `ntl replay` with explicit paths and budgets. It remains blocked for G6 outside a cold deployment session.

No upload/submission is performed. The fixed-refit route avoids attaching task-fitted models, but still needs permitted input data/assets and a passing cold deployment profile. No guess about artifact permissions enables a release gate.

## Evidence limitations

This implementation has local synthetic software checks, including a temporary committed Git receipt and synthetic confirmation lifecycle. `uv run python tests/verify_registered_inputs.py PATH_TO_INPUT_DIRECTORY` additionally checks the three registered originals through preparation in a disposable clean committed source snapshot, with no model scoring or holdout consumption. Real source audit/sealing, experiment execution, detailed artifact permissions, optional checkpoint license/assets and cold deployment replays require external inputs. Keep OpenSpec gate checkboxes unchecked until corresponding real evidence exists. Neither local tests nor a generated notebook establish model performance or release readiness.
