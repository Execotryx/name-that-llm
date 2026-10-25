## 1. Restore the deployment recipe
- [x] 1.1 Reproduce the isolated `ntl.release` import failure using only the current export; retain the traceback and environment inventory.
- [x] 1.2 Regenerate `requirements-runtime.txt` from the unchanged committed lock and confirm `packaging` is present without upgrades or neural additions.
- [x] 1.3 Add a normalized export-drift check covering additions, removals, version and marker changes.

## 2. Verify the actual staging path
- [x] 2.1 Include the runtime export in the shared execution inventory and release copying path; test source-root and bundled layouts.
- [x] 2.2 Run a fresh unseeded local-wheel-only installation and verify imports, profile capture, tiny synthetic fit and Parquet output without optional imports.
- [x] 2.3 Add the negative omitted-dependency regression and record the fixed isolated result.
- [x] 2.4 Update AGENTS.md and the runbook for the implemented export check, acquisition boundary and migration rule.

## 3. Acceptance
- [x] 3.1 Run Pyright, the full unittest suite, export verification and strict OpenSpec validation; retain outputs.
- [ ] 3.2 Re-run the mandatory cold target G1a packaging acceptance from change 02 using the corrected export; keep target acceptance pending until real evidence exists.
- [x] 3.3 Verify affected evidence regeneration preserves source/splits, text-only inference and every prior G5 ledger.

Software tasks above are verified by the [implementation log](../../../docs/25-10-2026-05-50-35-readiness-controls-implementation.md) and its linked validation records. Neural execution fixtures use computation doubles; actual cold target/checkpoint acceptance remains separately unchecked. No real holdout was consumed.
