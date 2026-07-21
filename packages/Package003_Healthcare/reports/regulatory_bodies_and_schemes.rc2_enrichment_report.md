# RC2 Enrichment Report — Medical Regulatory Bodies & Health Missions + Government Health Insurance Schemes

Package003_Healthcare | Enrichment pass date: 2026-07-22 | Baseline: RC1 (collected 2026-07-21)
Method: WebSearch only (WebFetch to .gov.in / .ac.in / Wikipedia re-confirmed blocked, HTTP 403, at session start). No field was fabricated; unresolved fields remain `PENDING_VERIFICATION`.

This report covers the RC1 -> RC2 enrichment pass on:
1. `datasets/medical_regulatory_bodies_and_health_missions.csv` (23 -> 24 rows)
2. `datasets/government_health_insurance_schemes.csv` (8 -> 9 rows)

Both CSVs were overwritten in place with the same column schema as RC1 (no columns added or removed). Only rows that were actually touched had their `collection_date` advanced to 2026-07-22; all untouched rows retain `collection_date = 2026-07-21`. No existing row's `id` was changed, and no previously-verified fact was removed or degraded — enrichment only added corroborating detail, filled previously-pending fields, or appended new `RC2 UPDATE` / `RC2 FILLED` notes.

---

## Part 1 — Medical Regulatory Bodies & Health Missions

### 1.1 Previously PENDING_VERIFICATION fields: resolution status

| Field | Row | Result | New value | Confidence change |
|---|---|---|---|---|
| CDSCO `established_year` | Central Drugs Standard Control Organisation | **Still unresolved** | remains `PENDING_VERIFICATION` | 82 -> 85 (other facts re-corroborated) |
| NHM Telangana `established_year` | National Health Mission - Telangana | **Still unresolved** | remains `PENDING_VERIFICATION` | 82 -> 84 |
| NHM Andhra Pradesh `established_year` | National Health Mission - Andhra Pradesh | **Still unresolved** | remains `PENDING_VERIFICATION` | 82 -> 84 |
| Telangana State Pharmacy Council `established_year` | Telangana State Pharmacy Council | **Filled** | `2015` | 81 -> 86 |
| AP Pharmacy Council `established_year` | Andhra Pradesh Pharmacy Council (APPC) | **Filled** | `1959` | 81 -> 88 |
| Rajiv Aarogyasri Health Care Trust (Telangana) `established_year` | Rajiv Aarogyasri Health Care Trust (Telangana) | **Filled** | `2014` | 80 -> 85 |
| AP Nurses Council `headquarters_city` | APNMC | **Filled** | `Vijayawada` | 80 -> 86 |

**5 of 7 target fields filled; 2 remain genuinely unverifiable** (CDSCO, and both state-specific NHM units) after renewed targeted search — left as `PENDING_VERIFICATION` per the no-guessing rule, with richer contextual notes added explaining what *was* found and why it stops short of a confirmed year.

