# Collection Report: machinery_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/machinery_mapping.csv`
**Layer**: 3 - Input Requirements
**Collection date**: 2026-07-25
**Source tier**: Tier 1-2 (MSME-DI project profiles; DC-MSME)

## Purpose

Machinery required per business, with role, investment category, automation level and whether it is essential.

## Methodology

Every business carries at least one machinery row, enforced by V11, including the asset-light ones where the requirement is IT infrastructure rather than plant. Where the machine already exists in Package005's farm_machinery dataset -- rice mill, dal mill, oil expeller, cold storage, solar dryer, packaging machine, cold chain, agricultural drone -- it is referenced by machinery_id rather than restated. That is the normalization rule applied at row level.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 64 |
| Columns | 16 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (64/64 distinct) |
| Total cells | 1024 |
| Bare `PENDING_VERIFICATION` cells | 108 (10.55%) |
| Blank cells | 0 |
| Confidence range | 61-72 (ceiling 85) |
| Confidence average | 66.8 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `business_id`
- `business_name`
- `machinery_name`
- `machinery_role`
- `package005_machinery_id`
- `package005_machinery_name`
- `investment_category`
- `automation_level`
- `is_essential`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package005_machinery_id` -> `Package005_Agriculture (cross-package)` (`farm_machinery.machinery_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package005_machinery_id` | 54 of 64 |
| `package005_machinery_name` | 54 of 64 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

No machinery cost is asserted: investment_category gives an ordinal band (Core Plant, Ancillary, Tooling, IT Infrastructure, Premises) instead. Machine names outside the Package005 scope carry the sentinel in package005_machinery_id, which means only that Package005 does not hold that machine, not that it is unimportant. Machinery lists are indicative of a typical configuration, not an exhaustive bill of plant.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/machinery_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/machinery_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/machinery_mapping.collection_report.md`
