# Tasks: Validate active runtime dependencies

**Status:** implementation/local verification complete; offline CLI and real-target acceptance remain pending.
**Traceability:** review P2 at `0566bc7`; G0–G6, P03–P10/P14–P19; changes 09/10/13 and coordinated change 14.

## 1. Requirement semantics

- [x] 1.1 Add a directly declared, locked `packaging` dependency and replace regex/substring requirement handling with standards-aware parsing, canonical names and marker evaluation.
- [x] 1.2 Define role-scoped root requirements/extras and capture the actual marker context used for activation without importing optional packages.
- [x] 1.3 Implement installed-closure traversal with transitive extra propagation, deterministic cycle termination and validation of every incoming version constraint.
- [x] 1.4 Reject malformed requirements, invalid versions, unknown extras and unsupported active direct URLs with actionable local errors and no installation/network fallback.

## 2. Runtime and lock integration

- [x] 2.1 Version runtime profiles/locks for validated closure semantics; record roots/extras, relevant marker context, canonical edges and package/build identities with explicit legacy rejection.
- [x] 2.2 Use validated profiles for lock creation/verification, metadata-only consumers and cache/stage identity; preserve staged-wheel coverage and sparse isolation.
- [x] 2.3 Move complete applicable dependency validation before optional encoder imports and model/tokenizer loads, including required core dependencies.
- [x] 2.4 Enforce validation at confirmation/replay boundaries in coordination with change 14; preserve historical selection identity and existing holdout/output incident semantics.

## 3. Regression verification

- [x] 3.1 Add metadata fixtures for active missing requirements, false markers with missing/installed dependencies, compound Python/OS/implementation predicates and canonicalized package names.
- [x] 3.2 Test satisfying and failing constraints, prerelease/local-version semantics, transitive failures and conflicting diamond constraints on already visited packages.
- [x] 3.3 Test explicit extras, late extra activation, unrequested extras, unknown extras, cyclic graphs and deterministic identities under reordered inputs.
- [x] 3.4 Test malformed/unsupported metadata, versioned legacy rejection, marker-context/profile drift, cache invalidation and failed lock preparation that cannot produce accepted evidence.
- [x] 3.5 Exercise encoder/profile consumers with loader/import/network spies, S isolation and G5/G6 failures; assert no neural work, new holdout reservation or final publication on invalid required dependencies.
- [x] 3.6 Run `uv run pyright` and `uv run python -m unittest discover -s tests -v`; retain outputs and trace every acceptance scenario to coverage.

## 4. Handoff and external acceptance

- [x] 4.1 Update AGENTS.md, runbook, dependency/profile schema and migration documentation plus a dated implementation log with actual validation evidence.
- [ ] 4.2 Validate OpenSpec structure using a permitted offline validator and preserve its output separately from test and gate evidence.
- [ ] 4.3 When separately authorized pinned assets/wheels and target hardware are available, validate the actual offline dependency closure and cold neural preflight; keep G1b/G6 blocked until genuine required evidence exists without consuming a real holdout for software validation.

## Local evidence and acceptance boundaries

See `tests/test_followups.py`, the expanded contract/correction tests and `docs/validation/followups-*`. Synthetic neural computation is a deterministic test double; real Git receipts, the verifier, reservation/consumption logic and release controls execute normally. No real holdout was consumed. Local structural validation is not a replacement claim for full OpenSpec CLI validation. Real checkpoint/GPU/Kaggle evidence stays pending.
