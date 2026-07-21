# Package Health Report — Package002_Education v1.0.0-RC2

## Scoring Methodology (mirrors Package001_Geography, unchanged from RC1)

Weighted components, 0-100 scale:

| Component | Weight | Score | Basis |
|---|---|---|---|
| Provenance completeness | 30% | 100 | Every row across all 4 datasets (141 as of RC2) has data_source, source_url, confidence_score, verification_status, and collection_date populated |
| Stable identifiers | 20% | 70 | UUID primary keys are 100% present and unique across all 141 rows; still no separate immutable ref-code system for cross-package linking |
| Geo-precision (lat/long) | 20% | 0 | Still not collected in RC2 — known gap, see docs/METHODOLOGY.md |
| Cross-government-ID linkage | 15% | 0 | Still no AISHE/UDISE/UGC institution codes captured per-row |
| FK integrity where data exists | 15% | 100 | Still no inter-dataset FKs declared, so none can be broken |

**Computed score: 0.30(100) + 0.20(70) + 0.20(0) + 0.15(0) + 0.15(100) = 59.0 → 59/100 (unchanged from RC1)**

### Why the score didn't move despite real quality improvements

RC2 made 3 substantive quality improvements — confidence scores up (avg 75.0 → 77.9), 198 additional
fields filled from PENDING_VERIFICATION across vice_chancellor/naac_grade/nirf_rank, and 3 new columns
added (ownership, contact_details, student_services_summary) — but **none of those map onto this
5-component rubric**, which specifically measures provenance/identifiers/geo/cross-gov-ID/FK-integrity,
not confidence level or field-fill-rate. This is a genuine limitation of reusing Package001's rubric
unchanged: it doesn't reward within-component quality gains. See "Field Completeness (informational)"
below for a metric that does move.

## AI Readiness Score

**Score: 59/100 (unchanged from RC1)** — same reasoning as above; the AI-readiness formula reuses the
identical 5 components.

## Component Detail

### Provenance completeness: 100%
All 141 rows (135 RC1 + 6 new in RC2) carry `data_source`, `source_url`, `collection_date`,
`confidence_score`, and `verification_status`. Verified programmatically — see
`reports/validation_report.md`.

### Stable identifiers: 70%
UUIDv4 `id` present and unique across all 141 rows (verified — see `reports/duplicate_analysis.md`).
Still no secondary immutable reference code (unchanged from RC1).

### Geo-precision: 0%
Unchanged from RC1 — no dataset includes latitude/longitude.

### Cross-government-ID linkage: 0%
Unchanged from RC1 — no AISHE/UDISE/UGC institution codes.

### FK integrity: 100% (of what exists)
Unchanged from RC1 — zero declared FKs, so nothing to break.

## Field Completeness (informational — not part of the health score)

| Metric | RC1 | RC2 | Delta |
|---|---|---|---|
| Total records | 135 | 141 | +6 |
| Overall confidence average | 75.0 | 77.9 | +2.9 |
| PENDING_VERIFICATION fields (universities dataset) | 160 / 1,159 (13.8%) | 198 / 1,452 (13.6%)* | see note |
| vice_chancellor filled (universities) | 0 / 61 | 54 / 66 | +54 (49 filled among RC1's 61 rows + 5 new rows arriving with this field pre-filled) |
| naac_grade filled (universities) | 13 / 61 | 46 / 66 | +33 (30 filled among RC1's 61 rows + 3 new rows arriving with this field pre-filled) |
| nirf_rank filled (universities) | 10 / 61 | 22 / 66 | +12 (11 filled among RC1's 61 rows + 1 new row arriving with this field pre-filled) |
| New columns (universities) | — | ownership (66/66), contact_details (5/66), student_services_summary (5/66) | +3 columns |

*Universities' PENDING_VERIFICATION *rate* held roughly steady because RC2 added 2 brand-new,
mostly-unpopulated columns (contact_details, student_services_summary) across all 66 rows — this
mechanically adds ~122 new PENDING_VERIFICATION cells even as existing fields got filled. The
`ownership` column, by contrast, was 100% filled on introduction. See
`reports/universities_telangana_andhra_pradesh.rc2_enrichment_report.md` for exact per-column deltas.

## Confidence & Verification Health

- 0 of 141 rows are `VST-VERIFIED` (100% `VST-NEEDS_REVIEW`) — unchanged, by design.
- Confidence scores range 58-92, average 77.9 (up from 75.0 in RC1) — still capped below
  Package001_Geography's 85-95 band since WebFetch remained blocked in RC2 (re-confirmed).
- 198 of 2,623 total fields (7.5%) are marked `PENDING_VERIFICATION` (was 161/2,315 = 7.0% in RC1;
  the rate ticked up slightly due to the 2 new mostly-unpopulated university columns, not due to any
  regression in existing fields).

## Comparison to Package001_Geography (health score 58/100)

Package002_Education RC2's 59/100 remains at parity with Package001_Geography's 58/100 on this
rubric — both share the same geo-precision and cross-government-ID gaps as primary weaknesses. RC2's
real quality gains (confidence, fill-rate, new fields) are documented in
`reports/rc1_vs_rc2_comparison.md` and are genuine improvements not captured by this specific scoring
formula.
