## ADDED Requirements

### Requirement: Lock-consistent sparse deployment export
The runtime requirements export MUST contain the complete locked sparse application dependency set, including directly imported `packaging`, and MUST exclude development-only and optional neural requirements.

#### Scenario: Current missing dependency regression
- **WHEN** the export omits `packaging` while the committed project lock requires it
- **THEN** the export-drift check fails and names the missing dependency before packaging can be accepted

#### Scenario: Reproducible regeneration
- **WHEN** the registered export command runs against an unchanged lock
- **THEN** its normalized requirement entries match the committed export without changing dependency versions

### Requirement: Isolated offline import proof
Packaging validation MUST exercise the sparse entry points in a fresh environment populated only from the exported runtime dependencies and local staged wheels, without ambient developer packages or network access.

#### Scenario: Clean runtime succeeds
- **WHEN** the complete export is installed offline and the bundled source layout is imported
- **THEN** CLI/help, `ntl.release`, runtime-profile capture and a synthetic text-only fit/Parquet round trip succeed without torch or transformers

#### Scenario: Incomplete environment fails locally
- **WHEN** a required application dependency is absent
- **THEN** the check fails with that dependency identified and makes no network installation attempt

### Requirement: Deployment recipe provenance
The runtime export MUST be included in the verified execution and release inventories used to justify offline staging.

#### Scenario: Export changes after evidence
- **WHEN** the dependency export changes after an execution identity was recorded
- **THEN** dependent evidence is rejected until explicitly regenerated under the established migration policy, while existing holdout consumption state remains unchanged
