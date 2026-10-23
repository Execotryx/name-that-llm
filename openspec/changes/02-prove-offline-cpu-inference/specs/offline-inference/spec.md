# offline-inference — Spec Delta

## Purpose

A valid attribution model is unusable unless a clean internet-disabled deployment environment can load its dependencies and process arbitrary independent test rows into a correct Parquet submission.

## ADDED Requirements

### Requirement: Text-only deterministic attribution

A predictor MUST take one or more response strings and produce source-label predictions independent of IDs, prompt IDs, other responses, batch size and row ordering.

#### Scenario: Companion-row invariance
- **WHEN** the same response is predicted alone, after unrelated rows are appended and after order is permuted
- **THEN** the restored label and 18-class probability vector agree within the registered tolerance and prediction label remains identical

#### Scenario: Schema isolation
- **WHEN** test input supplies only `id,text`
- **THEN** the predictor receives `text` only and has no dependency on `prompt_id`

### Requirement: Strict submission schema

The submission writer MUST output the exact ordered UTF-8 string columns `id` and `model`, preserving unique runtime test IDs in input order, with valid non-null labels and no extra columns.

#### Scenario: Parquet round trip
- **WHEN** the three-row fixture or any synthetic test is run
- **THEN** reading the generated Parquet reproduces the expected `id,model` dataframe schema, label membership and ID ordering

#### Scenario: Malformed IDs
- **WHEN** the test contains missing or duplicate IDs
- **THEN** the adapter fails explicitly instead of making ambiguous predictions

### Requirement: Offline CPU feasibility

A mandatory G1a run MUST complete in a restarted target CPU notebook without network activity, remote downloads or optional neural packages.

#### Scenario: Cold start
- **WHEN** the execution environment has an empty unrelated model cache and internet is disabled
- **THEN** all declared assets resolve locally and an output Parquet is produced with logged resource and runtime evidence

#### Scenario: Missing package
- **WHEN** a required local dependency is absent
- **THEN** the notebook fails with an actionable dependency error and makes no download attempt

### Requirement: Input robustness

A predictor MUST retain row identity for empty and unusual text strings, reject non-string/null text values and emit a typed empty output when given zero test rows.

#### Scenario: Empty string
- **WHEN** the text field is a literal empty string
- **THEN** the configured vectorizer/model path handles the row without dropping or replacing its ID

#### Scenario: Invalid type
- **WHEN** the text field is null or a non-string value
- **THEN** validation reports a schema error before model inference
