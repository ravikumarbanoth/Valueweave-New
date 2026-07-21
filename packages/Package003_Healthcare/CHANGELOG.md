# CHANGELOG — Package003_Healthcare

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
