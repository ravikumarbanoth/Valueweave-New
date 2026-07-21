# CHANGELOG — Package002_Education

## [1.0.0-RC2] — 2026-07-22 — NOT MERGED TO MAIN

Enrichment pass on the RC1 datasets below, per an explicit instruction to treat the prior release as
Release Candidate 1 and improve data quality before any promotion decision. This is a data-quality
release, not a domain-expansion release — still 4 of the 40 briefed domains.

### Added
- 6 new verified records: 5 universities (National Sanskrit University Tirupati, SVIMS Tirupati,
  RGUKT RK Valley, RGUKT Srikakulam, RGUKT Ongole — the RGUKT campuses were explicitly named as gaps
  in the RC1 collection report) and 1 entrance exam (NEET SS, excluded from RC1 only for row-count
  reasons).
- 3 new columns on `universities_telangana_andhra_pradesh.csv`: `ownership` (filled for all 66 rows),
  `contact_details` (filled for 5 flagship universities), `student_services_summary` (filled for the
  same 5 flagship universities).
- `reports/universities_telangana_andhra_pradesh.rc2_enrichment_report.md`,
  `reports/boards_exams_scholarships.rc2_enrichment_report.md`, and
  `reports/rc1_vs_rc2_comparison.md` — full enrichment methodology and RC1-vs-RC2 diff.

### Improved
- Confidence scores raised via stronger multi-source WebSearch corroboration (package overall average
  75.0 → 77.9); still capped below the 85-95 "direct fetch" band since WebFetch to `.gov.in`/`.ac.in`/
  Wikipedia domains was re-confirmed blocked (HTTP 403) before this pass began.
- `vice_chancellor` filled for 49 of RC1's 61 university rows (was 0), `naac_grade` for 30 additional
  rows, `nirf_rank` for 11 additional rows.
- APSCHE `headquarters_city` (the sole RC1 PENDING_VERIFICATION field outside universities) resolved
  to Mangalagiri, Guntur District.

### Corrected / Resolved
- GATE 2027 host institute confirmed (IIT Madras, official notification 20-Jul-2026).
- AP ICET conducting body/domain corroborated.
- NOS overseas maintenance figures, NFST JRF/SRF stipend rate confirmed; NFSC/NFST/NFPwD stipend
  "inconsistency" identified as three genuinely different current pay scales rather than stale data.
- Telangana overseas scholarships' ₹5L ceiling and AP NTR Videshi Vidyadharana's ₹6L ceiling confirmed.
- Kakatiya University NAAC grade (A → A+), BRAOU NAAC grade (A/3.12), Sri Venkateswara University VC
  vacancy (Dr. Tata Narasinga Rao appointed) — all resolved with multi-source corroboration.

### Disclosed, Not Resolved (left PENDING_VERIFICATION rather than guessed)
- BSEAP founding year (1953 vs 1969), AP Ambedkar Overseas Vidya Nidhi and NTR Vidyonnathi income
  ceilings, Krishna University NAAC grade (A++ vs B), Acharya Nagarjuna University and NIT Andhra
  Pradesh leadership (a likely search conflation with IIT Hyderabad's director was explicitly
  identified and rejected rather than adopted).
- **KL University integrity note**: its Vice-Chancellor was reportedly arrested in a CBI probe into
  alleged NAAC-inspector bribery. NAAC grade retained (not removed on the basis of an unrelated
  controversy) but flagged in `notes`; confidence raised only modestly.

### Known Issues (see `reports/rc1_vs_rc2_comparison.md` for full detail)
- `contact_details`/`student_services_summary` remain PENDING_VERIFICATION for 61 of 66 university
  rows.
- Package health/AI-readiness score is unchanged at 59/100 — the scoring rubric measures
  provenance/identifiers/geo/cross-gov-ID/FK-integrity, none of which this enrichment pass targeted;
  see `package_health_report.md` for why the real quality gains above don't move that number.
- Still 0 of 141 rows promoted to `VST-VERIFIED`.
- Still 36 of 40 briefed domains un-researched.

## [1.0.0] — 2026-07-21 (retroactively RC1)

