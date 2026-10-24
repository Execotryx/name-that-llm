# Design: Separate selection history from artifact execution identity

## Context

At reviewed commit `0566bc7`, one `execution` field serves two incompatible purposes: documenting a neural-enabled experiment and describing a saved sparse classifier. The mismatch occurs at `locked_eval.verify_decision`, before reservation, and also affects the identity inherited by release bundles. Replacing the neural identity with a sparse identity everywhere would discard relevant selection provenance.

## 1. Explicit identity roles

Introduce a decision/G4 provenance envelope with `provenance_version: 3`. Keep the existing execution-identity primitive versioned independently. Use these named fields consistently rather than interpreting a missing encoder as permission to ignore a mismatch:

| Field | Meaning | Verification |
|---|---|---|
| `selection_execution` | Exact implementation, runtime and optional encoder used for final selection, consistent with G2/G3 and applicable diagnostics | Compared with live selection execution at G4; preserved as historical evidence afterward |
| `artifact_execution` | Map keyed exactly like `artifacts` (`selected`, and conditional `reference`) | Each entry is derived from the actual saved/restored model and checked against that model's architecture and frozen recipe |
| `upstream` / evidence hashes | Exact eligible gates, run, diagnostics, topic and measured costs used to choose/veto | Verified before freeze; covered by the committed decision/G4 receipt |

Bind the role map, configs, artifact file hashes, schema, source/split identities and selection outcome into the immutable decision and G4. Enforce identical role maps between decision and G4; reject missing, extra or conflicting roles. Do not silently reinterpret the previous single `execution` field as either role.

S has a sparse runtime and no encoder; F has the exact verified frozen encoder; H has the registered sparse and frozen branches, with the frozen branch's assets/runtime. A reference S has its own sparse identity even when the selected model is F/H. The actual serialized object must agree with its declared architecture; do not trust only a top-level label. Keep the registered source implementation identity enforced across roles and allow documentation/receipt-only commits as before.

## 2. Freeze without changing selection

Retain all current checks against live selection execution: G2/G3, eligibility, exact G1a/G1b lineage and measured costs, artifact diagnostics, and topic report verification. Run the unchanged final selection and robustness veto. Capture artifact identities only after the outcome is fixed and each model is fitted, serialized, restored and checked.

A direct S win and a veto-driven S fallback both retain the original neural `selection_execution`. They both record a sparse `artifact_execution.selected`. F/H winners retain a neural selected identity and a sparse reference identity. Never rerun selection simply to make an identity match. G4 explicitly records the final choice, veto outcome and blocked-topic limitation when applicable.

## 3. Confirmation and historical evidence

`verify_decision()` must continue using the real clean executing checkout, committed receipt, full decision/G4 hashes, code identity, data/protocol hashes and required upstream evidence. Update gate validation deliberately for the new G4 envelope; do not remove identity checks globally or weaken G1/G2/G3 validation.

A consumer verifies the integrity and consistency of the frozen selection record, but does not recreate its historical neural runtime to execute a sparse artifact. After S is frozen, removing the unused neural packages/assets must not make G5/refit/replay require them. Relevant core runtime and code must still match. Historical gate files required by the verifier remain available and hash-verified; this exemption applies only to executing or requiring the unused encoder/runtime, not to missing selection evidence.

Before G5 reservation, verify every artifact that will predict, including the sparse reference for an F/H winner. Compare live identities against the corresponding role, not only against the selected role. An F/H asset/runtime mismatch remains a hard failure. Existing reservation, prediction-before-label ordering and one-use consumption rules remain intact.

## 4. Refit and replay

Carry `selection_execution`, the original role bindings and their frozen decision/G5 hashes as provenance. Derive and verify the full-data selected model's execution identity against the frozen selected identity; changing fitted coefficients during the registered full-data refit does not change the recipe/runtime identity. Bind the new fitted file hash separately.

Both attached-model and fixed-refit bundles use the selected identity for live execution. An S bundle contains no encoder and requires no neural packages, even if neural experiments preceded selection. F/H bundles retain cold asset verification and exact runtime checks. Replay preserves the role envelope, validates the decision/confirmation/refit chain, and publishes only after all G6 checks pass. No implicit cross-platform or numerical-policy compatibility is introduced.

## 5. Migration and failure behavior

Reject legacy ambiguous decisions/G4/bundles with an actionable schema/migration error before G5 reservation or release publication. Preserve old receipts, evidence, attempts and ledgers. The changed code identity invalidates affected evidence: a documented amendment must determine regeneration under the same registered data/split/search policy before an untouched campaign proceeds. Do not merely edit an old decision and recompute its hash. A reserved, exposed or closed G5 is never automatically reset; any permitted pre-exposure incident handling follows the existing custodian process. No regeneration grants a consumed campaign a new independent holdout.

## 6. Validation strategy

Use synthetic rows, a deterministic test encoder and disposable clean Git repositories. Parameterize the selection path to exercise S-only eligibility, neural direct-S, challenger-to-S veto, F and H. Cheap test doubles may replace neural computation; they must not replace `verify_decision`, role comparison, committed-receipt lookup or ledger operations. Include a subprocess that denies optional neural metadata/import access for post-freeze S execution.

Run the actual freeze → committed receipt → verify/confirm path and both refit modes. Keep confirmation fixtures separate so each ledger is used once. Tamper each role, selected/reference artifact, required runtime/asset identity, selection lineage and code; assert failure before reservation or publication as applicable. Verify docs-only commits, exact ordered output IDs, canonical labels and consumed-ledger preservation. Local replay remains blocked outside a real target; mocked target success establishes only publication control flow. Real cold target evidence stays separate and pending.
