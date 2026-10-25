## ADDED Requirements

### Requirement: Consistent resource acceptance
Feasibility evidence producers and consumers MUST use the same applicable resource limits and strict comparison rules for stage wall time, workload time, RAM and optional GPU memory.

#### Scenario: Slow extraction with fast inference
- **WHEN** G1b takes 100 seconds under a 100-second allowance even though projected or measured inference is below 70 seconds
- **THEN** the producer records a blocked time-reserve result and the consumer rejects the same resource violation

#### Scenario: Passing evidence is consumable
- **WHEN** a newly generated target record has unchanged valid provenance, files and all required resource measurements below their reserves
- **THEN** the consumer accepts its resource assessment without applying a different time definition

#### Scenario: Exact reserve boundary
- **WHEN** memory equals 80% of its allowance or applicable time equals 70% of its allowance
- **THEN** both production and consumption reject the record for insufficient reserve

### Requirement: Valid and device-specific measurements
The system MUST reject invalid budgets or resource measurements and MUST associate neural GPU measurements with the actual encoder device.

#### Scenario: Invalid numeric input
- **WHEN** a budget is zero, negative or nonfinite, or required measurements are missing, negative or nonfinite
- **THEN** no passing feasibility evidence is produced or accepted

#### Scenario: Nondefault GPU
- **WHEN** the encoder runs on a nondefault CUDA device
- **THEN** its memory peaks and capacity are measured on that device and the same recorded reserve policy is enforced by the consumer

### Requirement: Sparse independence and evidence honesty
Blocked neural feasibility MUST leave S-only eligibility available after its separate valid G1a evidence, and synthetic/local execution MUST NOT be presented as real target acceptance.

#### Scenario: Neural resource failure
- **WHEN** G1b fails a resource check and G1a remains valid
- **THEN** F/H remain unscored and the existing sparse-only execution route remains available

#### Scenario: Legacy resource record
- **WHEN** required measurements are absent from an older evidence schema
- **THEN** the consumer requests explicit revalidation without inventing measurements or resetting any holdout ledger
