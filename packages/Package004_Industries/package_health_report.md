# Package Health Report — Package004_Industries_and_Livelihoods v1.0.0-RC1

## Scoring Methodology (mirrors Package001-003)

Weighted components, 0-100 scale:

| Component | Weight | Score | Basis |
|---|---|---|---|
| Provenance completeness | 30% | 100 | Every row across all 5 datasets has data_source, source_url, confidence_score, verification_status, and collection_date populated |
| Stable identifiers | 20% | 70 | UUID primary keys are 100% present and unique (63 rows, 0 duplicates within or across datasets); no separate immutable ref-code system for cross-package linking |
| Geo-precision (lat/long) | 20% | 0 | Not collected in this release — this package doesn't carry per-entity location at all (it catalogues category-level opportunities, not sited institutions); see docs/METHODOLOGY.md |
| Cross-government-ID linkage | 15% | 0 | No Udyam/GSTIN/scheme-code identifiers captured per-row |
| FK integrity where data exists | 15% | 100 | No inter-dataset FKs declared, so none can be broken |

**Computed score: 0.30(100) + 0.20(70) + 0.20(0) + 0.15(0) + 0.15(100) = 59.0 → 59/100**

This lands at parity with Package001_Geography (58/100), Package002_Education (59/100), and
Package003_Healthcare (59/100) — the same rubric, applied to a structurally different kind of
content (livelihood categories rather than institutions), still produces the same result because the
package shares the same two structural gaps common to all four packages so far.

## AI Readiness Score

Same methodology and weighting as above.

**Score: 59/100**

Interpretation: the package is structurally AI-consumable — every fact is traceable to a specific
source URL, confidence score, and review status, and an AI system can reliably distinguish "known,
moderately confident" from "explicitly unknown" (`PENDING_VERIFICATION`) — but it lacks the
geo-spatial layer (not applicable in the same way here, since this package's unit of analysis is a
category, not a sited institution) and cross-government-ID layer (Udyam registration numbers, GSTIN,
scheme codes) that would let it plug into external MSME registries.

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
This package's datasets characterize industry/livelihood categories, not sited institutions, so
there is no per-row location to begin with (unlike Package001-003, where lat/long was a genuine gap
against real addressable entities). This is a structural difference, not a comparable omission —
documented here for consistency with the shared scoring rubric, not as an apples-to-apples
weakness against the other packages.

### Cross-government-ID linkage: 0%
No row carries a Udyam registration number, GSTIN, or scheme reference code. Known, disclosed gap.

### FK integrity: 100% (of what exists)
`schemas/schema_catalog.json` declares zero foreign keys for RC1's 5 datasets — this is accurate,
not aspirational.

## Confidence & Verification Health

- 0 of 63 rows are `VST-VERIFIED` (100% `VST-NEEDS_REVIEW`) — by design.
- Confidence scores range 48-82, average 70.5 — the lowest average confidence of any ValueWeave
  package released so far, because this package's core content (livelihood-opportunity investment
  ranges) is inherently harder to trace to a specific government document than institutional facts
  (a hospital's address, a university's establishment year). See `docs/METHODOLOGY.md`.
- 20 of 1,053 total fields (1.9%) are marked `PENDING_VERIFICATION`, concentrated in
  `typical_investment_range_summary`.

## Comparison to Prior Packages

| Package | Health/AI-Readiness Score | Overall Confidence Average |
|---|---|---|
| Package001_Geography | 58/100 | ~85 (with WebFetch access in early collection) |
| Package002_Education | 59/100 | 77.9 (RC2) |
| Package003_Healthcare | 59/100 | 85.8 (RC2) |
| Package004_Industries_and_Livelihoods | 59/100 | 70.5 (RC1) |

Package004's lower confidence average reflects a genuine difference in content type, not a quality
regression: prior packages verified discrete institutions against official sources, while this
package characterizes livelihood opportunities where the strongest available sources (government
project profiles) are themselves harder to locate and confirm via search-snippet-only research.
