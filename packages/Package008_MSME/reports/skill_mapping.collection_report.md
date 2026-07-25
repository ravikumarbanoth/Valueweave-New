# Collection Report: skill_mapping.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/skill_mapping.csv`
**Layer**: 6 - Cross-Package Mapping
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (Package006 reconciliation)

## Purpose

Which skills each business requires, in what role, at what criticality, and for whom.

## Methodology

Every business carries at least one skill row, enforced by V11. 46 of 53 rows resolve to a real Package006 skill_id. who_needs_it distinguishes owner-level from operator-level requirements, which changes hiring strategy. Skill detail -- NSQF level, learning duration, training route -- stays in Package006.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 53 |
| Columns | 14 |
| Primary key | `mapping_id` |
| Primary key uniqueness | PASS (53/53 distinct) |
| Total cells | 742 |
| Bare `PENDING_VERIFICATION` cells | 14 (1.89%) |
| Blank cells | 0 |
| Confidence range | 57-72 (ceiling 85) |
| Confidence average | 66.4 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `mapping_id`
- `business_id`
- `business_name`
- `package006_skill_id`
- `package006_skill_name`
- `skill_role`
- `criticality`
- `who_needs_it`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- `business_id` -> `msme_businesses.csv` (`business_id`)
- `package006_skill_id` -> `Package006_Skills_and_Training (cross-package)` (`skills.skill_id`)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `package006_skill_id` | 7 of 53 |
| `package006_skill_name` | 7 of 53 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

Seven rows carry the sentinel because Package006 v1.0.0 has no matching skill record: foundry casting, handloom weaving, corrugation machine operation, plastic reprocessing, chemical formulation, data entry and training delivery. Those are real gaps in Package006's coverage, recorded here as explicit sentinel rows with the requirement described in skill_role, rather than being pointed at an approximate skill. criticality is a judgement, not a job specification.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/skill_mapping.csv`
- Metadata: `packages/Package008_MSME/metadata/skill_mapping.metadata.json`
- This report: `packages/Package008_MSME/reports/skill_mapping.collection_report.md`
