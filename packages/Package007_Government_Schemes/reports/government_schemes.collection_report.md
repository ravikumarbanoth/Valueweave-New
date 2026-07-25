# Collection Report: government_schemes.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/government_schemes.csv`
**Layer**: 2 - Core Entity
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (each scheme's own portal and administering ministry)

## Purpose

Canonical registry of 40 government schemes with ministry, objective, benefit summary, coverage, application mode and portal.

## Methodology

Schemes were selected for national reach and for relevance to the citizen journeys this package is built to answer: student, farmer, worker, entrepreneur, and vulnerable household. Every row is attributed to the scheme's own portal rather than to an aggregator. The also_in_package column records where a scheme is already released in a domain package, so the overlap with Package002, Package003, Package004, Package005 and Package006 is explicit and reconcilable rather than a hidden fork.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 40 |
| Columns | 25 |
| Primary key | `scheme_id` |
| Primary key uniqueness | PASS (40/40 distinct) |
| Total cells | 1000 |
| Bare `PENDING_VERIFICATION` cells | 53 (5.3%) |
| Blank cells | 0 |
| Confidence range | 70-78 (ceiling 85) |
| Confidence average | 74.3 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `scheme_id`
- `scheme_name`
- `short_name`
- `category_id`
- `category_name`
- `ministry`
- `department`
- `government_level`
- `launch_year`
- `objective`
- `benefit_summary`
- `financial_assistance`
- `subsidy_component`
- `loan_support`
- `coverage`
- `application_mode`
- `official_portal`
- `status`
- `also_in_package`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `category_id` -> `scheme_categories.csv` (`category_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `financial_assistance` | 35 of 40 |
| `also_in_package` | 18 of 40 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

financial_assistance is the bare sentinel on almost every row. Scheme amounts, premium rates, loan ceilings and subsidy percentages are revised by notification and budget cycle; stating a figure without a primary-source read would date badly and mislead. Amounts must be re-verified at the official_portal before use. launch_year is the year of launch, not of the current version: PMKVY has run through four versions and PMS-SC dates to 1944 in its earliest form.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/government_schemes.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/government_schemes.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/government_schemes.collection_report.md`
