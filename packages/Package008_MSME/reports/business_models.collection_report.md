# Collection Report: business_models.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/business_models.csv`
**Layer**: 1 - Reference Taxonomy
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (MSME-DI project profiles; Ministry of MSME)

## Purpose

The delivery models an MSME can adopt, classified by what the model actually depends on.

## Methodology

Fifteen models classified by model_type into Asset-Based, Skill-Based, Working-Capital-Based, IP-Based, Infrastructure, Project-Based and hybrids. That classification is the useful part: it tells an entrepreneur what the binding constraint will be. primary_risk names the specific failure mode each model carries.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 15 |
| Columns | 14 |
| Primary key | `business_model_id` |
| Primary key uniqueness | PASS (15/15 distinct) |
| Total cells | 210 |
| Bare `PENDING_VERIFICATION` cells | 15 (7.14%) |
| Blank cells | 0 |
| Confidence range | 64-76 (ceiling 85) |
| Confidence average | 70.7 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `business_model_id`
- `business_model_name`
- `model_type`
- `description`
- `revenue_pattern`
- `asset_intensity`
- `typical_lead_time_to_revenue`
- `primary_risk`
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
| `typical_lead_time_to_revenue` | 15 of 15 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

typical_lead_time_to_revenue is the bare sentinel throughout: no published benchmark exists and the figure varies more by operator than by model. revenue_pattern and asset_intensity are qualitative.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/business_models.csv`
- Metadata: `packages/Package008_MSME/metadata/business_models.metadata.json`
- This report: `packages/Package008_MSME/reports/business_models.collection_report.md`
