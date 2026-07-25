# Collection Report: startup_ecosystem.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/startup_ecosystem.csv`
**Layer**: 10 - Support Ecosystem
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (DPIIT; Atal Innovation Mission; Ministry of MSME; state governments)

## Purpose

Incubators, accelerators, government institutes and trade bodies that support MSME and startup formation.

## Methodology

Twelve entities spanning national programmes, incubator networks, government institutes, district offices, state facilities and trade bodies. target_stage was included because ecosystem fit is stage-dependent: RSETI serves pre-establishment, MSME-DI serves pre-establishment through early operation, T-Hub serves early to growth stage.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 12 |
| Columns | 15 |
| Primary key | `ecosystem_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 180 |
| Bare `PENDING_VERIFICATION` cells | 3 (1.67%) |
| Blank cells | 0 |
| Confidence range | 66-76 (ceiling 85) |
| Confidence average | 70.2 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `ecosystem_id`
- `entity_name`
- `entity_type`
- `sponsoring_body`
- `jurisdiction`
- `services_offered`
- `target_stage`
- `sector_focus`
- `official_website`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `official_website` | 3 of 12 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

District-level and network entries (DIC, Rural Business Incubators, RSETI, Export Promotion Councils) describe entity types present across many locations, not named offices, and sentinel official_website where no single national URL exists. The two Telangana-specific facilities (T-Hub, WE-HUB) are named because they are single-site institutions; Andhra Pradesh's counterpart is recorded at programme level. No count of incubatees, funding deployed or success rate is asserted.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/startup_ecosystem.csv`
- Metadata: `packages/Package008_MSME/metadata/startup_ecosystem.metadata.json`
- This report: `packages/Package008_MSME/reports/startup_ecosystem.collection_report.md`
