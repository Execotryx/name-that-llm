# Design: Record and enforce the conditional neural runtime

## Context and scope

environment() records only core packages. Torch, Transformers and tokenizer dependencies are omitted, so release environment checks cannot detect changes to the neural stack even when F/H is selected.

Reviewed baseline: `a4499c73d8bdc6db89679cdffa36995a2128c0a6`. These controls now have implementation and local regression coverage; see tasks.md for remaining real execution evidence.

## Decisions and failure paths

### 1. Conditional package inventory

Capture package metadata without importing optional packages for sparse-only execution. The neural lock must cover torch, transformers, tokenizers, huggingface-hub, safetensors, sentencepiece/protobuf when required by the pinned tokenizer, and their resolved inference-relevant dependencies. Record exact versions, wheel/build identities and staged install artifact hashes; distinguish required, optional-present and not-required entries rather than treating missing required packages as an empty value.

### 2. Execution settings

Record Python/core dependency identities, CPU/GPU execution role, torch build/CUDA/cuDNN versions when applicable, device capability, driver details, dtype, encoder batch size, pooling/tokenization policy, TF32/determinism settings and relevant numerical/thread environment controls. Separate compatibility-enforced fields from diagnostic hardware descriptors. Device descriptors need not be identical across all supported machines, but any permitted difference must belong to an explicitly validated profile.

### 3. Enforcement and portability

Compare required package/build and numerical-setting identity before neural inference, extraction or fitting. Bind it into cache keys, G1b and downstream identities. Do not silently accept an upgrade, device switch or precision change; require a separately recorded compatibility/feasibility profile and dependent evidence invalidation where results may change. Cross-platform wheel differences must be explicit tested profiles, not ad hoc equality bypasses.

### 4. Offline and sparse operation

Resolve/install dependencies during preparation; stage the exact permitted wheels and lock. No gate, notebook or runtime recovery may download dependencies. Keep S usable when neural packages are absent; importing core modules and recording a sparse profile must not import torch/transformers. Real neural compatibility still requires offline target execution.

## Dependencies and evidence

Existing 02, 04 and 07; coordinates with asset identity 09 and evidence lineage 10. Neural obligations are conditional on F/H.

Implement [tasks.md](tasks.md) and verify every [acceptance scenario](specs/conditional-runtime-identity/spec.md). Retain commands, environment, failure logs and artifact identities. No test may inspect real locked labels or reserve a real G5 attempt merely to validate software behavior. Use temporary synthetic campaigns for destructive/failure-path checks.
