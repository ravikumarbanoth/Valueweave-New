# Collection Report: ai_precision_agriculture.csv

**Package**: Package005_Agriculture v1.0.0
**Dataset**: `datasets/ai_precision_agriculture.csv`
**Layer**: 11 - AI and Technology Readiness
**Collection date**: 2026-07-24
**Source tier**: Tier 1-4 (ICAR/ISRO/IMD for deployed systems; research and pilot reporting for emerging ones)

## Purpose

Precision-agriculture and AI technology readiness with adoption level, ROI potential and the binding constraint.

## Methodology

The ten technologies named in the package specification were assessed on current Indian adoption, AI readiness and the specific constraint that limits deployment. Confidence is deliberately the lowest in the package (50-66) because adoption and ROI for emerging technology are forward-looking judgements, not published statistics.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 10 |
| Columns | 16 |
| Primary key | `technology_id` |
| Primary key uniqueness | PASS (10/10 distinct) |
| Total cells | 160 |
| Bare `PENDING_VERIFICATION` cells | 10 (6.25%) |
| Blank cells | 0 |
| Confidence range | 50-66 (ceiling 85) |
| Confidence average | 58.2 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-24` (all rows) |

## Columns

- `technology_id`
- `technology_name`
- `technology_type`
- `application`
- `crop_suitability`
- `current_adoption_india`
- `ai_readiness_level`
- `approximate_cost_inr`
- `roi_potential`
- `primary_constraint`
- `data_source` — Authoritative body the row was attributed to
- `source_url` — Public URL for that body or scheme
- `collection_date` — Collection date; uniform 2026-07-24 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `approximate_cost_inr` | 10 of 10 |

Each sentinel above means no public source was found for that specific fact. No estimate was substituted.

## Known limitations

approximate_cost_inr is the bare sentinel on every row: no official public cost benchmark exists for any of these technologies in India. current_adoption_india is an ordinal band, not a measured penetration rate. Rows for farm robotics, autonomous tractors and digital twins describe research and pilot stages, not commercially available offerings.

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/ai_precision_agriculture.csv`
- Metadata: `packages/Package005_Agriculture/metadata/ai_precision_agriculture.metadata.json`
- This report: `packages/Package005_Agriculture/reports/ai_precision_agriculture.collection_report.md`
