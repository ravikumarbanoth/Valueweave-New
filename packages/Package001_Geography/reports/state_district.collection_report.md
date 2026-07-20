# ValueWeave Data Collection Report
## Dataset: `state.csv` + `district.csv` — Telangana & Andhra Pradesh
**Layer:** I — District Intelligent Digital Infrastructure · **Collection Profile:** P1 (Government Registry & Statistical Source)
**Collection Date:** 2026-07-18 · **Batch:** `vw-batch-2026-07-18-state-district-tg-ap` · **Version:** 1.0.0-draft

**Scoping note:** This run covers the two foundational datasets every other ValueWeave dataset geographically anchors to — the logical Phase 1 starting point per the Implementation Roadmap. Treat this as the first execution of the Data Collection Engine; subsequent messages can direct it at the next dataset (e.g., Industry, Skill, Company) using the identical 8-stage workflow below.

---

## 1. Research Summary

Telangana's district structure is stable and well-documented: **33 districts**, unchanged since the last two districts (Mulugu, Narayanpet) were carved out on 17 February 2019. The Telangana State Portal and a Wikipedia table citing it (in turn sourced from the 2011 Census and the state government) together give a clean, internally consistent picture.

Andhra Pradesh's district structure is **not stable** and required active conflict resolution (see Section 9): the state moved from 13 → 26 districts in April 2022, and — critically — from 26 → **28 districts** on 31 December 2025, with two new districts (Polavaram, carved from Alluri Sitharama Raju; Markapuram, carved from Prakasam) created by the Chandrababu Naidu-led Cabinet's December 2025 reorganisation. Several sources still in general circulation report the now-superseded 26-district figure. The source table itself carries an explicit editorial caveat that area/population statistics for the reorganised districts are "to be updated/verified" — meaning this dataset is being collected in the middle of an active administrative transition, not after it has settled.

## 2. Official Sources Used

| Source | Used For |
|---|---|
| Telangana State Portal (telangana.gov.in) | Telangana district list, headquarters |
| Census of India 2011 | Population, literacy %, urban %, sex ratio (Telangana) |
| AP Districts (Formation) Act, 1974 — 2022 notification and December 2025 Cabinet-approved amendment | Andhra Pradesh district list, government-assigned district codes, headquarters, revenue divisions |
| AP Directorate of Economics & Statistics — Socio-Economic Survey 2022–23 | Population, area (Andhra Pradesh, pre-Dec-2025-split boundaries) |

## 3. Secondary Sources Used

| Source | Role |
|---|---|
| Wikipedia — "List of districts of Telangana" and "List of districts of Andhra Pradesh" | Structured-table compilation of the official sources above; retrieval mechanism, not an independent authority — every figure traces to a footnoted official citation |
| The News Minute, Deccan Chronicle, tmv.in (news coverage, Dec 2025–Jan 2026) | Corroboration that the 28-district reorganisation is genuinely in effect and not a draft/proposal |

## 4. Source Reliability Score

| Source | Reliability (0–100) | Basis |
|---|---|---|
| Telangana State Portal | 95 | Primary government source, directly authoritative |
| Census of India 2011 | 95 | Primary government statistical source (dated but authoritative for its year) |
| AP Districts (Formation) Act notifications | 88 | Primary legal instrument, but accessed via secondary compilation in this pass rather than the gazette PDF directly |
| AP Socio-Economic Survey 2022-23 | 85 | Primary government statistical source, but pre-dates the Dec-2025 boundary change |
| Wikipedia compilations | 78 | Well-footnoted tertiary source; used for speed, flagged for primary-source confirmation |
| News coverage (Dec 2025 reorg) | 75 | Standard journalistic sourcing, multiple independent outlets agree |

## 5. Collection Method

**Web Portal** (Telangana State Portal, direct reference) + **Government Portal / Notification** (AP Districts Formation Act text, referenced via compilation) + **Manual Research** (cross-referencing multiple sources to resolve the 26-vs-28 and duplicate-code conflicts below). No API or bulk CSV/PDF download was available/used in this pass — see Section 11, Review Item 1, for the recommended follow-up using LGD's actual bulk API/download.

## 6. Cleaning Steps

