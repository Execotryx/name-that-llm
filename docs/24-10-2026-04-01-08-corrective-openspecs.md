# Corrective OpenSpec proposals

Created: 24-10-2026-04-01-08 (Asia/Qyzylorda).

Baseline reviewed: a4499c73d8bdc6db89679cdffa36995a2128c0a6.

Added six corrective change packages (08–13), each with schema metadata, proposal, design, additive capability delta and unchecked implementation tasks. They address sample Parquet string compatibility, frozen encoder asset integrity, cross-stage provenance, fail-closed submission publication, formatting-preserving prefixes and conditional neural runtime identity.

The canonical openspec/specs tree is absent; corrective requirements use distinct additive capability names and supplement the seven existing unarchived changes. No existing requirement or campaign evidence is removed. Updated the OpenSpec index and runbook to distinguish proposed corrections from executable behavior.

No Python, model configuration, source input, split, holdout ledger, receipt or release artifact is changed. No real campaign stage, training, holdout confirmation or submission is executed. All new tasks remain unchecked.

Validation:

- OpenSpec CLI 1.14.3 reported 13 changes passed and zero failed under `validate --all --strict --no-interactive`. Captured output: [corrective-openspecs.txt](validation/corrective-openspecs.txt). The captured invocation set `OPENSPEC_TELEMETRY=0`. Final process completion could not be verified: automatic approval review rejected a follow-up because the validator contacted an untrusted third-party host beyond the npm registry and the transmitted data was not established. No network retry or workaround was attempted after rejection. The printed validation result is recorded without claiming a verified successful exit.
- Structural/link checks: all six packages contain schema metadata, proposal, design, spec and tasks; 57 tasks remain unchecked; 43 WHEN/THEN scenarios; no broken relative Markdown file links.
- `git diff --check` passed; new Markdown files checked for trailing whitespace.
- Python tests/Pyright were not rerun for this documentation-only change. Each corrective task list requires them when executable controls are changed. No campaign gate was advanced.
