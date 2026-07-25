# Collection Report: soil_types.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/soil_types.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (ICAR-NBSS&LUP; Soil Health Card programme)

## Purpose

Soil classification with pH band, texture, state distribution and crop suitability.

## Methodology

Ten soil classes were taken from the ICAR-NBSS&LUP national classification, retaining the four problem-soil classes (saline, acidic, alkaline, clay) because reclamation and crop-choice decisions depend on them.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 10 |
| Columns | 15 |
| Primary key | `soil_id` |
| Primary key uniqueness | PASS (10/10 distinct) |
| Total cells | 150 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 72-78 (ceiling 85) |
| Confidence average | 75.5 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `soil_id`
- `soil_name`
- `description`
- `pH_range_min`
- `pH_range_max`
- `soil_color`
- `texture`
- `major_states`
- `crop_suitability`
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

pH bands are typical ranges, not guarantees; field pH varies within a single parcel. Composite textures used in crops.soil_type_preferred (for example sandy loam) are deliberately not separate soil_id rows.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/soil_types.csv`
- Metadata: `packages/Package005_Agriculture/metadata/soil_types.metadata.json`
- This report: `packages/Package005_Agriculture/reports/soil_types.collection_report.md`
