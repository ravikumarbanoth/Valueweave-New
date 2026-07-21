# CHANGELOG — Package003_Healthcare

## [1.0.0] — 2026-07-22 — STABLE, canonical release

Promoted RC2 to the final stable release, approved for merge to `main`. No dataset, schema, or
content changes beyond RC2 — this is a packaging finalization only (version strings bumped from
`1.0.0-RC2` to `1.0.0` across `VERSION`, `package_manifest.json`, `schema_catalog.json`,
`acquisition_backlog.json`, and all per-dataset `metadata/`, `evidence/`, and `imports/` files;
`registry/dataset_registry.csv` status values changed from `RELEASED_RC2` to `RELEASED`), per the
same convention used for Package001_Geography and Package002_Education's RC-to-stable promotions.

### Verified before promotion
- All 60 package files present per the documented folder structure.
- All JSON files parse as valid JSON.
- All 4 CSV datasets have consistent column counts, unique primary keys, and CSV column order
  matching `schema_catalog.json` (146 rows total, 0 duplicate IDs within or across datasets).
- All cross-references (metadata/evidence `*_reference` fields, registry `file_path` column, import
  manifest `file` fields) resolve correctly.
- Fixed 2 stale RC1 record-count mentions found during final review (`codex_handoff.md`,
  `docs/METHODOLOGY.md`) that had not been updated to RC2's 146-row total.

## [1.0.0-RC2] — 2026-07-22 — NOT MERGED TO MAIN

Enrichment pass on the RC1 datasets below, per explicit instruction to improve completeness,
confidence, and practical usefulness without sacrificing accuracy.

### Added
- 12 new verified records: National Board of Examinations in Medical Sciences (NBEMS), Rashtriya
  Arogya Nidhi (RAN), 4 medical colleges (GMC Sangareddy, GMC Kamareddy, GMC Ramagundam, AIIMS
  Mangalagiri), and 6 government hospitals (GGH Wanaparthy, GMC Rajanna Sircilla, GMC Nandyal, Area
  Hospital Bapatla, District Hospital Peddapalli, GMC Medak) — all explicitly flagged as RC1 gaps.
- 4 new columns on `government_hospitals_telangana_andhra_pradesh.csv`: `email`,
  `specialties_summary`, `available_services_summary`, `government_scheme_coverage_summary`.
- 3 new columns on `medical_colleges_telangana_andhra_pradesh.csv`: `email`, `departments_summary`,
  `government_scheme_coverage_summary`.
- `reports/rc1_vs_rc2_comparison.md` and 3 enrichment reports (`government_hospitals_*`,
  `medical_colleges_*`, `regulatory_bodies_and_schemes.rc2_enrichment_report.md`).

### Improved
- Confidence scores raised via stronger multi-source WebSearch corroboration (package overall
  average 82.9 → 85.8); still capped at 88 since WebFetch to `.gov.in`/`.ac.in`/Wikipedia domains was
  re-confirmed blocked (HTTP 403) live immediately before this pass began.
- 5 of 7 regulatory-body PENDING_VERIFICATION fields filled; `mbbs_seats` effectively fully filled
  for medical colleges via 2025-26 NEET-counselling data; 33 fields filled on government hospitals
  (address, contact_number, bed_capacity, emergency_services).

### Corrected / Resolved
- AP university naming split ("Dr NTR vs Dr YSR UHS") explained by a real 2019→2024
  rename-and-revert history.
- SVS Medical College affiliation corrected to KNRUHS (Telangana), fixing a real aggregator error.
- Katuri Medical College established_year (1997→2002) and Konaseema IMS&RF established_year (2005)
  resolved with stronger corroboration.
- National Dental Commission confirmed operationally active as of mid-July 2026.
- AP EHS coverage ceiling filled (Rs 2 lakh/episode).

### Notable Updates Found (developments since RC1, not corrections of RC1 errors)
- West Bengal became the 36th/final state to adopt PM-JAY — nationwide completion.
- APNMC's portal was found to be permanently migrated to a centralized INC system (NRTS), not merely
  suspended as RC1 had recorded.

### Disclosed, Not Resolved (left PENDING_VERIFICATION or flagged rather than guessed)
- TVVP/APVVP master hospital-list pages still did not surface their tabular content in WebSearch
  snippets after 2 collection passes — the single biggest structural gap in the package.
- 6 government hospital bed-count/address conflicts remain disclosed; one (Kakinada) grew more
  conflicting with additional sources rather than resolving.
- CDSCO's precise founding year and both states' NHM-unit establishment years remain unverifiable.
- CGHS beneficiary count narrowed to 47.44 lakh cited, but the underlying 42-50 lakh cross-source
  disagreement was not fully resolved.

### Known Issues
- `government_scheme_coverage_summary` remains PENDING_VERIFICATION for the majority of rows in both
  institution datasets (deliberately conservative fill — empanelment claims require a specific
  confirming source per institution).
- Package health/AI-readiness score is unchanged at 59/100 — the scoring rubric measures
  provenance/identifiers/geo/cross-gov-ID/FK-integrity, none of which this enrichment pass targeted;
  see `package_health_report.md`.
- Still 0 of 146 rows promoted to `VST-VERIFIED`.
- Still 36 of 40 briefed domains un-researched.

## [1.0.0-RC1] — 2026-07-21 — NOT MERGED TO MAIN

