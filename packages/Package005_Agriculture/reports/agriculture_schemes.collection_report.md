# Collection Report: agriculture_schemes.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/agriculture_schemes.csv`
**Layer**: 7 - Government Support
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (scheme portals; Ministry of Agriculture; NABARD)

## Purpose

Central government agriculture support schemes with objective, eligibility, benefit and application level.

## Methodology

Twelve schemes covering income support, insurance, organic conversion, mechanisation, horticulture, irrigation, infrastructure credit, working capital, soil testing, livestock and fisheries. Each row names its own scheme portal as source.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 12 |
| Columns | 13 |
| Primary key | `scheme_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 156 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 69-78 (ceiling 85) |
| Confidence average | 73.2 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `scheme_id`
- `scheme_name`
- `scheme_type`
- `objective`
- `beneficiary_eligibility`
- `benefit_amount_inr`
- `application_level`
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

Benefit amounts and eligibility rules change by budget cycle and differ by state top-up. Treat every figure as requiring re-verification against the scheme portal before it is relied on. This dataset is the agriculture slice; Package007_Government_Schemes will hold the comprehensive scheme registry.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/agriculture_schemes.csv`
- Metadata: `packages/Package005_Agriculture/metadata/agriculture_schemes.metadata.json`
- This report: `packages/Package005_Agriculture/reports/agriculture_schemes.collection_report.md`
