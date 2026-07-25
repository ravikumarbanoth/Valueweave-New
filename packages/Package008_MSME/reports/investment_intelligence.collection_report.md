# Collection Report: investment_intelligence.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/investment_intelligence.csv`
**Layer**: 11 - Investment Intelligence
**Collection date**: 2026-07-25
**Source tier**: Tier 1-3 (derived from msme_businesses.csv; MSME-DI project profile framing)

## Purpose

One investment profile per business: capex and working capital intensity, ROI and payback category, scalability, risk and outlook.

## Methodology

Exactly one row per business, enforced by V11. capex_intensity is derived deterministically from the business model rather than assigned per business, so it cannot drift from business_models.csv. working_capital_intensity, composite_risk and technology_adoption_requirement are carried from the business record. key_success_factor names the single variable that most determines outcome, which is the field with the most practical value.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 40 |
| Columns | 20 |
| Primary key | `intelligence_id` |
| Primary key uniqueness | PASS (40/40 distinct) |
| Total cells | 800 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 61-72 (ceiling 85) |
| Confidence average | 67.0 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `intelligence_id`
- `business_id`
- `business_name`
- `investment_band`
- `capex_intensity`
- `working_capital_intensity`
- `roi_category`
- `payback_category`
- `scalability`
- `technology_adoption_requirement`
- `composite_risk`
- `growth_potential`
- `future_outlook`
- `key_success_factor`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Every field is ordinal. roi_category, payback_category and scalability are judgements, not computed returns -- there is no rupee figure, no percentage and no payback period anywhere in this dataset, because computing any of them would require the investment and revenue figures this package deliberately does not assert. future_outlook is a directional 2026 view and is the field most likely to age. Use this dataset to compare businesses against each other, never to underwrite a decision.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/investment_intelligence.csv`
- Metadata: `packages/Package008_MSME/metadata/investment_intelligence.metadata.json`
- This report: `packages/Package008_MSME/reports/investment_intelligence.collection_report.md`
