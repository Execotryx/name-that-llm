## 1. Align the policy
- [x] 1.1 Preserve the synthetic producer-passed/consumer-rejected reproduction as a regression fixture.
- [x] 1.2 Define one resource-check helper and explicit measurement schema; preserve the existing reserve thresholds.
- [x] 1.3 Validate numeric budgets before expensive execution and use the shared checks at G1 producers, gate consumers and applicable G6 publication checks.
- [x] 1.4 Measure the explicit encoder device, with allocated/reserved peaks and documented phase boundaries.

## 2. Verify behavior
- [x] 2.1 Test slow extraction/fast inference, inference overflow, exact boundaries, valid passing records, malformed numbers and missing fields.
- [x] 2.2 Test nondefault-device accounting with computation doubles and keep actual device acceptance separate.
- [x] 2.3 Verify blocked local/non-cold runs, S-only continuation and preservation of release/holdout failure state.
- [x] 2.4 Update AGENTS.md and runbook with implemented resource semantics and explicit legacy-evidence handling.

## 3. Acceptance
- [x] 3.1 Run Pyright, the full unittest suite and strict OpenSpec validation and retain results.
- [ ] 3.2 If F/H is activated, run the corrected G1b on the pinned local checkpoint in a real cold target environment and show that the unchanged record is accepted by eligibility checks before scored fitting.
- [x] 3.3 Retain neural target acceptance as pending or explicitly not activated when assets/hardware are unavailable; never fabricate success or consume G5 for this check.

Software tasks above are verified by the [implementation log](../../../docs/25-10-2026-05-50-35-readiness-controls-implementation.md) and its linked validation records. Neural execution fixtures use computation doubles; actual cold target/checkpoint acceptance remains separately unchecked. No real holdout was consumed.
