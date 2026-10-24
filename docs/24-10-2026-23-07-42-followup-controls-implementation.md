# Follow-up controls implementation: OpenSpecs 14–15

## Result

Implemented provenance roles and validated installed requirements. Decision/G4 provenance v3 preserves `selection_execution` and per-model `artifact_execution`, with a checked selected `execution` alias for generic gate validation. Freeze retains selection-evidence snapshots. Confirmation validates all prediction artifacts before reservation. Full-data refit and both replay modes enforce the frozen selected identity while retaining decision/G5 and selection bindings. S can execute after neural selection without unused neural requirements.

Runtime profiles and locks use v2. A single metadata-only closure traversal parses requirements, evaluates actual markers, validates every active constraint and propagates explicit extras until stable. False-marker packages do not enter the closure. Cycles terminate and conflicting parents are checked even after a package was visited. Malformed metadata, unknown extras, unsupported active URLs and incompatible/missing requirements fail locally. The complete applicable closure is checked before optional imports. `packaging` is directly declared and locked.

## Simplicity critique and revisions

| Pass | Critique | Resolution |
|---|---|---|
| 1 | A single execution field conflated selection history and the live model; repairing it with special-case equality exceptions would spread architecture logic through consumers. | Use one explicit role envelope, retain immutable history, and use the selected-role alias with existing generic gates. Snapshot selection records in one directory. |
| 2 | Confirmation repeated recipe, asset and runtime checks in separate loading loops; envelope construction repeated the same selected identity. | Centralize prediction-model loading/verification and envelope construction. Both first verification and immediate pre-reservation loading use the shared checks. |
| 3 | Dependency handling could become a separate resolver with ad hoc marker/extras branches and platform workarounds. | Use packaging's parser and one finite installed-closure traversal, shared by inventory, profiles and locks. No resolver, installer, new framework or compatibility exceptions. |

Final scoped review found no further actionable simplification. The remaining fixed-point traversal is necessary for late extras and cycles; exact marker-context comparison is intentional and requires fresh platform evidence. This does not claim that no future critique is possible.

## Validation

- [Full unittest output](validation/followups-unittest.txt): 37 tests passed in 68.635 seconds.
- [Pyright](validation/followups-pyright.txt): zero errors/warnings.
- [Local document checks](validation/followups-structure.txt): package/scenario/task/link/whitespace checks; not full OpenSpec CLI validation.
- `test_followups` exercises actual freeze serialization for direct S, veto-to-S, F and H using deterministic neural computation doubles. For every result, a disposable clean Git source snapshot and committed receipt exercise the actual verifier, first confirmation and repeat denial with unchanged ledger bytes.
- Existing real-receipt coverage now uses historical neural selection with S and denies optional neural metadata lookup. Docs-only commits pass and real code drift fails. Both sparse refit/replay modes retain historical neural selection but contain no encoder.
- Dependency cases include active missing/incompatible requirements, false compound markers with installed/absent packages, explicit/late extras, cycles, conflicting parents, reordered traversal, malformed/unsupported requirements, legacy profiles and drift. Transitive encoder failure occurs before optional imports.

## Migration and limitations

Old ambiguous decisions, runtime profiles and locks are rejected explicitly. Preserve historical evidence and all reserved/exposed/closed G5 state; affected campaign evidence needs documented revalidation under unchanged source/split/search policy, not silent rehashing or renewed independent confirmation.

Source rows, canonical labels, split seeds/policy, model families and tuning/veto budgets were unchanged. No real holdout was consumed, no benchmark training/selection ran, and no external competition submission occurred. Neural computation in regression fixtures is synthetic. Real pinned-checkpoint/GPU and cold target evidence remain pending; G1b/G6 are not advanced by these tests.

Full OpenSpec CLI validation remains pending: the earlier automatic approval review rejected its external telemetry/egress, so it was not retried. Local offline structural checks are recorded separately. The two packages retain unchecked offline CLI and real-target tasks.
