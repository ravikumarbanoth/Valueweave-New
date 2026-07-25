# Collection Report: district_business_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/district_business_mapping.csv`
**Layer**: 6 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Package001 district master; Package005 crop district attribution)

## Purpose

District-to-business suitability, each row grounded in a named district characteristic.

## Methodology

Suitability is asserted ONLY where a documented district characteristic drives it, and every row names that characteristic in suitability_basis -- Nizamabad's turmeric market yard, Guntur's chilli yard, Anantapur's groundnut area, Hyderabad's IT concentration. All 32 dist_id values resolve against Package001. No blanket district-by-business cross-product was generated.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 32 |
| Columns | 16 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (32/32 distinct) |
| Total cells | 512 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 62-74 (ceiling 85) |
| Confidence average | 67.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `package001_dist_id`
- `dist_ref`
- `district_name`
- `state`
- `business_id`
- `business_name`
- `suitability_basis`
- `resource_strength`
- `market_access_score`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package001_dist_id` -> `Package001_Geography (cross-package)` (`district.dist_id`)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

32 rows across 61 districts and 40 businesses is deliberately sparse: a full cross-product would be 2,440 rows of mostly unfounded assertion. Absence of a district-business pair is not evidence the business is unsuitable there, only that no specific documented basis was found. resource_strength and market_access_score are ordinal ratings, not indices.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/district_business_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/district_business_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/district_business_mapping.collection_report.md`
