# Package003_Healthcare — RC1 vs RC2 Comparison

RC1: 2026-07-21 (initial collection). RC2: 2026-07-22 (enrichment pass). Neither has been merged to
`main` at the time RC2 was produced — this comparison exists to inform the promotion decision.

## 1. New Records Added

| Dataset | RC1 | RC2 | New Records |
|---|---|---|---|
| medical_regulatory_bodies_and_health_missions | 23 | 24 | **1** |
| medical_colleges_telangana_andhra_pradesh | 54 | 58 | **4** |
| government_hospitals_telangana_andhra_pradesh | 49 | 55 | **6** |
| government_health_insurance_schemes | 8 | 9 | **1** |
| **Total** | **134** | **146** | **12** |

New rows added (all newly-verified, not padding):
- **National Board of Examinations in Medical Sciences (NBEMS)**, est. 1975 — a genuine MoHFW body missed in RC1
- **Rashtriya Arogya Nidhi (RAN)**, est. 1997 — a genuine MoHFW financial-assistance scheme missed in RC1
- **GMC Sangareddy, GMC Kamareddy, GMC Ramagundam** (Telangana government medical colleges) and **AIIMS Mangalagiri** (Andhra Pradesh) — all explicitly flagged as gaps in the RC1 collection report, now individually verified
- **GGH Wanaparthy, GMC Rajanna Sircilla, GMC Nandyal, Area Hospital Bapatla, District Hospital Peddapalli, GMC Medak** — government hospitals in districts flagged as RC1 gaps

## 2. Fields Enriched

### New columns added
| Dataset | New Columns | Fill Rate |
|---|---|---|
| government_hospitals_telangana_andhra_pradesh | email, specialties_summary, available_services_summary, government_scheme_coverage_summary | email 17/55, specialties 17/55, services 25/55, scheme coverage 10/55 |
| medical_colleges_telangana_andhra_pradesh | email, departments_summary, government_scheme_coverage_summary | email 12/58, departments 26/58, scheme coverage 34/58 |

Fill rates are deliberately conservative, especially `government_scheme_coverage_summary` — the
enrichment agents required a specific confirming source per institution rather than assuming
government facilities in these states universally accept the state Aarogyasri-family scheme.

### Existing PENDING_VERIFICATION fields filled
| Dataset | Fields Filled |
|---|---|
| medical_regulatory_bodies_and_health_missions | 5 of 7: Telangana Pharmacy Council established_year (2015), AP Pharmacy Council established_year (1959), Telangana Aarogyasri Trust established_year (2014), AP Nurses Council headquarters_city (Vijayawada). CDSCO's founding year and both states' NHM-unit establishment years remain unverifiable. |
| medical_colleges_telangana_andhra_pradesh | `mbbs_seats` effectively fully filled via 2025-26 NEET-counselling data; both remaining `established_year` gaps closed (Fathima Institute 2010, Great Eastern 2010) |
| government_hospitals_telangana_andhra_pradesh | 33 fields: address (10), contact_number (12), bed_capacity (7), emergency_services (4). `official_website` had 0 new fills — no lead was corroborated enough to trust. |
| government_health_insurance_schemes | AP EHS coverage ceiling (Rs 2 lakh/episode); ECHS contribution partially resolved (~Rs 30k-1.2 lakh by rank tier); CGHS beneficiary count narrowed to 47.44 lakh cited (not fully resolved against the 42-50 lakh range) |

## 3. Confidence Improvements

| Dataset | RC1 Avg | RC2 Avg | Delta | RC1 Range | RC2 Range |
|---|---|---|---|---|---|
| medical_regulatory_bodies_and_health_missions | 82.3 | 84.1 | +1.8 | 80-85 | 81-88 |
| medical_colleges_telangana_andhra_pradesh | 84.0 | 87.1 | +3.1 | 73-88 | 80-88 |
| government_hospitals_telangana_andhra_pradesh | 82.0 | 85.1 | +3.1 | 78-85 | 78-88 |
| government_health_insurance_schemes | 83.1 | 85.6 | +2.5 | 80-85 | 82-88 |
| **Package overall** | **82.9** | **85.8** | **+2.9** | 73-88 | 78-88 |

