# Design: Validate active runtime dependencies

## Context

The current regex extracts only a distribution name. Missing requirements with any marker are ignored, constraints are not checked, and extra predicates are filtered by text. As a result an inventory/lock can omit a required package or endorse an installed incompatible version. Conversely, an installed package behind a false marker is traversed, making identity depend on unrelated ambient packages.

## 1. Parse requirements and define the context

Use `packaging.requirements.Requirement`, its marker evaluator and version/specifier support rather than a handwritten parser. Declare `packaging` as a direct core runtime dependency and lock its compatible version; it is needed for sparse profiling too. Include the parser's installed identity in the inventory.

Evaluate markers against the executing runtime's standard marker environment, never a guessed deployment environment. Record the marker values used by active/skipped edge decisions and the explicitly requested root extras. A simulated environment is a test fixture, not target evidence. Roots remain role-scoped: core for S; core plus required neural/tokenizer roots for F/H.

For each distribution, evaluate base dependencies with the empty extra and dependencies for each explicitly activated extra. Parse compound expressions, `extra != ...`, parentheses and whitespace through the marker parser. Inactive requirements are not required, version-checked or traversed merely because they happen to be installed. They become relevant only if another active edge or root requires them.

## 2. Resolve the installed closure without installation

Traverse installed distribution metadata using canonicalized names. Each active edge must find its installed dependency and satisfy that edge's specifier using the standards-aware version parser. Check every incoming constraint even when the distribution has already been visited; diamond graphs must not hide conflicting parents.

Propagate extras requested by requirements such as `child[feature]>=1`. Track visited distribution/extra contexts, merge newly requested extras and revisit that distribution's dependency edges until the closure stabilizes. Cycles must terminate deterministically without dropping later constraints or newly activated extras. Do not enable unrequested extras globally.

Reject malformed requirements, invalid installed versions, unsupported marker contexts and active direct-URL requirements with actionable errors rather than dropping them or downloading anything. The current workflow is a pinned local wheel inventory; direct-URL requirements have no supported provenance policy and therefore fail explicitly. Unknown requested extras should also fail clearly rather than falsely claiming their closure was verified.

Errors name the parent, full requirement, evaluated marker context and missing or installed incompatible version as applicable. Preparation may leave the existing non-eligible staging record, but must not emit an accepted lock or gate for an invalid environment. This validates an installed environment; it does not solve dependencies or select alternative package versions.

## 3. Deterministic versioned evidence

Introduce runtime-profile and runtime-lock schema versions that distinguish validated closure semantics from the legacy inventory. Record canonical package versions/build hashes, root requirements and extras, relevant marker context and deterministically ordered active dependency edges/constraints. A stable skipped-edge summary may be included for audit, but must not incorporate installed metadata of irrelevant packages.

Identical installed required distributions and marker context produce the same profile regardless of traversal/metadata order. Different active closures, required versions/builds or relevant marker values are reflected in compatibility checks and cache identity. Adding/removing an irrelevant package behind a false marker does not change the applicable profile. Retain exact staged-wheel coverage/hash checks; this correction does not replace the existing asset inventory.

Reject old profiles/locks explicitly instead of treating the newly discovered closure as the old one. Preserve historical artifacts and document necessary revalidation under the original experiment policy. Changing the code/lock invalidates affected execution evidence; no silent cache relabeling, evidence rehash or G5 reset is permitted.

## 4. Preflight ordering and consumers

Keep metadata discovery free of optional imports. Check the entire applicable dependency closure, including core requirements, before `FrozenEncoder.runtime()` imports torch and before any tokenizer/model loader executes. Numerical settings may be measured afterward, under the existing verified-asset policy. The sparse path never probes optional neural distributions simply because they are installed or previously participated in selection.

Use the same validated closure logic in runtime capture, asset-lock preparation, metadata-only historical-result consumption where applicable, current-lock verification and live neural execution. Lock creation must not accept a caller-supplied unchecked legacy profile. A missing or incompatible dependency must fail before embeddings, fitting, cache creation, passing gate publication or G5 reservation. Replay may retain its existing reserved attempt/incident record but must not publish final output.

Coordinate with change 14: historical neural selection evidence remains immutable, while live S artifact verification evaluates only S requirements. F/H execution still validates the full applicable neural closure. No network requests, installers or fallback downloads occur on any error path.

## 5. Validation strategy

Use synthetic local distribution metadata fixtures rather than changing installed packages. Include active/inactive Python, OS and implementation markers; compound predicates; installed-but-inactive packages; satisfying/unsatisfying versions; transitive requirements; extra activation through multiple parents; cycles; and conflicting diamond constraints. Assert deterministic ordering and actionable errors. Test supported prerelease/local-version cases through the chosen standards parser, not lexical string comparisons.

Add integration tests that fail actual profile/lock preparation and encoder preflight before optional import or loading. Verify no sparse optional-package discovery, no network, no passing evidence, no new G5 ledger and no final submission on invalid required environments. Existing negative/positive core runtime, asset relocation and cache tests must continue to pass. Run Pyright and the complete suite. Real checkpoint/hardware and cold target checks remain external acceptance, not mocked success.
