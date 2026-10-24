# active-runtime-dependency-validation — Spec Delta

## ADDED Requirements

### Requirement: Marker-aware dependency activation

Runtime inventories MUST evaluate parsed requirement markers against the executing environment and explicitly activated extras. Only applicable dependency edges MUST determine the required installed closure.

#### Scenario: Active conditional dependency is absent
- **WHEN** a requirement marker is true for the runtime and the dependency is missing
- **THEN** discovery fails with the parent, requirement and evaluated context instead of ignoring the dependency because a semicolon is present

#### Scenario: Inactive dependency is absent or installed
- **WHEN** a marker is false and no other active edge or root requires that distribution
- **THEN** its absence causes no failure and its presence or version does not alter the required closure or applicable runtime identity

#### Scenario: Compound markers
- **WHEN** a requirement combines Python, platform, implementation or extra predicates
- **THEN** activation follows the parsed expression rather than substring tests or the presence of an environment marker

#### Scenario: Explicit transitive extra
- **WHEN** an active edge requests a child extra, including one discovered after that child was first visited
- **THEN** the extra's applicable dependencies are validated while unrequested extra-only dependencies remain inactive

### Requirement: Every active version constraint is enforced

Each installed dependency MUST satisfy every applicable incoming requirement. Invalid or unsupported active requirement metadata MUST fail explicitly without automatic installation.

#### Scenario: Installed version is incompatible
- **WHEN** `required-child>=2.0` is active and version `0.1` is installed
- **THEN** discovery rejects the environment and identifies the parent, required constraint and installed version

#### Scenario: Compatible installed closure
- **WHEN** all active requirements are present with satisfying versions
- **THEN** metadata-only discovery succeeds and retains their exact installed versions and build identities

#### Scenario: Conflicting parents
- **WHEN** a previously visited dependency satisfies one parent but violates another active parent constraint
- **THEN** discovery rejects the conflict instead of skipping validation because the dependency was already inventoried

#### Scenario: Cycles and ordering
- **WHEN** valid active dependencies form cycles or metadata/root traversal order changes
- **THEN** discovery terminates and produces the same canonical closure without losing later constraints or extra activation

#### Scenario: Malformed or unsupported requirement
- **WHEN** applicable metadata is unparseable, an installed version is invalid, an extra is unknown, or an active direct-URL requirement lacks supported local-wheel provenance
- **THEN** discovery fails with an actionable error and performs no fetch, install or silent omission

### Requirement: Validated closure binds runtime evidence

Profiles, locks, cache keys and applicable stage evidence MUST bind versioned validated dependency closure semantics and relevant marker context. Legacy unchecked profiles MUST NOT be silently accepted as validated.

#### Scenario: Required environment changes
- **WHEN** required versions/builds, activated extras or relevant marker values change the validated profile
- **THEN** lock/evidence compatibility rejects unapproved drift and stale cache identity is not reused

#### Scenario: Invalid environment during lock preparation
- **WHEN** the installed closure is incomplete or incompatible during asset/runtime-lock preparation
- **THEN** no accepted runtime lock or passing eligibility evidence is produced, and any staging record remains explicitly non-eligible

#### Scenario: Legacy inventory or lock
- **WHEN** a profile or lock lacks the validated closure schema
- **THEN** consumers report explicit revalidation/migration requirements without rewriting historical artifacts or resetting holdout state

### Requirement: Offline preflight before optional execution

The complete applicable dependency closure MUST be checked before optional imports/loads or dependent neural work. Sparse execution MUST remain independent of optional neural packages.

#### Scenario: Invalid neural closure
- **WHEN** a required core, neural or tokenizer dependency is missing or incompatible at encoder preflight
- **THEN** failure precedes torch/transformers imports, loader calls, embedding creation or fitting and makes no network request

#### Scenario: Sparse execution without neural packages
- **WHEN** the current execution role is S and its core requirements are valid
- **THEN** metadata capture and inference neither require nor import optional neural packages, including after a historical neural-selection-to-S fallback

#### Scenario: Confirmation or replay with invalid required dependencies
- **WHEN** a frozen model's required closure is invalid at confirmation or replay
- **THEN** G5 does not reserve a new holdout attempt, existing ledger bytes remain unchanged, and G6 publishes no final submission
