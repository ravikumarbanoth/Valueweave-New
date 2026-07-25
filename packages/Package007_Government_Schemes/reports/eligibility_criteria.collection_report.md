# Collection Report: eligibility_criteria.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/eligibility_criteria.csv`
**Layer**: 3 - Eligibility Logic
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (scheme guidelines via MyScheme and scheme portals)

## Purpose

Decomposed eligibility conditions per scheme, typed by criterion and flagged mandatory or not.

## Methodology

Eligibility was decomposed into one row per condition rather than held as prose, because that is what makes machine eligibility matching possible. criterion_type uses a closed vocabulary (Age, Gender, Income, Category, Occupation, Education, Land Holding, Business Size, Citizenship, Banking, Other, Exclusion) matching the axes named in the specification. Every scheme carries at least one criterion row, enforced by validation check V11; for universal schemes the row states the universality explicitly rather than being absent.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 55 |
| Columns | 13 |
| Primary key | `criterion_id` |
| Primary key uniqueness | PASS (55/55 distinct) |
| Total cells | 715 |
| Bare `PENDING_VERIFICATION` cells | 11 (1.54%) |
| Blank cells | 0 |
| Confidence range | 70-76 (ceiling 85) |
| Confidence average | 72.7 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `criterion_id`
- `scheme_id`
- `scheme_short_name`
- `criterion_type`
- `criterion_value`
- `is_mandatory`
- `verification_document_hint`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `verification_document_hint` -> `required_documents.csv` (`document_name`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `verification_document_hint` | 11 of 55 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

criterion_value describes the condition qualitatively. Numeric thresholds (income ceilings, age bands, land limits) are stated as 'below the prescribed ceiling' rather than as figures, because those thresholds are revised by notification. is_mandatory distinguishes hard gates from criteria that only affect benefit quantum, for example category affecting SMAM subsidy percentage without affecting eligibility.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/eligibility_criteria.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/eligibility_criteria.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/eligibility_criteria.collection_report.md`
