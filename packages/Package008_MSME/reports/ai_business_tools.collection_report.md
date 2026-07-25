# Collection Report: ai_business_tools.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/ai_business_tools.csv`
**Layer**: 9 - Technology Adoption
**Collection date**: 2026-07-25
**Source tier**: Tier 2-3 (MeitY; NASSCOM; industry reporting)

## Purpose

AI and software tool classes with MSME relevance, Indian adoption maturity and implementation complexity.

## Methodology

Twelve tool classes rather than named products, because products churn and classes do not. expected_benefit states the business outcome, and implementation_complexity is separated from msme_relevance -- a tool can be highly relevant and still be impractical for a micro unit, which is the case for predictive maintenance and AI quality inspection.

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
| Primary key | `tool_id` |
| Primary key uniqueness | PASS (12/12 distinct) |
| Total cells | 180 |
| Bare `PENDING_VERIFICATION` cells | 0 (0.0%) |
| Blank cells | 0 |
| Confidence range | 57-72 (ceiling 85) |
| Confidence average | 63.1 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `tool_id`
- `tool_class`
- `function_area`
- `description`
- `msme_relevance`
- `adoption_maturity_india`
- `implementation_complexity`
- `typical_deployment`
- `expected_benefit`
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

No cost is asserted. adoption_maturity_india is an ordinal judgement from industry reporting, not a measured penetration rate, and carries the lowest confidence in the package alongside the emerging-technology rows. Generative AI is rated the lowest-friction entry point, which reflects current tooling and may date quickly.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/ai_business_tools.csv`
- Metadata: `packages/Package008_MSME/metadata/ai_business_tools.metadata.json`
- This report: `packages/Package008_MSME/reports/ai_business_tools.collection_report.md`
