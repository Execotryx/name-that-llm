# cross-stage-provenance — Spec Delta

## ADDED Requirements

### Requirement: Consistent stage identity

Every passing stage MUST bind its artifacts to a versioned execution identity and exact required upstream evidence; consumers MUST verify those bindings before dependent work.

#### Scenario: Modeling code drift
- **WHEN** feature extraction or model code changes between nested evaluation and freeze
- **THEN** G4 refuses stale evidence before fitting a new final model or publishing a receipt

#### Scenario: Documentation-only commit
- **WHEN** only documentation or the required decision receipt changes
- **THEN** unchanged executable identity remains compatible despite a different Git commit

#### Scenario: Asset or cost drift
- **WHEN** candidate names are unchanged but encoder assets, measured selection costs or required runtime profile differ
- **THEN** freeze rejects reuse of the previous evaluation evidence

### Requirement: Verified topic provenance

A completed topic report MUST be backed by verified artifacts and the matching data, representation, implementation and row identity.

#### Scenario: Bare or stale topic report
- **WHEN** a completed report lacks its evidence manifest or belongs to a different encoder/view/runtime
- **THEN** freeze rejects it instead of applying its scores as a veto

#### Scenario: Report and predictions disagree
- **WHEN** a report metric differs from recomputation on its persisted aligned predictions
- **THEN** validation fails even if the report itself has a valid file hash

#### Scenario: Topic unavailable
- **WHEN** topic execution is blocked
- **THEN** the limitation is recorded and a challenger cannot pass the existing topic veto

### Requirement: Frozen confirmation boundary

Confirmation MUST verify committed frozen provenance before reserving the holdout, and incompatible evidence MUST NOT be repaired by resetting consumption state.

#### Scenario: Pre-exposure mismatch
- **WHEN** a real committed receipt resolves to incompatible code or evidence
- **THEN** the unmocked decision verifier denies confirmation before reservation or prediction

#### Scenario: Previously exposed campaign
- **WHEN** a provenance defect is found after G5 exposure
- **THEN** the consumed ledger and results are preserved and no automatic second independent confirmation is permitted
