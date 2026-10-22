# Name That LLM: implementation plan

**Version:** 1.1 • **Prepared:** 19 October 2026 • **Technology-stack update:** 22 October 2026 • **Status:** implementation specification; no formal protocol or deployment gate is marked passed. Earlier exploratory CPU results are not registered confirmation evidence.

**Basis:** the supplied 30-page *A Methodologically Defensible Rewrite for Kaggle “Name That LLM”(2).pdf*, the supplied training/test files, and the additional requirements for independent text-only inference, selection control, and early offline execution. Page references below refer to that report.

## 1. Objective and non-negotiable requirements

Build an offline classifier that attributes each response independently to one of the existing 18 source labels. Preserve the original data and label set. Use prompt-disjoint evaluation, retain a genuinely untouched final holdout, and justify every increase in complexity against a strong sparse baseline.

The deliverable is a reproducible training/evaluation package and a Kaggle notebook that reads the actual runtime test file and writes `submission.parquet`. The primary metric is the mean recall across all 18 classes. The defensible claim concerns the benchmark's labeled generation pipelines, not causal identification of an underlying LLM independently of its serving settings.

Mandatory invariants:

1. The prediction function consumes **text only**. `id` is carried by the submission adapter; `prompt_id` is restricted to splitting and evaluation. No prompt reconstruction, prompt-conditioned features, batch balancing, or dependence on companion responses is permitted.
2. Original rows, text, IDs, and labels are immutable. Diagnostic views are derived copies. Never fabricate the missing response or drop outlying lengths.
3. Learned preprocessing is fitted on the relevant training partition only. Validation labels never enter fitting, calibration, checkpoint selection, or blend selection for that validation partition.
4. The 30-prompt holdout is allocated before modeling, excluded from all development work, and opened once after the complete decision is committed.
5. Architecture selection is part of the selection process. A development winner's score is not automatically an unbiased estimate just because each candidate used nested CV.
6. The neural path cannot enter extensive experimentation until its actual local checkpoint, dependencies, extraction loop, and Parquet output execute offline on the intended hardware.
7. Leaderboard feedback is not a tuning input. No training/test combined vocabulary, test-fitted normalization, inferred test class proportions, or one-label-per-prompt assignment.

## 2. Facts verified from the supplied files

These are preparation-time integrity observations, not model-performance results. No holdout was allocated or scored during preparation of this plan.

| Item | Observed result | Consequence |
|---|---|---|
| Training schema | `id, prompt_id, text, model` | Select `text` explicitly; do not infer a feature column by elimination. |
| Training size | 2,699 rows; 150 prompt IDs; 18 labels | Preserve all rows and labels. |
| Prompt blocks | 149 blocks of 18 rows; one block of 17 | Do not assume perfect blocks in metrics or tests. |
| Missing pair | `p002` / `claude-fable-5` | Record as absent; do not impute or synthesize. |
| Class counts | `claude-fable-5`: 149; every other class: 150 | Fixed 18-class balanced accuracy remains the primary metric. |
| IDs / exact duplicates | Training IDs unique; no duplicate prompt/model pairs; no duplicate exact response texts | Still implement repeatable checks. |
| Whitespace-normalized text duplicates | None detected | This does not rule out near-duplicates. |
| Empty CSV fields | None in either supplied CSV | Implement an explicit missing-value policy for later runtime inputs. |
| Whitespace word counts | Minimum 36; maximum 274; median 101 | The report's 40–250 wording is not a row-filtering rule. Tokenization conventions may differ. |
| Supplied test | 3 rows; `id, text`; IDs unique | A schema fixture, not a representative hidden-test performance or runtime sample. |
| Train/test overlap | No shared IDs or exact texts | Do not introduce lookup-based prediction. |
| Sample Parquet metadata | 3 rows; ordered fields `id, model`; both optional UTF-8 strings; writer identifies itself as Polars | Match names, order, logical string types, and row identity; verify via a standard reader in the execution gate. |

The sample Parquet footer was inspected structurally. A standard Parquet engine was unavailable in this planning environment, so a full decode/write/read round trip has **not** been claimed. Neither a checkpoint nor the Kaggle execution environment was supplied here.

Input SHA-256 hashes:

| File | SHA-256 |
|---|---|
| `train.csv` | `40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707` |
| `test.csv` | `4545aa3a3459f4c0724f97ad5bd06c4caa3506bdfea5fab905e8203184fc0c57` |
| `sample_submission.parquet` | `ccf86796b80fd7f83d8463664603fd1208e17559abcf416f198776b819646188` |

Use paths supplied through configuration. The current copies are named `01-train.csv`, `02-test.csv`, and `03-sample_submission.parquet`; those prefixes must not become assumptions about Kaggle paths.

### Authoritative label/provider manifest

The observed labels agree with the report's mapping (p. 13). Persist this explicit mapping and a single canonical class order; never infer providers by substring matching.

| Provider | Exact labels |
|---|---|
| Anthropic | `claude-fable-5`, `claude-opus-4-6`, `claude-opus-4-8`, `claude-opus-5`, `claude-sonnet-5` |
| Google | `gemini-3.1-pro-preview`, `gemini-3.6-flash`, `gemini-3.7-flash`, `gemini-3.8-flash` |
| ZAI | `glm-5.3`, `glm-5.3-flash` |
| OpenAI | `gpt-5.5`, `gpt-5.6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-6-astra` |
| Moonshot AI | `kimi-k3` |
| Qwen | `qwen3.8-max` |

Use lexicographic sorting of these exact 18 strings for `classes.json`. Reindex every estimator's probability columns against it before combining predictions.

## 3. Execution sequence and gates

All outputs named below are files to be created during implementation, not artifacts already produced. A gate passes only with persisted evidence. Do not equate a checkbox or a planned test with execution.

| Stage | Dependency | Required exit evidence | Stop condition |
|---|---|---|---|
| G0: protocol and data | None | Source hashes, audit, label manifest, protocol version, sealed split | Invalid schema/labels or unresolved cross-boundary duplicate leakage |
| G1: offline vertical slice | G0 | G1a mandatory CPU sparse end-to-end offline run, independent-row tests and Parquet round trip; G1b optional frozen-encoder load/extraction/profile on target hardware | G1a failure blocks the release; G1b failure blocks neural candidates F/H, not the sparse-only path |
| G2: trusted sparse benchmark | G1 submission path; neural failure may leave sparse work available | Nested grouped sparse OOF, convergence logs, leakage tests | Overlapping prompts, invalid probabilities, unresolved convergence |
| G3: frozen challenger and selector | G1b passing + G2; otherwise record F/H as feasibility-ineligible | If feasible, frozen-probe and blend OOF plus complete-selector outer predictions; otherwise signed sparse-only eligibility record | Outer-label tuning, unregistered candidate expansion, or treating a blocked neural branch as evaluated |
| G4: robustness and development decision | G3, including documented F/H infeasibility if applicable | Predeclared diagnostics, uncertainty report, final development configuration | Unresolved robustness veto or insufficient justification for complexity |
| G5: one-time confirmation | Frozen G4 decision | Sealed prediction artifacts, one holdout report, consumption record | Protocol breach or serious contradiction; no holdout-driven repair |
| G6: refit and release | G5 report closed | Full-data refit, clean offline notebook replay, validated submission | Output/contract/runtime mismatch |

