# Collection Report: export_opportunities.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/export_opportunities.csv`
**Layer**: 8 - Export
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (DGFT; APEDA; Spices Board; Export Promotion Councils)

## Purpose

Export-capable businesses with destination markets, required certifications, standards and the binding readiness barrier.

## Methodology

Twelve businesses with realistic export potential. export_readiness_barrier is the most useful field and is stated per row: for garments it is social compliance audit readiness rather than product quality; for spices it is residue testing capability; for software it is data-protection compliance rather than any physical certification. Naming the actual blocker is more actionable than listing certifications alone.

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
| Primary key | `opportunity_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 180 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 60-72 (ceiling 85) |
| Confidence average | 66.2 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `opportunity_id`
- `business_id`
- `business_name`
- `export_product`
- `destination_markets`
- `required_certifications`
- `applicable_standards`
- `export_readiness_barrier`
- `promotion_body`
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

No export price, volume or realisation is asserted. Destination markets are the established ones for each category, not an exhaustive list. Certification requirements change with importing-country regulation -- the EU AI Act row is explicitly flagged as an emerging obligation. Only 12 of 40 businesses appear; the rest are domestic-market propositions and were not padded into this dataset.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/export_opportunities.csv`
- Metadata: `packages/Package008_MSME/metadata/export_opportunities.metadata.json`
- This report: `packages/Package008_MSME/reports/export_opportunities.collection_report.md`