### Added
- `medical_regulatory_bodies_and_health_missions.csv` — 23 rows: 11 national bodies (NMC, Indian Nursing Council, Pharmacy Council of India, National Dental Commission, ICMR, CDSCO, NHM, NABH, NABL, MoHFW, NHA/PM-JAY) + 6 Telangana bodies (TSMC, TVVP, NHM-Telangana, TS Pharmacy Council, TS Nurses & Midwives Council, Rajiv Aarogyasri Trust) + 6 Andhra Pradesh bodies (APMC, APVVP, NHM-AP, AP Pharmacy Council, AP Nurses/Midwives Council, Dr. YSR Aarogyasri Trust)
- `medical_colleges_telangana_andhra_pradesh.csv` — 54 rows: 29 Telangana colleges (17 government incl. 1 ESIC-central and 1 AIIMS-autonomous, 12 private incl. 1 deemed-university-affiliated) + 25 Andhra Pradesh colleges (12 government, 13 private incl. 1 deemed-university)
- `government_hospitals_telangana_andhra_pradesh.csv` — 49 rows: 28 Telangana + 21 Andhra Pradesh, spanning 33 Teaching Hospitals, 5 District Hospitals, 11 Area Hospitals
- `government_health_insurance_schemes.csv` — 8 rows: PM-JAY, CGHS, ESIC, ECHS (national) + Rajiv Aarogyasri, NEHS (Telangana) + Dr. NTR Vaidya Seva, EHS (Andhra Pradesh)
- `schemas/schema_catalog.json` — column-level schema reference for all 4 datasets, including documented (non-enforced) cross-references between medical_colleges and government_hospitals
- `imports/import_sequence.json` and 4 per-dataset import manifests
- `evidence/*.evidence_manifest.json` — per-dataset source citation lists, including the WebFetch environment-block disclosure
- `raw_sources/*.source_inventory.md` — human-readable per-dataset source listings
- `reports/` — per-dataset collection reports, data dictionaries, and quality reports; package-level coverage, confidence-analysis, source-analysis, duplicate-analysis, district-wise-statistics, healthcare-category-statistics, government-vs-private-distribution, known-gaps, future-expansion-roadmap, and validation reports
- `docs/METHODOLOGY.md`, `docs/USAGE.md` — collection methodology (including the WebFetch environment constraint) and consumption guide
- `acquisition_backlog.json` — every one of the remaining 36 healthcare domains (of the 40 named in the package brief) and every non-TG/AP state, each marked BLOCKED or QUEUED with a specific unblock path
- `codex_handoff.md`, `integration_checklist.md`, `package_health_report.md`, top-level `validation_report.md` — release-management artifacts

### Scope Decision
- RC1 deliberately covers 4 of the 40 named healthcare data domains (Medical Regulatory Bodies & Health Missions, Medical Colleges, Government Hospitals, Government Health Insurance Schemes), scoped to Telangana, Andhra Pradesh, and genuinely national-level entities — directly following this package's own brief instruction to "prioritize depth, accuracy and verification over maximum coverage."

### Environment Constraint Disclosed
- This session's organizational egress proxy blocked direct WebFetch to `.gov.in`, `.ac.in`, `.edu.in`, and Wikipedia domains (confirmed HTTP 403 policy denial, re-tested live immediately before collection began) for the entire collection period — same constraint documented in Package001_Geography and Package002_Education. All 134 rows in this release were sourced via WebSearch result snippets rather than direct page fetch. Confidence scores were capped at 88; every row starts at `verification_status: VST-NEEDS_REVIEW`; no row has been promoted to verified.

### Corrected / Time-Sensitive Findings
- **Dental Council of India → National Dental Commission**: DCI was dissolved and replaced effective 19 March 2026 — only ~4 months before this research date. Still operating on the legacy `dciindia.gov.in` domain at collection time; recorded under its new name with the transition noted.
- **Andhra Pradesh health insurance scheme renames**: the state's flagship BPL scheme has been renamed across recent government transitions, most recently Dr. YSR Aarogyasri → Dr. NTR Vaidya Seva (July 2024, TDP-NDA coalition). Dataset uses the current name with prior names cross-referenced in `notes`.
- **Telangana NEHS relaunch**: Telangana's employee health scheme was relaunched as NEHS under a new "Employees Health Care Trust" on 17 July 2026 — only 4 days before this collection date. Confidence deliberately capped lower on this row given how recent the change is.
- **CGHS domain migration**: `cghs.gov.in` was deactivated in April 2025; `cghs.mohfw.gov.in` is now canonical. Flagged during research to avoid citing a dead domain.

### Known Issues
- TVVP's (Telangana) and APVVP's (Andhra Pradesh) own master hospital-list pages exist but their tabular contents did not surface in WebSearch snippets — only aggregate counts (~175 TVVP hospitals, ~228 APVVP hospitals) were found. This dataset's 49 rows are a verified subset, not the full state rosters.
- ~17-19 of Telangana's newer (2022-2023) government medical colleges and several Andhra Pradesh colleges were excluded rather than guessed.
- `bed_capacity` and `contact_number` are `PENDING_VERIFICATION` for many government hospital rows; where sources disagreed on bed counts (e.g. King George Hospital Visakhapatnam: 1037 vs 1562 vs 2000), the conflict is recorded rather than silently resolved.
- `mbbs_seats` is `PENDING_VERIFICATION` for most medical college rows.
- No dataset in this release has any row promoted to `VST-VERIFIED`.
- 215 of 2,443 total fields (8.8%) across the package are marked `PENDING_VERIFICATION`.

### Future Work
- See `reports/future_expansion_roadmap.md` for the full 10-item roadmap: re-verification with restored WebFetch, unlocking TVVP/APVVP full rosters, filling missing medical colleges, adding PHCs/CHCs/UHCs via bulk source, expanding to specialty hospital and service-infrastructure domains, adding programme/campaign domains, extending geographic coverage, populating descoped fields, and evaluating cross-package FK wiring.
