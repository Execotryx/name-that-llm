# frozen-challenger — Spec Delta

## Purpose

A frozen contextual encoder may capture attribution cues complementary to sparse stylistic fingerprints, but neural experimentation cannot proceed without demonstrated offline load, resource budget and a bounded selection procedure.

## ADDED Requirements

### Requirement: Offline frozen-encoder eligibility

A neural challenger MUST NOT run scored experiments until a single pinned DeBERTa-v3-small checkpoint and its tokenizer load offline with measured safe resource use on target hardware.

#### Scenario: Offline load succeeds
- **WHEN** an eligible notebook starts with internet disabled and only attached local assets
- **THEN** the configured checkpoint extracts deterministic finite embeddings with logged memory/time headroom

#### Scenario: Offline load fails
- **WHEN** an asset is missing or profiling shows unsafe memory/runtime
- **THEN** F and H are marked infeasible and the S-only path remains operational

### Requirement: Frozen, identity-safe representation

The encoder MUST remain in evaluation mode without gradient updates, use a registered 512-token mask-aware pooling policy, and cache only authorized development data with full provenance.

#### Scenario: Row order changes
- **WHEN** development rows are shuffled before embedding lookup
- **THEN** cache identity validation returns the correct embedding for each original row

#### Scenario: Configuration changes
- **WHEN** tokenizer revision or pooling policy differs from cache manifest
- **THEN** the stale cache is rejected and embeddings must be recomputed

### Requirement: Bounded S/F/H nested selection

The original predeclared S/F/H candidates MUST be compared using grouped inner-fold OOF probabilities with the fixed four C choices per component, 11 blend weights and complexity threshold.

#### Scenario: Complexity not justified
- **WHEN** the best F/H inner score improves S by less than 0.03 balanced accuracy
- **THEN** S is selected regardless of a small raw rank advantage

#### Scenario: Outer validation exposed
- **WHEN** selection code requests outer validation labels to choose weights
- **THEN** the request is denied and no selected outer OOF is produced

### Requirement: Feasibility exclusion semantics

If G1b fails, the project MUST record a neural eligibility failure and MUST NOT report F or H as evaluated or inferior in accuracy.

#### Scenario: Blocked challenger
- **WHEN** DeBERTa cannot meet offline resource requirements
- **THEN** the G3 record states S-only eligibility, the reason, and which neural comparisons were not run
