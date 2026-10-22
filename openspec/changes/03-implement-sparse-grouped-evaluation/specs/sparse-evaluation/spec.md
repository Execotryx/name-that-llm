# sparse-evaluation — Spec Delta

## Purpose

The release requires a competitive, reproducible CPU baseline and an evaluation runner that isolates prompt groups and prevents preprocessing and hyperparameter leakage.

## ADDED Requirements

### Requirement: Sparse reference classifier

The project MUST implement S as the fixed word+character TF-IDF logistic regression with four registered `C` choices and 18-class probabilistic output.

#### Scenario: Fit on training fold
- **WHEN** a new grouped fold is evaluated
- **THEN** both TF-IDF vocabularies, IDF weights and classifier parameters are fitted using only that fold's training IDs

#### Scenario: Convergence failure
- **WHEN** a trained estimator emits unresolved convergence warnings
- **THEN** the run is flagged and applies a predeclared uniform remedy or fails

### Requirement: Nested grouped OOF evaluation

The project MUST create exactly one outer prediction per development row using inner prompt-grouped selection and MUST never tune on that row's outer validation label.

#### Scenario: Fold integrity
- **WHEN** five outer folds and four inner folds are executed
- **THEN** all 120 development prompt groups remain disjoint within each train/validation division and OOF covers each development row once

#### Scenario: Outer-label intrusion
- **WHEN** an inner selection component is passed outer validation labels
- **THEN** the interface rejects the operation rather than using labels for tuning

### Requirement: Canonical probabilities and metric

All S probabilities MUST be finite, have exactly 18 canonical-label columns and sum to one; primary balanced accuracy MUST average recall over all 18 true classes.

#### Scenario: Class order changes
- **WHEN** a fitted estimator stores classes in a different order
- **THEN** probability reindexing reproduces identical canonical predictions

#### Scenario: Incomplete prompt block
- **WHEN** one class has 149 rather than 150 examples
- **THEN** balanced accuracy uses class recall denominators and does not assume uniform prompt completeness

### Requirement: Unregistered baseline control

The project MUST NOT use word-only, char-only LinearSVC or other diagnostic scores to replace S in the registered selection protocol without an explicitly recorded amendment before holdout access.

#### Scenario: Diagnostic scores high
- **WHEN** a LinearSVC variant beats S in exploratory analysis
- **THEN** the registry records this as diagnostic rather than silently adding it to candidate selection

#### Scenario: Ensemble request
- **WHEN** a caller attempts to blend LinearSVC `decision_function` margins as probabilities
- **THEN** the implementation rejects the uncalibrated input
