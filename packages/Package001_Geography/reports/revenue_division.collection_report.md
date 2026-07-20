# ValueWeave Data Factory — Collection Report
## Dataset: `revenue_division` — Telangana (ACQUIRED) & Andhra Pradesh (BLOCKED)
## Package: 001 — Geography Foundation

---

## 0. Mode Determination & Dependency-Order Confirmation

**Dependency order:** State → District → **Revenue Division** → Mandal → Village → Municipality → ... (per the roadmap now in effect). Revenue Division depends only on State + District, both already produced — it is correctly next, and it must complete before Mandal, since Mandal's own `revenue_division_name` field (added in the prior run's schema-evolution note) should be populated from verified Revenue Division records rather than left as a floating text guess.

**Mode determined per state, not per dataset as a whole — this run has two different official-source situations:**
- **Telangana → MODE A/B (ACQUIRE/PROCESS).** A single, internally-near-consistent, government-sourced structured table exists (Section 2) and was processed into a production CSV.
- **Andhra Pradesh → MODE C (BLOCKED).** The only structured source available carries Wikipedia's own "this article needs to be updated (February 2026)" flag, its row-level division counts don't sum to its own stated total, and a specific, independently-confirmed division (Nakkapalli, Anakapalli district) is verifiably missing from it. Per the explicit MODE C protocol — "Do NOT scrape unreliable sources" — no AP revenue division rows were produced this run. Section 6 below is the full Blocking Report.

---

## 1. Research Summary

**Telangana** has 74 revenue divisions across all 33 districts per its dedicated, single-topic Wikipedia compilation (citing the Telangana State Portal, the Chief Commissioner of Land Administration, and individual district revenue departments) — internally consistent with one small exception (Section 3, Conflict 1), which this run resolves to 75. **Andhra Pradesh** has a stated 79 revenue divisions across 28 districts, but the source carrying that figure is demonstrably out of date following the state's 31 December 2025 district reorganization (Section 6) — this run does not produce AP revenue division rows as a result.

**Important cross-check completed this run:** while researching Andhra Pradesh, a Group-of-Ministers proposal from 25 November 2025 was found describing a **29-district** outcome (a third new district, Madanapalle, in addition to Polavaram and Markapuram). This could have meant the District dataset shipped in the prior run (28 districts) was already stale. Direct investigation (Section 4) confirms it was **not**: the AP Cabinet's final decision on 29 December 2025 approved only Polavaram and Markapuram as new districts, kept Madanapalle as the (renamed) headquarters of the already-existing Annamayya district rather than spinning it off separately, and the state's district count remains **28** at final notification. The prior District dataset's figure is confirmed correct, not superseded — recorded here as a closed-out verification, not a silent correction.

## 2. Official Sources

| Source | Coverage | Status |
|---|---|---|
| Telangana State Portal — State Profile | TG revenue division structure | Used (via compiled citation) |
| Chief Commissioner of Land Administration, Telangana (ccla.telangana.gov.in) | TG revenue division structure | Used (via compiled citation) |
| Individual Telangana district revenue department notifications (Karimnagar, Mahabubnagar, Nalgonda, Nizamabad district portals; Government of Telangana GOs on district formation) | TG revenue division structure, cross-district confirmation | Used (via compiled citation) |
| Andhra Pradesh Cabinet decision, 29 December 2025 (district/revenue-division reorganization) | AP district and revenue division count — final authority | Identified; not yet directly fetched (gazette PDF) — used via corroborated news reporting instead (Section 4) |
| Andhra Pradesh State Portal — Administrative and Geographical Profile (2014 edition, archived) | AP revenue division structure (pre-2022 baseline) | Identified, dated, superseded |

## 3. Conflicts Identified — Telangana

### Conflict 1 — Suryapet district: table states 2 divisions but lists 3
- **Sources in disagreement:** The summary table's "No. of Divisions" column says 2 for Suryapet; the same row's "Revenue Divisions" column lists three names (Suryapet, Kodad, Huzurnagar). Independently, the dedicated "Suryapet revenue division" Wikipedia page states it is "one of the **3** revenue divisions" in Suryapet district, and the dedicated "Kodad revenue division" page independently states the same thing.
- **Recommended authoritative reading:** 3, not 2 — two independent, dedicated pages corroborate each other against the summary table's own internal arithmetic error.
- **Decision documented:** This dataset uses 3 for Suryapet, bringing the Telangana total from the source's stated 74 to a corrected **75**. This has not been confirmed against a primary government document — flagged for Review (Section 7).

## 4. Conflict Resolved — Andhra Pradesh District Count (29-proposal vs. 28-final)

| Stage | Date | Districts | Status |
|---|---|---|---|
| Group of Ministers recommendation, approved by CM Naidu | 25 Nov 2025 | 29 (adds Polavaram, Markapuram, **Madanapalle**) | Proposal stage — "will now be placed before the Cabinet for final approval" |
| Public feedback window on gazette notification | until 27 Dec 2025 | — | Objections/suggestions incorporated |
| **AP Cabinet final decision** | **29 Dec 2025** | **28** (adds Polavaram, Markapuram only) | **Final — effective 31 Dec 2025** |

