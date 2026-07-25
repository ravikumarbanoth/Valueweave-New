# Collection Report: agriculture_business_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/agriculture_business_mapping.csv`
**Layer**: 6 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Package005 reconciliation)

## Purpose

Agro-based MSME businesses linked to Package005 crops and processing opportunities.

## Methodology

Two Package005 foreign keys per row. All 14 processing-side links resolve; 10 of 14 crop-side links resolve, with crop-agnostic businesses (cold storage, packaging, vermicompost) carrying the crop sentinel deliberately because they serve multiple crops.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 14 |
| Columns | 14 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (14/14 distinct) |
| Total cells | 196 |
| Bare `PENDING_VERIFICATION` cells | 8 (4.08%) |
| Blank cells | 0 |
| Confidence range | 58-74 (ceiling 85) |
| Confidence average | 70.0 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `business_id`
- `business_name`
- `package005_crop_id`
- `package005_crop_name`
- `package005_processing_opportunity_id`
- `package005_processing_opportunity_name`
- `value_add_stage`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package005_crop_id` -> `Package005_Agriculture (cross-package)` (`crops.crop_id`)
- `package005_processing_opportunity_id` -> `Package005_Agriculture (cross-package)` (`agri_processing_opportunities.opportunity_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package005_crop_id` | 4 of 14 |
| `package005_crop_name` | 4 of 14 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

One row (drone services against rice milling) is a deliberately weak link retained at confidence 58 to record the agriculture adjacency; the notes column says so explicitly rather than presenting it as a strong relationship. Crop agronomy and processing economics stay in Package005.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/agriculture_business_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/agriculture_business_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/agriculture_business_mapping.collection_report.md`
