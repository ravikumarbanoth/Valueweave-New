# Collection Report: implementing_agencies.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/implementing_agencies.csv`
**Layer**: 5 - Institutions
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (agency official websites and enabling ministries)

## Purpose

Agencies that design, fund and deliver schemes, from central ministries to Gram Panchayats.

## Methodology

Twenty agencies spanning every tier at which scheme delivery actually happens: central ministry, central authority, development financial institution, statutory body, state department, district office, local body and assisted-service network. The tiering matters because the agency a citizen approaches is almost never the agency that owns the scheme.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 20 |
| Columns | 14 |
| Primary key | `agency_id` |
| Primary key uniqueness | PASS (20/20 distinct) |
| Total cells | 280 |
| Bare `PENDING_VERIFICATION` cells | 6 (2.14%) |
| Blank cells | 0 |
| Confidence range | 68-78 (ceiling 85) |
| Confidence average | 73.8 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `agency_id`
- `agency_name`
- `agency_type`
- `government_level`
- `jurisdiction`
- `primary_role`
- `sectors_covered`
- `official_website`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `official_website` | 6 of 20 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

District and state-level entries (DIC, District Collector, state departments, Gram Panchayat) describe agency types that exist in every district, not named offices; official_website is the sentinel for those. No named district office is asserted.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/implementing_agencies.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/implementing_agencies.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/implementing_agencies.collection_report.md`
