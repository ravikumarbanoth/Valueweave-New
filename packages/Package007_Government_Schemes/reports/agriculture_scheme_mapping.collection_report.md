# Collection Report: agriculture_scheme_mapping.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/agriculture_scheme_mapping.csv`
**Layer**: 7 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Ministry of Agriculture; Package005 reconciliation)

## Purpose

Agriculture schemes mapped to Package005 scheme and crop records, farmer category and farm activity.

## Methodology

Both Package005 sides were resolved against the released CSVs at generation time. Crop-specific rows were created only where the crop genuinely changes the scheme's relevance, for example chilli's high input cost driving KCC demand, or sugarcane's water intensity making it a PMKSY priority.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 14 |
| Columns | 15 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (14/14 distinct) |
| Total cells | 210 |
| Bare `PENDING_VERIFICATION` cells | 8 (3.81%) |
| Blank cells | 0 |
| Confidence range | 68-76 (ceiling 85) |
| Confidence average | 71.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `scheme_id`
- `scheme_short_name`
- `package005_scheme_id`
- `package005_scheme_name`
- `package005_crop_id`
- `package005_crop_name`
- `farmer_category`
- `farm_activity`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `package005_scheme_id` -> `Package005_Agriculture (cross-package)` (`agriculture_schemes.scheme_id`)
- `package005_crop_id` -> `Package005_Agriculture (cross-package)` (`crops.crop_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package005_crop_id` | 2 of 14 |
| `package005_crop_name` | 2 of 14 |
| `package005_scheme_id` | 2 of 14 |
| `package005_scheme_name` | 2 of 14 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

12 of 14 rows resolve on both sides. Crop-agnostic schemes (PM-KISAN, Soil Health Card) carry the crop sentinel deliberately, because support is per landholding not per crop. PM-KUSUM and PMFME are not in Package005 v1.0.0, so their scheme-side links are sentinelled.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/agriculture_scheme_mapping.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/agriculture_scheme_mapping.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/agriculture_scheme_mapping.collection_report.md`