The early vertical slice precedes extensive neural experiments. G1a is mandatory and proves the CPU sparse submission path; G1b is mandatory **only for neural eligibility** and proves an offline encoder path, not accuracy. If the encoder cannot pass G1b, record F/H as excluded by feasibility rather than evaluated and rejected on accuracy. Development and release can proceed with S; keep G5 untouched.

## 4. Package structure and interfaces

Use a small Python package with a thin notebook wrapper. Keep development, holdout evaluation, and final refit entry points separate.

| Module / directory | Responsibility |
|---|---|
| `configs/protocol.json` | Frozen seeds, grids, gates, diagnostics, budgets, tolerances, runtime target |
| `configs/labels.json` | Exact classes and provider mapping |
| `src/ntl/data.py` | Explicit schemas, parsing, hashes, audit; distinct development/holdout loaders |
| `src/ntl/splits.py` | Locked membership, outer/inner folds, overlap assertions |
| `src/ntl/views.py` | Pure, deterministic, per-text diagnostic transformations |
| `src/ntl/features.py` | Sparse/stylometric factories; training-only fitted transforms |
| `src/ntl/encoder.py` | Offline loading, deterministic pooling, extraction, cache identity |
| `src/ntl/models.py` | Sparse, frozen probe, probability blend; canonical class alignment |
| `src/ntl/selection.py` | Inner selection and deterministic tie breaking |
| `src/ntl/evaluation.py` | Fixed-label BA, OOF integrity, bootstrap, paired tests, provider diagnostics |
| `src/ntl/diagnostics.py` | Topic-proxy stress tests and artifact interventions |
| `src/ntl/locked_eval.py` | One-time confirmation, consumed-state marker, integrity checks |
| `src/ntl/inference.py` | Text-only predictor and strict submission writer |
| `notebooks/submission.ipynb` | Restart-and-run-all offline entry point; no research loop |
| `tests/` | Leakage, metric, inference, cache, serialization, and submission contract tests |
| `artifacts/manifests/` | Immutable source, split, experiment, environment, and release identities |
| `artifacts/runs/<run_id>/` | Config, metrics, predictions, logs, timing and resource measurements |
| `sealed/` | Restricted holdout material and its consumption ledger |

Required logical interfaces:

```python
fit_model(texts: Sequence[str], labels: Sequence[str], config) -> TextClassifier
TextClassifier.predict_proba(texts: Sequence[str]) -> ndarray  # shape (n, 18)
TextClassifier.predict(texts: Sequence[str]) -> Sequence[str]
build_submission(test_frame, predictor, schema) -> DataFrame  # exactly id, model
```

`fit_model` does not receive `prompt_id`; the external evaluator uses groups to select its training rows. Neither predictor method receives an ID, a group, a class-frequency estimate, or a test dataframe. A model may retain learned parameters and vocabulary but must not consult a stored response lookup table.

### Independent-row inference acceptance tests

- Predict a single text with no metadata; obtain one valid prediction and 18 finite probabilities.
- Compare that text alone, with unrelated texts, and with repeated copies of itself. Compare chunk sizes 1, 2, and the selected production batch size.
- Shuffle inputs, reverse them, and change all IDs in the adapter. Restore original order; predictions must agree.
- Append arbitrary unrelated test rows. Existing predictions must remain unchanged.
- Vary or omit `prompt_id` in upstream test fixtures; predictor inputs must still be exactly the original text sequence.
- Serialize/reload the full artifact and repeat the checks. Validate all probability rows sum to one within `1e-6`; use `atol=1e-5, rtol=1e-4` for cross-batch neural probability comparisons initially.
- Require exact final-label agreement in the contract suite. If near-ties cause batch-dependent labels, fix numerical execution before release; tolerances are not permission for metadata- or batch-dependent decisions.
- Synthetic cases include empty and whitespace-only strings, Unicode punctuation, markup, code/math, and long text. Accept strings as-is; reject null/non-string values with a clear schema error. An empty string uses the normal vectorizer/tokenizer path; do not drop the row.
- Handle an empty test dataframe by producing a typed zero-row output. Reject duplicate or missing IDs because the output contract requires unique row identity.

For neural models, use evaluation mode, no dropout, attention-mask-aware pooling, fixed padding/truncation behavior, and no batch-fitted transformation. Sorting by length for batching is allowed only if the original row order is restored.

## 5. G0 tasks: protocol, audit, and lock

### P00 — Confirm execution requirements

- [ ] Record the current competition rules, input locations, permitted pretrained assets, notebook time limit, accelerator allocation, external-data restrictions, and required output format.
- [ ] Treat the report's nine-hour limit and approximately 4,000 hidden passages as planning assumptions until verified in the competition environment. The public page could not be read as substantive text during this plan's preparation.
- [ ] Choose the deployment profile: Kaggle scoring hardware is the release target. The user's RTX 3050 Ti 4 GB / 32 GB laptop is an additional local profile only if it is the machine actually used.
- [ ] Capture Python, package versions, CPU/RAM, GPU model/VRAM, CUDA/driver, and accelerator visibility. Do not assume two visible GPUs are automatically used by one model.

**Acceptance:** `environment-target.json` records confirmed facts separately from assumptions. No execution claim relies solely on historical hardware details.

### P01 — Reproduce the data audit

- [ ] Read IDs, prompts, text, and labels as strings. Preserve Unicode, line breaks, casing, and literal text such as `NA`; explicitly distinguish missing fields from valid strings.
- [ ] Recompute hashes, schema, uniqueness, missingness, class counts, prompt completeness, duplicate pairs, exact duplicates, and length summaries.
- [ ] Produce machine-readable audit JSON and a concise human-readable report. Match the observations in section 2 or explain any source-version difference.
- [ ] Audit near-duplicates with one fixed, label-independent rule registered before scoring. Record candidate pairs and prompt membership; do not delete rows.
- [ ] If meaningful duplicate responses link different prompts, form connected components for partitioning so linked prompts cannot cross evaluation boundaries. This may change the exact 30/120 allocation and fold sizes; resolve and version that change before modeling. The current exact-duplicate audit does not trigger it.

**Acceptance:** all 18 labels retained, original bytes unchanged, no unresolved structural discrepancy. Row-level metadata audit is permitted before locking; content-driven modeling and per-label exploratory plots are not performed on the future holdout.

### P02 — Create the lock and development manifests

- [ ] On the current data, sort the 150 prompt IDs, shuffle with NumPy `default_rng(2027)`, and assign the first 30 to the locked set. Preserve the other 120 for development. Use component-aware allocation if P01 required it.
- [ ] Save `split_roles.csv` with row ID, prompt ID, and role. Save membership itself, not only the random seed; record library versions and SHA-256.
- [ ] Construct five development outer folds and four inner folds per outer-training partition using a pinned grouped splitter. Prefer stratified grouped splitting because of the incomplete block.
- [ ] Construct a separate fixed four-fold grouped partition of the full development pool for final configuration selection.
- [ ] Persist `outer_folds.csv`, `inner_folds.csv`, and `final_selection_folds.csv`. Verify disjointness, all-class support, complete row coverage, and deterministic replay.
- [ ] Place locked rows in a separate input unavailable to routine experiment commands. Development commands load a development-only file and reject locked IDs. Record file hashes and accesses.
- [ ] Keep any initial all-data object out of development workers. Do not precompute locked embeddings, topic vectors, per-label diagnostics, or holdout predictions before G5.

