# Collection Report: district_scheme_mapping.csv

**Package**: Package007_Government_Schemes v1.0.0
**Dataset**: `datasets/district_scheme_mapping.csv`
**Layer**: 7 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Package001 district master; scheme guidelines)

## Purpose

District-delivered schemes mapped to all 61 Package001 districts with the district-level agency and application channel.

## Methodology

Five schemes whose application is genuinely mediated by a district-level institution were mapped across all 61 Telangana and Andhra Pradesh districts, giving 305 rows with every dist_id resolving. The insight this encodes is that central schemes are nationally uniform in coverage but not in access route: what varies by district is which office you approach.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the scheme portal or ministry that governs the fact in `data_source`, and `confidence_score`
is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 305 |
| Columns | 16 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (305/305 distinct) |
| Total cells | 4880 |
| Bare `PENDING_VERIFICATION` cells | 305 (6.25%) |
| Blank cells | 0 |
| Confidence range | 71-73 (ceiling 85) |
| Confidence average | 71.8 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `scheme_id`
- `scheme_short_name`
- `package001_dist_id`
- `dist_ref`
- `district_name`
- `state_scope`
- `district_level_agency`
- `application_channel`
- `district_specific_variation`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body, scheme or portal
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `scheme_id` -> `government_schemes.csv` (`scheme_id`)
- `package001_dist_id` -> `Package001_Geography (cross-package)` (`district.dist_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `district_specific_variation` | 305 of 305 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

district_specific_variation is the bare sentinel on all 305 rows. District-level variation in benefit quantum, empanelled hospital availability or DIC processing capacity is real but was not confirmable per district without primary-source access. Only 5 of 40 schemes appear here: the remaining 35 are nationally administered with no district-mediated application step, and padding them across 61 districts would assert a district dimension that does not exist.

## Validation

This dataset passes all twelve package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with
denormalised-name agreement, cross-package foreign keys, no blank cells, scheme
coverage, closed enum domains). Re-run with `python3 validate.py` from the package root.

## Files

- Dataset: `packages/Package007_Government_Schemes/datasets/district_scheme_mapping.csv`
- Metadata: `packages/Package007_Government_Schemes/metadata/district_scheme_mapping.metadata.json`
- This report: `packages/Package007_Government_Schemes/reports/district_scheme_mapping.collection_report.md`
