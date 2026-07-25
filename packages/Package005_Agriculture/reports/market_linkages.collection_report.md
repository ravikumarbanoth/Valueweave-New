# Collection Report: market_linkages.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/market_linkages.csv`
**Layer**: 9 - Market Access
**Collection date**: 2026-07-24
**Source tier**: Tier 1-2 (Ministry of Agriculture; eNAM; APEDA; MoFPI)

## Purpose

Market channel types available to producers, from regulated mandis to digital platforms and export routes.

## Methodology

Six channel types characterised by the commodities they handle and their infrastructure basis, spanning APMC mandis, eNAM, FPO direct marketing, processor contracts, modern retail and export.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 6 |
| Columns | 12 |
| Primary key | `linkage_id` |
| Primary key uniqueness | PASS (6/6 distinct) |
| Total cells | 72 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 66-76 (ceiling 85) |
| Confidence average | 70.0 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `linkage_id`
- `market_type`
- `market_infrastructure`
- `description`
- `commodities_traded`
- `major_locations`
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

Describes channel types, not named mandis or buyers. Counts such as APMC and integrated-mandi numbers move over time and should be re-verified.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/market_linkages.csv`
- Metadata: `packages/Package005_Agriculture/metadata/market_linkages.metadata.json`
- This report: `packages/Package005_Agriculture/reports/market_linkages.collection_report.md`