- Standardized district name spellings against the government-portal form (e.g., "Bhadradri Kothagudem" not "Kothagudem district").
- Converted all population/area/density figures from source formatting (Indian numeral grouping, e.g. "21,91,471") into plain integers.
- Removed footnote markers and citation brackets from all extracted text values.
- Where a source cell was blank (Polavaram's area/density), preserved as an explicit missing value rather than inferring or interpolating one.

## 7. Standardization Steps

- Applied the ValueWeave Coding Standard (Part 0.3 of the Master Lookup Tables document): `{STATE}-{3-letter mnemonic}` for `dist_ref`.
- For Andhra Pradesh, adopted the **government's own** 3-letter district codes as the mnemonic wherever unique (e.g., `AP-SRI`, `AP-GUN`) rather than inventing new ones — preserving traceability to the official source.
- For Telangana, no official 3-letter code table was located in this pass, so ValueWeave assigned mnemonics (e.g., `TG-MDK` for Medak, `TG-HYD` for Hyderabad) — flagged in Section 11 for confirmation against Telangana's own RTO/administrative code conventions if one exists.
- Every non-verifiable field was set to the literal sentinel `PENDING_VERIFICATION` (or `PENDING_GEOCODING` for coordinates) rather than left blank or estimated — this is a deliberate, greppable marker so no downstream system can mistake an unverified field for a confirmed zero/empty value.
- `district_readiness_score` was explicitly **not** populated — per the Governance Framework, this is a Profile P5 (AI-derived) field and must never be hand-populated during a collection pass.

## 8. Validation Rules Applied

- **Uniqueness:** All 61 `dist_ref` values confirmed programmatically unique (validated post-generation — see Section 12).
- **Referential integrity:** Every district row's `st_id` value matches a `st_id` generated in `state.csv` (2 of 2 states resolve correctly).
- **Duplicate detection:** Caught and resolved a source-level duplicate (AP government code "ANA" used for two different districts — see Section 9).
- **Mandatory fields:** `district_name`, `st_id`, `district_headquarters` populated for all 61 rows with zero nulls.
- **Lookup validation:** N/A for this dataset — District does not reference any of the 61 lookup tables directly (it is itself referenced by other entities' lookups).

## 9. Conflicts Identified, Compared, and Resolved

### Conflict 1 — Andhra Pradesh district count (26 vs. 28)
- **Sources in disagreement:** Most pre-2026 web content (Rau's IAS, Testbook, Brainly, several GK sites) states 26 districts. Wikipedia's current table and December 2025/January 2026 news coverage (The News Minute, Deccan Chronicle) state 28.
- **Explanation:** The 26-district figure was correct from April 2022 until 31 December 2025. On 29 December 2025 the AP Cabinet (under CM N. Chandrababu Naidu) approved creating two new districts — Polavaram (from Alluri Sitharama Raju) and Markapuram (from Prakasam) — effective 31 December 2025.
- **Recommended authoritative source:** The AP Cabinet decision and its implementing gazette notification (effective 31 Dec 2025), corroborated by contemporaneous, independent news reporting.
- **Decision documented:** This dataset uses **28** as the current district count for Andhra Pradesh. The 26-district sources are not wrong for their own time — they are simply superseded, and this should not be read as those sources being unreliable in general.

### Conflict 2 — Duplicate government district code "ANA"
- **Sources in disagreement:** N/A (single source, internal inconsistency) — the compiled table assigns code "ANA" to both Anakapalli (district #6) and Ananthapuramu (district #23).
- **Explanation:** Almost certainly a transcription artifact in the secondary compilation, since Anantapur's long-standing conventional abbreviation in AP administrative usage is "ATP," not "ANA."
- **Recommended authoritative source:** The AP government's own district-code gazette notification — **not yet directly fetched in this pass** (flagged as Review Item 2, Section 11).
- **Decision documented:** ValueWeave assigns `AP-ANK` (Anakapalli) and `AP-ATP` (Ananthapuramu) to preserve the coding standard's uniqueness requirement, pending direct primary-source confirmation.

## 10. Missing Data Report

| Field | Rows Affected | Status |
|---|---|---|
| `lgd_state_code`, `lgd_district_code` | All 63 (2 states + 61 districts) | Not retrieved in this pass — requires a dedicated LGD bulk-download (Government Portal/CSV Download method), not manual research |
| `latitude`, `longitude` | All 61 districts | Not populated — flagged for automated batch geocoding (Nominatim/Bhuvan), not manual estimation, to avoid introducing imprecise coordinates into a Tier-1 dataset |
| `district_gdp_inr_cr` | All 61 districts | No official district-level GSDP-equivalent series was located in this pass |
| `primary_industry_sector_id` | All 61 districts | Requires either a dedicated district economic-profile research pass or field-survey input — cannot be responsibly inferred from the sources used here |
| `area_sq_km`, `density_per_sq_km` | Polavaram only (1 district) | Not yet published by the source; explicitly flagged rather than estimated |
| `urban_pct`, `literacy_rate_pct`, `sex_ratio` | All 28 Andhra Pradesh districts | The AP source table used did not include these fields (unlike the Telangana table) — requires a supplementary AP Census/Socio-Economic Survey pull |
| `industrial_policy_name` (state-level) | Andhra Pradesh (1 row) | Not confirmed in this pass |
| `state_gdp_inr_cr` | Both states | Not confirmed in this pass |

## 11. Recommended Review Items (priority order)

1. **Directly fetch the LGD (Local Government Directory) bulk district/state code download** rather than relying on secondary compilations — this single action resolves the largest missing-data category and gives ValueWeave a government-verified crosswalk code for every record.
2. **Directly fetch the AP government's district-code gazette notification** to resolve the ANA/ANA duplicate with primary-source certainty (currently resolved by reasonable inference, not confirmed).
3. **Run automated batch geocoding** (OpenStreetMap Nominatim or ISRO Bhuvan) for all 61 district headquarters — do not hand-estimate coordinates.
4. **Re-pull AP population/area statistics** once the state's Directorate of Economics & Statistics publishes updated figures reflecting the Polavaram/Markapuram split (the source itself flags this as pending).
5. **Confirm the license terms** for telangana.gov.in and the AP government notification sources directly (see Governance Framework Part 5) before this data is treated as freely redistributable within any ValueWeave-published derivative.
6. Given the Overall Confidence scores in `metadata.json`, **hold the Andhra Pradesh district batch at `VST-NEEDS_REVIEW`** (average confidence 73.75, below the 85 Tier-1 threshold) while the Telangana batch (88 average) is closer to promotion-ready pending only the LGD/geocoding items above.

## 12. Confidence Score (summary — full detail in `metadata.json`)

| Dataset | Confidence Score | Notes |
|---|---|---|
| `state.csv` (Telangana row) | 85 | |
| `state.csv` (Andhra Pradesh row) | 80 | Slightly lower — capital/GDP/policy-name fields less confirmed |
| `district.csv` (33 Telangana rows) | 88 (uniform) | Above the 85 Tier-1 threshold |
| `district.csv` (26 stable Andhra Pradesh rows) | 75 (uniform) | Below the 85 Tier-1 threshold — missing urban%/literacy%/sex-ratio fields drag completeness down |
| `district.csv` (Markapuram) | 65 | New district, area/density confirmed but statistics still settling |
| `district.csv` (Polavaram) | 55 | New district, area/density not yet published anywhere located |

## 13. Production-Ready CSVs

Delivered as `state.csv` (2 rows) and `district.csv` (61 rows) — see attached files. Every row carries `data_source`, `source_url`, `collection_date`, `last_verified_date`, `confidence_score`, `verification_status`, `reviewer`, and `version` as required.

## 14. CSV Data Dictionary

### `state.csv`
| Column | Type | Description |
|---|---|---|
| `st_id` | UUID | Primary key |
| `st_ref` | TEXT | ValueWeave code (state abbreviation, e.g. `TG`) |
| `state_name` | TEXT | Full state name |
| `state_code` | TEXT | 2-letter state code |
| `capital_city` | TEXT | State capital |
| `industrial_policy_name` | TEXT | Name of current industrial policy, where confirmed |
| `state_gdp_inr_cr` | TEXT/DECIMAL | GSDP in ₹ crore, where confirmed |
| `msme_department_url` | TEXT | Official MSME/industries department URL |
| `lgd_state_code` | TEXT | Local Government Directory numeric state code (pending) |
| `data_source` / `source_url` / `collection_date` / `last_verified_date` / `confidence_score` / `verification_status` / `reviewer` / `version` | — | Provenance columns per this collection run's requirements |
| `created_by` / `created_at` / `updated_at` / `is_active` | — | Standard system columns per the CSV Schema Reference |

### `district.csv`
| Column | Type | Description |
|---|---|---|
| `dist_id` | UUID | Primary key |
| `dist_ref` | TEXT | ValueWeave code, `{STATE}-{3-letter mnemonic}` |
| `district_name` | TEXT | Official district name |
| `st_id` | UUID (FK) | → `state.st_id` |
| `govt_district_code` | TEXT | Official government-assigned district code, where one exists (AP only in this pass) |
| `lgd_district_code` | TEXT | LGD numeric code (pending) |
| `district_headquarters` | TEXT | HQ town/city |
| `area_sq_km` | DECIMAL/TEXT | District area |
| `population` | INTEGER | Population per cited source/year |
| `population_source_detail` | TEXT | Which specific source and vintage the population figure comes from |
| `mandal_count` | INTEGER | Number of mandals/revenue sub-divisions |
| `revenue_divisions` | INTEGER/TEXT | Number of revenue divisions (AP only in this pass) |
| `density_per_sq_km`, `urban_pct`, `literacy_rate_pct`, `sex_ratio` | DECIMAL/TEXT | Demographic detail, where the source provided it |
| `latitude`, `longitude` | TEXT | Pending geocoding |
| `district_gdp_inr_cr`, `primary_industry_sector_id` | TEXT | Pending — not yet sourced |
| `district_readiness_score` | TEXT | Explicitly not populated — AI-derived field, out of scope for a collection pass |
| Provenance + system columns | — | Same set as `state.csv` above |

## 15. Metadata JSON & Import Manifest
Delivered as `metadata.json` (source catalogue, reliability scores, conflict log, confidence summary) and `import_manifest.json` (batch ID, import order, dependency/FK checks, rollback plan, post-import action list) — see attached files.

---
*Prepared by the ValueWeave Data Collection Engine. All records held at `VST-NEEDS_REVIEW` pending human Data Steward and Reviewer sign-off per the Data Collection & Governance Framework — none of this batch should be treated as `VST-VERIFIED` until the Review Items in Section 11 are actioned.*
