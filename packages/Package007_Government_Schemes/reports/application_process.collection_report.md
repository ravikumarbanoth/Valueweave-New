# Collection Report: application_process.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/application_process.csv`
**Layer**: 4 - Process
**Collection date**: 2026-07-25
**Source tier**: Tier 1-3 (scheme portals; operational guidelines)

## Purpose

Ordered step-by-step application workflow per scheme with channel, responsible actor and step output.

## Methodology

Eight schemes with well-documented multi-stage processes were modelled end to end, one row per step, ordered by step_number. output_of_step names the artifact or state change each step produces, which is what makes the workflow actionable rather than descriptive. responsible_actor distinguishes steps the citizen must act on from steps that happen inside the administration.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 43 |
| Columns | 16 |
| Primary key | `step_id` |
| Primary key uniqueness | PASS (43/43 distinct) |
| Total cells | 688 |
| Bare `PENDING_VERIFICATION` cells | 39 (5.67%) |
| Blank cells | 0 |
| Confidence range | 68-74 (ceiling 85) |
| Confidence average | 72.1 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `step_id`
- `scheme_id`
- `scheme_short_name`
- `step_number`
- `step_name`
- `step_description`
- `channel`
- `responsible_actor`
- `typical_timeline`
- `output_of_step`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `typical_timeline` | 39 of 43 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

typical_timeline is the bare sentinel on every row. Except for MGNREGA's statutory work-allocation period, no published service standard was confirmable without a primary-source read; inventing plausible durations would be fabrication in the field applicants care most about. Only 8 of 40 schemes have process rows; the rest are single-step or lack documented multi-stage workflows.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/application_process.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/application_process.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/application_process.collection_report.md`
