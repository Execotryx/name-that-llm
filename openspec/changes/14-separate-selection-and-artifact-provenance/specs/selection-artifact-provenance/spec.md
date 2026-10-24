# selection-artifact-provenance — Spec Delta

## ADDED Requirements

### Requirement: Distinct selection and artifact identities

A frozen decision and G4 MUST use an explicit versioned envelope binding immutable selection provenance and an execution identity for every saved artifact. Identity roles MUST be complete, consistent and derived from the actual artifacts.

#### Scenario: Neural evaluation chooses S directly
- **WHEN** F/H were eligible but the unchanged final selector chooses S
- **THEN** the decision retains neural selection provenance and binds the selected S artifact to a sparse execution identity with no encoder

#### Scenario: Challenger fails a robustness veto
- **WHEN** a selected F/H candidate fails an existing veto, including unavailable topic evidence
- **THEN** the prescribed S fallback receives a sparse artifact identity while the original selection evidence and veto result remain bound and unchanged

#### Scenario: Challenger survives selection
- **WHEN** F or H remains selected after all vetoes
- **THEN** the selected role binds its verified neural execution identity and the reference S role independently binds a sparse identity

#### Scenario: Invalid role envelope
- **WHEN** a role is missing, unexpected, inconsistent between decision and G4, or incompatible with its actual model architecture
- **THEN** the consumer rejects the decision before prediction or holdout reservation

### Requirement: Preserved selection integrity

Separating roles MUST NOT bypass live G4 validation of implementation, eligible gates, assets/runtime, costs, data/splits or diagnostics, and later consumers MUST verify the receipt-bound historical evidence.

#### Scenario: Evidence changes before freeze
- **WHEN** a required G2/G3, G1b, measured cost, topic or implementation identity changes after evaluation
- **THEN** freeze rejects reuse before final-selection fitting or receipt publication

#### Scenario: Selection history changes after freeze
- **WHEN** the recorded selection identity or required upstream evidence changes after its receipt is committed
- **THEN** confirmation refuses the modified history before reservation even if the selected artifact itself is unchanged

### Requirement: Architecture-scoped confirmation and release

G5 MUST preflight every model it will execute against that model's role identity. Refit and replay MUST validate the selected recipe's applicable identity while preserving selection history, text-only inference, canonical labels and exact runtime IDs.

#### Scenario: Unused neural runtime is absent
- **WHEN** a valid neural-selection-to-S decision is consumed with matching code/core dependencies but no unused neural packages or encoder assets
- **THEN** receipt verification, confirmation and refit can proceed without neural metadata requirements, imports or loads, and S replay reaches the ordinary G6 checks

#### Scenario: S-only campaign
- **WHEN** only S was eligible and its frozen evidence remains valid
- **THEN** the new envelope supports the original sparse workflow without requiring G1b or neural dependencies

#### Scenario: Required selected or reference artifact drifts
- **WHEN** a model that will predict has changed bytes, recipe, code, required runtime or encoder identity
- **THEN** G5 fails before reservation and leaves existing consumption state unchanged

#### Scenario: Both release modes
- **WHEN** either an attached-model or fixed-refit bundle is created from a valid S fallback
- **THEN** replay checks its sparse selected identity, preserves the exact decision/G5/selection bindings and publishes no final submission unless G6 passes

#### Scenario: Required neural execution drifts
- **WHEN** an F/H winner is replayed with incompatible required neural assets or runtime
- **THEN** the role split does not bypass preflight and no final submission is published

### Requirement: Versioned migration without renewed holdout access

Legacy ambiguous provenance MUST fail explicitly, and migration MUST preserve historical artifacts and all holdout consumption state.

#### Scenario: Legacy single execution field
- **WHEN** an old decision or bundle lacks the new role envelope
- **THEN** verification reports the required migration rather than inferring roles or silently rewriting evidence

#### Scenario: Documentation-only commit
- **WHEN** only documentation or the required receipt commit changes and all executable identities remain equal
- **THEN** the new role checks do not invalidate otherwise valid evidence solely because the Git commit differs

#### Scenario: Existing holdout attempt
- **WHEN** a migration or repeated confirmation encounters a reserved, exposed or closed G5 ledger
- **THEN** it preserves that ledger and does not authorize a second independent confirmation or automatic reset
