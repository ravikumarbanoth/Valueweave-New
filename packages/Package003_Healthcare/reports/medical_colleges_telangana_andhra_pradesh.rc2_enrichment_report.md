# Enrichment Report: Medical Colleges — Telangana & Andhra Pradesh (RC1 → RC2)

**Package:** Package003_Healthcare
**Dataset:** medical_colleges_telangana_andhra_pradesh.csv
**RC1 collection date:** 2026-07-21
**RC2 enrichment date:** 2026-07-22
**Rows before enrichment:** 54 (29 Telangana, 25 Andhra Pradesh)
**Rows after enrichment:** 58 (33 Telangana, 25 Andhra Pradesh) — 4 new rows added
**Columns before:** 17 → **Columns after:** 20 (added `email`, `departments_summary`, `government_scheme_coverage_summary`)

## 1. Methodology

Identical constraint as RC1: direct WebFetch to `.gov.in`, `.ac.in`, and Wikipedia domains remained blocked (re-confirmed HTTP 403 at the start of this pass), so all enrichment was performed via WebSearch, reading search-result snippets from admissions aggregators (mbbscouncil, edufever, careermarg, medicalneetug/medicalneetpg, collegedunia, bodmaseducation, moksh16, and others), official college websites (identified via search, not fetched), and official-domain contact pages. Every new or changed fact traces to a specific search query and is reflected in the row's `notes` and/or `source_url`. No field was invented or inferred without a corroborating source; where corroboration was insufficient or contradictory, the field was left or set to `PENDING_VERIFICATION`.

Roughly 70 targeted WebSearch queries were run across this pass: per-college seat/website/email/department lookups, four flagged-conflict resolution queries, and general-policy queries on the AP/Telangana government health-scheme naming history.

## 2. Rows with improved confidence

- **50 of 54** original rows had `confidence_score` raised (the remaining 4 were already at or effectively at the 88 cap with no new corroborating fact found this session).
- **Average delta across all 54 original rows: +3.4** (average delta among only the rows that increased: +3.7).
- Per the task's rules, no increase exceeded +8, and no row was pushed above the 88 cap.
- Confidence increases were driven by: (a) new corroboration of previously-PENDING `official_website`/`mbbs_seats` fields from multiple independent aggregator sources, and (b) resolution of specific conflicts flagged in RC1 (see §4).

## 3. PENDING_VERIFICATION fields filled, by column (out of 58 total rows post-enrichment)

