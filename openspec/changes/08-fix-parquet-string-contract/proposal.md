# Proposal: Accept the registered Parquet string schema

## Why

At reviewed commit a4499c7, all three supplied input hashes match the registered originals, but prepare() rejects sample_submission.parquet because both fields are Arrow large_string and the validator accepts only string. The writer separately hardcodes string. G0 cannot start on its own registered inputs.

## What Changes

- Define one logical UTF-8 contract for ordered id,model fields, explicitly accepting Arrow string and large_string.
- Persist the accepted sample physical schema and the chosen output physical schema in the protocol artifacts; use them consistently in validation, writing and replay.
- Add direct preparation and adapter tests using the observed sample schema, without changing any original input bytes or hashes.

## Capabilities

### New Capabilities

- `submission-schema-compatibility`: corrective requirements in [spec.md](specs/submission-schema-compatibility/spec.md).

### Modified Capabilities

None in the canonical spec tree, which is currently empty. This additive corrective capability supplements the existing unarchived changes; it does not replace their requirements.

## Impact

- **Plan traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G0, G1a, G6; P00–P02, P05, P18–P19.
- **Dependencies:** Existing changes 01, 02 and 07. Deliver before new real G0 and before 11-fail-closed-release acceptance.
- **Affected files:** src/ntl/protocol.py, src/ntl/inference.py, relevant smoke/release callers, schema regression tests and docs/runbook.md.
- **Status:** implemented with local regression coverage; real target/campaign acceptance remains pending.

## Non-Goals

No new candidate family, hyperparameter search, source-data modification, split reseeding, automatic holdout reset or external submission. Text-only prediction, the canonical 18 labels and prompt-group isolation remain mandatory. Synthetic validation does not pass real target gates.
