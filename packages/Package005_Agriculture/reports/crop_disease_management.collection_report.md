# Collection Report: crop_disease_management.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/crop_disease_management.csv`
**Layer**: 8 - Crop Protection
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (ICAR crop-protection institutes; IPM guidance)

## Purpose

Major crop diseases and pests with symptoms, chemical and biological control, and AI-detection feasibility.

## Methodology

Ten high-incidence problems across cereals, vegetables, cotton, citrus and potato. affected_crops is free text rather than a crop_id foreign key because most of these pathogens have host ranges wider than the 45 crops in this release.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 10 |
| Columns | 14 |
| Primary key | `disease_id` |
| Primary key uniqueness | PASS (10/10 distinct) |
| Total cells | 140 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 65-76 (ceiling 85) |
| Confidence average | 72.4 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `disease_id`
- `disease_name`
- `affected_crops`
- `symptom_description`
- `disease_type`
- `chemical_treatment`
- `biological_treatment`
- `ai_detection_possible`
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

Chemical treatments are named actives, not dose recommendations, and are not a prescription; pesticide legality and dosage are governed by CIB&RC labels and change over time. Always confirm current label approval before use.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/crop_disease_management.csv`
- Metadata: `packages/Package005_Agriculture/metadata/crop_disease_management.metadata.json`
- This report: `packages/Package005_Agriculture/reports/crop_disease_management.collection_report.md`
