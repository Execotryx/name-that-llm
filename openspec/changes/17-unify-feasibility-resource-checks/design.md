# Design: consistent feasibility decisions

## Minimal interface

Implement one pure helper accepting budgets and measured resource fields and returning explicit failure reasons (or raising for malformed input). Producers use those reasons to determine status; consumers apply the same helper after provenance/file verification. Avoid a hierarchy of gate classes or a second policy configuration. Continue using registered `.8` and `.7` limits.

Separate total stage wall time, measured workload time, process peak memory and optional GPU measurements. Both total wall and the applicable workload time must fit the registered allowance. Measurements must be finite and nonnegative; required inference costs must be strictly positive. Budget inputs must be finite and positive, validated before fitting, creating an eligible record or reserving release output. Equality at either reserve boundary fails, matching current strict behavior.

For GPU measurements, use the encoder's actual device explicitly, record its identity and allocated/reserved peaks, and apply the declared device-memory reserve consistently. Do not accidentally measure the default device for `cuda:1`. Capture or reset peak statistics at the documented phase boundary without excluding a model that was already loaded; record the timing boundary. Do not infer device headroom from process RAM.

## Reproduction and tests

Use synthetic fixtures and a deterministic clock to reproduce a short projected inference time with excessive stage wall time. The current producer says `passed`; after the fix it must say `blocked`, and the consumer must agree on the reason. Include exact-boundary, just-below-boundary, inference-over-budget, invalid/NaN/infinite, memory-over-budget and nondefault-device fixtures. A valid unchanged record must pass the consumer in a synthetic target fixture. A local or non-cold run remains blocked regardless of resource sufficiency.

Synthetic target flags test control flow only. Real evidence requires actual cold target execution, staged dependencies/assets and recorded allowances. Do not consume a real holdout in these tests.

## Migration

Version any changed resource evidence fields explicitly. Preserve old records and reject incomplete legacy evidence instead of silently filling measurements. Record the amendment and regenerate affected upstream/downstream evidence; do not rehash old results or clear G5 state. The S-only branch remains usable after its own G1a proof if the neural branch is blocked.
