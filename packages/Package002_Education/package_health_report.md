# Package Health Report — Package002_Education v1.0.0

## Scoring Methodology (mirrors Package001_Geography)

Weighted components, 0-100 scale:

| Component | Weight | Score | Basis |
|---|---|---|---|
| Provenance completeness | 30% | 100 | Every row across all 4 datasets has data_source, source_url, confidence_score, verification_status, and collection_date populated |
| Stable identifiers | 20% | 70 | UUID primary keys are 100% present and unique; unlike Package001_Geography, no separate immutable ref-code system exists yet for cross-package linking |
| Geo-precision (lat/long) | 20% | 0 | Not collected in this release — known gap, see docs/METHODOLOGY.md |
| Cross-government-ID linkage | 15% | 0 | No AISHE/UDISE/UGC institution codes captured per-row in this release |
| FK integrity where data exists | 15% | 100 | No inter-dataset FKs declared in v1.0.0, so none can be broken; schema_catalog.json documents this as a deliberate absence, not an unverified claim |

**Computed score: 0.30(100) + 0.20(70) + 0.20(0) + 0.15(0) + 0.15(100) = 59.0 → 59/100**

## AI Readiness Score

Same methodology as above (this package reuses Package001_Geography's AI-readiness formula):
provenance (30%) + stable identifiers (20%) + geo-precision (20%) + cross-gov-ID linkage (15%) +
FK integrity (15%).

**Score: 59/100**

Interpretation: the package is structurally AI-consumable — every fact is traceable to a specific
source URL, confidence score, and review status, and an AI system can reliably distinguish "known,
moderately confident" from "explicitly unknown" (`PENDING_VERIFICATION`) — but it is missing the
geo-spatial layer and cross-government-ID layer needed to plug into external GIS or UDISE/AISHE-keyed
systems, and (unlike Package001_Geography) does not yet have an immutable ref-code scheme for
cross-package joins.

## Component Detail

### Provenance completeness: 100%
All 135 rows across 4 datasets carry `data_source`, `source_url`, `collection_date`,
`confidence_score`, and `verification_status`. Verified programmatically at build time (see
`reports/validation_report.md`).

### Stable identifiers: 70%
UUIDv4 `id` is present and unique in all 4 datasets (verified — see `reports/duplicate_analysis.md`).
Deducted 30 points versus a hypothetical 100 because there is no secondary immutable reference code
(e.g. an AISHE institution code) that would survive a UUID regeneration or dataset rebuild.

### Geo-precision: 0%
No dataset in this release includes latitude/longitude. This is a known, disclosed gap (see
`package_manifest.json` known_gaps and `docs/METHODOLOGY.md`), not a silent omission.

### Cross-government-ID linkage: 0%
No row carries an AISHE code, UDISE code, or UGC institution ID. Same disclosure status as
geo-precision.

### FK integrity: 100% (of what exists)
`schemas/schema_catalog.json` declares zero foreign keys for v1.0.0's 4 datasets — this is accurate,
not aspirational, so there is nothing to be broken. Once cross-dataset or cross-package FKs are
introduced in a future release, this component's basis will need re-evaluation.

## Confidence & Verification Health

- 0 of 135 rows are `VST-VERIFIED` (100% `VST-NEEDS_REVIEW`) — by design, per package governance
  policy (see `integration_checklist.md` item 6).
- Confidence scores range 58-92, average 75.0 — capped below Package001_Geography's 85-95 band due to
  this session's WebFetch environment restriction (see `docs/METHODOLOGY.md`).
- 161 of 2,315 total fields (7.0%) are marked `PENDING_VERIFICATION`.

## Comparison to Package001_Geography (health score 58/100)

Package002_Education's 59/100 is essentially at parity with Package001_Geography's 58/100 — both
packages score well on provenance and identifier hygiene, and both share the same geo-precision and
cross-government-ID gaps as their primary weaknesses. This package additionally lacks Package001's
immutable ref-code layer, offset by not yet having any FK relationships that could be broken.
