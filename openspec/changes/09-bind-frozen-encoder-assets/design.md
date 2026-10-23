# Design: Bind frozen encoder loads to complete verified assets

## Context and scope

Asset hashes are verified only by FrozenEncoder.__init__(). Joblib restoration skips that constructor; load() then reads external files without verifying them. A nonempty inventory can also omit every inference asset. The frozen probe artifact can therefore survive while the representation used at confirmation changes.

Reviewed baseline: `a4499c73d8bdc6db89679cdffa36995a2128c0a6`. These controls now have implementation and local regression coverage; see tasks.md for remaining real execution evidence.

## Decisions and failure paths

### 1. Complete local inventory

Enumerate every inference-relevant file that the selected loader may read: configuration, tokenizer assets, weight files and shard indexes plus referenced shards. Reject unlisted alternative loadable weights or configs that could alter loader choice, missing required roles, path traversal and symlink escapes. Do not require one serialization format universally; validate the selected supported layout. Non-runtime documentation may be present without affecting the identity.

### 2. Load-time verification

Store a canonical asset-manifest digest with the encoder and verify both it and file bytes before any from_pretrained call. Restore through an explicit verified lifecycle; __init__ alone is insufficient. Keep verified assets immutable for an execution, with verification immediately before first materialization, and invalidate loaded state if the asset root is intentionally rebound. Hash checks are integrity controls for trusted artifacts, not a security sandbox for untrusted pickle.

### 3. Packaging and confirmation

Validate originals before copying and the destination after copying; rebind portable paths only through the same verifier. Include runtime manifests and assets in bundle hashes. G5 must preflight assets for all selected/reference models before reserving the attempt; any subsequent failure preserves its existing reserved/exposed ledger and incident rules. Never reset a lock or replace a checkpoint automatically.

### 4. Offline compatibility

Retain local_files_only=True and trust_remote_code=False. Do not fetch missing files. Synthetic loader spies prove rejection order; actual neural eligibility still requires the pinned checkpoint in a cold offline target run.

## Dependencies and evidence

Conditional on F/H use; the S-only path remains available. Coordinate identity fields with changes 10 and 13.

Implement [tasks.md](tasks.md) and verify every [acceptance scenario](specs/encoder-asset-integrity/spec.md). Retain commands, environment, failure logs and artifact identities. No test may inspect real locked labels or reserve a real G5 attempt merely to validate software behavior. Use temporary synthetic campaigns for destructive/failure-path checks.
