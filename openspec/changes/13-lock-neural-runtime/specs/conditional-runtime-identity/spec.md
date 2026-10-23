# conditional-runtime-identity — Spec Delta

## ADDED Requirements

### Requirement: Conditional runtime manifest

Each execution MUST record the required runtime profile, and neural execution MUST bind exact dependencies and relevant numerical settings to its evidence.

#### Scenario: Sparse-only environment
- **WHEN** torch and transformers are absent and S is selected
- **THEN** core profiling and inference work without importing or requiring them

#### Scenario: Neural profile
- **WHEN** F or H is enabled
- **THEN** the manifest includes required neural packages/builds, execution settings and applicable accelerator metadata

#### Scenario: Missing required dependency
- **WHEN** the chosen encoder/tokenizer needs an absent package
- **THEN** preflight fails with an actionable local dependency error and makes no download attempt

### Requirement: Runtime drift rejection

Required dependency or numerical-setting drift MUST be rejected before neural work unless an explicit validated compatible profile authorizes it.

#### Scenario: Package upgrade
- **WHEN** transformers or torch changes while all core package versions stay identical
- **THEN** the G1b/downstream compatibility check fails before extraction or prediction

#### Scenario: Numerical setting drift
- **WHEN** precision, TF32, determinism or an enforced execution setting changes
- **THEN** existing evidence/cache identity is not silently reused

#### Scenario: Declared compatible target
- **WHEN** the runtime matches a separately validated profile referenced by the stage evidence
- **THEN** execution may proceed under that recorded profile without claiming it is byte-identical to a different environment

### Requirement: Runtime-bound artifacts

Neural caches, decisions and release bundles MUST carry and verify the applicable runtime identity along with asset and implementation identities.

#### Scenario: Stale embeddings
- **WHEN** cache entries were produced under an incompatible neural profile
- **THEN** they are rejected rather than loaded by row/text identity alone

#### Scenario: Offline replay
- **WHEN** a bundle is replayed with a missing or incompatible neural runtime
- **THEN** release is blocked before final submission publication and records the mismatched fields
