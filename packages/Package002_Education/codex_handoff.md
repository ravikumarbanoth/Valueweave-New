# Codex Handoff — Package002_Education v1.0.0

Integration guide for an AI coding agent picking up this package, mirroring Package001_Geography's
`codex_handoff.md`.

## What this package is

4 CSV datasets (135 rows total) covering Educational Boards & Regulatory Bodies, Universities,
Entrance Exams, and Scholarships, scoped to Telangana, Andhra Pradesh, and national-level entities.
This is a *narrow, real, cited* slice of a much larger 40-domain / all-India brief — see
`acquisition_backlog.json` for everything not yet shipped.

## Before you write any integration code

1. Read `README.md`, `docs/METHODOLOGY.md`, and `docs/USAGE.md` in full.
2. Understand that **no row is `VST-VERIFIED`** — every row is `VST-NEEDS_REVIEW`. Do not build any
   downstream feature that presents this data to end users as fully confirmed fact without a
   visible confidence/review-status indicator.
3. Understand that `PENDING_VERIFICATION` is a distinct sentinel from empty/null — your code must
   handle it explicitly (e.g. render "Not yet verified" rather than a blank field).
4. This package's confidence scores (58-92) were capped by an environment constraint in the
   collection session (WebFetch to gov/edu domains was blocked) — do not treat a 90 here as
   equivalent to a 90 in a future package collected with full WebFetch access.

## Data model

- 4 independent CSVs, each with a UUIDv4 `id` primary key, no declared foreign keys between them or
  into Package001_Geography in this release (see `schemas/schema_catalog.json`).
- `jurisdiction` (or `state` in the universities dataset) is a free-text enum
  (`National`/`Telangana`/`Andhra Pradesh`), not a foreign key into Package001_Geography's
  `state.csv`/`district.csv`. If you need to join against Package001_Geography, do it by name-match
  with a manual review step — do not treat it as a verified relational join.

## Validation before load

Run the same checks documented in `reports/validation_report.md` (PK uniqueness, column-count
consistency, verification_status default) — they passed at build time but should be re-verified after
any transform in your pipeline.

## What NOT to do

- Do not silently drop rows with `PENDING_VERIFICATION` fields — they represent real entities with
  incomplete data, not noise.
- Do not infer/backfill missing fields (fee structure, lat/long, contact details, etc.) — they were
  deliberately left out of scope for v1.0.0 rather than guessed; see `docs/METHODOLOGY.md`
  "Field-Depth Scope Reduction."
- Do not auto-promote `verification_status` to `VST-VERIFIED` anywhere in application code — that
  requires human governance sign-off against a directly-fetched primary source.

## Extending this package

If you are asked to add one of the 36 queued/blocked domains, start from `acquisition_backlog.json`
for the specific unblock requirement per domain, and follow the same collection methodology in
`docs/METHODOLOGY.md` (source-priority order, confidence calibration, PENDING_VERIFICATION sentinel
discipline) rather than inventing a new approach per domain.
