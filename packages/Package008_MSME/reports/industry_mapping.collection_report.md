# Collection Report: industry_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/industry_mapping.csv`
**Layer**: 6 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Package004 reconciliation)

## Purpose

How each MSME business relates to a Package004 business opportunity record.

## Methodology

All 19 rows resolve to a real Package004 opportunity id with zero sentinels. The relationship column is the honest part: it distinguishes Same opportunity (a genuine one-to-one match), Adjacent (closest counterpart but not identical), Broader Package004 record (this business sits inside a wider Package004 scope) and Channel counterpart (Package004 records the sales channel rather than the enterprise). Without that distinction the mapping would overstate how well the two packages align.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 19 |
| Columns | 13 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (19/19 distinct) |
| Total cells | 247 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 60-74 (ceiling 85) |
| Confidence average | 68.6 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `business_id`
- `business_name`
- `package004_dataset`
- `package004_opportunity_id`
- `package004_opportunity_name`
- `relationship`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package004_opportunity_id` -> `Package004_Industries (cross-package)` (`id`)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Coverage is 19 rows across 40 businesses. The remaining 21 have no Package004 counterpart, and no row was fabricated to close the gap. Package004's investment and machinery detail is the authoritative source for the opportunities that do match -- Package008 deliberately does not restate it.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/industry_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/industry_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/industry_mapping.collection_report.md`
