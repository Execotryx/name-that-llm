# Tasks: Implement sparse baseline and prompt-grouped nested evaluation

**Gate:** G2 · **Plan packages:** P07, P09–P10 (sparse component), P11 metric basics · **Status:** not started (documentation only).

## 1. Implement S precisely

- [ ] 1.1 Implement separate word and character vectorizer branches with raw text, specified n-grams/limits, unit-weight sparse concatenation and fold-fitted logistic regression.
- [ ] 1.2 Implement canonical class reindexing, deterministic prediction, stable serialization and fixed `C`/solver/seeds from G0.
- [ ] 1.3 Add deliberately validation-only sentinel strings, moved-label test fixtures and no-dense-materialization assertions.

## 2. Build the evaluation runner

- [ ] 2.1 Consume sealed development-only outer and inner manifests; do not load the locked texts or infer prompt IDs in production model code.
- [ ] 2.2 For each outer fold, use four inner folds to choose C, refit on outer-training only and persist all outer OOF probabilities and selections.
- [ ] 2.3 Implement pooled 18-class balanced accuracy and per-class supports; test the incomplete block's weighting versus simple accuracy and fold averaging.
- [ ] 2.4 Track fit counts, warnings, timing, input/split/code hashes and all failures in experiment_registry.csv.

## 3. Verify and expose diagnostics

- [ ] 3.1 Run predefined fixed-setting word-only / char-only LinearSVC / style controls only in diagnostic namespace, clearly disjoint from S candidate selection.
- [ ] 3.2 Prove OOF row coverage, 18 probability columns, class order, isolation under shuffle and deterministic reruns.
- [ ] 3.3 Persist G2 acceptance evidence; do not score sealed data or claim unbiased architecture selection.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`sparse-evaluation` specification](specs/sparse-evaluation/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
