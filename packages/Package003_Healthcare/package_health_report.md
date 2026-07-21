# Package Health Report — Package003_Healthcare v1.0.0-RC1

## Scoring Methodology (mirrors Package001_Geography and Package002_Education)

Weighted components, 0-100 scale:

| Component | Weight | Score | Basis |
|---|---|---|---|
| Provenance completeness | 30% | 100 | Every row across all 4 datasets has data_source, source_url, confidence_score, verification_status, and collection_date populated |
| Stable identifiers | 20% | 70 | UUID primary keys are 100% present and unique (134 rows, 0 duplicates within or across datasets); no separate immutable ref-code system for cross-package linking |
| Geo-precision (lat/long) | 20% | 0 | Not collected in this release — known gap, see docs/METHODOLOGY.md |
| Cross-government-ID linkage | 15% | 0 | No NMC/NABH/NABL facility codes captured per-row in this release |
| FK integrity where data exists | 15% | 100 | No inter-dataset FKs declared; the two free-text cross-references (attached_teaching_hospital / medical_college_affiliation) are explicitly documented as non-enforced in schema_catalog.json, so nothing unverified is silently claimed |

**Computed score: 0.30(100) + 0.20(70) + 0.20(0) + 0.15(0) + 0.15(100) = 59.0 → 59/100**

This lands at parity with Package001_Geography (58/100) and Package002_Education (59/100), for the
same underlying reason: strong provenance and identifier hygiene, offset by the same two structural
gaps (geo-precision, cross-government-ID linkage) common to all three packages so far.

## AI Readiness Score

Same methodology and weighting as above.

**Score: 59/100**

Interpretation: the package is structurally AI-consumable — every fact is traceable to a specific
source URL, confidence score, and review status, and an AI system can reliably distinguish "known,
moderately confident" from "explicitly unknown" (`PENDING_VERIFICATION`) — but it is missing the
geo-spatial layer and cross-government-ID layer (NMC/NABH/NABL codes) needed to plug into external
GIS or facility-registry-keyed systems.

## Component Detail

### Provenance completeness: 100%
All 134 rows across 4 datasets carry `data_source`, `source_url`, `collection_date`,
`confidence_score`, and `verification_status`. Verified programmatically — see `reports/validation_report.md`.

### Stable identifiers: 70%
UUIDv4 `id` is present and unique in all 4 datasets and across the package (verified — see
`reports/duplicate_analysis.md`). Deducted 30 points because there is no secondary immutable
reference code (e.g. an NMC or NABH facility ID) that would survive a UUID regeneration.

### Geo-precision: 0%
No dataset in this release includes latitude/longitude. Known, disclosed gap (see
`package_manifest.json` known_gaps and `docs/METHODOLOGY.md`).

### Cross-government-ID linkage: 0%
No row carries an NMC college code, NABH/NABL accreditation ID, or facility registry code. Same
disclosure status as geo-precision.

### FK integrity: 100% (of what exists)
`schemas/schema_catalog.json` declares zero enforced foreign keys for RC1's 4 datasets, and
explicitly documents the two free-text cross-references between medical_colleges and
government_hospitals as non-enforced — this is accurate, not aspirational.

## Confidence & Verification Health

- 0 of 134 rows are `VST-VERIFIED` (100% `VST-NEEDS_REVIEW`) — by design, per package governance
  policy (see `integration_checklist.md` item 6).
- Confidence scores range 73-88, average 82.9 — capped below a hypothetical 90+ "direct fetch" band
  due to this session's WebFetch environment restriction (see `docs/METHODOLOGY.md`).
- 215 of 2,443 total fields (8.8%) are marked `PENDING_VERIFICATION`.

## Comparison to Package001_Geography (58/100) and Package002_Education (59/100)

Package003_Healthcare's 59/100 is consistent with both prior packages on this rubric. All three share
the same geo-precision and cross-government-ID gaps as primary weaknesses, reflecting a structural
limitation of this session's environment (no direct fetch access) rather than a package-specific
quality issue.
