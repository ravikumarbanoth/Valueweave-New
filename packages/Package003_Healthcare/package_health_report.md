# Package Health Report — Package003_Healthcare v1.0.0

## Scoring Methodology (mirrors Package001_Geography and Package002_Education, unchanged from RC1)

Weighted components, 0-100 scale:

| Component | Weight | Score | Basis |
|---|---|---|---|
| Provenance completeness | 30% | 100 | Every row across all 4 datasets (146 as of RC2) has data_source, source_url, confidence_score, verification_status, and collection_date populated |
| Stable identifiers | 20% | 70 | UUID primary keys are 100% present and unique across all 146 rows; still no separate immutable ref-code system for cross-package linking |
| Geo-precision (lat/long) | 20% | 0 | Still not collected in RC2 — known gap, see docs/METHODOLOGY.md |
| Cross-government-ID linkage | 15% | 0 | Still no NMC/NABH/NABL facility codes captured per-row |
| FK integrity where data exists | 15% | 100 | Still no enforced inter-dataset FKs declared |

**Computed score: 0.30(100) + 0.20(70) + 0.20(0) + 0.15(0) + 0.15(100) = 59.0 → 59/100 (unchanged from RC1)**

### Why the score didn't move despite real quality improvements

RC2 made substantive quality improvements — confidence up (avg 82.9 → 85.8), 12 new verified records,
2 institution datasets each gained 3-4 new columns with real (if partial) fill rates, and several
source conflicts resolved — but **none of those map onto this 5-component rubric**, which measures
provenance/identifiers/geo/cross-gov-ID/FK-integrity specifically, not confidence level or
field-fill-rate. This is the same structural limitation documented in Package002_Education's RC2
health report: the rubric doesn't reward within-component quality gains.

## AI Readiness Score

**Score: 59/100 (unchanged from RC1)** — same reasoning; the AI-readiness formula reuses the
identical 5 components.

## Component Detail

### Provenance completeness: 100%
All 146 rows carry `data_source`, `source_url`, `collection_date`, `confidence_score`, and
`verification_status`. Verified programmatically — see `reports/validation_report.md`.

### Stable identifiers: 70%
UUIDv4 `id` present and unique across all 146 rows (verified — see `reports/duplicate_analysis.md`).
Still no secondary immutable reference code (unchanged from RC1).

### Geo-precision: 0%
Unchanged from RC1 — no dataset includes latitude/longitude.

### Cross-government-ID linkage: 0%
Unchanged from RC1 — no NMC/NABH/NABL facility codes.

### FK integrity: 100% (of what exists)
Unchanged from RC1 — zero enforced FKs, so nothing to break.

## Field Completeness (informational — not part of the health score)

| Metric | RC1 | RC2 | Delta |
|---|---|---|---|
| Total records | 134 | 146 | +12 |
| Overall confidence average | 82.9 | 85.8 | +2.9 |
| Total columns across datasets | 70 | 77 | +7 (4 hospital + 3 college new columns) |
| PENDING_VERIFICATION fields (total) | 215 / 2,443 (8.8%) | 374 / 3,063 (12.2%) | see note |
| Regulatory bodies PENDING fields | 7 | 3 | -4 (5 filled, 1 new field on new row) |
| Government hospitals rows | 49 | 55 | +6 |
| Medical colleges rows | 54 | 58 | +4 |

Note: the PENDING_VERIFICATION *rate* rose because RC2 added 7 brand-new, partially-unpopulated
columns across the two institution datasets (email, specialties_summary, available_services_summary,
government_scheme_coverage_summary for hospitals; email, departments_summary,
government_scheme_coverage_summary for colleges) — this mechanically adds pending cells even as
existing fields got filled. See `reports/rc1_vs_rc2_comparison.md` for exact per-column deltas.

## Confidence & Verification Health

- 0 of 146 rows are `VST-VERIFIED` (100% `VST-NEEDS_REVIEW`) — unchanged, by design.
- Confidence scores range 78-88, average 85.8 (up from 82.9 in RC1) — still capped at 88 since
  WebFetch remained blocked in RC2 (re-confirmed live before enrichment began).
- 374 of 3,063 total fields (12.2%) are marked `PENDING_VERIFICATION`.

## Comparison to Package001_Geography (58/100) and Package002_Education (59/100)

Package003_Healthcare's final 59/100 remains at parity with both prior packages on this rubric — all
three share the same geo-precision and cross-government-ID gaps as primary weaknesses. The RC1→RC2
quality gains are documented in `reports/rc1_vs_rc2_comparison.md` and are genuine improvements not
captured by this specific scoring formula.
