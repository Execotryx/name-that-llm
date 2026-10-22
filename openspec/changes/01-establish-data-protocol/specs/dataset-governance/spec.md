# dataset-governance — Spec Delta

## Purpose

A small benchmark containing 2,699 responses from 150 prompts can yield optimistic author-attribution scores when responses from the same prompt leak across validation boundaries or the final holdout is repeatedly consulted.

## ADDED Requirements

### Requirement: Immutable benchmark inventory

The implementation MUST retain all 2,699 labeled rows, the exact 18 labels and their raw text, and MUST account for the single absent prompt/model pair rather than imputing it.

#### Scenario: Missing class-prompt response
- **WHEN** the audit reads prompt `p002` with only 17 responses
- **THEN** it records missing `claude-fable-5` without inventing a row; all other original rows are unchanged

#### Scenario: Integrity drift
- **WHEN** any source hash or expected schema deviates
- **THEN** the run fails with a versioned discrepancy report before training

### Requirement: Prompt-disjoint partition

The implementation MUST persist a deterministic 30-prompt holdout and 120-prompt development allocation (unless a documented near-duplicate component adjustment is required), together with outer and inner grouped splits.

#### Scenario: Validation isolation
- **WHEN** a development fold is created
- **THEN** no prompt or connected near-duplicate component appears on both sides and every development example is assigned exactly once to an outer validation fold

#### Scenario: Replay
- **WHEN** the split manifest is reloaded on the pinned environment
- **THEN** the exact row/group membership reproduces without relying only on a seed

### Requirement: Holdout isolation

Routine development code MUST NOT read, vectorize, extract embeddings from, tune on, or examine labels for the locked partition.

#### Scenario: Unauthorized development access
- **WHEN** a normal training/EDA command requests a locked ID
- **THEN** the command refuses the access and records the violation

#### Scenario: Past exposure
- **WHEN** evidence of previously inspected holdout content emerges
- **THEN** the project documents the exposure and does not claim unexposed confirmation

### Requirement: Frozen experiment policy

Before registered comparisons, the project MUST version the finite S/F/H candidates, eligibility conditions, fixed grouped folds, metric, promotion thresholds, and diagnostic budget.

#### Scenario: Unregistered architecture
- **WHEN** an experiment runner receives an unregistered candidate or seed
- **THEN** it rejects the launch and requires a recorded protocol amendment

#### Scenario: Protocol reconfiguration
- **WHEN** a user requests to reseed splits after viewing scores
- **THEN** the system refuses to present the reseeded run as preregistered confirmation
