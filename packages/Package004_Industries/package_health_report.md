# Package Health Report — Package004_Industries_and_Livelihoods v1.0.0 (Business Opportunity Knowledge Base)

## Scoring Methodology (mirrors Package001-003)

Weighted components, 0-100 scale:

| Component | Weight | Score | Basis |
|---|---|---|---|
| Provenance completeness | 30% | 100 | Every row across all 5 datasets has data_source, source_url, confidence_score, verification_status, and collection_date populated |
| Stable identifiers | 20% | 70 | UUID primary keys are 100% present and unique (63 rows, 0 duplicates within or across datasets); no separate immutable ref-code system for cross-package linking |
| Geo-precision (lat/long) | 20% | 0 | Not collected — this package doesn't carry per-entity coordinates (it catalogues opportunity types, not sited institutions); `district_suitability_summary` is free-text, not structured geo data, so it does not change this score |
| Cross-government-ID linkage | 15% | 0 | No Udyam/GSTIN/scheme-code identifiers captured per-row |
| FK integrity where data exists | 15% | 100 | No inter-dataset FKs declared, so none can be broken |

**Computed score: 0.30(100) + 0.20(70) + 0.20(0) + 0.15(0) + 0.15(100) = 59.0 → 59/100**

Unchanged from RC1's 59/100 — the v2 enrichment pass added 24 new columns per opportunity dataset
(entrepreneurship-practicality depth), but none of those columns are geo-coordinates or
cross-government IDs, so the structural gaps driving this score are untouched. This is expected: this
pass was about *content depth*, not *structural* identifiers.

## AI Readiness Score

Same methodology and weighting as above.

**Score: 59/100**

Interpretation: the package is now substantially more useful to an AI system answering a practical
entrepreneurship question ("what machinery do I need for cold-pressed oil extraction," "which AI
tools help a freelance digital marketer") because 4 of 5 datasets now carry 24 additional sourced,
confidence-scored fields per row versus RC1. The structural AI-readiness score is unchanged because
this rubric measures identifier/geo/FK infrastructure, not content richness — a system consuming this
package gets meaningfully more *answerable questions per row* in v1.0.0 without any change to how
reliably it can be linked to other packages.

## Component Detail

### Provenance completeness: 100%
All 63 rows across 5 datasets carry `data_source`, `source_url`, `collection_date`,
`confidence_score`, and `verification_status`. Verified programmatically — see
`reports/validation_report.md`.

### Stable identifiers: 70%
UUIDv4 `id` present and unique in all 5 datasets and across the package (verified — see
`reports/duplicate_analysis.md`). Deducted 30 points because there is no secondary immutable
reference code.

### Geo-precision: 0%
Unchanged from RC1. `district_suitability_summary` (new in v1.0.0) is a free-text description of
which Telangana/AP districts suit an opportunity, not a structured `district_id` or lat/long — it
improves human/LLM readability but does not satisfy this rubric's structured-geo criterion.

### Cross-government-ID linkage: 0%
No row carries a Udyam registration number, GSTIN, or scheme reference code. Known, disclosed gap,
unchanged from RC1.

### FK integrity: 100% (of what exists)
`schemas/schema_catalog.json` declares zero foreign keys for v1.0.0's 5 datasets — this is accurate,
not aspirational.

## Confidence & Verification Health

- 0 of 63 rows are `VST-VERIFIED` (100% `VST-NEEDS_REVIEW`) — by design; promotion to verified is a
  separate governance action.
- Confidence scores range 55-85, average 74.4 — up from RC1's 48-82 range / 70.5 average. Every
  increase during the v2 enrichment pass was capped at +8 and justified by genuinely stronger
  corroborating sources found for previously-thin fields; no score was ever lowered.
- 320 of 1,890 total fields (16.93%) are marked `PENDING_VERIFICATION`, concentrated in
  `minimum_investment`, `working_capital_summary`, `estimated_setup_time_summary`,
  `seasonal_factors_summary`, `ai_tools_summary`, and `success_stories_summary` — see
  `reports/business_opportunity_enrichment_summary.md` for the exact per-field breakdown.
- This 16.93% rate is *higher* than RC1's 1.9% not because the package got less reliable, but because
  the schema expanded from 18 to 36 columns per opportunity dataset — the 24 new fields are
  inherently harder to source than the original 18, and every field that couldn't be sourced was
  marked `PENDING_VERIFICATION` rather than guessed. A higher disclosed-gap rate on a much richer
  schema is the intended outcome of this methodology, not a regression.

## Comparison to Prior Packages / Prior Release of This Package

| Package | Health/AI-Readiness Score | Overall Confidence Average |
|---|---|---|
| Package001_Geography | 58/100 | ~85 (with WebFetch access in early collection) |
| Package002_Education | 59/100 | 77.9 (RC2) |
| Package003_Healthcare | 59/100 | 85.8 (RC2) |
| Package004_Industries_and_Livelihoods (RC1) | 59/100 | 70.5 |
| Package004_Industries_and_Livelihoods (v1.0.0) | 59/100 | 74.4 |

Package004's confidence average remains the lowest of the four packages released so far, and that
continues to reflect a genuine difference in content type rather than a quality regression: prior
packages verify discrete institutions against official sources, while this package characterizes
livelihood opportunities where even the strongest available sources (government project profiles) are
themselves harder to locate and confirm via search-snippet-only research.
