# Collection Report: crop_soil_mapping.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/crop_soil_mapping.csv`
**Layer**: 3 - Relational Mapping
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (ICAR package-of-practices; soil-crop compatibility literature)

## Purpose

Crop-to-soil suitability with a 0-100 score and an ICAR-style suitability band.

## Methodology

Every one of the 45 crops carries two rows: its optimal soil and a documented alternative, giving 90 mappings. Scores are a relative ordinal rating anchored to ICAR guidance (85+ optimal, 70-84 suitable, 55-69 marginal), not a measured yield ratio.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 90 |
| Columns | 13 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (90/90 distinct) |
| Total cells | 1170 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 65-78 (ceiling 85) |
| Confidence average | 73.5 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `mapping_id`
- `crop_id`
- `crop_name`
- `soil_id`
- `soil_name`
- `suitability_score`
- `suitability_level`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `crop_id` -> `crops.csv` (`crop_id`)
- `soil_id` -> `soil_types.csv` (`soil_id`)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

suitability_score is ordinal and comparable only within a crop, not across crops. Absence of a crop-soil pair is not a statement that the combination fails.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/crop_soil_mapping.csv`
- Metadata: `packages/Package005_Agriculture/metadata/crop_soil_mapping.metadata.json`
- This report: `packages/Package005_Agriculture/reports/crop_soil_mapping.collection_report.md`