Detail on the two still-open fields:
- **CDSCO**: multiple independent sources consistently trace the regulatory lineage to the Drug Controller of India (1930, post-Chopra Committee) and the Drugs and Cosmetics Act, 1940, but no source specifies when the organization took its current "Central Drugs Standard Control Organisation" name/form. Recorded as a documented ambiguity, not a guess.
- **NHM Telangana / NHM AP**: both states implement NHM through a "State Health & Family Welfare Society" registered under the applicable state Societies Registration Act; found the Telangana Societies Registration Act, 2001 (amended 2014) and the AP Reorganisation Act, 2014 as the relevant legal scaffolding, and ruled out a false-positive candidate date (AP's 2008 District Project Management Unit, which predates the 2014 bifurcation and pertains to undivided AP). No document gives the exact registration date of either state-specific society, so both remain pending.

### 1.2 New corroboration found for existing facts (confidence raised)

- **AP Pharmacy Council `established_year` = 1959**: sourced directly from the Council's own official history page (`appharmacycouncil.gov.in/site/history`), quoted consistently across two independent search passes — G.O.Ms.1021 (9 July 1955, enabling Rules) -> first register 1956 (236 pharmacists) -> Council **formally constituted 19 March 1959** -> Rules amended via G.O.Ms.2073 (15 July 1963). This is the strongest single find of the pass; confidence raised to the session ceiling of 88.
- **Telangana State Pharmacy Council `established_year` = 2015**: G.O.Ms No. 30 dated 06-04-2015 constituted the council under the Pharmacy Act, 1948, post-bifurcation. A secondary nuance was also found and preserved in notes: 2018 news coverage describes the council's first *elected* executive committee/president taking office in 2018 — recorded as an Act-vs-operational-date distinction analogous to the NMC row already in this dataset.
- **Rajiv Aarogyasri Health Care Trust (Telangana) `established_year` = 2014**: G.O.Ms.No.94, HM&FW (M2) Dept., dated 23-05-2014, ratified the Trust's continued "Trust Mode" operation for Telangana immediately after the 2 June 2014 bifurcation — reasonably strong, though indirect, corroboration.
- **APNMC `headquarters_city` = Vijayawada**: confirmed via the Council's own contact page (address: Old Govt. General Hospital, Hanumanpet, Main Road, Vijayawada – 520001), cross-checked against an independent local business-directory listing at the same location.

### 1.3 Updates found since RC1 (regulatory transitions / administrative changes)

- **National Dental Commission (NDC)**: confirmed operationally active — mid-July 2026 news reports the NDC abolishing the mandatory provisional-registration requirement for BDS graduates before internship. This shows the DCI->NDC transition (already caught in RC1) has moved from paper notification to functioning regulatory activity. Confidence raised 82 -> 86.
- **APNMC portal migration (significant, previously understated in RC1)**: RC1 recorded the APNMC portal as "reported suspended... resumption date to be informed." RC2 research found this was in fact a **permanent closure** (15 March 2026) with functions migrated to the centralized National Registration and Tracking System (NRTS, `nrts.indiannursingcouncil.gov.in`) run by the Indian Nursing Council — a structural administrative transition comparable in kind (smaller in scale) to the DCI->NDC transition. Flagged prominently in the row's notes; the existing `official_website` field was **not** changed (per the "don't degrade existing data" rule), but downstream consumers are pointed to NRTS as the current operational system.
- **National Health Authority / PM-JAY (national scope)**: West Bengal became the **36th and final State/UT** to implement AB PM-JAY — approved at the new BJP state government's first cabinet meeting (11 May 2026), rolled out from 1 July 2026, reportedly covering ~1.43 crore approved families. This completes nationwide State/UT-level coverage of PM-JAY, a significant milestone that predates but was missed by the RC1 collection (2026-07-21). Confidence raised 83 -> 86.
- **Dr. YSR Aarogyasri / Dr. NTR Vaidya Seva Trust (AP)**: current operational scale refreshed — Trust CEO reported 782 of 785 designated private hospitals actively empanelled (May 2026), alongside a Rs 919.13 crore government disbursement in May 2026 to clear hospital dues, evidencing an actively-running network. Confidence raised 81 -> 85.

### 1.4 New row added

- **National Board of Examinations in Medical Sciences (NBEMS)** — new UUID `bb634be0-cb19-4150-9c51-471bd5a1b987`. Type: Standards/Accreditation Body, National, parented by MoHFW. Established 1975 (registered as a society 1 March 1982); HQ New Delhi; runs NEET-PG, NEET-SS, FMGE, and the DNB/DrNB/FNB postgraduate qualification and hospital-accreditation track — a parallel structure to NMC's university-based PG medical education. This was a genuine, currently active, national, MoHFW-parented body not covered in the RC1 pass; the RC1 report's exclusions list (AYUSH bodies, FSSAI, NPPA, state drug control administrations, district commissionerates) did not name it, and it survived verification against two independent sources (its own official site and Wikipedia). Confidence set at 84 (session ceiling band, WebSearch-only methodology).
  - No other candidate from the RC1 "excluded" list was added: AYUSH bodies, FSSAI, NPPA, and state Drug Control Administrations remain reasonably excluded on scope grounds (different parent ministry / different regulatory domain), not because of any factual error in RC1's reasoning.

---

## Part 2 — Government Health Insurance Schemes

Dataset 1 had 0 `PENDING_VERIFICATION` fields at RC1, but four known gaps were explicitly flagged for a future pass. Status:

| Known gap (RC1) | Result | Confidence change |
|---|---|---|
| AP EHS exact coverage ceiling | **Filled**: Rs 2 lakh per episode of illness, per APIMA Rules, 1972 (cross-corroborated across 4 independent aggregator sources) | 80 -> 85 |
| ECHS contribution amounts | **Partially filled**: broad two-tier range found (~Rs 30,000 for JCOs/Other Ranks up to ~Rs 1.2 lakh for Officers); full rank-by-rank table still not located | 83 -> 87 |
| Exact current empanelled-hospital counts | **Filled for 3 of 3 relevant rows** (PM-JAY, Rajiv Aarogyasri Telangana, Dr. NTR Vaidya Seva AP) — see below | see below |
| CGHS beneficiary count (42-50 lakh disagreement) | **Narrowed but not resolved**: most specific individual figure found is 47.44 lakh (Wikipedia-sourced), but other sources still round to "~50 lakh" / "over 40 lakh" — range retained as the honest answer rather than forcing a single number | 84 -> 87 |

### 2.1 Empanelled-hospital counts refreshed

- **AB PM-JAY (national)**: ~36,229 hospitals (~19,483 government + ~16,746 private) as of Feb 2026, per secondary sources citing NHA dashboard data — up from ~27,000 in 2023. Confidence 85 -> 88.
- **Rajiv Aarogyasri (Telangana)**: ~1,400+ empanelled hospitals, ~1,835 total procedures (consistent with the previously-recorded "1,672 + 163 new = 1,835" procedure math). Confidence 84 -> 87.
- **Dr. NTR Vaidya Seva (AP)**: 782 of 785 designated private hospitals actively empanelled (Trust CEO statement, May 2026), plus a Rs 919.13 crore dues-clearance disbursement in May 2026 — sourced via a specialist health-news outlet (medicaldialogues.in), not a generic insurance aggregator. Confidence 82 -> 86.

All three figures are explicitly flagged as approximate/fluctuating, consistent with RC1's own caveats — this pass narrowed the range rather than claiming false precision.

### 2.2 Updates found since RC1

- **West Bengal / AB PM-JAY nationwide completion** (see Part 1.3 above — same fact, cross-referenced into both datasets' relevant rows: the NHA/PM-JAY row in dataset 1, and the AB PM-JAY row in dataset 2).
- No scheme rename or coverage-amount change was found for CGHS, ESIC, Rajiv Aarogyasri, NEHS, Dr. NTR Vaidya Seva, or AP EHS beyond what RC1 already captured. NEHS (Telangana, launched 17 July 2026) was left untouched — at only 5 days old versus RC1's snapshot, no further independent corroboration beyond launch-week coverage had emerged, so its capped RC1 confidence (82) stands unchanged with `collection_date` unchanged at 2026-07-21.

### 2.3 New row added

- **Rashtriya Arogya Nidhi (RAN), including the Health Minister's Cancer Patient Fund (HMCPF)** — new UUID `880bc50a-c57f-428e-9a65-a03f64586cc2`. Central Scheme, National, administered by MoHFW. Established 13 January 1997 (initial Rs 5 crore corpus). Provides grant-in-aid financial assistance (up to Rs 15 lakh general life-threatening disease / Rs 15 lakh HMCPF cancer / Rs 20 lakh rare disease) paid directly to the treating government hospital's Medical Superintendent, for BPL patients with family income ≤ Rs 1,25,000/year.
  - This differs in *mechanism* from the insurance-style schemes elsewhere in the dataset (one-time grant vs. an annual per-family floater), but was judged in-scope because it is a defined, non-discretionary scheme with fixed eligibility and coverage ceilings — unlike the CM Relief Fund grants that RC1 correctly excluded as "discretionary, case-by-case ex-gratia" aid. Confidence set at 83 (session ceiling band).
  - Other RC1-excluded items (RSBY, PMSBY, NHM service-delivery programs, UHIS) were re-examined and remain correctly excluded: RSBY/UHIS are discontinued, PMSBY is a Finance Ministry accidental-death product, and NHM programs are service-delivery incentives rather than financial-coverage schemes.

---

## Summary of confidence-score changes

All increases respect the task's cap (max +8 per row, ceiling of 88; no row raised to 90+). The largest single increase (+7, to 88) was AP Pharmacy Council, on the strength of a direct primary-source (council's own history page) citation. No row's confidence was lowered, and no previously-recorded fact was removed.

## Remaining gaps for a future RC3 pass

- CDSCO precise founding/naming year.
- NHM Telangana and NHM AP state-society formal establishment dates.
- A complete ECHS one-time-contribution table by exact rank (only a two-tier range was found).
- A single authoritative CGHS beneficiary count (range persists at 42-50 lakh; 47.44 lakh is the most specific figure found).
- Direct .gov.in / primary-document fetch remains blocked this session (HTTP 403, re-confirmed) for both datasets; all figures above trace to WebSearch snippets of secondary and (where cited) primary sources, not directly rendered pages. A follow-up pass with direct fetch access is recommended to move confidence scores above the current ceiling.
