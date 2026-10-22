# Tasks: Run one-time locked holdout confirmation

**Gate:** G5 · **Plan packages:** P16 · **Status:** not started (documentation only).

## 1. Verify prerequisites

- [ ] 1.1 P16: assert a hash-stable G4 `decision.json`, fitted development-only artifact(s), class manifest, evidence of G1/G2/G4 completion and no previous lock consumption.
- [ ] 1.2 Read stored source and split hashes and check exact locked prompt IDs; refuse unexpected access or missing artifact.

## 2. Perform one locked inference

- [ ] 2.1 Under the single-use evaluator, generate predictions and persist the hashes before making labels available to scoring code.
- [ ] 2.2 Score one selected candidate and, if different, the predeclared S reference; compute BA, class recalls and paired prompt-group uncertainty.
- [ ] 2.3 Apply only the predeclared interpretation/contradiction table; disclose limited 30-group evidence and any negative direction.

## 3. Close the lock

- [ ] 3.1 Persist consumed-state ledger, access audit, decision/model/input/prediction hashes, execution timestamp and immutable confirmation report.
- [ ] 3.2 Add tests that repeat opening after result exposure fails, and that mechanical pre-exposure failures use an auditable incident path only.
- [ ] 3.3 Do not modify registered winner or use holdout for remedial tuning; authorize G6 only with G5 closed state.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`locked-confirmation` specification](specs/locked-confirmation/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
