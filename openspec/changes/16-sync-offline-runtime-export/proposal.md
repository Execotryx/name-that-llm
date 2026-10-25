# Synchronize the offline sparse runtime export

## Why

Review of `8fdf97a323c9b3169cacee73bce22593d2c3b1d0` reproduced a deployment failure outside the development environment. `pyproject.toml` and `uv.lock` include `packaging`, but `requirements-runtime.txt` does not. Installing only that export in a fresh, unseeded environment and importing `ntl.release` raises `ModuleNotFoundError: No module named 'packaging'` at `environment.py:13`. The existing 37 tests run in the complete development environment and do not detect this drift.

This is mandatory for G1a and G6, mapping to P04–P06 and P18–P19. It must be resolved before relying on the exported dependencies to stage target execution. Sparse fitting under `uv sync --locked` is a separate, working installation route.

## What Changes

- Regenerate the sparse runtime requirements from the committed lock, including `packaging`.
- Add a deterministic export-drift check and a fresh-environment import/contract check that cannot inherit development packages.
- Bind the dependency export used for offline staging to the relevant execution/bundle inventory, so a changed deployment recipe cannot reuse evidence silently.
- Document acquisition versus offline execution and the supported source-root layout.

## Capabilities

### New Capabilities
- `offline-runtime-export-integrity`: the deployed sparse dependency recipe is complete, reproducible and verified independently of the developer environment.

### Modified Capabilities
- None. This additive capability supplements changes 02, 07, 10 and 15.

## Impact

Affected: `requirements-runtime.txt`, export verification, `common.code_files`, release bundle copying, relevant tests and runbook. Dependencies: existing lock, runtime-profile v2 and execution identity v2. Keep optional neural distributions out of the sparse export.

Non-goals: package upgrades, a new dependency resolver, online installation during inference, changing source data or statistical protocol, consuming G5, or claiming Kaggle readiness from a local install.
