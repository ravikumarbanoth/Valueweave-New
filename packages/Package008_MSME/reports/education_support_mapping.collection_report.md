# Collection Report: education_support_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/education_support_mapping.csv`
**Layer**: 6 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1-2 (Package002 and Package006 reconciliation)

## Purpose

Educational and skilling institutions that supply talent to MSME categories.

## Methodology

Two upstream packages, referenced by whichever holds the institution: degree-granting universities from Package002, and ITI, polytechnic, skill-mission and sector-academy networks from Package006. Each row states which MSME categories it feeds and the nature of the support, so the dataset answers 'where does my workforce come from' rather than just listing institutions.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 13 |
| Columns | 15 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (13/13 distinct) |
| Total cells | 195 |
| Bare `PENDING_VERIFICATION` cells | 26 (13.33%) |
| Blank cells | 0 |
| Confidence range | 64-70 (ceiling 85) |
| Confidence average | 67.4 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `support_entity_type`
- `entity_name`
- `package002_institution_id`
- `package002_institution_name`
- `package006_provider_id`
- `package006_provider_name`
- `supports_business_categories`
- `support_nature`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `package002_institution_id` -> `Package002_Education (cross-package)` (`universities_telangana_andhra_pradesh.id`)
- `package006_provider_id` -> `Package006_Skills_and_Training (cross-package)` (`training_providers.provider_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package002_institution_id` | 9 of 13 |
| `package002_institution_name` | 9 of 13 |
| `package006_provider_id` | 4 of 13 |
| `package006_provider_name` | 4 of 13 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

Nine of 13 rows sentinel the Package002 id and four sentinel the Package006 id, because most rows legitimately belong to one package or the other, not both. Incubation and innovation-cell activity is noted in support_nature but is not separately catalogued -- startup_ecosystem.csv holds incubators. This is the only dataset in the package with no business_id: it maps institutions to categories, not to individual businesses.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/education_support_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/education_support_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/education_support_mapping.collection_report.md`
