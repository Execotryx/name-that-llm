# locked-confirmation — Spec Delta

## Purpose

The only genuinely independent confirmation is a single evaluation of the previously frozen development choice. Repeated holdout comparisons would destroy the methodological safeguard.

## ADDED Requirements

### Requirement: Single authorized lock access

The project MUST refuse a G5 run until G4 configuration, artifact hashes, source/split integrity and previous-consumption status are verified.

#### Scenario: First authorized run
- **WHEN** a valid signed decision exists and the lock has no prior exposure
- **THEN** exactly the registered development-trained candidate may predict locked texts

#### Scenario: Second holdout attempt
- **WHEN** consumed-state or score exposure is recorded
- **THEN** a second independent confirmation run is denied

### Requirement: Predictions precede labels

Predictions and their hashes MUST be sealed before true locked labels, metrics or error lists are made available.

#### Scenario: Authorized evaluation
- **WHEN** the predictor scores the locked texts
- **THEN** prediction and artifact hashes are persisted before the scoring stage can inspect labels

#### Scenario: Configuration drift
- **WHEN** loaded model hashes differ from `decision.json`
- **THEN** the evaluation aborts without silently substituting artifacts

### Requirement: Prespecified interpretation only

Holdout results MUST be interpreted under the fixed reversal thresholds and paired uncertainty logic without selecting or tuning a new winner.

#### Scenario: Material reversal
- **WHEN** a selected challenger scores at least .03 balanced accuracy below S
- **THEN** the report flags contradiction and withholds a claim of robust challenger superiority

#### Scenario: Inconclusive difference
- **WHEN** the paired interval includes zero
- **THEN** the report states uncertainty and does not change the frozen candidate
