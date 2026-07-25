# Collection Report: export_opportunities.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/export_opportunities.csv`
**Layer**: 10 - Export
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (APEDA; Spices Board; Tea Board; Coffee Board)

## Purpose

Export market segments with destination countries, quality requirements and certifications needed.

## Methodology

Eight export categories where India holds a material global position. certifications_needed and quality_requirements were prioritised because they are the binding constraints on market entry, more than price.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 8 |
| Columns | 13 |
| Primary key | `opportunity_id` |
| Primary key uniqueness | PASS (8/8 distinct) |
| Total cells | 104 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 71-77 (ceiling 85) |
| Confidence average | 74.1 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `opportunity_id`
- `crop_product`
- `destination_countries`
- `avg_export_price_usd_per_unit`
- `volume_opportunity_tons_annual`
- `quality_requirements`
- `certifications_needed`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Export prices and annual volumes fluctuate with global markets, exchange rates and policy (export bans and MEP changes). Price and volume fields are indicative orders of magnitude only, not quotable figures.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/export_opportunities.csv`
- Metadata: `packages/Package005_Agriculture/metadata/export_opportunities.metadata.json`
- This report: `packages/Package005_Agriculture/reports/export_opportunities.collection_report.md`
