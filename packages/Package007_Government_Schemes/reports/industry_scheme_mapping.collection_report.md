# Collection Report: industry_scheme_mapping.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/industry_scheme_mapping.csv`
**Layer**: 7 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Ministry of MSME; Package004 reconciliation)

## Purpose

Enterprise schemes mapped to Package004 business opportunities, industry sector, investment stage and enterprise size.

## Methodology

Opportunity names were matched against the released Package004 CSVs at generation time. investment_stage was included because scheme fit is stage-dependent: PMEGP suits greenfield, CGTMSE suits collateral-constrained growth, and SISFS suits pre-revenue ideation.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 12 |
| Columns | 14 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 168 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 68-73 (ceiling 85) |
| Confidence average | 71.1 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `scheme_id`
- `scheme_short_name`
- `package004_dataset`
- `package004_opportunity_name`
- `industry_sector`
- `investment_stage`
- `enterprise_size`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `package004_opportunity_name` -> `Package004_Industries (cross-package)` (`name / scheme_name / adapted_indian_concept`)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

All 12 rows resolve, with zero sentinels. Coverage is limited to the 12 clearest scheme-to-opportunity fits rather than an exhaustive cross-product, which would assert relevance that has not been checked.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/industry_scheme_mapping.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/industry_scheme_mapping.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/industry_scheme_mapping.collection_report.md`
