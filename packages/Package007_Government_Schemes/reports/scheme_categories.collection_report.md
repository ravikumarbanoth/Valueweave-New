# Collection Report: scheme_categories.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/scheme_categories.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (administering ministries; India.gov.in; MyScheme)

## Purpose

Scheme classification across sector, beneficiary-group and instrument axes.

## Methodology

The 24 categories named in the package specification were enumerated and each attributed to the ministry that owns it. The category_group column separates the three genuinely different axes present in the list: Sector (what domain), Beneficiary Group (who qualifies) and Instrument (what financial mechanism). Without that separation the taxonomy would appear to be a single flat classification when it is not.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 24 |
| Columns | 12 |
| Primary key | `category_id` |
| Primary key uniqueness | PASS (24/24 distinct) |
| Total cells | 288 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 72-78 (ceiling 85) |
| Confidence average | 75.3 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `category_id`
- `category_name`
- `category_group`
- `description`
- `primary_beneficiary`
- `typical_benefit_type`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Categories are not mutually exclusive: a women's MSME scheme is legitimately both cat-005 and cat-006. government_schemes.csv assigns each scheme its single dominant category, so counting schemes per category understates cross-cutting reach.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/scheme_categories.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/scheme_categories.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/scheme_categories.collection_report.md`
