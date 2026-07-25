# Collection Report: skill_scheme_mapping.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/skill_scheme_mapping.csv`
**Layer**: 7 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (MSDE; Package006 reconciliation)

## Purpose

Skill schemes mapped to Package006 scheme, skill, certification and training provider records.

## Methodology

Four separate Package006 foreign keys per row, all resolved against the released CSVs at generation time. This is the widest cross-package surface in the package and the strictest: the generator aborts rather than writing an unresolvable id.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 12 |
| Columns | 17 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 204 |
| Bare `PENDING_VERIFICATION` cells | 42 (20.59%) |
| Blank cells | 0 |
| Confidence range | 62-73 (ceiling 85) |
| Confidence average | 69.7 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `scheme_id`
- `scheme_short_name`
- `package006_scheme_id`
- `package006_scheme_name`
- `package006_skill_id`
- `package006_skill_name`
- `package006_certification_id`
- `package006_certification_name`
- `package006_provider_id`
- `package006_provider_name`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `package006_scheme_id` -> `Package006_Skills_and_Training (cross-package)` (`government_skill_schemes.scheme_id`)
- `package006_skill_id` -> `Package006_Skills_and_Training (cross-package)` (`skills.skill_id`)
- `package006_certification_id` -> `Package006_Skills_and_Training (cross-package)` (`certifications.certification_id`)
- `package006_provider_id` -> `Package006_Skills_and_Training (cross-package)` (`training_providers.provider_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package006_provider_id` | 9 of 12 |
| `package006_provider_name` | 9 of 12 |
| `package006_certification_id` | 8 of 12 |
| `package006_certification_name` | 8 of 12 |
| `package006_scheme_id` | 3 of 12 |
| `package006_scheme_name` | 3 of 12 |
| `package006_skill_id` | 1 of 12 |
| `package006_skill_name` | 1 of 12 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

Certification and provider links are sparse (4 and 3 resolved of 12) because most scheme-to-skill relationships do not run through one named certificate or one named provider. PM Vishwakarma and PMEGP have no Package006 scheme counterpart. One row (PMEGP) carries the sentinel on all four Package006 columns: Package006 v1.0.0 has no entrepreneurship skill record, which validation surfaced when an assumed link failed to resolve.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/skill_scheme_mapping.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/skill_scheme_mapping.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/skill_scheme_mapping.collection_report.md`
