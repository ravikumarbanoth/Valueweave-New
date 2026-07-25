# Collection Report: scheme_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/scheme_mapping.csv`
**Layer**: 6 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Package007 reconciliation)

## Purpose

Which government schemes support which MSME business, at which stage, and in what form.

## Methodology

Every business carries at least one scheme mapping, enforced by V11, and all 57 rows resolve to a real Package007 scheme_id with zero sentinels. The dataset stores only the relationship and its attributes -- relevance, applicable_stage, support_nature. Scheme benefit, eligibility and application process are reached by joining on package007_scheme_id. This is the clearest instance of the normalization rule in the package.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 57 |
| Columns | 14 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (57/57 distinct) |
| Total cells | 798 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 61-73 (ceiling 85) |
| Confidence average | 67.8 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `business_id`
- `business_name`
- `package007_scheme_id`
- `package007_scheme_short_name`
- `relevance`
- `applicable_stage`
- `support_nature`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package007_scheme_id` -> `Package007_Government_Schemes (cross-package)` (`government_schemes.scheme_id`)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

relevance (Primary or Secondary) is a judgement about fit, not an eligibility determination: a business appearing against a scheme does not mean any given operator qualifies. Package007's own caveat applies transitively -- no scheme amount is asserted anywhere in either package.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/scheme_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/scheme_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/scheme_mapping.collection_report.md`