**Acceptance:** every development row receives exactly one outer validation fold; every inner split is nested in its outer-training partition; no prompt/component crosses boundaries. Ordinary experiment code cannot load `sealed/` through its configured data path.

A manifest, path convention, and audit log reduce accidents; they are not a security boundary if the same operator retains unrestricted raw-file access. If stronger assurance is needed, run the holdout evaluator under separate credentials or have a custodian retain the lock. Never imply inaccessible data when it is merely marked as held out.

### P03 — Register the complete experiment policy

- [ ] Commit the candidate list, fixed encoder revision, preprocessing, grids, folds, random seeds, metric, tie-breaking, robustness thresholds, ablations, and hardware budget before viewing model scores.
- [ ] Record one row per planned experiment with `experiment_id`, hypothesis, role (`selection` or `diagnostic`), parameters, seed, permitted inputs, output paths, and maximum fits.
- [ ] Record protocol amendments with timestamps and reasons. A new architecture, representation, seed choice, feature family, or blend prompted by observed OOF results is adaptive exploration, not a preregistered result.
- [ ] Do not reset the lock or split seed to improve a score. Declare any earlier exposure that is discovered; do not relabel inspected data as untouched.

**Acceptance:** a machine-readable protocol has a stable hash and a finite experiment budget. A new unregistered candidate cannot be launched by the main runner.

## 6. G1 tasks: early proof of offline execution

### P04 — Package the optional encoder and dependencies (G1b)

- [ ] Primary neural challenger: `microsoft/deberta-v3-small` (technology decision of 22 October 2026), with one explicitly pinned repository revision. This intentionally replaces the report's proposed `microsoft/deberta-v3-base` to reduce resource requirements; confirm checkpoint license, tokenizer, memory headroom, and actual compatibility during acquisition. Do not compare both sizes as an unregistered architecture sweep.
- [ ] Download/stage weights, config, tokenizer, vocabulary/SentencePiece files, and any required tokenizer configuration before disabling networking. Record per-file hashes and the source revision.
- [ ] Pin the tested environment, including `torch`, `transformers`, tokenizer dependencies, NumPy/SciPy/scikit-learn, and a standard Parquet engine such as PyArrow. Use attached compatible wheels if installation is needed during an offline Kaggle run.
- [ ] Load both tokenizer and model from explicit local paths with `local_files_only=True`; set `HF_HUB_OFFLINE=1`. Do not rely on a pre-warmed personal Hub cache.
- [ ] Prefer native supported model code and `trust_remote_code=False`. If the chosen asset requires additional code, package and audit it before the gate; never fetch it during scoring.

**Acceptance:** the assets load after restarting the kernel with an empty unrelated cache and networking disabled. Removing a required local asset produces an immediate, useful failure rather than a download attempt.

### P05 — Run the complete vertical slice

- [ ] Select a fixed development-only fixture containing examples from all 18 labels. Include synthetic edge cases and long texts near/above the 512-token boundary. Fixture selection must not use performance scores.
- [ ] Run the raw sparse CPU pipeline once for mandatory G1a. When G1b is activated, also run the frozen encoder plus linear probe once with fixed smoke-test hyperparameters. Never compare smoke-test scores to select a model.
- [ ] Extract embeddings with `encoder.eval()`, `torch.inference_mode()`, max length 512, and attention-mask-aware last-layer mean pooling. L2-normalize per row. Fix whether special tokens participate; the default follows the report's attention mask and includes non-padding special tokens.
- [ ] Start conservatively at batch size 1 on the 4 GB local profile, then profile 2, 4, and higher only if safe. On Kaggle, measure its actual hardware rather than importing the laptop setting blindly.
- [ ] Record truncation rate on development data, token lengths, pooling dimension, numerical dtype, peak GPU allocated/reserved memory, process RAM, cold-load time, and passages per second.
- [ ] Write and reopen `submission.parquet` for the supplied three-row test using a standard Parquet engine. Compare its schema with the decoded sample, verify exact ID order, label membership, absence of nulls, and no extra index column.
- [ ] Run all independent-row acceptance tests from section 4.

**Acceptance:** G1a passes when the network-disabled CPU sparse inference notebook executes, text-only independence tests pass, and Parquet round-trip succeeds. G1b passes separately when its exact local encoder checkpoint loads and extracts with measured memory/runtime headroom, including independent-row tests. Neither smoke path is scored for model selection.

### P06 — Demonstrate scale and reserve capacity

- [ ] Use fixed development texts and synthetic variations to create 4,000- and 8,000-row inference workloads with fresh IDs. Disable text-cache shortcuts in this benchmark so repeated inputs do not hide extraction cost. Do not use locked texts.
- [ ] Benchmark at the intended 512-token maximum, including tokenization, embedding transfer, classifier prediction, and Parquet writing. Measure realistic and worst-case length workloads separately.
- [ ] Extract embeddings for the entire development pool as an initial real workload. Stream batches to a cache/memory map rather than keeping all token-level hidden states.
- [ ] Target measured peak resource use below 80% of the available memory allowance and projected total notebook time below 70% of the confirmed limit. These are engineering reserves, not competition rules.
- [ ] Estimate final refit plus inference cost explicitly if training happens inside the scoring notebook. Otherwise include artifact loading and verify that pre-trained task artifacts are allowed. Do not put nested CV in the final notebook.
- [ ] On OOM, reduce batch size without changing the representation. Test any precision change against a reference output. If still blocked, test the same checkpoint on CPU if its measured runtime fits.
- [ ] If a smaller encoder or shorter maximum length is necessary, amend the protocol for feasibility before neural performance comparisons; rerun G1. Do not conceal a failed DeBERTa test as a completed representation experiment.

**Acceptance:** `offline_smoke.json`, environment lock, notebook execution log, contract-test report, and runtime profile jointly establish feasibility. A projected runtime alone does not substitute for the final full notebook replay at G6.

## 7. G2/G3 tasks: bounded model building and honest selection

### P07 — Implement the sparse anchor

Use the report's raw-text baseline (pp. 5–6, 18–20):

| Parameter | Fixed initial value |
|---|---|
| Word TF-IDF | word analyzer, `(1,2)` n-grams, `min_df=2`, `max_df=0.995`, cap 150,000 |
| Character TF-IDF | character analyzer, `(3,5)` n-grams, `min_df=2`, cap 250,000 |
| Both spaces | `lowercase=False`, `sublinear_tf=True`, float32 storage; default L2 normalization per branch |
| Composition | Sparse horizontal concatenation; branch weights fixed at 1 |
| Classifier | Multiclass logistic regression with L2 penalty; compatible pinned `saga` configuration |
| Search | `C ∈ {0.5, 1, 2, 4}` only |
| Solver | Maximum 2,500 iterations initially; seed 2027; no class weighting initially |

- [ ] Fit the entire vectorizer/classifier pipeline inside each training split. No vocabulary or IDF is learned globally.
- [ ] Keep matrices sparse. Log vocabulary sizes, convergence warnings, fit time, and memory.
- [ ] Define a convergence remedy before scoring: an increased iteration ceiling/tighter verified solver configuration applied consistently, not selective rescue of a favorable fold. Record any unresolved nonconvergence as failure.
- [ ] Implement word-only and stylometry controls as diagnostic variants; do not silently allow them to expand the final-model search.

