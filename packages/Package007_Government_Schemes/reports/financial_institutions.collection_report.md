# Collection Report: financial_institutions.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/financial_institutions.csv`
**Layer**: 5 - Institutions
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (RBI; institution websites; NABARD; SIDBI)

## Purpose

Banks and development financial institutions that deliver credit-linked schemes.

## Methodology

Twelve institutions across public sector banks, development financial institutions, regional rural banks, cooperative structures and small finance banks. scheme_roles names which schemes each institution actually delivers, which is the join-relevant field.

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
| Primary key | `institution_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 168 |
| Bare `PENDING_VERIFICATION` cells | 4 (2.38%) |
| Blank cells | 0 |
| Confidence range | 68-76 (ceiling 85) |
| Confidence average | 72.7 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `institution_id`
- `institution_name`
- `institution_type`
- `ownership`
- `government_level`
- `scheme_roles`
- `priority_sector_lending`
- `official_website`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `official_website` | 4 of 12 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

Institution-type entries (Regional Rural Banks, District Central Cooperative Banks, PACS, Small Finance Banks) describe categories, not named institutions; official_website is the sentinel for those. No branch-level or district-level lead-bank data is asserted.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/financial_institutions.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/financial_institutions.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/financial_institutions.collection_report.md`
