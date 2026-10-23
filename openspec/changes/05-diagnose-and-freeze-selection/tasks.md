# Tasks: Measure robustness, quantify uncertainty and freeze the development decision

**Gate:** G4 · **Plan packages:** P11–P15 · **Status:** code implemented; local synthetic verification available; real campaign acceptance pending.

## 1. Build rigorous metric and uncertainty layer

- [ ] 1.1 P11: implement pooled 18-class BA, per-class recall/support, confusion/provider diagnostics and artificial incomplete-block metric tests.
- [ ] 1.2 P12: implement 10,000 prompt bootstrap replicates, 100,000 group-swap Monte Carlo paired test, fixed BA contribution weighting and Holm adjustment for eligible planned F/H hypotheses.
- [ ] 1.3 Record intervals as conditional development diagnostics, acknowledging selection and overlapping training folds.

## 2. Run diagnostic matrix

- [ ] 2.1 P13: execute nine fixed controls on development-only OOF with transformed text and explicit subset/class support; handle blank prefixes, Unicode, math/markup/code without dropping rows.
- [ ] 2.2 P14: if a permitted frozen representation exists, form six development-only topic-proxy clusters and leave-cluster-out stress without tuning on withheld cluster; otherwise log blocked representation check.
- [ ] 2.3 Record scores, input views, refit-vs-perturbation status, exclusion populations, hashes and all caveats; apply only preregistered vetoes.

## 3. Freeze G4 decision

- [ ] 3.1 P15: run full-development four-fold candidate selection under the exact frozen S/F/H policy or S-only documented eligibility.
- [ ] 3.2 Check +0.03 per-candidate development uplift and predeclared class/topic/provider vetoes for a complex candidate; select S if unqualified.
- [ ] 3.3 Fit chosen configuration and at most one registered S comparator on development only; serialize exact artifact identities and `decision.json`.
- [ ] 3.4 Assert G5 cannot access holdout unless a fully hashed decision and G4 acceptance report already exist.

## 4. Gate acceptance and handoff

- [ ] 4.1 Execute all scenarios in [`robustness-and-decision` specification](specs/robustness-and-decision/spec.md) and persist logs, failed attempts, input hashes, resource profiles and test outputs.
- [ ] 4.2 Verify the plan's relevant gate exit criteria and stop conditions against actual artifacts; do not mark passing gates on documentation alone.
- [ ] 4.3 Commit a gate acceptance/blocker record with changed source paths, reproduction commands, tested environment versions, and links to evidence; hand off only eligible subsequent changes.
