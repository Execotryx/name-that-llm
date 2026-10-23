# submission-schema-compatibility — Spec Delta

## ADDED Requirements

### Requirement: Logical UTF-8 sample acceptance

Preparation MUST accept both Arrow string and large_string under the registered ordered id,model logical schema while retaining source-hash and ID checks.

#### Scenario: Registered sample
- **WHEN** the exact registered sample has large_string fields and matching test IDs
- **THEN** preparation passes schema validation without editing or re-encoding any supplied file

#### Scenario: Equivalent string storage
- **WHEN** a controlled schema fixture uses string, large_string or a mixture across the two fields
- **THEN** the logical schema is accepted and the physical field types are recorded

#### Scenario: Invalid input
- **WHEN** field order, a field type, null values, ID uniqueness or sample/test ID alignment is invalid
- **THEN** validation fails before a complete G0 manifest is published

### Requirement: Consistent output representation

The adapter and release verifier MUST consume the persisted schema contract, preserve test ID order and enforce canonical output labels.

#### Scenario: Round trip
- **WHEN** zero-row and nonempty submissions are serialized
- **THEN** their physical field types match the recorded output schema and round-trip values and ID order are exact

#### Scenario: Prompt-free input
- **WHEN** runtime input contains only id,text with a row count different from the sample
- **THEN** all rows are predicted independently and no sample placeholder label or prompt metadata is used
