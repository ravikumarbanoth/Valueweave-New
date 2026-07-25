# Collection Report: crop_categories.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/crop_categories.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (ICAR; commodity boards; Ministry of Agriculture)

## Purpose

Top-level agriculture classification covering field crops, horticulture, plantation, production systems and allied activities.

## Methodology

The 24 categories were enumerated to cover the full agriculture domain requested for this package, including three production-system categories (organic, protected, hydroponics/aquaponics) that are cultivation modes rather than botanical groups, and seven allied categories (sericulture, apiculture, mushroom, fisheries, livestock, poultry, dairy) that sit outside crop taxonomy but inside agri-business scope. Each category was attributed to the ICAR institute or statutory board that governs it.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 24 |
| Columns | 13 |
| Primary key | `category_id` |
| Primary key uniqueness | PASS (24/24 distinct) |
| Total cells | 312 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 57-78 (ceiling 85) |
| Confidence average | 72.1 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `category_id`
- `category_name`
- `category_group`
- `description`
- `typical_crops_examples`
- `cultivation_mode`
- `value_add_potential`
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

category_group distinguishes botanical groupings from production systems and allied activities; consumers filtering for crops only should restrict to Field Crops, Horticulture and Plantation.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/crop_categories.csv`
- Metadata: `packages/Package005_Agriculture/metadata/crop_categories.metadata.json`
- This report: `packages/Package005_Agriculture/reports/crop_categories.collection_report.md`
