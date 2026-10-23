# Design: Bind stage evidence to the evaluated implementation

## Context and scope

G4 accepts G2/G3 evidence based on data identity and file hashes without requiring the same modeling implementation. A synthetic check accepted OLD_IMPLEMENTATION evaluation with NEW_IMPLEMENTATION freeze. Topic reports are accepted without a manifest binding their scores to predictions, assets and implementation.

Reviewed baseline: `a4499c73d8bdc6db89679cdffa36995a2128c0a6`. These controls now have implementation and local regression coverage; see tasks.md for remaining real execution evidence.

## Decisions and failure paths

### 1. Relevant implementation identity

Create a deterministic versioned manifest covering executable ntl modules, submission notebook, effective protocol/labels, preprocessing/view versions and relevant dependency lock. Record Git revision separately. Exclude prose-only docs and receipt commits from executable identity; resolve files against the verified source/package root, not arbitrary current working directory. Record training versus replay roles explicitly where a stage-specific identity is required.

### 2. Evidence lineage

Each stage stores execution identity plus hashes of required upstream gates. G2 captures G1a and conditional G1b identities; G4 compares these to current identities and the exact G2/G3 run, diagnostics and topic evidence. Candidate-name equality is insufficient: encoder identity, measured selection costs and runtime profile must match the registered run. G5 checks the committed receipt and full frozen identity before reservation. G6 binds exact decision, confirmation and refit identities.

### 3. Topic evidence

Write a manifest hashing cluster membership, vectors or their identity, fold assignments/selections, OOF predictions, experiment registry and report. Bind the root data/splits, raw and transformed encoder identities, view version and execution identity. Freeze verifies files, row alignment and report metrics against persisted predictions; a bare completed JSON is insufficient. A blocked topic record remains explicit and prevents challenger promotion under existing veto policy.

### 4. Changes and recovery

Any relevant code/config/runtime/asset change invalidates affected downstream evidence, even if committed and clean. Re-execution is allowed only with preserved attempt history and a recorded protocol amendment when required. No migration may silently relabel old evidence as current. If G5 was exposed, block any claim of fresh independent confirmation and require explicit incident review; never automatically regenerate the lock. Environment role differences must use explicit validated compatibility profiles from change 13, not arbitrary equality exceptions.

## Dependencies and evidence

Uses asset identity from 09 and conditional runtime identity from 13; sparse provenance may be implemented independently. Integrates with 11 release publication and 12 versioned diagnostic views.

Implement [tasks.md](tasks.md) and verify every [acceptance scenario](specs/cross-stage-provenance/spec.md). Retain commands, environment, failure logs and artifact identities. No test may inspect real locked labels or reserve a real G5 attempt merely to validate software behavior. Use temporary synthetic campaigns for destructive/failure-path checks.
