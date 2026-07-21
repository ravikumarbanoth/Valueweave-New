# RC2 Enrichment Report: Government Hospitals — Telangana & Andhra Pradesh

**Package:** ValueWeave Package003_Healthcare
**Dataset:** `government_hospitals_telangana_andhra_pradesh.csv`
**Base:** RC1 (collection date 2026-07-21, 49 rows, 21 columns)
**This pass:** RC2 enrichment (collection date 2026-07-22 for all touched/added rows), 55 rows, 25 columns
**Method:** WebSearch only (WebFetch to `.gov.in`/`.ac.in`/Wikipedia re-confirmed blocked, HTTP 403, at session start). No direct page fetches were performed in this pass either — every fact below comes from WebSearch result snippets/summaries, consistent with the RC1 methodology and its stated limitations.

## Summary of changes

- **Rows re-verified / touched:** 49 of 49 RC1 rows (100%). Every row was searched again; 47 rows had `confidence_score` raised, 2 rows (Aswaraopeta, Mahabubabad — both already flagged with unresolved conflicts/gaps in RC1) were re-searched but yielded no new corroborated facts, so confidence was held flat. All 49 rows have `collection_date` updated to 2026-07-22 because all were genuinely re-searched, even where no new fact was confirmed.
- **Confidence improvement:** 47/49 rows improved; average delta among improved rows = **+3.77** (range +2 to +7); average delta across all 49 existing rows (including the 2 flat ones) = **+3.61**. No row exceeds the 88 cap; no row moved by more than the +8 per-row maximum.
- **New rows added:** **6** (see below), bringing the dataset to 55 rows. Not padded to the top of the 3–8 range — 6 was the number of gap-district hospitals for which genuinely credible, cross-checkable information could be found this pass.

## PENDING_VERIFICATION fields filled (existing 49 rows only)

Counted only where a RC1 `PENDING_VERIFICATION` value was replaced with a real, sourced value:

| Field | Fields filled |
|---|---|
| `address` | 10 |
| `contact_number` | 12 |
| `bed_capacity` | 7 |
| `emergency_services` | 4 |
| `official_website` | 0 (no new official-domain website was found with enough independent corroboration to overwrite a RC1 `PENDING_VERIFICATION`; several unverified leads are noted in-row instead) |
| **Total** | **33** |

Many fields legitimately remain `PENDING_VERIFICATION` (per-hospital `contact_number` for the smaller TVVP Area Hospitals, most `bed_capacity` figures for AP District/Area Hospitals, essentially all `official_website` fields for non-teaching District/Area Hospitals) because no credible source surfaced this pass — these were not guessed.

## New columns — fill rate across all 55 rows

| Column | Filled | PENDING_VERIFICATION |
|---|---|---|
| `email` | 17 | 38 |
| `specialties_summary` | 17 | 38 |
| `available_services_summary` | 25 | 30 |
| `government_scheme_coverage_summary` | 10 | 45 |

`government_scheme_coverage_summary` has the lowest fill rate by design: the task explicitly warned against assuming Aarogyasri/PM-JAY coverage without an explicit source, and the large majority of hospitals searched had only generic district-level or state-level scheme context (e.g., "Aarogyasri is the state's flagship scheme") rather than a hospital-specific empanelment statement. Only 10 rows had an explicit, hospital-specific confirmation:
- **Explicit Dr. YSR Aarogyasri confirmation:** GGH Rajahmundry (East Godavari), RIMS Ongole (Prakasam), District Hospital Peddapalli (via news coverage of TVVP/Aarogyasri awards — Rajiv Aarogyasri equivalent)
- **Explicit Ayushman Bharat PM-JAY empanelment:** RIMS Adilabad, Area Hospital Bhadrachalam, GGH Guntur, RIMS Srikakulam, Area Hospital Tadepalligudem
- **Both Rajiv Aarogyasri (state) and PM-JAY:** GGH Suryapet, Osmania General Hospital

## Conflicts found and how they were resolved

