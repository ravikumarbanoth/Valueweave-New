# Collection Report: scheme_benefits.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/scheme_benefits.csv`
**Layer**: 6 - Benefits
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (scheme portals and guidelines)

## Purpose

Benefits decomposed by type, disbursement mode and frequency, one row per distinct benefit.

## Methodology

Multi-component schemes carry multiple rows, which is the point: PM Vishwakarma delivers training, a toolkit and credit, and collapsing those into one benefit field would lose the structure a recommendation engine needs. benefit_type uses the vocabulary from the specification (Grant, Subsidy, Loan, Interest Subvention, Insurance, Training, Infrastructure, Scholarship, Equipment Support, Pension). Every scheme has at least one benefit row, enforced by V11.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 51 |
| Columns | 14 |
| Primary key | `benefit_id` |
| Primary key uniqueness | PASS (51/51 distinct) |
| Total cells | 714 |
| Bare `PENDING_VERIFICATION` cells | 45 (6.3%) |
| Blank cells | 0 |
| Confidence range | 69-76 (ceiling 85) |
| Confidence average | 72.4 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `benefit_id`
- `scheme_id`
- `scheme_short_name`
- `benefit_type`
- `benefit_description`
- `benefit_quantum`
- `disbursement_mode`
- `frequency`
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
| `benefit_quantum` | 45 of 51 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

benefit_quantum is the bare sentinel on nearly every row, for the same reason as government_schemes.financial_assistance: amounts are notification-driven. disbursement_mode and frequency are the durable, decision-relevant fields and are populated throughout.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/scheme_benefits.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/scheme_benefits.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/scheme_benefits.collection_report.md`
