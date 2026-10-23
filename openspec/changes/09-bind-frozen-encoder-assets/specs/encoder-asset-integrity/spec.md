# encoder-asset-integrity — Spec Delta

## ADDED Requirements

### Requirement: Complete checkpoint inventory

An eligible encoder MUST bind every inference-relevant asset and loader-selected layout to one pinned revision and a canonical asset identity.

#### Scenario: Marker-only manifest
- **WHEN** a manifest lists only an unrelated marker while weights, tokenizer or config are omitted
- **THEN** construction or eligibility fails before a neural loader is invoked

#### Scenario: Changed loader inputs
- **WHEN** a required shard is missing, an indexed shard hash differs, a path escapes the root or an unlisted competing checkpoint could be selected
- **THEN** verification rejects the assets with the offending role or path identified

### Requirement: Verified restored loads

Every cold encoder load MUST verify its frozen manifest and file hashes before loading a tokenizer or model, including after joblib restoration.

#### Scenario: Mutation after serialization
- **WHEN** a listed checkpoint file changes after the encoder is serialized and the object is restored
- **THEN** load fails before from_pretrained and no predictions or passing evidence are produced

#### Scenario: Valid relocation
- **WHEN** an unchanged verified asset tree moves to a new bundle location
- **THEN** restored inference succeeds offline with the same identity and registered prediction tolerance

#### Scenario: Confirmation preflight
- **WHEN** asset drift is detected before G5 reservation
- **THEN** confirmation refuses the attempt before locked texts are predicted; existing consumed ledgers remain unchanged

### Requirement: Verified packaging

Release packaging MUST validate source and copied assets and retain their exact identity.

#### Scenario: Copy or source drift
- **WHEN** source assets changed since freeze or copied bytes differ
- **THEN** refit/replay fails and cannot publish a passing release

#### Scenario: Sparse-only use
- **WHEN** the selected architecture is S
- **THEN** the workflow neither loads neural assets nor imports torch or transformers
