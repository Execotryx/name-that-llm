# Tasks: Optionally enable frozen DeBERTa and bounded hybrid selector

**Gate:** G1b + G3 (conditional) · **Plan packages:** P04–P06 neural path, P08–P10 · **Status:** code implemented; local synthetic verification available; real campaign acceptance pending.

## 1. Pass or explicitly fail G1b

- [ ] 1.1 Stage one revision-pinned DeBERTa-small checkpoint and pinned runtime wheels; verify hashes, licensing, local-files-only load and missing-asset negative behavior with internet disabled.
- [ ] 1.2 Implement 512-token deterministic mask-aware mean pooling/L2 normalization and verify identical embeddings after cache reload and input permutation.
- [ ] 1.3 Profile small batches (starting at 1 on local 4 GB hardware) and 4,000/8,000 synthetic loads, recording truncation, peak VRAM/RAM, throughput and time reserve.
- [ ] 1.4 Write a machine-readable `neural_eligibility.json`: passing headroom allows F/H; failure means S-only without quality claims about neural models.

## 2. Implement frozen probe

- [ ] 2.1 Implement development-only embedding cache keyed by text hash, checkpoint/tokenizer revision, dtype, pooling and text view; explicitly assert row identity.
- [ ] 2.2 Fit four registered logistic-probe C settings on grouped inner training portions only, align 18-class probabilities and generate matched outer OOF for F.
- [ ] 2.3 Include cache corruption/missing file, GPU-vs-CPU tolerance, batch invariance and no-locked-rows tests.

## 3. Run bounded S/F/H selector

- [ ] 3.1 Build inner-OOF candidate comparison for S/F/H with the original 11 fixed blend weights, 0.03 improvement requirement and 0.005 cost/tie rule.
- [ ] 3.2 Persist per-candidate versus complete-selector outer OOF separately, including architecture chosen on each outer fold and all cost/fit-count logs.
- [ ] 3.3 Verify no outer labels influence candidate/weight selection; do not add calibration, fine-tuning or other candidates.
- [ ] 3.4 If F/H blocked, generate an explicit G3 S-only completion record for downstream G4 rather than fabricated neural OOF.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`frozen-challenger` specification](specs/frozen-challenger/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
