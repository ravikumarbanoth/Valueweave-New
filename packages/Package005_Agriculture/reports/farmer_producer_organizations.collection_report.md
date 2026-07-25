# Collection Report: farmer_producer_organizations.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/farmer_producer_organizations.csv`
**Layer**: 6 - Institutions
**Collection date**: 2026-07-24
**Source tier**: Tier 1-2 (Ministry of Agriculture FPO programme; NABARD; MCA; NRLM)

## Purpose

Collective organisation models available to farmers for aggregation, input purchase and market access.

## Methodology

Five legal and organisational forms were characterised by registration route, typical membership scale and services offered, because the choice between them is a legal-structure decision with different compliance consequences.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 5 |
| Columns | 12 |
| Primary key | `fpo_id` |
| Primary key uniqueness | PASS (5/5 distinct) |
| Total cells | 60 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 68-75 (ceiling 85) |
| Confidence average | 71.6 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `fpo_id`
- `organization_type`
- `description`
- `typical_size_members`
- `services_offered`
- `major_states`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

Describes organisation types, not a registry of named FPOs. typical_size_members is an indicative band.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/farmer_producer_organizations.csv`
- Metadata: `packages/Package005_Agriculture/metadata/farmer_producer_organizations.metadata.json`
- This report: `packages/Package005_Agriculture/reports/farmer_producer_organizations.collection_report.md`
