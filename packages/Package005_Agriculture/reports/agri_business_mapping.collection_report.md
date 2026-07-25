# Collection Report: agri_business_mapping.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/agri_business_mapping.csv`
**Layer**: 12 - Cross-Package Spine
**Collection date**: 2026-07-24
**Source tier**: Tier 1-2 (MoFPI; Spices Board; internal cross-package reconciliation)

## Purpose

The integration spine: crop to processing opportunity to Package004 business opportunity to Package006 skill.

## Methodology

Thirty mappings trace a crop through a processing route to a named business opportunity and the skill required to run it. Package004 opportunity names were matched by reading the released Package004 CSVs directly, and Package006 skill_id values are the actual UUIDs from the released skills.csv, so both sides are verifiable foreign keys rather than descriptive text.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 30 |
| Columns | 15 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (30/30 distinct) |
| Total cells | 450 |
| Bare `PENDING_VERIFICATION` cells | 13 (2.89%) |
| Blank cells | 0 |
| Confidence range | 62-74 (ceiling 85) |
| Confidence average | 69.0 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `mapping_id`
- `crop_id`
- `crop_name`
- `processing_opportunity_id`
- `processing_opportunity_name`
- `package004_opportunity_name`
- `package006_skill_id`
- `package006_skill_name`
- `value_add_stage`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `crop_id` -> `crops.csv` (`crop_id`)
- `processing_opportunity_id` -> `agri_processing_opportunities.csv` (`opportunity_id`)
- `package004_opportunity_name` -> `Package004_Industries (cross-package)` (`name / adapted_indian_concept`)
- `package006_skill_id` -> `Package006_Skills_and_Training (cross-package)` (`skill_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package004_opportunity_name` | 13 of 30 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

Thirteen of thirty rows carry the bare sentinel for package004_opportunity_name: Package004 v1.0.0 has no counterpart for rice milling, dal milling, jaggery, cold storage, essential-oil distillation, animal feed, vermicompost or cashew shelling. Those links become populatable when Package004 expands, and are left unasserted rather than approximated. value_add_stage is a qualitative stage label; no value-add percentage is asserted anywhere in this release.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/agri_business_mapping.csv`
- Metadata: `packages/Package005_Agriculture/metadata/agri_business_mapping.metadata.json`
- This report: `packages/Package005_Agriculture/reports/agri_business_mapping.collection_report.md`
