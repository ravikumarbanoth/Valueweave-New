# Collection Report: msme_businesses.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/msme_businesses.csv`
**Layer**: 2 - Core Entity
**Collection date**: 2026-07-25
**Source tier**: Tier 1-3 (MSME-DI project profiles; sector ministries; industry associations)

## Purpose

Forty MSME business opportunities profiled on classification, difficulty, risk, technology, market and geography.

## Methodology

Businesses were selected to span all four category groups and to be realistically startable at MSME scale, weighted to Telangana and Andhra Pradesh relevance. udyam_classification uses the statutory Micro/Small/Medium categories from the MSMED Act rather than inventing bands. Every attribute column is an ordinal judgement with a closed domain, enforced by validation check V12, so the dataset is machine-filterable rather than free text.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 40 |
| Columns | 26 |
| Primary key | `business_id` |
| Primary key uniqueness | PASS (40/40 distinct) |
| Total cells | 1040 |
| Bare `PENDING_VERIFICATION` cells | 40 (3.85%) |
| Blank cells | 0 |
| Confidence range | 63-74 (ceiling 85) |
| Confidence average | 69.0 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `business_id`
- `business_name`
- `category_id`
- `category_name`
- `business_model_id`
- `business_model_name`
- `description`
- `udyam_classification`
- `investment_range`
- `working_capital_need`
- `employment_generation`
- `difficulty`
- `risk_level`
- `technology_level`
- `automation_level`
- `ai_readiness`
- `market_demand`
- `export_potential`
- `profitability_outlook`
- `district_suitability`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `category_id` -> `msme_categories.csv` (`category_id`)
- `business_model_id` -> `business_models.csv` (`business_model_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `investment_range` | 40 of 40 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

investment_range is the bare sentinel on all 40 rows. The MSMED Act thresholds that define Micro, Small and Medium are official, but a per-business rupee requirement is not: it depends on capacity, location, degree of automation and whether premises are owned or rented. udyam_classification carries the classification signal instead. employment_generation is an indicative band, not a projection. profitability_outlook is a directional judgement, never a margin figure.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/msme_businesses.csv`
- Metadata: `packages/Package008_MSME/metadata/msme_businesses.metadata.json`
- This report: `packages/Package008_MSME/reports/msme_businesses.collection_report.md`