**Acceptance:** one nested grouped run produces valid baseline outer OOF probabilities for every development row; a held-out-only sentinel token cannot enter the fold's vocabulary.

### P08 — Implement the frozen encoder probe

- [ ] Reuse the one checkpoint and extraction configuration that passed G1. Freeze all encoder parameters; no training-mode stochasticity or gradient updates.
- [ ] Fit a linear logistic probe with `C ∈ {0.5, 1, 2, 4}` on each training partition. No PCA or learned whitening in v1; if introduced later, it must be fold-fitted and count as another selection choice.
- [ ] Cache development embeddings only. Cache identity includes source text hash, row ID, text-view version, checkpoint/revision, tokenizer, maximum length, pooling, special-token policy, dtype, and implementation version.
- [ ] Verify cache row alignment explicitly after filtering/shuffling. Invalidate the cache whenever one of those inputs changes.
- [ ] Fixed, externally pretrained, label-independent embeddings may be reused across development folds. Do not reuse fold-trained neural weights or learned normalizers across validation boundaries.

**Acceptance:** valid frozen-probe OOF predictions on the same outer folds as the sparse model; cache replay reproduces fresh extraction within tolerance.

### P09 — Put architecture and blend selection inside the inner loop

The v1 selection candidates are exactly:

- **S:** word + character TF-IDF logistic regression.
- **F:** frozen encoder + linear probe.
- **H:** `w * p_S + (1-w) * p_F`, with `w ∈ {0, 0.1, ..., 1}`.

Stylometry, stripped text, alternate prefixes, and topic proxies are diagnostic only. No flexible stacker or probability calibration is included in v1. Adding calibration would require its own training-only fitting procedure and renewed budget.

For each of the five outer folds:

1. Exclude the outer validation partition from every selection operation.
2. On the outer-training partition, generate four-fold grouped inner OOF probabilities for each of the four sparse `C` values and four probe `C` values.
3. Align all probability columns. Compute pooled inner OOF BA for S and F and for every H combination of sparse `C`, probe `C`, and `w`. This is 176 blend combinations, computed from cached predictions rather than 176 encoder trainings.
4. Apply the frozen selection rule below using only these inner predictions.
5. Refit the selected component configuration(s) on all outer-training rows. Predict the outer validation rows once.
6. Also retain outer predictions of each prespecified candidate's own inner-selected configuration for paired development diagnostics.
7. Persist the selected architecture, hyperparameters, blend weight, training IDs, seeds, probability order, and artifact hashes.

This yields two different outputs that must not be confused:

| Output | Interpretation |
|---|---|
| Per-candidate nested OOF | Development comparisons of a finite, predeclared candidate family |
| Complete-selector outer OOF | Evaluation of the procedure that chooses architecture, hyperparameters, and blend internally |

**Frozen selection rule:** find the best sparse setting first. A more complex candidate must improve pooled inner BA by at least **0.03**. Among qualifying candidates within **0.005** BA of the best qualifying score, choose the less expensive candidate, using measured G1 cost; then fewer components; then lower `C`; then greater sparse blend weight. If none qualifies, select S. End-point blends collapse to the corresponding single model. Ties and rounding are handled by deterministic code, not manual judgment.

The 3-point margin is a practical threshold, not a significance claim. It deliberately removes the report's discretionary “or comparably strong evidence” exception, which otherwise permits post-hoc promotion.

**Acceptance:** no outer labels are passed into `selection.py`; the selector's final OOF row coverage is exact; repeated runs with identical inputs make identical selection decisions. Publish the outer-fold architecture choices even if they differ.

### P10 — Bound compute and experiment count

- [ ] Five outer folds × four inner folds × four `C` values require 80 sparse fits and 80 probe fits, plus necessary outer refits. The blend grid itself is cheap probability arithmetic.
- [ ] Budget up to 30 outer refits to retain candidate and complete-selector outputs; deduplicate identical fitted configurations.
- [ ] The final full-development four-fold selection adds 16 sparse and 16 probe fits plus final development refits.
- [ ] Register diagnostic fit counts separately. Run controls with fixed settings rather than tuning each diagnostic into a new contender.
- [ ] Do not rerun splits or choose a favorable neural seed. The frozen encoder is deterministic; repeating extraction under three RNG seeds is not three independent neural representations. Check probe/solver seed sensitivity separately if needed.

Default diagnostic budget: nine fixed-setting controls in P13 × five outer folds = 45 fits, plus three fixed-setting prefix refit variants × five folds = 15 fits. Use `C=2` for these diagnostic classifiers, with the same convergence policy as P07; do not select their settings from outer scores. For the six topic stress folds, four inner folds × four `C` values × two branches × six clusters = 192 component fits, plus up to 36 component refits for selected S/F/H configurations. Reuse fixed encoder embeddings where the text view matches. Extra extraction is required for changed text views; its cost belongs in the registry. Reuse identical fitted configurations whenever possible. This is the v1 compute ceiling before failure retries, which must be logged with reasons.

**Acceptance:** all trials, including failures, appear in `experiment_registry.csv`; no unreported architecture or seed search.

## 8. G4 tasks: metrics, uncertainty, and robustness

### P11 — Implement metrics correctly for the incomplete block

Compute the primary score as:

`BA = (1 / 18) * sum_k(correct_k / support_k)`.

- [ ] Require all 18 true classes in primary evaluation partitions and define a clear error for absent support. Never let a library silently change the averaging label set.
- [ ] Use pooled OOF BA as the primary development score. Fold mean and SD are descriptive; the five overlapping-training folds are not five independent experiments.
- [ ] Report per-class support/recall and a true-normalized 18×18 confusion matrix.
- [ ] Map predicted exact labels to providers to compute provider BA. For an optional probability-aggregated provider prediction, sum class probabilities by provider and label it as a different diagnostic.
- [ ] For sibling diagnostics, select rows by true provider and keep all 18 prediction columns, or add an explicit “other provider” column. Do not renormalize after dropping cross-provider mistakes.
- [ ] Provider BA and exact BA use different label weightings; their gap is descriptive, not a formal decomposition of error.

**Acceptance:** hand-constructed tests reproduce BA when one class has fewer observations, distinguish it from raw accuracy, and preserve cross-provider mistakes in family plots.

### P12 — Estimate uncertainty without disguising selection

- [ ] Bootstrap prompt groups with replacement 10,000 times, retaining every sampled group's rows and its multiplicity. Recompute 18-class BA in each replicate and pair model comparisons on the same resample.
- [ ] Report point differences in percentage points and percentile intervals. Validate all-class support; record and handle invalid resamples explicitly if future data make them possible.
- [ ] For a paired randomization test, swap the two models' complete prediction vectors within each prompt with probability 0.5, then recompute the **same BA difference**. Use 100,000 Monte Carlo draws and `(extreme + 1)/(B + 1)`.
- [ ] Do not use an unweighted mean of per-prompt accuracy differences as an exact test of BA on incomplete blocks. An equivalent fixed-support contribution is `d_p = sum_(i in p) [(correct_A_i-correct_B_i)/(18*n_class(i))]`; its sum is the observed BA difference.
- [ ] Predeclare F-vs-S and H-vs-S as the v1 comparison family; apply Holm adjustment to their p-values. This addresses those tests, not arbitrary adaptive searching.
- [ ] Describe CV bootstrap intervals and p-values as conditional development diagnostics: shared training folds, model fitting, and architecture selection add uncertainty that bootstrapping fixed predictions does not fully capture.
- [ ] Report holdout uncertainty separately. Do not claim that a nonsignificant 30-prompt result proves equivalence or absence of a useful effect.
- [ ] Retain the report's MDE discussion as approximate planning context, clearly noting its assumptions. Do not equate an observed-score-based “power” number with new confirmatory evidence.

