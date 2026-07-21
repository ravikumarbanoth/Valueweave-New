# Codex Handoff — Package003_Healthcare v1.0.0-RC1

Integration guide for an AI coding agent picking up this package, mirroring Package001_Geography and
Package002_Education's `codex_handoff.md`.

## What this package is

4 CSV datasets (134 rows total) covering Medical Regulatory Bodies & Health Missions, Medical
Colleges, Government Hospitals, and Government Health Insurance Schemes, scoped to Telangana, Andhra
Pradesh, and national-level entities. This is a *narrow, real, cited* slice of a much larger
40-domain / all-India brief — see `acquisition_backlog.json` for everything not yet shipped. **This
is RC1 — not yet merged to main.**

## Before you write any integration code

1. Read `README.md`, `docs/METHODOLOGY.md`, and `docs/USAGE.md` in full.
2. Understand that **no row is `VST-VERIFIED`** — every row is `VST-NEEDS_REVIEW`. Do not build any
   downstream feature that presents this data to end users as fully confirmed medical/institutional
   fact without a visible confidence/review-status indicator.
3. Understand that `PENDING_VERIFICATION` is a distinct sentinel from empty/null — your code must
   handle it explicitly (e.g. render "Not yet verified" rather than a blank field).
4. This package's confidence scores (73-88) were capped by an environment constraint (WebFetch to
   gov/edu domains was blocked) — do not treat an 88 here as equivalent to a directly-verified fact.

## Data model

- 4 independent CSVs, each with a UUIDv4 `id` primary key, no enforced foreign keys between them or
  into other packages (see `schemas/schema_catalog.json`).
- `medical_colleges_telangana_andhra_pradesh.attached_teaching_hospital` and
  `government_hospitals_telangana_andhra_pradesh.medical_college_affiliation` are free-text
  cross-references to each other, collected independently — do not treat as a verified relational
  join; do a name-match with manual review if you need to link them.
- `state`/`district` fields are free-text (`Telangana`/`Andhra Pradesh`/district names), not foreign
  keys into Package001_Geography's `state.csv`/`district.csv`.

## Validation before load

Run the same checks documented in `reports/validation_report.md` and the top-level
`validation_report.md` (PK uniqueness within and across datasets, column-count consistency, schema
column order, verification_status default) — they passed at build time but should be re-verified
after any transform in your pipeline.

## What NOT to do

- Do not silently drop rows with `PENDING_VERIFICATION` fields — they represent real entities with
  incomplete data, not noise.
- Do not infer/backfill missing fields (bed capacity, contact numbers, MBBS seat counts, lat/long,
  ICU/dialysis/ambulance availability, etc.) — they were deliberately left out of scope for RC1
  rather than guessed; see `docs/METHODOLOGY.md` "Field-Depth Scope Reduction."
- Do not auto-promote `verification_status` to `VST-VERIFIED` anywhere in application code.
- Do not merge this package to `main` or otherwise treat it as canonical — it is RC1, explicitly
  awaiting review before promotion to Stable.

## Extending this package

If you are asked to add one of the 36 queued/blocked domains, start from `acquisition_backlog.json`
for the specific unblock requirement per domain (PHCs/CHCs/Urban Health Centres are `BLOCKED`
specifically — they need a bulk data source, not more research time), and follow the same collection
methodology in `docs/METHODOLOGY.md` (source-priority tiers, confidence calibration,
PENDING_VERIFICATION sentinel discipline) rather than inventing a new approach per domain.
