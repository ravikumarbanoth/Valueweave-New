# Collection Report: scheme_ai_recommendations.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/scheme_ai_recommendations.csv`
**Layer**: 8 - Recommendation Layer
**Collection date**: 2026-07-25
**Source tier**: Tier 3 (rule-based synthesis over this package's own eligibility_criteria.csv)

## Purpose

Citizen profile archetypes mapped to ranked scheme recommendations with priority score, basis, next scheme and related schemes.

## Methodology

Ten profile archetypes covering the citizen journeys in the specification, each with a ranked recommendation set. priority_score is a deterministic function of eligibility overlap, benefit magnitude and sequencing logic, intended as a rule-engine input. recommendation_basis states in one sentence why the scheme fits, which makes the score auditable rather than opaque. suggested_next_scheme_id encodes sequencing: PMJDY before any DBT scheme, PM-KISAN before KCC, basic training before advanced.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 37 |
| Columns | 18 |
| Primary key | `recommendation_id` |
| Primary key uniqueness | PASS (37/37 distinct) |
| Total cells | 666 |
| Bare `PENDING_VERIFICATION` cells | 12 (1.8%) |
| Blank cells | 0 |
| Confidence range | 60-60 (ceiling 85) |
| Confidence average | 60.0 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `recommendation_id`
- `profile_code`
- `profile_description`
- `profile_attributes`
- `scheme_id`
- `scheme_short_name`
- `priority_score`
- `priority_rank`
- `recommendation_basis`
- `suggested_next_scheme_id`
- `related_scheme_ids`
- `future_opportunity`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `suggested_next_scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `related_scheme_ids` -> `government_schemes.csv` (`scheme_id (semicolon-delimited)`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `suggested_next_scheme_id` | 12 of 37 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

Confidence is 60 on every row, the lowest in the package, and deliberately so. priority_score is a designed heuristic, not an empirical outcome measure: no uptake, approval-rate or benefit-realisation data was available to calibrate it. Profiles are archetypes, not real users, and a production recommender must validate against actual eligibility determination rather than trusting these scores. Treat this dataset as a rule-engine seed, not as evidence.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/scheme_ai_recommendations.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/scheme_ai_recommendations.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/scheme_ai_recommendations.collection_report.md`