**Acceptance:** metric tests include duplicated bootstrap groups and the missing prompt/class case; selected-candidate development intervals are never described as selection-adjusted confidence guarantees.

### P13 — Run registered artifact diagnostics

Use development data only, preserve row identities, and keep the same group boundaries. Diagnostic settings are fixed in advance; no diagnostic winner automatically becomes a release candidate.

| Diagnostic | Procedure | Required interpretation |
|---|---|---|
| Word-only | Same word vectorizer, fixed registered `C` | Describes the character branch's increment |
| Stylometry | Length, punctuation rates, case, sentence/paragraph, Unicode and markup counts; training-fold scaler + linear classifier | Quantifies explicit surface information |
| Length-only | Word/character/sentence/paragraph counts | Tests verbosity/termination proxies |
| Format-only | Fixed lexical masking, retaining punctuation/markup; document remaining length leakage | Tests formatting plus explicitly acknowledged residual structure |
| No explicit length | Remove registered length fields from style model | Other rate/diversity features may still encode length indirectly |
| Format-stripped | Apply deterministic stripping to both training and evaluation text; refit | Interventional sensitivity, not proof that remaining signals are causal |
| Lexical-only | Remove registered punctuation/markup, preserve words/case; refit | Complementary vocabulary signal |
| Opening only / removed | Fixed sentence segmentation and short/empty outcome policy | Dependence on boilerplate; do not drop emptied rows |
| Prefixes 40/80/120 | Evaluate each prefix against raw text on the same eligible rows; also compare all prefixes on the ≥120-word common subset | Avoid conflating different sample populations with a length effect |

For prefix work, distinguish input perturbation of an already fitted model from retraining on truncated text. Register which is primary; recommended v1 uses perturbation of frozen fold models plus one fixed-setting sparse refit sensitivity analysis. Report row/class support for every subset; do not issue an 18-class BA if support is incomplete.

Formatting transformations can damage math or code. Include such examples in transformation unit tests and report this limitation. Diagnostic exclusions affect only the specified analysis; all 2,699 original rows remain eligible for final training.

**Acceptance:** every table states whether the model was refitted, the evaluation subset, support, and transformation version. Large artifact sensitivity narrows the scientific claim; it is not automatically evidence of invalid competition features.

### P14 — Run six topic-proxy stress folds

- [ ] Derive format-stripped response embeddings using a fixed frozen representation. Average per prompt across its available responses; the incomplete prompt uses its 17 observed responses.
- [ ] Build six development-only clusters with fixed `KMeans(n_clusters=6, n_init=50, random_state=2027)`. Save prompt vectors, memberships, cluster sizes, and seed.
- [ ] Call these topic-proxy clusters, not known semantic domains. Source style may remain in the average; format stripping and averaging do not prove removal of style.
- [ ] For each cluster, train on the other clusters and evaluate on it. Tune candidate settings only with grouped inner folds within that training side, or use a separately preregistered fixed configuration; never tune on the held-out cluster.
- [ ] Report six cluster scores and pooled leave-cluster-out BA, including baseline/challenger paired differences and support.
- [ ] Acknowledge that clustering all development texts designs a transductive stress partition, although no held-out cluster labels train the classifier. This is a robustness diagnostic, not an independent unbiased topic-generalization estimate.

**Default development vetoes, to freeze at P03:** challenger pooled topic BA must be no more than 0.02 below S; no class recall may fall more than 0.10 below S in grouped OOF; improvement must remain nonnegative after removing each provider in turn and recomputing macro recall over the remaining exact labels. Publish the complete per-cluster and per-class results rather than only pass/fail.

These thresholds are proposed engineering policy, not conclusions from observed performance. If too conservative for the intended project, change them before scoring and record the choice. Diagnostic vetoes may only reject a contender in favor of S; they may not tune its architecture or parameters.

### P15 — Freeze the final development decision

- [ ] Use the fixed four-fold full-development inner selection to determine the final architecture, component `C` values, and blend weight with the same registered rule.
- [ ] Require a more complex selected candidate to show at least +0.03 pooled per-candidate outer OOF BA versus S and pass the registered development vetoes. Otherwise choose S.
- [ ] Report the complete-selector outer OOF score separately. The final decision's additional diagnostic vetoes use development results, so the complete-selector score evaluates its nested inner selection component, not the whole later human/diagnostic decision.
- [ ] State explicitly that the chosen model's development score is selection-affected. Bounded candidates, nested architecture selection, and transparent diagnostics reduce optimism; they do not make adaptive comparison free of bias.
- [ ] Fit the final candidate on development only. If it differs from S, fit one baseline comparator with its development-selected settings.
- [ ] Commit `decision.json`: architecture, every preprocessing choice, encoder/assets, class order, all hyperparameters, blend weights, seeds, precision, batch policy, environment, source/split/code hashes, rationale, holdout protocol, and fitted artifact hashes.

**Acceptance:** the final scientific/deployment candidate is selected before G5. No model, blend, preprocessing, or seed decision remains open for the holdout to resolve.

## 9. Optional neural fine-tuning: a separate bounded extension

The report's fine-tuned transformer and likelihood approaches are not part of the v1 release search. Complete the sparse/frozen/hybrid study first. This avoids quietly turning diagnostics into a broad architecture sweep.

If a fine-tuning extension is explicitly activated **before the lock is opened**:

- [ ] Register it as an adaptive development extension if the decision followed observed v1 results; do not call it preregistered from the outset.
- [ ] Require G1 success and evidence of contextual complementarity from the frozen branch. Preserve the same untouched lock and input data.
- [ ] Fix one backbone, max length 512, learning rates `{1e-5, 2e-5}`, maximum three epochs, weight decay 0.01, effective batch size 16–32, seeds `{17,43,101}`.
- [ ] Select checkpoint/epoch only within inner training/validation. Never use outer validation labels for early stopping. For the outer refit, choose an epoch count by a fixed aggregate rule from inner runs, or reserve an inner training subset for stopping.
- [ ] Evaluate the registered seed-averaging strategy and report per-seed results; never promote the best seed alone. Include the three-seed model's full inference cost.
- [ ] Expand the nested selection process and comparison family explicitly. Predeclare whether it is a standalone candidate or a specific blend; do not sweep arbitrary three-way weights.
- [ ] Rerun affected development selection and feasibility evidence. All configurations must still be frozen before the original untouched lock is consumed.

After G5, any performance-driven extension requires new independent confirmation data or an explicitly exploratory status. Repartitioning already inspected rows cannot recreate an untouched holdout. Proxy likelihood/source adapters remain a later research project with a separate protocol and offline feasibility proof.