| Column | PENDING before (of 54, RC1) | PENDING after (of 58, RC2) | Notes |
|---|---|---|---|
| `mbbs_seats` | ~40 (majority of RC1 rows) | **0** | Every row now has a specific current seat figure, sourced from 2025-26 NEET-counselling aggregator data or official admissions pages. Several genuine cross-source seat-count variances (e.g. Mamata, CAIMS Karimnagar, Santhiram, ASRAM, RIMS Adilabad) were resolved by picking the more specific/more corroborated figure and flagging the alternate in `notes` rather than silently discarding it. |
| `official_website` | ~18 | **11** | Newly identified for GMC Nalgonda, GMC Suryapet, AIIMS Bibinagar, GMC Mancherial, GMC Wanaparthy, GMC Khammam, SVS Medical College, Bhaskar Medical College, Kamineni Academy, Ayaan Institute, Guntur Medical College, Rangaraya Medical College, Kurnool Medical College, GMC Anantapur, Fathima Institute, GITAM (GIMSR), Great Eastern Medical School. Remaining PENDING rows are ones where only unconfirmed/alumni-run or implausibly generic domains surfaced (e.g. SV Medical College Tirupati, Konaseema) — deliberately not populated to avoid misattribution. |
| `established_year` | 2 (Fathima Institute, Great Eastern Medical School) | **0** | Both filled: Fathima Institute of Medical Sciences (2010) and Great Eastern Medical School (2010). |
| `email` (new column) | n/a | 12 of 58 filled | Filled with genuine college-specific addresses (e.g. `omc_hyd-ts@nic.in` Osmania, `kmc_knl@nic.in` Kurnool, `pwarangal@gmail.com` Kakatiya, `ugadmissiongmckarimnagar@gmail.com` GMC Karimnagar, `info@gmcmancherial.telangana.gov.in`, `principaldcms@yahoo.com` Deccan, `p.mnrmc@mnrindia.org` MNR, `info@maheshwaramedical.com`, `asram@asram.in`, `gmc.sangareddy@gmail.com`, `gmc.kamareddy@gmail.com`, `ms@aiimsmangalagiri.edu.in`). **Deliberately excluded:** `dmetelangana@gmail.com` and `dmegoap@yahoo.co.in`, which surfaced repeatedly across many unrelated private colleges — these are the Telangana/AP Directorate of Medical Education's generic *state counselling-authority* addresses, not each college's own contact, and populating them would have been misleading. |
| `departments_summary` (new column) | n/a | 26 of 58 filled | Filled wherever a source named specific clinical/PG departments for that institution (Osmania[seats only, left PENDING], Kakatiya, GMC Jagtial/Karimnagar, Deccan, Kamineni Narketpally, Mamata, CAIMS Karimnagar, Prathima, MNR, Maheshwara, Andhra Medical College, Guntur Medical College, Kurnool, RIMS Srikakulam, RIMS Kadapa, ACSR Nellore, GMC Anantapur, Narayana, NRI, ASRAM, GSL, Katuri, Santhiram, Apollo Chittoor, GMC Sangareddy, AIIMS Mangalagiri). Left PENDING where only seat/PG-count numbers (not named departments) were found, per the strict no-invention rule. |
| `government_scheme_coverage_summary` (new column) | n/a | 34 of 58 filled | All Government-owned rows (except ESIC and the two AIIMS institutes) filled with a sourced general-policy statement: government teaching hospitals are, by default, part of the state's own cashless-scheme network (Telangana Aarogyasri / AP Dr. NTR Vaidya Seva). ESIC Sanathnagar and both AIIMS rows were kept PENDING_VERIFICATION with an explanatory note, since they sit under distinct central schemes (ESI Act / general PM-JAY policy) whose specific empanelment could not be confirmed this session. MNR Medical College's hospital was confirmed by name in an Aarogyasri hospital listing (filled as "Yes"). All other private colleges left PENDING_VERIFICATION — empanelment varies hospital-by-hospital and could not be confirmed against an official network list this session (Kamineni Narketpally and NRI General Hospital had soft/indirect signals of possible empanelment, documented in `notes` but not asserted in the data field). |

## 4. Conflicts investigated and resolved

