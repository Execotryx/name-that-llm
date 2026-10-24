# Proposal: Validate active runtime requirements before accepting an inventory

## Why

Review of `0566bc76abfd76341d674c6d5c480dd1d5cdfb40` found a **P2** gap in `package_inventory()`. A missing dependency is ignored whenever its requirement contains a semicolon, even when its marker evaluates true. Installed dependencies are accepted without checking version constraints. Focused reproductions accepted a missing `required-child>=1; python_version >= "3.0"` and installed version `0.1` for `required-child>=2.0`. Extra-related requirements are skipped by substring matching rather than resolved according to selected extras.

## What Changes

- Parse distribution requirements and evaluate markers for the actual runtime and explicitly requested extras.
- Require every active dependency and validate every active incoming version constraint, including transitive requirements.
- Record a deterministic, versioned dependency closure and marker context in runtime profiles and locks; retain offline, metadata-only discovery.
- Fail before optional imports, extraction, fitting or publication when the required runtime is incomplete or incompatible.

## Capabilities

### New Capabilities

- `active-runtime-dependency-validation`: [requirements and acceptance scenarios](specs/active-runtime-dependency-validation/spec.md).

### Modified Capabilities

None in the canonical tree, which is absent. This additive correction supplements unarchived change 13 and its consumers in 09/10.

## Impact

- **Traceability:** [IMPLEMENTATION_PLAN.md](../../../IMPLEMENTATION_PLAN.md), G0 runtime capture, G1a/G1b and downstream G2–G6; P03–P10, P14–P19.
- **Dependencies:** changes 09, 10 and 13; coordinate profile version/role consumption with 14.
- **Affected files:** `src/ntl/environment.py`, `encoder.py`, `provenance.py`, relevant gate consumers, `pyproject.toml`/`uv.lock`, tests and runbook.
- **Applicability:** mandatory for core dependency discovery; neural packages/extras remain conditional on the applicable execution role.
- **Status:** implemented with local synthetic verification; real target acceptance remains pending.

## Non-Goals

No package installer, online resolver, automatic dependency repair, version upgrade or permissive compatibility whitelist. Do not activate all extras or make sparse execution depend on torch. No dataset, label, split, candidate, fit-budget or holdout-state changes. Real neural/target feasibility still requires its own evidence.
