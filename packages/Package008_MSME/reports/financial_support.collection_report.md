# Collection Report: financial_support.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/financial_support.csv`
**Layer**: 5 - Finance
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (RBI; SIDBI; NABARD; NSIC; Department of Financial Services)

## Purpose

Finance sources with instrument, typical use, collateral requirement and the Package007 scheme each is linked to.

## Methodology

Twelve sources across institutional lenders, development financial institutions, credit enhancement, government credit programmes and equity investors. linked_package007_scheme_short_name is a navigational pointer to Package007, not a restatement: the scheme's benefit, eligibility and process stay in Package007. collateral_requirement was prioritised because it is the single question that determines whether a first-time entrepreneur can actually access a source.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 12 |
| Columns | 15 |
| Primary key | `finance_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 180 |
| Bare `PENDING_VERIFICATION` cells | 8 (4.44%) |
| Blank cells | 0 |
| Confidence range | 62-76 (ceiling 85) |
| Confidence average | 71.2 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `finance_id`
- `finance_source_name`
- `source_type`
- `institution_type`
- `instrument`
- `typical_use`
- `collateral_requirement`
- `linked_package007_scheme_short_name`
- `official_website`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
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
| `linked_package007_scheme_short_name` | 4 of 12 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

No interest rate, loan ceiling or subsidy percentage is asserted -- those live in Package007 for scheme-linked instruments and change by notification. Institution-type rows (Regional Rural Banks, State Finance Corporations, Small Finance Banks) describe categories, not named entities, and sentinel official_website. Equity sources are relevant to a narrow slice of MSMEs and the rows say so.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/financial_support.csv`
- Metadata: `packages/Package008_MSME/metadata/financial_support.metadata.json`
- This report: `packages/Package008_MSME/reports/financial_support.collection_report.md`