### Added
- `education_boards_regulatory_bodies.csv` — 21 rows: 13 national bodies (UGC, AICTE, NCTE, NCVET, NCERT, NIOS, CBSE, CISCE, NTA, NAAC, NBA, NIRF, AISHE) + 4 Telangana bodies (SCERT-TG, BSE Telangana, TSBIE, TSCHE) + 4 Andhra Pradesh bodies (SCERT-AP, BSEAP, BIEAP, APSCHE)
- `universities_telangana_andhra_pradesh.csv` — 61 rows: 29 Telangana universities (15 state, 3 central, 3 deemed, 6 private, 2 Institute of National Importance), 32 Andhra Pradesh universities (21 state, 2 central, 4 deemed, 2 private, 3 Institute of National Importance)
- `entrance_exams.csv` — 28 rows: 14 national exams (JEE Main/Advanced, NEET UG/PG, CUET UG/PG, CLAT, CAT, GATE, UGC NET, CTET, XAT, ICAR AIEEA-PG, GPAT) + 14 Telangana/Andhra Pradesh state exams (EAPCET, ICET, EdCET, PGECET, LAWCET, PGLCET, POLYCET families)
- `scholarships.csv` — 25 rows: 15 central schemes + 5 Telangana schemes + 5 Andhra Pradesh schemes
- `schemas/schema_catalog.json` — column-level schema reference for all 4 datasets
- `imports/import_sequence.json` and 4 per-dataset import manifests
- `evidence/*.evidence_manifest.json` — per-dataset source citation lists, including the WebFetch environment-block disclosure
- `raw_sources/*.source_inventory.md` — human-readable per-dataset source listings
- `reports/` — per-dataset collection reports, data dictionaries, and quality reports; package-level coverage, missing-data, duplicate-analysis, source-analysis, confidence-analysis, state-wise-statistics, institution-wise-statistics, and validation reports
- `docs/METHODOLOGY.md`, `docs/USAGE.md` — collection methodology (including the WebFetch environment constraint) and consumption guide
- `acquisition_backlog.json` — every one of the remaining 36 education domains (of the 40 named in the package brief) and every non-TG/AP state, each marked BLOCKED or QUEUED with a specific unblock path
- `codex_handoff.md`, `integration_checklist.md`, `package_health_report.md` — release-management artifacts

### Scope Decision
- v1.0.0 deliberately covers 4 of the 40 named education data domains (Boards & Regulatory Bodies, Universities, Entrance Exams, Scholarships), scoped to Telangana, Andhra Pradesh, and genuinely national-level entities. This scope was set explicitly with the requester before collection began, to keep the release real-data-only rather than attempting full nationwide 40-domain breadth at the cost of fabrication or unverifiable placeholder rows.

### Environment Constraint Disclosed
- This session's organizational egress proxy blocked direct WebFetch to `.gov.in`, `.ac.in`, `.edu.in`, and Wikipedia domains (confirmed HTTP 403 policy denial, not a retriable error) for the entire collection period. All 135 rows in this release were sourced via WebSearch result snippets rather than direct page fetch. Confidence scores were capped accordingly (58-92 range, versus Package001_Geography's 85-95 band); every row starts at `verification_status: VST-NEEDS_REVIEW`; no row has been promoted to verified.

### Corrected
- **Andhra Pradesh scholarship scheme names**: several state schemes were renamed under GO No. 4 (18-Jun-2024) following a change of state government (e.g. "Jagananna Vidya Deevena" → "Post Matric Scholarship (RTF)", "Jagananna Vasathi Deevena" → "Post Matric Scholarship (MTF)"). The dataset uses current official names with prior names cross-referenced in `notes`, since some third-party aggregators still display the superseded branding.
- **GPAT conducting body**: transferred from NTA to NBEMS in 2024; dataset reflects the current conducting body.

### Known Issues
- `vice_chancellor` is `PENDING_VERIFICATION` for all 61 university rows by design (not systematically searched, given appointment volatility).
- `naac_grade`/`nirf_rank` populated only where a clearly-dated source was found; several rows carry `PENDING_VERIFICATION`.
- No dataset in this release has any row promoted to `VST-VERIFIED`.
- 161 of 2,315 total fields (7.0%) across the package are marked `PENDING_VERIFICATION`.

### Future Work
- Re-verify all rows once direct WebFetch access to government/institution domains is available in a future session, promoting confirmed rows to `VST-VERIFIED`.
- Expand to the remaining 36 education domains and to states/UTs beyond Telangana & Andhra Pradesh, per `acquisition_backlog.json`.
- Populate `vice_chancellor`, `naac_grade`, and `nirf_rank` via a dedicated bulk-source pass.
- Evaluate wiring `state`/`jurisdiction` fields to Package001_Geography's `district_id` once a defensible per-institution district mapping is verified.
