# Collection Report: climate_zones.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/climate_zones.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (ICAR-CRIDA; India Meteorological Department)

## Purpose

Agro-climatic zone reference with rainfall, temperature, humidity and growing-season counts.

## Methodology

Eight zones were derived from the ICAR-CRIDA agro-climatic framing, collapsed to a tractable set that still separates arid from semi-arid and wet from tropical, because those distinctions drive crop choice.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 8 |
| Columns | 16 |
| Primary key | `climate_zone_id` |
| Primary key uniqueness | PASS (8/8 distinct) |
| Total cells | 128 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 72-77 (ceiling 85) |
| Confidence average | 74.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `climate_zone_id`
- `zone_name`
- `description`
- `rainfall_mm_min`
- `rainfall_mm_max`
- `temperature_min_c`
- `temperature_max_c`
- `humidity_percent`
- `growing_seasons`
- `major_states`
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

This is a simplified eight-zone model, not the 127-zone NARP agro-ecological classification; use it for crop-suitability screening, not for site-specific recommendation.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/climate_zones.csv`
- Metadata: `packages/Package005_Agriculture/metadata/climate_zones.metadata.json`
- This report: `packages/Package005_Agriculture/reports/climate_zones.collection_report.md`
