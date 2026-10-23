# release-publication-control — Spec Delta

## ADDED Requirements

### Requirement: Gate-controlled publication

The release workflow MUST publish submission.parquet only after all target G6 checks pass and MUST preserve a hash-linked completion record.

#### Scenario: Passing target replay
- **WHEN** schema, identity, offline/cold target and resource checks all pass
- **THEN** the candidate is atomically published as submission.parquet and completion evidence identifies its exact hash

#### Scenario: Resource failure
- **WHEN** time or memory exceeds the registered reserve threshold
- **THEN** blocked evidence is retained, the attempt produces no final submission and target execution fails

#### Scenario: Other gate failure
- **WHEN** schema, environment, provenance, target detection, cold restart or independence validation fails
- **THEN** no final output is published and a specific failure reason is retained

#### Scenario: Local diagnostic replay
- **WHEN** inference works outside a qualifying target environment
- **THEN** a blocked diagnostic result may be returned with non-final output, but submission.parquet is not published

### Requirement: Explicit execution failure

The target notebook and CLI MUST terminate unsuccessfully on blocked or failed release rather than only printing status.

#### Scenario: Notebook blocked
- **WHEN** replay returns a blocked outcome in the real notebook code path
- **THEN** the notebook raises an exception and cannot be mistaken for successful release

#### Scenario: CLI blocked
- **WHEN** target release is blocked
- **THEN** the CLI exits nonzero with an actionable reason

### Requirement: Attempt-safe output handling

Publication MUST NOT overwrite prior output or evidence and interrupted attempts MUST NOT be represented as completed releases.

#### Scenario: Existing output
- **WHEN** a final submission or release manifest already exists
- **THEN** preflight refuses the new attempt before inference and leaves existing bytes unchanged

#### Scenario: Publication failure
- **WHEN** rename or final evidence persistence fails
- **THEN** execution fails, preserves incident evidence where possible and does not report completion

#### Scenario: Interrupted publication
- **WHEN** a restart finds a final output without matching completed evidence
- **THEN** the workflow refuses automatic reuse and requests explicit reconciliation without resetting G5