## 10. G5 tasks: one-time locked confirmation

### P16 — Open the lock exactly once

Before access, require all of the following:

- [ ] `decision.json` exists with committed hashes and a selected candidate.
- [ ] Development-only fitted candidate and, if different, baseline artifacts exist.
- [ ] G1, independent-row tests, class order, and submission schema checks pass for that exact implementation.
- [ ] No holdout consumption or prior score exposure is recorded.
- [ ] Locked data hashes and expected membership match the original manifest.

Then:

1. Run inference on all locked texts using the frozen development-trained artifact(s). Save prediction hashes before displaying labels, scores, plots, or per-example errors.
2. Score the selected model and at most the prespecified S comparator. Compute BA, class recalls, paired prompt bootstrap intervals, and the fixed diagnostics requested by the confirmation protocol.
3. Mark the lock consumed and record execution time, operator/run ID, input/model/prediction hashes, and results.
4. Produce a confirmation report. Do not change the winner, weights, thresholds, or training recipe based on its values.

Suggested predeclared interpretation when a challenger was selected:

| Locked outcome | Interpretation / action |
|---|---|
| Positive difference with interval above zero | Direction supported under this holdout; acknowledge limited prompt coverage |
| Interval spans zero without a material reversal | Inconclusive; retain the frozen decision and report uncertainty |
| Challenger is at least 0.03 BA below S, or the paired interval is wholly below zero | Material contradiction flag; report instability, withhold a claim of robust superiority, and close the experiment |

A negative point estimate smaller than the material threshold still gets reported as a directional reversal; do not hide it behind an “inconclusive” label. The confirmation categories are reporting/claim rules, not a second model-selection stage.

If the holdout contradicts development, the frozen candidate can still be produced as an honestly labeled experimental submission, but selecting a different model because it scored better on that holdout forfeits an untouched evaluation for the newly selected model. Do not silently fall back and then claim independent confirmation.

A crash before any prediction/score exposure may be repaired for mechanical execution and rerun with an incident log. Once predictions or outcomes are inspected, any rerun is a reproducibility check on a consumed holdout, not a new confirmation trial.

**Acceptance:** one closed confirmation record, no post-lock tuning, and a clear distinction between measured results and claims the evidence does not support.

## 11. G6 tasks: final refit and Kaggle release

### P17 — Refit on all original labeled rows

- [ ] After confirmation is closed, refit the chosen fixed pipeline on all 2,699 rows, including the former lock. Do not add synthetic examples or rebalance/drop labels.
- [ ] Refit TF-IDF vocabulary/IDF and classifier parameters on full training data. Reuse the same externally pretrained frozen encoder; generate full-training embeddings only now.
- [ ] Keep the development-selected hyperparameters, views, class order, blend weights, seed policy, and numerical behavior fixed. Do not retune with the former holdout.
- [ ] Save the fitted artifacts, dependency/environment lock, provenance manifest, and exact preprocessing implementation.
- [ ] If a fine-tuned extension is active, use its preselected epoch/seed procedure with no holdout-based early stopping.

**Acceptance:** training row count and label set match the originals; the resulting full-data model is a refit of the evaluated recipe. The holdout score estimates the development-trained recipe, not a fresh independent evaluation of this larger-data refit.

### P18 — Build the submission notebook

Notebook sequence:

1. Validate local assets and dependency versions without networking.
2. Resolve configured competition paths and load the actual runtime `test.csv`.
3. Load the final fitted artifact, or perform only the fixed final training recipe if the rules/execution design require training in the notebook.
4. Validate `id,text`, preserve runtime row order, and send only text to the predictor.
5. Predict in bounded batches, realign after any length sorting, and write `/kaggle/working/submission.parquet` with exactly `id,model` and no index.
6. Reopen the output and assert schema, types, row count, ID order, uniqueness, no nulls, and valid labels.
7. Log timings and artifact identities; do not run CV, tune parameters, open the holdout, or fetch remote assets.

Do not copy the sample submission's three IDs into production output. Do not hard-code three rows, 4,000 rows, test order, or the sample's placeholder labels. Sample IDs can be checked against the local three-row fixture during G1, but the production authority for IDs is the actual runtime test file.

### P19 — Final release verification

- [ ] Restart-and-run-all in a clean Kaggle session with Internet disabled and only declared inputs attached.
- [ ] Test on the supplied fixture and on a differently ordered, differently sized synthetic test file, including a one-row file.
- [ ] Re-run the 4,000/8,000-row resource checks on the selected final architecture. Include cold-start and any full-data refit time.
- [ ] Verify model/checkpoint and package hashes; ensure a cache miss cannot trigger networking.
- [ ] Re-run independent-row and artifact reload tests on the exact release bundle.
- [ ] Reopen the final Parquet using the pinned standard engine and compare with a typed expected dataframe. Logical schema/row identity matter; byte-for-byte equality with the sample writer is not required.
- [ ] Record notebook wall time, peak memory, output hash, row count, environment, source version, and final model version in `release_manifest.json`.

**Acceptance:** a completed offline notebook run produces a validated output within the confirmed runtime budget with reserve capacity. Uploading/submitting to Kaggle is a separate action; preparation of this plan does not imply a submission has occurred.

## 12. Essential verification matrix

These tests protect methodological or deployment risks; avoid adding tests that merely restate constructor arguments.

| Risk | Verification | Failure consequence |
|---|---|---|
| Same prompt in train/validation | Pairwise group/component intersection assertions for every split | Abort evaluation |
| Holdout accidentally used | Loader allowlists, split provenance, access ledger, dev-only worker input | Invalidate affected result; investigate lock exposure |
| Fold feature leakage | Validation-only sentinel token absent from fitted vocabulary; scaler fit-ID provenance | Fix and regenerate affected predictions |
| Outer tuning/early stopping | Selection API cannot accept outer labels; fit/selection membership audit | Invalidate optimistic evaluation |
| Misaligned probabilities | Deliberately permuted estimator classes recover identical blend after reindexing | Abort blend |
| Wrong metric | Imbalanced toy labels and incomplete prompt blocks checked by hand | Abort score reporting |
| Cache contamination | Change text/view/checkpoint and require miss; shuffle rows and verify alignment | Rebuild cache |
| Batch dependence | Single/mixed/shuffled/chunked/reloaded equality checks | Block release |
| Silent data loss | Every original row ID accounted for; diagnostic subsets explicitly separate | Block refit |
| Offline asset gap | Empty-cache network-disabled load; missing-file negative test | Block neural experimentation |
| Invalid output | Parquet round trip, IDs/types/order/labels/count assertions | Block release |
| Holdout-driven repair | Immutable decision and consumed-state checks | Mark subsequent work exploratory |

## 13. Work packages and planning estimates

These are engineering-effort estimates for one implementer familiar with Python/ML, not measured compute durations or guaranteed calendar deadlines. Hardware experiments determine wall time after G1.

