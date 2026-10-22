# robustness-and-decision — Spec Delta

## Purpose

Grouped nested CV alone does not remove bias from repeated model and diagnostic comparisons. Claims of source attribution also require uncertainty, artifact sensitivity and a complete decision frozen before holdout access.

## ADDED Requirements

### Requirement: Fixed-label performance reporting

The system MUST report pooled 18-class BA and per-class support/recall without silently changing the evaluation label set or averaging fold scores as if independent.

#### Scenario: Incomplete prompt
- **WHEN** the `p002` missing pair affects sample balance
- **THEN** the scorer uses true support for each class and reports correct class recalls

#### Scenario: Missing class support
- **WHEN** an evaluated subset lacks a true class
- **THEN** the primary BA calculation refuses an invalid 18-class claim

### Requirement: Group-aware uncertainty

Inference MUST use prompt-group bootstrap and BA-consistent paired randomization tests with the registered replicate counts and multiplicity-aware resampling.

#### Scenario: Prompt resampled twice
- **WHEN** a bootstrap draw includes the same prompt twice
- **THEN** all of its member rows contribute twice to the replicate statistics

#### Scenario: Candidate comparison
- **WHEN** F and/or H eligible OOF exists
- **THEN** paired differences, descriptive intervals and multiplicity policy are reported without claiming selection-adjusted coverage

### Requirement: Artifact and topic stress disclosure

Registered diagnostics MUST preserve row identities, report class support and transformation/refit status, and MUST disclose any blocked topic-representation test.

#### Scenario: Tokenizer stripping empties a response
- **WHEN** a format or prefix transform produces an empty text
- **THEN** the row remains and is scored under the normal text-only inference contract

#### Scenario: Encoder unavailable
- **WHEN** the required topic-proxy representation cannot be obtained
- **THEN** the diagnostic is marked blocked, never passed

### Requirement: Irreversible pre-holdout decision

Before locked evaluation, the team MUST freeze architecture, parameters, class mapping, assets, batch settings and artifact hashes in `decision.json` with a reproducible G4 report.

#### Scenario: Unfixed parameter
- **WHEN** the holdout command sees missing blend weight, checkpoint revision or training artifact hash
- **THEN** it refuses locked evaluation

#### Scenario: Weak challenger
- **WHEN** F/H fails promotion margin or a registered veto
- **THEN** the selected candidate is S rather than an ad hoc revised challenger
