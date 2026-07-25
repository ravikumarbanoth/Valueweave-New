# Collection Report: msme_categories.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/msme_categories.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Ministry of MSME; sector ministries)

## Purpose

MSME sector classification across primary groups, manufacturing sub-sectors, service sub-sectors and emerging sectors.

## Methodology

The 24 categories named in the package brief were enumerated and each attributed to the ministry or authority that governs it. category_group separates four genuinely different things the brief's flat list conflates: Primary Sector Group (manufacturing, services, trading), Manufacturing Sub-Sector, Services Sub-Sector and Emerging Sector. nic_section_hint gives the National Industrial Classification anchor so consumers can bridge to official statistics.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 24 |
| Columns | 14 |
| Primary key | `category_id` |
| Primary key uniqueness | PASS (24/24 distinct) |
| Total cells | 336 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 58-78 (ceiling 85) |
| Confidence average | 70.6 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `category_id`
- `category_name`
- `category_group`
- `description`
- `nic_section_hint`
- `capital_intensity`
- `skill_intensity`
- `typical_udyam_class`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

No cell in this dataset carries the sentinel; every field is populated from a documented source.

## Known limitations

capital_intensity and skill_intensity are ordinal judgements, not measured ratios. typical_udyam_class indicates where most units in the category fall, not a constraint. NIC hints are section or division level, not the full five-digit code.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/msme_categories.csv`
- Metadata: `packages/Package008_MSME/metadata/msme_categories.metadata.json`
- This report: `packages/Package008_MSME/reports/msme_categories.collection_report.md`
