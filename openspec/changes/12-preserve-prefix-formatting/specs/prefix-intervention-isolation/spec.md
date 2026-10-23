# prefix-intervention-isolation — Spec Delta

## ADDED Requirements

### Requirement: Formatting-preserving prefixes

A registered prefix transform MUST return an original-string prefix at the nth Unicode non-whitespace span boundary and MUST leave inputs with at most n words unchanged.

#### Scenario: Exact length
- **WHEN** a 120-word input contains newlines, tabs, leading or trailing whitespace
- **THEN** prefix-120 returns the identical original string

#### Scenario: Actual truncation
- **WHEN** an input has more than n words
- **THEN** the result is exactly the original slice ending at the nth token, with no internal normalization

#### Scenario: Short or unusual text
- **WHEN** input is empty, whitespace-only, shorter than n or contains Unicode/code/math text
- **THEN** the transform follows the same span rule without deleting rows or rewriting preserved characters

### Requirement: Comparable diagnostic evidence

Prefix reports MUST identify the view version, refit versus perturbation mode and exact evaluation subset, and MUST use matched raw comparisons.

#### Scenario: Paired comparison
- **WHEN** eligible or common-120 prefix scores are generated
- **THEN** raw and transformed scores use the same row IDs and class support

#### Scenario: Stale report
- **WHEN** an existing prefix artifact was produced by the whitespace-normalizing view
- **THEN** it is rejected as current evidence and retained with a superseded identity

#### Scenario: Incomplete support
- **WHEN** a diagnostic subset lacks any canonical class
- **THEN** support is reported and an 18-class balanced-accuracy claim is withheld
