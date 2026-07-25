# Collection Report: required_documents.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/required_documents.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (issuing authorities: UIDAI, Income Tax Department, state revenue departments, GSTN, Ministry of MSME)

## Purpose

Document catalogue with issuing authority, typical use and digital availability.

## Methodology

Fifteen documents covering the identity, eligibility, asset, financial, business and education classes that gate scheme access. digilocker_available was included because it materially changes application friction, and is marked Partial where availability depends on state or institution onboarding rather than being uniform.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 15 |
| Columns | 13 |
| Primary key | `document_id` |
| Primary key uniqueness | PASS (15/15 distinct) |
| Total cells | 195 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 68-78 (ceiling 85) |
| Confidence average | 72.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `document_id`
- `document_name`
- `document_type`
- `issuing_authority`
- `typical_use`
- `is_digital_available`
- `digilocker_available`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Certificate validity periods, issuing officer rank and application routes differ by state and are not asserted per state here. Land records digitisation is uneven and tenant farmers frequently cannot produce the documentation that agriculture schemes assume, which is a real access barrier this dataset records but does not resolve.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/required_documents.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/required_documents.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/required_documents.collection_report.md`
