# Public documentation wording update

Created: 24-10-2026-03-17-31 (Asia/Qyzylorda)

Removed platform branding from public-facing Markdown: project and specification READMEs, the implementation plan, OpenSpec proposals/designs/tasks/specifications, the runbook and prior public change log. Replaced branded prose with neutral deployment terminology, removed the platform-specific source URL and normalized output references to `submission.parquet`.

Renamed the release change and capability documentation directories to `07-refit-and-release-offline` and `offline-release` so public Markdown links and capability names remain valid without platform branding. Executable code, configuration, notebook content, internal agent instructions and existing non-Markdown evidence logs retain their behavior/content.

Simplicity review, cycle 1: contextual replacements and one documentation-directory rename avoid link aliases or duplicated documents. Reviewed surrounding wording for redundant or awkward phrases; corrected those phrases. No further actionable simplification was identified.

Performance review, cycle 1: changes affect documentation only and introduce no runtime work, dependencies or allocations. The edit processes each document once. No performance changes were needed.

Validation: case-insensitive search across public Markdown; local Markdown file-link resolution; all OpenSpec changes validated. No Python or Rust files changed, so language checks and runtime tests are not required for this documentation change.
