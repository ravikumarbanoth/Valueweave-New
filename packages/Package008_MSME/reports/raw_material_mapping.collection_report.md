# Collection Report: raw_material_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/raw_material_mapping.csv`
**Layer**: 3 - Input Requirements
**Collection date**: 2026-07-25
**Source tier**: Tier 1-2 (MSME-DI project profiles; commodity boards)

## Purpose

Raw materials per business with supplier type, availability, seasonality and price volatility.

## Methodology

Where an input is an agricultural crop, it is referenced by Package005 crop_id rather than restated, so the crop's season, yield and district footprint remain reachable by join without being copied. seasonality and price_volatility were prioritised because they are what determine working capital need, which is the field entrepreneurs most often underestimate.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 33 |
| Columns | 17 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (33/33 distinct) |
| Total cells | 561 |
| Bare `PENDING_VERIFICATION` cells | 42 (7.49%) |
| Blank cells | 0 |
| Confidence range | 60-72 (ceiling 85) |
| Confidence average | 66.5 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `business_id`
- `business_name`
- `raw_material_name`
- `material_class`
- `package005_crop_id`
- `package005_crop_name`
- `supplier_type`
- `availability`
- `seasonality`
- `price_volatility`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package005_crop_id` -> `Package005_Agriculture (cross-package)` (`crops.crop_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package005_crop_id` | 21 of 33 |
| `package005_crop_name` | 21 of 33 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

No price is asserted anywhere; price_volatility is an ordinal rating. availability is a national-level judgement and can differ sharply by district. Non-crop inputs carry the crop sentinel, which records that the input is not agricultural rather than that data is missing.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/raw_material_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/raw_material_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/raw_material_mapping.collection_report.md`