| Work package | Tasks | Estimated effort | Deliverable |
|---|---|---|---|
| Protocol and contracts | P00–P03 | 1–2 days | Audit, explicit schemas, frozen experiment/split manifests |
| Offline feasibility | P04–P06 | 1–2 days plus asset transfer | Executed smoke notebook, memory/time evidence, valid Parquet |
| Baseline and nested runner | P07, P09, P10 | 2–3 days | Reliable grouped CV and sparse OOF |
| Frozen probe and hybrid | P08–P10 | 1–2 days plus measured compute | Comparable neural/blend/selector OOF |
| Diagnostics and decision | P11–P15 | 2–3 days | Metrics, robustness evidence, frozen decision |
| Confirmation and release | P16–P19 | 1–2 days | One-time report, full-data artifact, tested notebook |
| Optional fine-tuning | Separate extension | Budget only after profiling | Additional registered experiment; no automatic schedule commitment |

Critical path: freeze the data/protocol → prove offline inference/output → establish the sparse baseline → evaluate the frozen branch and bounded blend → freeze the development decision → consume the lock once → refit and validate the release.

## 14. Definition of done

The implementation is complete only when:

- [ ] All 2,699 original training rows and the 18 exact labels are accounted for, including the documented missing pair.
- [ ] The released classifier predicts each text independently with no need for `prompt_id`, companion responses, IDs as features, or test-distribution fitting.
- [ ] Split and experiment manifests make every score reproducible; per-candidate and complete-selector OOF are distinguished.
- [ ] All mandatory controls are executed or explicitly blocked with reasons; no missing control is presented as passed.
- [ ] The final decision precedes holdout access; the lock is consumed once and never used to repair a winner.
- [ ] Reported uncertainty acknowledges small prompt-level sample size, selection, and correlated CV fits.
- [ ] The final offline notebook has actually executed with the declared assets, measured resource headroom, and correctly formatted Parquet.
- [ ] The final report limits its claims to benchmark source attribution and measured robustness, without claiming intrinsic causal fingerprints.

## 15. Source traceability and deliberate changes to the report

| Plan requirement | Report location / additional basis |
|---|---|
| Preserve labels/data; raw-text sparse model | pp. 5–6, 13, 16–20 |
| Frozen encoder and restrained neural escalation | pp. 7–9, 26–29 |
| 30-prompt lock, 120-prompt development, nested grouped CV | pp. 9–11 |
| Topic proxies and provider diagnostics | pp. 11–13, 20, 24 |
| Clustered uncertainty and practical promotion threshold | pp. 13–15 |
| Artifact controls | pp. 17–18, 22–24, 26 |
| Offline notebook and Parquet output | pp. 16, 21–22 |
| Explicit text-only API and independence tests | User requirement 1; confirmed `id,text` test schema |
| Architecture selection inside inner folds; finite candidate policy | User requirement 2; strengthens report's per-architecture nesting |
| Holdout confirms a previously frozen choice rather than choosing a winner | User requirement 2; tightens report pp. 28–29 |
| Offline vertical slice before extensive neural experiments | User requirement 3; moves feasibility ahead of research |
| Metric-consistent paired permutation test | Corrects report's prompt-average approximation for incomplete blocks |
| Fixed seed policy interpreted appropriately for frozen versus trained encoders | Avoids treating identical frozen extraction as independent neural evidence |
| 36–274 observed word-count range and missing pair | Direct supplied-data audit; supersedes assumptions about perfect blocks/length bounds |

Implementation references checked during preparation:

- Hugging Face Transformers, **Installation / Offline mode**: https://huggingface.co/docs/transformers/installation#offline-mode — local assets, `HF_HUB_OFFLINE=1`, and `local_files_only=True`.
- scikit-learn, **Nested versus non-nested cross-validation**: https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html — separation of selection from evaluation. Pin the actual installed API version during G1.
- Competition overview to verify at P00: https://www.kaggle.com/competitions/name-that-llm/overview — substantive rule text was unavailable to this planning run; report-stated limits remain assumptions until checked.

The literature claims cited inside the supplied report were not independently re-audited for this implementation plan. The plan operationalizes the report's methodological requirements and explicitly records where it strengthens them.

## 16. Technology-stack selection and execution policy (22 October 2026)

This section supplements the original report-derived implementation plan. It settles implementation technology and deployment order while preserving the original G0–G6 controls, P00–P19 tasks, text-only inference contract, 18 canonical labels, prompt-grouped nested validation, and one-time holdout. Where the original plan and this section differ, the explicit stack decisions below supersede only **tool choice, checkpoint size, and CPU/neural gate eligibility**; methodological safeguards and experiment boundaries remain unchanged.

### 16.1 Decisions and rationale

| Area | Chosen technology | Why / permitted usage |
|---|---|---|
| Language/runtime | Python 3, version pinned from a passing Kaggle execution | Shared environment for inspection, modeling, notebook submission; no separate serving stack |
| Data/Parquet | `pandas` + `pyarrow` | Exact CSV schemas; write/read `submission.parquet` and verify the Arrow string columns; do not silently switch Parquet engines |
| Sparse ML | `scikit-learn`, `numpy`, `scipy` | `TfidfVectorizer`, sparse matrix concatenation, `LogisticRegression`, `GroupKFold` / `StratifiedGroupKFold` where supported, balanced accuracy; `Pipeline` prevents fold preprocessing leakage |
| Serialization | `joblib` (through the compatible scikit-learn installation), JSON and CSV manifests | Reproducible artifacts and audit trail; do **not** deserialize untrusted model files |
| Protocol config | JSON (`configs/protocol.json`), Python stdlib `json` / `hashlib` | Avoid a mandatory PyYAML dependency; hashes and explicit manifest versions |
| Tests | Python stdlib `unittest` or small assertion scripts | Data, leakage, OOF, text-only/batch-independence and Parquet contract tests without pytest requirement |
| Primary runtime | Kaggle notebook in CPU mode; remote execution allowed | Keep model training/inference feasible without a GPU and usable on the user's local laptop |
| Optional neural runtime | Kaggle GPU (T4 where available) or another permitted accelerator | Only for the frozen encoder G1b/G3 branch; hardware and quota must be measured, not assumed |
| Neural packages (conditional) | `torch`, `transformers`, `sentencepiece` (if needed by pinned tokenizer) | Install/stage only if G1b is authorized; freeze encoder and use one linear probe |
| Neural checkpoint (conditional) | `microsoft/deberta-v3-small` at one exact revision | Smaller fixed transformer challenger than report-proposed `deberta-v3-base`; verify actual memory/runtime/license offline |
| Excluded from v1 | MLflow, DVC, Optuna, Ray, Docker, Airflow, vLLM, Ollama, LightGBM/CatBoost, mandatory neural training services | No evidence they improve attribution enough to justify extra dependencies, deployment paths, or selection degrees of freedom |

**Core declaration:** `pandas`, `scikit-learn`, `pyarrow` are the only direct application-level packages required for the sparse track. NumPy, SciPy, threadpoolctl, and joblib are compatible transitive dependencies; list them explicitly in the *resolved runtime lock* if imported or used. A three-line unpinned `requirements.in` is acceptable as an intent manifest, **not** as the deployable environment lock. At G1a capture the actual wheel/package versions from Kaggle and validate an offline restart. Optional `requirements-neural.in` must not be installed by the sparse submission path. Do not add a requirements file with speculative version pins merely to satisfy this plan.

### 16.2 Preserve the probabilistic original baseline; constrain LinearSVC

The original v1 prespecified selection candidates **remain unchanged**:

