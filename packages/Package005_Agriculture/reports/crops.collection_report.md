# Collection Report: crops.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/crops.csv`
**Layer**: 2 - Core Entity
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (ICAR crop-specific institutes; commodity boards)

## Purpose

Agronomic and commercial profile for 45 crops spanning all 12 crop-bearing categories.

## Methodology

Crops were selected for national acreage significance plus Telangana/Andhra Pradesh relevance, since those two states are the geographic spine of the wider knowledge base. Agronomic fields (season, duration, water requirement, temperature range, indicative yield) follow ICAR package-of-practices conventions. major_districts was populated only where a district is publicly and specifically associated with the crop; for crops with no TG/AP footprint the field is the bare sentinel rather than an invented list.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 45 |
| Columns | 25 |
| Primary key | `crop_id` |
| Primary key uniqueness | PASS (45/45 distinct) |
| Total cells | 1125 |
| Bare `PENDING_VERIFICATION` cells | 25 (2.22%) |
| Blank cells | 0 |
| Confidence range | 66-78 (ceiling 85) |
| Confidence average | 74.4 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `crop_id`
- `crop_name`
- `scientific_name`
- `category_id`
- `category_name`
- `season`
- `duration_days`
- `water_requirement_mm`
- `soil_type_preferred`
- `rainfall_mm`
- `temperature_min_c`
- `temperature_max_c`
- `avg_yield_tons_per_ha`
- `major_states`
- `major_districts`
- `organic_possible`
- `export_potential`
- `processing_potential`
- `mechanization_level`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `category_id` -> `crop_categories.csv` (`category_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `major_districts` | 14 of 45 |
| `duration_days` | 9 of 45 |
| `avg_yield_tons_per_ha` | 2 of 45 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

avg_yield_tons_per_ha is an indicative national average, not a district figure, and is not comparable across crops with different harvested products (lint vs seed cotton, dry vs fresh rhizome, nuts per palm for coconut). duration_days is the bare sentinel for perennials where the concept does not apply.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/crops.csv`
- Metadata: `packages/Package005_Agriculture/metadata/crops.metadata.json`
- This report: `packages/Package005_Agriculture/reports/crops.collection_report.md`
