## ADDED Requirements

### Requirement: Deterministic development-only capacity inputs
G1 capacity profiles MUST use a bound deterministic workload containing representative authorized development texts and explicit long-input stress, with fresh unique IDs and no locked texts or labels used in workload selection.

#### Scenario: Workload reproducibility
- **WHEN** the same development manifest and workload version are supplied
- **THEN** the generated ordered text/ID identities are reproducible for each registered scale

#### Scenario: Holdout contamination
- **WHEN** a workload source row is outside the development allowlist
- **THEN** workload construction fails before inference and does not open the sealed partition

### Requirement: Actual scale and full-batch measurement
Accepted profiles MUST execute the 0/1/3/4,000/8,000-row workloads without prediction or embedding-cache shortcuts and MUST exercise the configured full batch on the long-input stress case.

#### Scenario: Seven-row extrapolation
- **WHEN** evidence contains only a seven-row neural timing multiplied to estimate 4,000-row cost
- **THEN** it is insufficient for accepted capacity evidence and neural eligibility remains blocked

#### Scenario: Maximum-token full batch
- **WHEN** optional encoder feasibility is measured
- **THEN** at least one complete configured encoder batch of maximum-token-length inputs is executed, with device memory and runtime recorded

#### Scenario: Missing scale or failed output
- **WHEN** a required scale is absent, exceeds reserve, fails prediction, or produces invalid IDs/Parquet
- **THEN** the relevant feasibility gate remains blocked with a recorded reason

### Requirement: Comparable selection costs
Selection costs MUST derive from the same bound primary workload scale, ordered texts and timing definition for S and F, while retaining the registered additive cost rule for H.

#### Scenario: Mismatched component profiles
- **WHEN** G1a and G1b use different primary workload identities or timing definitions
- **THEN** eligibility rejects their joint use before scored F/H fitting or selection

#### Scenario: Comparable profiles
- **WHEN** both profiles contain valid measured costs for the same 4,000-row primary workload
- **THEN** selection receives those positive finite S/F costs and their sum for H without changing statistical thresholds

### Requirement: Evidence regeneration is explicit
Workload-policy or timing-definition changes MUST invalidate affected feasibility and dependent selection evidence without modifying prior holdout state.

#### Scenario: Legacy synthetic profile
- **WHEN** old repeated-sentence or extrapolated evidence lacks the new workload contract
- **THEN** the consumer requests new feasibility evidence rather than silently upgrading the old record
