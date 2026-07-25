# Collection Report: farm_machinery.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/farm_machinery.csv`
**Layer**: 4 - Capital and Technology
**Collection date**: 2026-07-24
**Source tier**: Tier 1 (SMAM; MoFPI; PMKSY scheme documents)

## Purpose

Farm machinery and post-harvest equipment with power class, automation level, AI readiness and the subsidy scheme that applies.

## Methodology

Sixteen machinery types spanning land preparation, sowing, crop protection, harvesting, post-harvest, processing, packaging, cold chain, irrigation and monitoring. Scheme attribution is the field of highest practical value and is sourced to the named scheme.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 16 |
| Columns | 18 |
| Primary key | `machinery_id` |
| Primary key uniqueness | PASS (16/16 distinct) |
| Total cells | 288 |
| Bare `PENDING_VERIFICATION` cells | 50 (17.36%) |
| Blank cells | 0 |
| Confidence range | 62-72 (ceiling 85) |
| Confidence average | 67.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `machinery_id`
- `machinery_name`
- `machinery_type`
- `function`
- `investment_inr`
- `fuel_type`
- `capacity`
- `power_hp`
- `annual_maintenance_inr`
- `automation_level`
- `ai_readiness`
- `subsidy_scheme`
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
| `investment_inr` | 16 of 16 |
| `annual_maintenance_inr` | 16 of 16 |
| `power_hp` | 10 of 16 |
| `capacity` | 7 of 16 |
| `subsidy_scheme` | 1 of 16 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

investment_inr, annual_maintenance_inr and most capacity figures are the bare sentinel throughout. Equipment prices are set by manufacturer and model and no single official public figure exists; a plausible number here would be fabrication. Consumers needing costs must obtain current DIC or dealer quotations.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/farm_machinery.csv`
- Metadata: `packages/Package005_Agriculture/metadata/farm_machinery.metadata.json`
- This report: `packages/Package005_Agriculture/reports/farm_machinery.collection_report.md`