- **S (primary sparse anchor):** word TF-IDF (1–2) plus character TF-IDF (3–5), sparse-concatenated and passed to multinomial-capable L2 logistic regression using the tested, explicitly pinned scikit-learn API. `predict_proba` has shape `(n, 18)` and uses canonical class order.
- **F (only after G1b passes):** frozen DeBERTa-v3-small attention-mask-aware mean embeddings + linear logistic probe with the existing `C` grid.
- **H (only after G1b passes):** fixed probability blend of S/F with the original prespecified weight grid and promotion threshold.

The newer exploratory char-only TF-IDF + `LinearSVC` result justifies a **CPU smoke/diagnostic comparator**, not an automatic replacement for S. `LinearSVC` has `decision_function`, not calibrated `predict_proba`; its margins cannot be treated as probabilities or dropped into H. Run it only at fixed configuration outside architecture selection, label it diagnostic, and do not let its observed score expand the candidate family, the nested grids, or G4 winner selection without a versioned amendment **before** lock access. No `CalibratedClassifierCV` should be introduced by default: calibration adds another train-only fit and selection dimension.

If G1b is infeasible, record the reason and set candidate eligibility to S-only **before running G3/G4 model comparisons**. Use S as the honest sparse-only release, do not impute neural results, and do not claim that an unrun F or H lost on quality.

### 16.3 Minimal architecture and deployment contract

- Keep the package/interface boundaries from section 4 even when individual modules are initially lightweight; avoid introducing an orchestrator, model server, database, remote API dependency, or Docker requirement.
- The notebook is a **thin offline submission adapter**: load local artifacts/data, call `predict(texts)`, preserve the input row order/IDs, and output exactly the two string columns `id, model` as `/kaggle/working/submission.parquet`. The notebook does not run nested CV or access `prompt_id` in final inference.
- If the competition runtime permits task-fitted artifacts, attach an immutable Kaggle Dataset snapshot containing the full-data refit and optional pinned encoder; otherwise perform the *fixed* refit inside the notebook and include its cost in the runtime budget. Verify permitted artifacts with P00 before choosing this route.
- During scoring, internet must be disabled. The neural loader uses local paths, `HF_HUB_OFFLINE=1`, `local_files_only=True` and `trust_remote_code=False`; all needed assets must be attached to the notebook environment before the run.
- Prefer deterministic CPU/GPU execution, explicit seeds and thread counts, well-bounded sparse feature arrays, `float32` where appropriate, and a declared memory limit. Sparse features remain sparse; no accidental dense `toarray()` on the training matrix.
- Keep the exact 18-class ordering in `configs/labels.json`. Always align classifier probability columns to this ordering; a test of intentionally permuted estimator class columns must reproduce the same blend.
- S must be deployable without importing `torch` or `transformers`. Conditionally import neural packages only if the frozen selection is F/H and offline assets passed G1b.

### 16.4 Runtime and feasibility gates, with evidence

| Gate | Required proof | If it fails |
|---|---|---|
| **G1a (mandatory, CPU)** | Clean offline Kaggle notebook reads sample `id,text` test, fits/loads sparse S on permitted data, predicts each row independently, performs Parquet write/read and schema/id/label checks, records memory/time and dependency lock | Block G2/G6 release and repair deployment; do not use leaderboard as debugger |
| **G1b (optional, neural eligibility)** | Pinned `deberta-v3-small` weights/config/tokenizer loaded offline without Hub cache, finite deterministic embeddings for a development-only fixture, safe inference memory, measured extraction cost and scale estimate | Mark F/H infeasible; proceed with S-only |
| **G2 (required)** | Five outer/four inner prompt-grouped sparse logistic baseline, valid OOF probability matrix and leak/convergence tests | Repair G2 without using outer labels for selection |
| **G3 (conditional)** | If G1b passes, fit original F and H nested selector; otherwise produce machine-readable eligibility/exclusion record | Do not treat blocked F/H as scored or missing-at-random |
| **G4–G6 (required)** | Robustness, pre-holdout decision freeze, one-time holdout, full-data refit, full offline replay | Block release or record contradiction as prescribed in sections 8–11 |

**Acceptance conditions for the minimum stack:** G1a must run on a fresh remote notebook with internet disabled, no runtime package download, and measured end-to-end output. Record both the measured result and any unverified prerequisites; a locally tested snippet is not evidence of Kaggle completion. `sample_submission.parquet` is a schema example, not a source of labels for hidden rows. Hidden-run timing must include the intended inference batch size and worst-case length checks. The original proposed 80%-of-memory and 70%-of-time engineering reserves remain in force.

### 16.5 How this affects the original work packages

| Task | New technology-specific instruction |
|---|---|
| P00 | Verify current rules, CPU runtime, optional Kaggle GPU availability and offline artifact mechanics; capture tested Python, package, CUDA and driver versions, rather than assuming the laptop or Kaggle GPU configuration |
| P01–P03 | Use stdlib JSON manifests, pandas/NumPy audits and scikit-learn grouped folds; record the exact 30-prompt lock; previous informal development runs are not evidence that the locked manifest exists |
| P04–P06 | Treat the CPU sparse notebook/Parquet smoke as G1a; only stage/test DeBERTa-small as conditional G1b; profile batch 1 first on a 4 GB GPU if used, and measure accelerator headroom on remote hardware |
| P07 | Keep the report-backed word+character TF-IDF logistic classifier as S. A char TF-IDF LinearSVC may run as a frozen diagnostic but is not promoted by observing its score |
| P08–P10 | Run F/H only after G1b; cache frozen embeddings with full provenance; preserve nested architecture selection, fixed candidate family and original cost accounting |
| P11–P16 | No change to metric, group-aware inference, robustness, paired uncertainties, one-time holdout or prohibition on post-lock tuning |
| P17–P19 | Keep final refit separate from development; generate two-column Parquet with pyarrow and validate it via a fresh internet-disabled Kaggle notebook execution |

### 16.6 System One is research-only, not an implicit fourth candidate

`vllm-sr/Decision-2.0-Eos-0.8B` and newer System One / semantic-router checkpoints are **not** part of v1 or its deployable dependencies. Zero-shot 18-choice classification may be tried in a separately registered exploratory extension **before** the holdout opens, on identical prompt-disjoint development partitions. Its custom-code and hardware requirements increase the attack surface and resource burden. No decision-model score may silently enter S/F/H selection or ensembles. A future registered comparison must prove text-only independent prediction, offline loading, fair group-level evaluation and complementarity against S before a new selection protocol is warranted.

### 16.7 Documentation/source hierarchy and current evidence status

- Original methodology and task gates: sections 1–15 above, derived from the supplied 30-page report and project constraints.
- Technology decisions in this section: subsequent project technology investigation (22 October 2026); these are deliberate engineering choices, **not** experimental outcomes from the original report.
- The original report proposed `deberta-v3-base`; `deberta-v3-small` is an intentional lower-resource substitution and must be recorded as such in the frozen experiment registry.
- Earlier exploratory CPU benchmark comparisons have not been promoted to registered nested-CV evidence in this plan. They do not license post-hoc changes to S/F/H, and **no assumption is made that the locked split/holdout has actually been sealed** until P02 produces its durable manifests and access controls.
- This is a **plan**, not a claim that the repository contains implemented code, a passing Kaggle smoke run, a sealed holdout, or a trained model.
