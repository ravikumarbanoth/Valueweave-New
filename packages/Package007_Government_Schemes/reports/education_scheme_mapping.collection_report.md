# Collection Report: education_scheme_mapping.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/education_scheme_mapping.csv`
**Layer**: 7 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (National Scholarship Portal; Package002 reconciliation)

## Purpose

Education schemes mapped to Package002 records, student category, education stage and institution type.

## Methodology

Package002 scholarship UUIDs were resolved by reading the released scholarships.csv at generation time, so a link either matches a real record or is not asserted.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 7 |
| Columns | 15 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (7/7 distinct) |
| Total cells | 105 |
| Bare `PENDING_VERIFICATION` cells | 9 (8.57%) |
| Blank cells | 0 |
| Confidence range | 68-76 (ceiling 85) |
| Confidence average | 71.6 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `scheme_id`
- `scheme_short_name`
- `package002_dataset`
- `package002_record_id`
- `package002_record_name`
- `student_category`
- `education_stage`
- `institution_type`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `package002_record_id` -> `Package002_Education (cross-package)` (`scholarships.id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package002_dataset` | 3 of 7 |
| `package002_record_id` | 3 of 7 |
| `package002_record_name` | 3 of 7 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

4 of 7 rows resolve. Three carry the sentinel: Samagra Shiksha and PM POSHAN are institutional and entitlement schemes with no Package002 counterpart record, and Skill Loan is education financing while Package002 covers scholarships only.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/education_scheme_mapping.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/education_scheme_mapping.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/education_scheme_mapping.collection_report.md`
