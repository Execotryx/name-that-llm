# Design: Accept the registered Parquet string schema

## Context and scope

At reviewed commit a4499c7, all three supplied input hashes match the registered originals, but prepare() rejects sample_submission.parquet because both fields are Arrow large_string and the validator accepts only string. The writer separately hardcodes string. G0 cannot start on its own registered inputs.

Reviewed baseline: `a4499c73d8bdc6db89679cdffa36995a2128c0a6`. These controls now have implementation and local regression coverage; see tasks.md for remaining real execution evidence.

## Decisions and failure paths

### 1. Logical and physical types

Accept pa.string() and pa.large_string() as logical UTF-8 strings; reject binary, numeric, dictionary and other types unless separately specified. Keep exact ordered column names, non-null values, unique nonblank IDs and sample/test ID alignment. Sample placeholder model values are not classifier outputs and must not train or select a model.

### 2. One persisted contract

Record the observed sample field types and choose those physical types for emitted output, including zero-row output. Pass this immutable contract to the adapter rather than reconstructing it from inferred pandas dtypes. Verify physical schema and values on round trip; do not weaken runtime canonical-label checks.

### 3. Failure and migration

Invalid schema or IDs must fail before publishing a complete development/sealed manifest. Use fresh temporary roots for tests. Existing campaigns require an explicit versioned artifact migration or fresh pre-exposure preparation with unchanged source/split policy; never silently rewrite manifests or reset a consumed lock.

## Dependencies and evidence

Existing changes 01, 02 and 07. Deliver before new real G0 and before 11-fail-closed-release acceptance.

Implement [tasks.md](tasks.md) and verify every [acceptance scenario](specs/submission-schema-compatibility/spec.md). Retain commands, environment, failure logs and artifact identities. No test may inspect real locked labels or reserve a real G5 attempt merely to validate software behavior. Use temporary synthetic campaigns for destructive/failure-path checks.
