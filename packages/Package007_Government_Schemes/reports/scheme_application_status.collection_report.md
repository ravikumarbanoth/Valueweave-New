# Collection Report: scheme_application_status.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/scheme_application_status.csv`
**Layer**: 4 - Process
**Collection date**: 2026-07-25
**Source tier**: Tier 3 (observed common workflow across scheme portals)

## Purpose

Generic application status workflow with ordering, terminality and whether citizen action is required.

## Methodology

Eight statuses covering the workflow named in the specification, plus QUERY_RAISED which the specification omitted but which is the single most common cause of silent application failure when an applicant does not respond in time. citizen_action_required is the operationally important column: it distinguishes waiting from being blocked.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 8 |
| Columns | 15 |
| Primary key | `status_id` |
| Primary key uniqueness | PASS (8/8 distinct) |
| Total cells | 120 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 69-72 (ceiling 85) |
| Confidence average | 70.9 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `status_id`
- `status_code`
- `status_name`
- `status_order`
- `status_group`
- `description`
- `typical_next_status`
- `is_terminal`
- `citizen_action_required`
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

This is a generic reference workflow, not any one portal's state machine. Individual portals use different status labels and some add scheme-specific states. Consumers should map portal-specific statuses onto these codes rather than expecting an exact match.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/scheme_application_status.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/scheme_application_status.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/scheme_application_status.collection_report.md`