1. **AP health-university naming split ("Dr. NTR" vs. "Dr. YSR" University of Health Sciences)** — **RESOLVED.** This was flagged across ~10 rows in RC1 as an unexplained discrepancy. Research this session found the actual history: the university was legislatively renamed Dr. NTR UHS → Dr. YSR UHS in 2019 (Andhra Pradesh Gazette Act No.19/2022 formalized an interim naming), then reverted back to **Dr. NTR University of Health Sciences** in July 2024 (Amendment Bill), which is the current, correct name as of 2026. Every affected row (Andhra Medical College, Kurnool Medical College, RIMS/GMC Ongole, Santhiram Medical College, Maharajah's Institute of Medical Sciences, and others where aggregators still show "YSR") now carries a note explaining that the "YSR" name reflects the 2019–2024 window rather than an aggregator error, and the existing "Dr. NTR University of Health Sciences" value was confirmed as currently correct rather than changed.

2. **SVS Medical College (Mahabubnagar, Telangana) affiliation** — **RESOLVED.** RC1 flagged a likely aggregator error listing affiliation as "Dr. NTR University of Health Sciences, Vijayawada" (the Andhra Pradesh university), geographically implausible for a Telangana college. Multiple current, independent aggregator sources this session explicitly and consistently confirm the correct affiliation is **Kaloji Narayana Rao University of Health Sciences (KNRUHS), Warangal**. Field corrected; confidence raised 78 → 86.

3. **Katuri Medical College, Guntur — establishment year (1997 vs. 2002)** — **RESOLVED ON PREPONDERANCE OF EVIDENCE (not conclusively proven).** RC1 could not resolve this. This session's search found current (2026-dated) aggregator listings predominantly and specifically describing the institution as "a Trust established in 2002," while 1997 traces to older/fewer sources. `established_year` changed from 1997 to 2002; flagged in `notes` as resolved on the balance of evidence since no primary NMC/college-charter document was directly accessible.

4. **Konaseema Institute of Medical Sciences & Research Foundation — establishment year (2005 vs. 2014)** — **RESOLVED.** A clear preponderance of independent current sources supports 2005, with only one outlier citing 2014. Retained 2005, confidence raised 76 → 84.

5. **Siddhartha Medical College, Vijayawada vs. Dr. Pinnamaneni Siddhartha Institute of Medical Sciences, Gannavaram** — no new conflict; both rows retained as distinct institutions per RC1's existing clarifying notes.

## 5. New rows added (4)

All four were explicitly named as gaps in the RC1 collection report ("Colleges considered but excluded" / "Known gaps" sections) and are now independently verifiable with an official website, a specific current seat count, and (for three of four) a specific contact email:

1. **Government Medical College, Sangareddy** (Telangana, est. 2022, KNRUHS, 150 MBBS seats) — official website `gmcsangareddy.org`, email `gmc.sangareddy@gmail.com`.
2. **Government Medical College, Kamareddy** (Telangana, est. 2023, KNRUHS, 100 MBBS seats) — official website `gmckamareddy.in`, email `gmc.kamareddy@gmail.com`.
3. **Government Medical College, Ramagundam** (Telangana, est. 2022, KNRUHS, 150 MBBS seats, Peddapalli district) — official website `gmcramagundam.in`; email and departments left PENDING_VERIFICATION.
4. **All India Institute of Medical Sciences, Mangalagiri** (Andhra Pradesh, est. 2018, autonomous/AIIMS Act, 125 MBBS seats, Guntur district) — official website `aiimsmangalagiri.edu.in`, email `ms@aiimsmangalagiri.edu.in`.

No additional rows were added purely to pad the count; several other gap-list colleges (Jayashankar Bhupalpally, Komaram Bheem Asifabad, Nirmal, Rajanna Sircilla, Vikarabad, Jangaon, Mahaboobabad, Bhadradri Kothagudem) were searched for or considered but not added this pass because a dedicated, well-corroborated per-college verification query was not run for them within the session's scope.

## 6. Remaining known gaps (carried into RC2 / for a future RC3 pass)

- **`official_website`** still `PENDING_VERIFICATION` for 11 of 58 rows (Gandhi Medical College, RIMS Adilabad, GMC Nizamabad, GMC Mahabubnagar, GMC Siddipet, GMC Nagarkurnool, GMC Khammam*, SV Medical College Tirupati, Konaseema IMS&RF, Maharajah's IMS, GMC Ramagundam-partial — see per-row notes). (*GMC Khammam now has a website; list reflects rows still genuinely unresolved.)
- **`email`** still `PENDING_VERIFICATION` for 46 of 58 rows — most private colleges and several newer government colleges have no publicly-listed, college-specific admissions email distinguishable from generic counselling-authority addresses.
- **`departments_summary`** still `PENDING_VERIFICATION` for 32 of 58 rows, including flagship institutions like Osmania Medical College and Siddhartha Medical College Vijayawada, where only seat/PG-count data (not named department lists) could be corroborated this session.
- **`government_scheme_coverage_summary`** still `PENDING_VERIFICATION` for 24 of 58 rows — primarily private colleges where hospital-specific Aarogyasri/Vaidya Seva/PM-JAY empanelment could not be checked against an official network list, plus ESIC Sanathnagar and the two AIIMS institutes (distinct central-scheme context).
- **~13-15 further Telangana government medical colleges** from the 2022-2023 expansion wave (Jayashankar Bhupalpally, Komaram Bheem Asifabad, Nirmal, Rajanna Sircilla, Vikarabad, Jangaon, Mahaboobabad, Bhadradri Kothagudem, and others) remain unrepresented as individual rows.
- **Direct primary-source access** (NMC official college list, KNRUHS/Dr NTR UHS official affiliated-college lists, the official Aarogyasri/Vaidya Seva Trust network-hospital portals, and Wikipedia full articles) remained unavailable this session (HTTP 403 on `.gov.in`/`.ac.in`/Wikipedia), so confidence scores remain capped at 88 per the task's instructions even for well-corroborated rows.
- A handful of minor cross-source seat-count variances were resolved by picking the better-corroborated figure rather than by independent primary confirmation (e.g. Mamata Medical College 150 vs. 200; CAIMS Karimnagar 150 vs. 200; Santhiram 150 vs. 100; ASRAM 150 vs. a possible 2026 increase to 250; RIMS Adilabad 120 vs. 125) — each is flagged in the row's `notes`.
