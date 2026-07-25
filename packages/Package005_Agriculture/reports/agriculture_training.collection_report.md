# Collection Report: agriculture_training.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/agriculture_training.csv`
**Layer**: 6 - Institutions
**Collection date**: 2026-07-24
**Source tier**: Tier 1-2 (ICAR KVK network; state agriculture departments; NPTEL)

## Purpose

Agricultural training and extension provider categories with coverage and course focus.

## Methodology

Seven provider categories from district KVKs through state agricultural universities to digital platforms, characterised by reach and typical programme duration.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 7 |
| Columns | 13 |
| Primary key | `training_id` |
| Primary key uniqueness | PASS (7/7 distinct) |
| Total cells | 91 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 64-77 (ceiling 85) |
| Confidence average | 71.1 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `training_id`
- `training_provider`
- `provider_type`
- `services`
- `typical_duration`
- `course_focus`
- `state_coverage`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Describes provider categories, not named institutions. Package006_Skills_and_Training carries the named-provider and named-centre datasets; this is the agriculture-specific extension layer, not a duplicate of it.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/agriculture_training.csv`
- Metadata: `packages/Package005_Agriculture/metadata/agriculture_training.metadata.json`
- This report: `packages/Package005_Agriculture/reports/agriculture_training.collection_report.md`