No row in either RC1 or RC2 exceeds a confidence score of 88, since WebFetch to `.gov.in`/`.ac.in`/
Wikipedia domains remained blocked in both passes (re-confirmed via a live test fetch immediately
before RC2 enrichment began). The improvement reflects stronger multi-source WebSearch corroboration,
not a change in fetch method.

## 4. Conflicts Resolved in RC2

- **AP university naming split**: "Dr NTR vs Dr YSR University of Health Sciences" explained by a
  real 2019→2024 rename-and-revert history across ~10 affected college rows.
- **SVS Medical College affiliation**: corrected to KNRUHS (Telangana), fixing a real aggregator error
  that had it affiliated to an Andhra Pradesh university.
- **Katuri Medical College established_year**: 1997 → 2002 on preponderance of current evidence.
- **Konaseema IMS&RF established_year**: 2005 confirmed with much stronger corroboration.
- **Sri Venkateswara** and other regulatory established-year conflicts: resolved where clearer sources
  were found (see per-dataset RC2 enrichment reports for full detail).
- **National Dental Commission**: confirmed operationally active as of mid-July 2026 (RC1 had only
  caught the 19 March 2026 dissolution/replacement notification).

## 5. Conflicts Explicitly NOT Resolved (left disclosed, not guessed)

- **TVVP/APVVP master hospital-list pages**: still did not surface their tabular content in
  WebSearch snippets after 2 collection passes — the single biggest structural gap in the package.
- **6 government hospital bed-count/address conflicts**: remain disclosed in `notes` rather than
  silently resolved; Kakinada's bed-count conflict actually grew *more* conflicting with additional
  RC2 sources (now 4 disagreeing figures) rather than resolving.
- **CDSCO precise founding year, both states' NHM-unit establishment years**: genuinely unverifiable
  after 2 passes.
- **CGHS beneficiary count**: narrowed to a most-cited 47.44 lakh figure, but the underlying 42-50
  lakh disagreement across sources was not fully resolved.

## 6. Notable Updates Found During RC2 (developments since RC1, not corrections of RC1 errors)

- **West Bengal adopted PM-JAY**, becoming the 36th/final state — nationwide completion, a genuine
  development missed in RC1 collection.
- **APNMC's portal** was found to be permanently migrated to a centralized INC system (NRTS), not
  merely "suspended" as RC1 had recorded — a correction based on newer information, not a RC1 error.

## 7. Source Statistics

| Metric | RC1 | RC2 | Delta |
|---|---|---|---|
| Total distinct source URLs | 128 | 140 | +12 |
| Total records | 134 | 146 | +12 |
| Total columns across datasets | 70 | 77 | +7 |
| Total fields | 2,443 | 3,063 | +620 |
| PENDING_VERIFICATION fields | 215 (8.8%) | 374 (12.2%) | +159 (rate rose due to 7 new partially-filled columns, not regression in existing fields) |

## 8. Remaining Gaps After RC2

- 36 of 40 briefed healthcare domains remain entirely un-researched (BLOCKED/QUEUED in
  `acquisition_backlog.json`), unchanged from RC1.
- `government_scheme_coverage_summary` remains PENDING_VERIFICATION for the majority of rows in both
  institution datasets (deliberately conservative fill).
- No row in the package (0 of 146) has been promoted to `VST-VERIFIED`.
- Field depth per entity is still short of the ~30 fields named in the original brief (lat/long,
  Google Maps links, ICU/dialysis availability, working hours remain unaddressed).
- Latitude/longitude remains 0% populated package-wide.
- TVVP/APVVP full rosters, the CDSCO/NHM establishment-year gaps, and the CGHS beneficiary-count
  disagreement remain open after 2 collection passes.

## 9. Recommendation Inputs for the Merge Decision

RC2 improved confidence (+2.9 avg), added 12 new verified records, filled dozens of previously-pending
fields, introduced 7 new columns with real (if partial) population, and resolved 6 source conflicts
while explicitly declining to guess on several more. It did not change the package's structural
health/AI-readiness score (59/100, see `package_health_report.md`), since that rubric measures
provenance/identifiers/geo/cross-gov-ID/FK-integrity — none of which RC2 targeted. This is the same
outcome pattern observed in Package002_Education's RC1→RC2 promotion.