1. **GGH Suryapet bed capacity:** RC1 recorded "600 (planned/under-construction)" from the official district page. A new source (drlogy.com) states the hospital "was upgraded to a 400-bedded" facility. Both are plausible (400 currently operational vs. 600 planned/under construction) — original official-domain figure retained, conflict disclosed in `notes`.
2. **GMC Mancherial address:** A second address ("19, Mancherial-Chandrapur-Nagpur Road, Iqbal Ahmed Nagar") surfaced, differing from the RC1 address ("708, Garmilla village, Mancherial tehsil"). Not resolved — both may describe the same campus; original retained, conflict noted.
3. **GGH Sangareddy address:** Two further address variants surfaced ("Indra Colony, Ahmed Nagar" and "Tadlapalle") on top of RC1's existing address, consistent with the category-churn/multi-facility ambiguity already flagged in RC1. Not resolved; original retained.
4. **Area Hospital Mahabubabad bed capacity:** A new source states "54 total beds," conflicting further with RC1's already-recorded COVID-era ad hoc ward counts and the pre-existing two-address conflict. Left unresolved and disclosed; confidence held flat rather than raised.
5. **ACSR GGH Nellore bed capacity:** RC1 recorded 750 (teaching beds) from spsnellore.ap.gov.in. The college's own site (acsrgmcnlr.com) and aggregators state 350 beds (proposed increase to 450) — a substantial, newly-surfaced conflict between two official-adjacent sources. Original 750 figure retained per RC1; conflict now explicitly disclosed.
6. **GGH Kakinada bed capacity:** RC1 already disclosed a 1200/1462/1800 conflict. This pass surfaced yet another figure ("over 1,000 beds" / "500 beds" from other aggregators), worsening rather than resolving the conflict. Disclosed, not resolved.
7. **GGH Yadadri Bhuvanagiri / "Government Hospital, Bhongir":** A contact (msahbngr@gmail.com / 7702131479) surfaced for what appears to be a separate town-level facility, not the GMC teaching hospital at Pagdipally village recorded in this row. Not applied, to avoid conflating two distinct facilities — same caution applied to an SCCL-branded number found for "Area Hospital Yellandu" (likely a Singareni Collieries company hospital, not the TVVP government facility).

## New rows added (6)

All were selected because they had genuinely locatable official-domain-adjacent contact information (college/hospital site, or the state district government directory), not merely a name mention, and each fills a district explicitly named in the RC1 gap list:

| Hospital | District (gap filled) | Category | Confidence |
|---|---|---|---|
| Government General Hospital, Wanaparthy | Wanaparthy (TG) | Teaching | 80 |
| Government Medical College Hospital, Rajanna Sircilla | Rajanna Sircilla (TG) | Teaching | 82 |
| Government Medical College Hospital, Nandyal | Nandyal (AP, 2022 reorg) | Teaching | 83 |
| Area Hospital, Bapatla | Bapatla (AP, 2022 reorg) | Area Hospital | 80 |
| District Hospital, Peddapalli | Peddapalli (TG) | District Hospital | 82 |
| Government Medical College Hospital, Medak | Medak (TG) | Teaching | 78 (lowest — official website unconfirmed, most fields aggregator-only) |

Several other gap-list candidates (Warangal Rural/Hanumakonda, Rangareddy, Medchal-Malkajgiri, Jayashankar Bhupalpally, Mulugu, Komaram Bheem Asifabad, Jogulamba Gadwal in TG; Anakapalli, Alluri Sitharama Raju, Parvathipuram Manyam, Palnadu, Sri Sathya Sai, Annamayya, Dr. B.R. Ambedkar Konaseema in AP) were searched but yielded no hospital-specific facts credible enough to add — they remain gaps, consistent with "quality over count."

## Remaining major gaps (unchanged from RC1, still open)

- **TVVP's and APVVP's own master hospital-list pages** (`vvp.telangana.gov.in/content.php?U=2`, `apvvp.ap.gov.in`) were again located but their tabular content never surfaced in any WebSearch snippet, and direct fetch remains blocked. This is still the single biggest structural gap in both states' coverage.
- **`official_website` PENDING_VERIFICATION rate remains high** for non-teaching District/Area Hospitals — these generally have no dedicated domain distinct from the district government portal.
- **Several address/bed-count conflicts remain genuinely unresolved** (Sangareddy, Mancherial, Mahabubabad, Kakinada, ACSR Nellore, Chittoor) — direct-fetch access to the underlying official pages would likely be required to adjudicate these, not further search-only passes.
- **`government_scheme_coverage_summary` is PENDING for 45/55 rows** — this is an intentionally conservative outcome per the task's explicit instruction not to assume Aarogyasri/PM-JAY coverage without a hospital-specific source.

## Confidence-score methodology (unchanged from RC1, reapplied)

Deltas were capped at +8 per row and the resulting score capped at 88 (per task instructions — direct-fetch access is still unavailable, so no row was allowed to claim 90+). Rows where new facts were found but a pre-existing conflict remained unresolved were given smaller or zero deltas rather than being rewarded for volume of search activity alone.
