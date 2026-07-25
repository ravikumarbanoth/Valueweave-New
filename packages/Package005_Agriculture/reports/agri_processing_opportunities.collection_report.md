# Collection Report: agri_processing_opportunities.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/agri_processing_opportunities.csv`
**Layer**: 5 - Value Addition
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (MoFPI/PMFME; Spices Board; National Bee Board; NMPB)

## Purpose

Value-add processing enterprise types with input crop, finished product, licence requirements and linked scheme.

## Methodology

Seventeen opportunities spanning primary processing, secondary processing, infrastructure, packaging, by-product processing and input manufacturing. licenses_required and linked_scheme were prioritised because they are the fields that gate whether an enterprise can legally operate.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 17 |
| Columns | 18 |
| Primary key | `opportunity_id` |
| Primary key uniqueness | PASS (17/17 distinct) |
| Total cells | 306 |
| Bare `PENDING_VERIFICATION` cells | 34 (11.11%) |
| Blank cells | 0 |
| Confidence range | 62-70 (ceiling 85) |
| Confidence average | 66.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `opportunity_id`
- `opportunity_name`
- `opportunity_type`
- `input_crop`
- `finished_product`
- `investment_band`
- `capacity_indicative`
- `skill_requirement`
- `market_demand`
- `value_add_potential`
- `licenses_required`
- `linked_scheme`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `investment_band` | 17 of 17 |
| `capacity_indicative` | 17 of 17 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

investment_band and capacity_indicative are the bare sentinel. Package004_Industries already carries sourced investment and machinery detail for the overlapping food-processing opportunities; this dataset intentionally does not duplicate or approximate those figures.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/agri_processing_opportunities.csv`
- Metadata: `packages/Package005_Agriculture/metadata/agri_processing_opportunities.metadata.json`
- This report: `packages/Package005_Agriculture/reports/agri_processing_opportunities.collection_report.md`