The Cabinet explicitly declined to make Madanapalle a standalone district ("the Cabinet concluded that Rayachoti could not be designated as a district. Instead, Madanapalle will become the district headquarters of Annamayya district, replacing Rayachoti") — matching this dataset's existing District record, which already listed Annamayya's headquarters as Madanapalli. **Recommendation:** treat any source citing "29 districts" as describing the superseded 25 November proposal, not the final outcome, unless it is dated after 29 December 2025 and explicitly reflects the Cabinet's final decision.

## 5. Cleaning / Normalization Applied (Telangana)
- Normalized district name spellings to match the existing `district.csv` values (e.g., "Hanmakonda"→"Hanumakonda", "Komaram Bheem"→"Kumuram Bheem Asifabad", "Medchal"→"Medchal-Malkajgiri", "Narayanapet"→"Narayanpet") so `dist_ref` foreign keys resolve correctly.
- Assigned `revenue_division_ref` per the ValueWeave Coding Standard: `TG-{DISTRICT_REF}-RD-{SEQUENCE}` (e.g., `TG-MDK-RD-1` for Medak's first-listed division).
- Divisional headquarters defaulted to the division's own name (standard convention for Telangana revenue divisions, where the division is named after its HQ town) — flagged as not independently re-verified per row, since a small number of divisions nationally are named for something other than their literal HQ.

## 6. Blocking Report — Andhra Pradesh Revenue Divisions (MODE C)

1. **Blocking Report:** The only available structured source (Wikipedia's "List of revenue divisions in Andhra Pradesh") is self-flagged "needs to be updated (February 2026)"; its 28 row-level division counts sum to 82, not the 79 the article itself states as the total; and this session independently confirmed the table is missing at least one specific division ("Nakkapalli," created in Anakapalli district as part of the 31 December 2025 reorganization, per multiple corroborating news sources) that should be present. Producing row-level data from a source with a confirmed gap and an unreconciled internal total would risk shipping wrong data under a false confidence label.
2. **Official Source Identification:** The Andhra Pradesh government's official gazette notification implementing the 29 December 2025 Cabinet decision (district and revenue-division reorganization) is the correct authoritative source; the AP CCLA-equivalent land administration portal (if one exists analogous to Telangana's) would be the correct ongoing-maintenance source.
3. **Exact Download URL:** Not yet identified with certainty this session — the specific gazette PDF URL was not located (news coverage references "a formal notification will be issued" but does not link the notification itself). Recommended next search: the AP Gazette portal (https://gazette.ap.gov.in, unverified this session) or Andhra Pradesh Revenue Department official site.
4. **Download Instructions:** Search the AP Gazette portal for the December 2025/January 2026 notification on "reorganisation of districts and revenue divisions"; alternatively request the notification directly from the AP Revenue Department.
5. **Expected File Format:** Government Gazette PDF (bilingual Telugu/English typical for AP gazette notifications).
6. **Parser Specification:** Once obtained, extract per the pattern already validated for Telangana — District name, Revenue Division name(s), constituent mandals where listed — using PDF text extraction (tables in AP gazettes are typically extractable as structured text, not scanned images, based on the pattern of other AP gazette notifications reviewed in this project).
7. **Validation Rules:** Row-level division counts per district must sum to the document's own stated state total (the exact check that caught this block in the first place); every division name must resolve to exactly one `dist_ref` already present in `district.csv`.
8. **Import Schema:** Identical to `revenue_division_telangana.csv` (Section 8, Data Dictionary) — no schema change needed, only data.
9. **Evidence Requirements:** Per `evidence_manifest.json` (Section 10) — retain the actual gazette PDF, not just a parsed CSV, given this dataset's demonstrated history of secondary-source drift.
10. **Resume Instructions:** Once the gazette PDF is obtained (via direct download or user upload to this session), re-run this dataset through Stages 3–8 of the standard workflow; do not merge new data into `revenue_division_andhra_pradesh.csv` without re-validating the full district-level sum against the source's own stated total first.

## 7. Recommended Review Items
1. Confirm the Suryapet 2-vs-3 correction (Section 3) against a primary Telangana government source before promoting Telangana's batch past `VST-NEEDS_REVIEW`.
2. Locate and fetch the actual AP gazette notification (Section 6, items 2–3) — this is the single action that unblocks Andhra Pradesh.
3. Populate `mandal_count` for the 69 (of 75) Telangana revenue divisions not yet individually verified (Section 8 documents which 6 are already confirmed).
4. LGD codes and geocoding remain outstanding for all rows, consistent with the pattern already established for State/District/Mandal.

## 8. Confidence Scores
| Batch | Confidence | Notes |
|---|---|---|
| Telangana rows with independently verified `mandal_count` (6 of 75) | 90 | Cross-confirmed via dedicated per-division Wikipedia pages |
| Telangana rows without independently verified `mandal_count` (69 of 75) | 82 | Division name/district assignment solid; mandal-level detail still pending |
| Andhra Pradesh | N/A — zero rows produced | See Blocking Report |

---
*Prepared by the ValueWeave Data Factory. Telangana data held at `VST-NEEDS_REVIEW`. Andhra Pradesh intentionally not populated — see Blocking Report — rather than risk shipping data from a source with a confirmed, uncorrected gap.*
