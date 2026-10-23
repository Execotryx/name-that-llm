# Running Name That LLM

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

The command fits development-only S at fixed C=2, tests independent rows/reload, writes and reads Parquet, profiles native process peak RAM and 0/1/3/4000/8000 synthetic workloads, and records environment versions and source revision. A successful deployment run publishes `artifacts/protocol/G1a.json`. Local execution writes a blocked G1a record even if local contracts pass. `--cold-restart` is an operator assertion about notebook lifecycle, not automatic proof of a restart. The Python network guard rejects normal socket connections; platform Internet-disabled execution is still required. No runtime installer or downloader is used.

For neural eligibility, register an exact 40-character DeBERTa-small repository revision in `configs/protocol.json` **before preparing G0**. Stage a permitted complete local asset directory with `encoder.json` containing `model`, `revision` and a `files` mapping of relative filenames to SHA-256. Tokenizer/weights/config must all be listed. Install tested torch/transformers/tokenizer wheels into a separate pinned target environment. Call `ntl.smoke.neural_smoke` on a fresh target session with a `FrozenEncoder`, a measured memory allowance, time limit and `cold_restart=True`. Preserve its `G1b.json` and failure logs. No checkpoint download, license verification or GPU run has occurred in this checkout. Missing eligibility excludes F/H; it does not give them accuracy scores.

## G2/G3: bounded nested evaluation

```powershell
uv run ntl evaluate --root artifacts/protocol --output artifacts/runs/nested-001
```

This requires passing G1a. To activate verified F/H, add `--encoder-assets PATH --neural-gate PATH/G1b.json --device cuda:0`. S-only operation does not import neural packages. The registry includes starts, successes, failures, training IDs, settings and fit budget. Five outer folds each use four grouped inner folds. S/F component C choices are .5/1/2/4; H uses the registered grid, collapsing endpoints to S/F. Component refits are deduplicated. Pooled OOF results and complete-selector OOF are separate. F/H-vs-S paired intervals/randomization tests are conditional development diagnostics; Holm correction is limited to that registered family.

## G4: diagnostics and freeze

```powershell
uv run ntl diagnose --root artifacts/protocol --run artifacts/runs/nested-001 --output artifacts/runs/diagnostics-001
uv run ntl topic --root artifacts/protocol --output artifacts/runs/topic-001
uv run ntl freeze --root artifacts/protocol --run artifacts/runs/nested-001 --diagnostics artifacts/runs/diagnostics-001 --topic-report artifacts/runs/topic-001/topic_report.json --output artifacts/decision
```

The topic command records **blocked** without a verified encoder. With a verified encoder and gate arguments, it generates six fixed topic-proxy clusters and nested leave-cluster-out scores. Blocked topic evidence cannot pass a challenger veto. S can be frozen with the topic limitation disclosed. Artifact controls use fixed C=2; primary prefix perturbations reuse nested outer S models and compare raw/perturbed results on identical eligible/common subsets. They do not enter architecture selection.

Freeze uses separate full-development four-fold selection, outer improvement checks and fixed robustness vetoes. It saves fitted development artifacts, recipe, class order, source/code/split/environment hashes, rationale, contract checks and `configs/decision-receipt.json`. **Commit the receipt before continuing.** The receipt binds the exact G4/decision hashes to Git history; it is not a cryptographic external custodian signature.

## G5: one confirmation

```powershell
uv run ntl confirm --root artifacts/protocol --sealed sealed --decision artifacts/decision --operator OPERATOR_ID
```

After checking the committed receipt and artifacts, this atomically reserves the attempt, writes predictions and hashes, then opens the label file. It records fixed interpretation rules and closes the consumed ledger. A second call is denied. Mechanical errors leave an incident and reserved/exposed state; there is no automatic retry or reset. A pre-exposure recovery needs explicit custodian review. Once predictions/results are exposed, any reproduction uses a consumed lock and is not independent confirmation. The frozen candidate never changes because of the holdout ranking.

## G6: refit and release

After G5 closes, use the fixed-refit notebook route by default. Add the flag below only after confirming that attached task-fitted artifacts are permitted:

```powershell
uv run ntl refit --root artifacts/protocol --sealed sealed --decision artifacts/decision --train PATH/01-train.csv --output artifacts/release --task-artifacts-permitted
```

With `--task-artifacts-permitted`, the bundle contains the exact unchanged full-data model. Without the flag, it contains the eligible full training CSV and the fixed recipe; the notebook performs that refit and includes its cost in measured runtime. Both modes contain package source, optional local encoder, input identities and manifest. They account for all original rows. Only trusted locally authored joblib artifacts may be loaded; a hash supplied by an attacker does not make an untrusted pickle safe.

Attach the bundle and matching pinned dependencies to the target platform. Configure `NTL_BUNDLE`, `NTL_TEST`, `NTL_AVAILABLE_MEMORY_BYTES` and `NTL_COLD_RESTART=1`, then restart and run `notebooks/submission.ipynb` with Internet disabled. The default runtime test path comes from the competition overview. The thin notebook loads only text and writes `submission.parquet`. A local replay is available through `ntl replay` with explicit paths and budgets. It remains blocked for G6 outside a cold deployment session.

No upload/submission is performed. The fixed-refit route avoids attaching task-fitted models, but still needs permitted input data/assets and a passing cold deployment profile. No guess about artifact permissions enables a release gate.

## Evidence limitations

This implementation has local synthetic software checks. Real source audit/sealing, experiment execution, detailed artifact permissions, optional checkpoint license/assets and cold deployment replays require external inputs. Keep OpenSpec gate checkboxes unchecked until corresponding real evidence exists. Neither local tests nor a generated notebook establish model performance or release readiness.
