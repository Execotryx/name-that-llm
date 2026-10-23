# offline-release — Spec Delta

## Purpose

The released classifier must be a faithful full-data refit of the evaluated recipe and must pass a cold, offline replay in the target environment on real test schema without introducing inference-time dependencies on prompt context.

## ADDED Requirements

### Requirement: Exact full-data refit

After G5 closure, the implementation MUST refit the unchanged selected recipe on all original labeled rows and MUST NOT use the former lock for new model/seed/parameter decisions.

#### Scenario: Final fit
- **WHEN** all 2,699 labeled examples are supplied to the frozen training recipe
- **THEN** the fitted model accounts for every row and all 18 exact labels

#### Scenario: Recipe drift
- **WHEN** the final run tries new C or a different checkpoint revision
- **THEN** the release checker rejects the artifact as not matching `decision.json`

### Requirement: True text-only target platform inference

The final notebook MUST read actual runtime `id,text` input, predict each text independently and write correct two-column `submission.parquet` in the identical ID order.

#### Scenario: Hidden test size differs
- **WHEN** runtime test row count is not 3 or 4,000
- **THEN** the notebook processes exactly the present rows and never imports sample placeholder labels

#### Scenario: Missing prompt ID
- **WHEN** the runtime test file lacks `prompt_id`
- **THEN** inference succeeds without reconstructing or looking up a prompt

### Requirement: Offline reproducible release

A release MUST pass clean internet-disabled runtime restart with declared assets, pinned versions, validated Parquet round trip, and measured resource headroom.

#### Scenario: Warm cache absent
- **WHEN** the scoring notebook starts with no unrelated Hugging Face cache
- **THEN** all permitted artifacts load locally or the run fails with a clear missing-asset error rather than downloading

#### Scenario: Deployment artifact invalid
- **WHEN** Parquet fields, IDs, row order, types or label membership differ
- **THEN** release is blocked and an execution failure record is produced

### Requirement: Evidence-backed completion

G6 MUST produce a manifest linking exact committed source, trained artifacts, dependencies, notebook execution and output hashes; documentation alone is not proof of success.

#### Scenario: Notebook not executed
- **WHEN** only a generated `.ipynb` exists
- **THEN** the release gate remains incomplete, regardless of checklist completion

#### Scenario: Release score claimed
- **WHEN** a refit artifact has not been independently evaluated
- **THEN** the report distinguishes its inherited evaluated recipe from a fresh validation result
