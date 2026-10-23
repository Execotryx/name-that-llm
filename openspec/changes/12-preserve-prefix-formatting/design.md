# Design: Preserve formatting in prefix-length diagnostics

## Context and scope

The prefix transform joins split words with spaces, changing newlines, tabs, indentation and repeated spaces. A 120-word text changes under prefix-120 despite retaining every word. Character TF-IDF can respond to these changes, confounding length and formatting effects.

Reviewed baseline: `a4499c73d8bdc6db89679cdffa36995a2128c0a6`. These controls now have implementation and local regression coverage; see tasks.md for remaining real execution evidence.

## Decisions and failure paths

### 1. Exact boundary semantics

For a positive registered limit n, find Unicode non-whitespace spans using the same word-count semantics as eligibility. If there are at most n spans, return the original string byte-for-byte in its Unicode representation, including trailing whitespace. Otherwise return text[:end_of_nth_span]. Preserve leading whitespace, punctuation, line breaks, tabs and repeated spaces within that slice; never rebuild the prefix with join(). Empty and whitespace-only strings remain unchanged.

### 2. Diagnostic interpretation

Use the same view in frozen-model perturbations and fixed-C refit sensitivity controls. Continue reporting these separately, with raw and perturbed predictions on identical eligible/common-120 subsets and complete class support. The intervention isolates removal of the suffix from incidental whitespace normalization; it does not separate length from the semantic information removed with that suffix.

### 3. Version and migration

Bump the view identity and include it in affected caches/manifests. Reject old prefix reports as evidence for the corrected intervention; preserve them as superseded records. Record the change before interpreting corrected scores. Do not expand candidate families, C grids, prefix choices or budgets. Existing exposed G5 cannot be rerun or used to select a new model because diagnostics changed.

## Dependencies and evidence

Existing 05; provenance integration with 10. Required before interpreting newly generated prefix diagnostics.

Implement [tasks.md](tasks.md) and verify every [acceptance scenario](specs/prefix-intervention-isolation/spec.md). Retain commands, environment, failure logs and artifact identities. No test may inspect real locked labels or reserve a real G5 attempt merely to validate software behavior. Use temporary synthetic campaigns for destructive/failure-path checks.
