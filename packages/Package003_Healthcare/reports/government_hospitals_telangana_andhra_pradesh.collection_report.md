# Collection Report: Government Hospitals — Telangana & Andhra Pradesh

**Package:** ValueWeave Package003_Healthcare v1.0.0
**Dataset:** `government_hospitals_telangana_andhra_pradesh.csv`
**Collection date:** 2026-07-21
**Rows collected:** 49 (28 Telangana, 21 Andhra Pradesh)

## Scope

District Hospitals, Area Hospitals, and Teaching/Medical-College-attached Hospitals run by the
Telangana and Andhra Pradesh state governments — i.e. facilities under the Telangana Vaidya
Vidhana Parishad (TVVP), the AP Vaidya Vidhana Parishad (APVVP)/AP Health, Medical & Family
Welfare Department, or directly under the respective state Directorate of Medical Education
(DME). PHCs, CHCs, and Urban Health Centres were explicitly excluded per task scope.

## Methodology

1. All research was conducted via the **WebSearch** tool only. **WebFetch was not usable** for
   this task: the session's organizational egress policy blocks WebFetch to `.gov.in`, `.ac.in`,
   and Wikipedia domains (confirmed HTTP 403 in a pre-flight check), and these domains account
   for nearly all primary sources for Indian government hospitals. As a result, every fact in
   this dataset is sourced from **search-engine-returned snippets/summaries** of those pages
   (and of secondary aggregator sites), not from directly-fetched and read page content. This is
   a material limitation — see "Known Limitations" below.
2. Search strategy: (a) established the administrative structure first (TVVP vs DME in
   Telangana; APVVP vs DME in Andhra Pradesh) via searches on `dme.telangana.gov.in`,
   `vvp.telangana.gov.in`, `apvvp.ap.gov.in`, `hmfw.ap.gov.in`; (b) searched for each state's
   known government medical colleges (using existing general knowledge of TG's ~9 newly
   established GMCs and AP's district-wise GMC expansion program) to identify their attached
   teaching hospitals; (c) searched district-by-district for TVVP/APVVP District and Area
   Hospitals where medical-college coverage was sparse; (d) cross-checked bed counts,
   addresses, and contact details across 2-3 independent search results per hospital where
   possible.
3. Every row's `data_source` and `source_url` fields record which pages the WebSearch snippets
   were drawn from. Where facts could not be found in any search result, the field was set to
   the literal string `PENDING_VERIFICATION` rather than guessed.
4. `confidence_score` was capped per instructions: 82 for single-source facts, up to 85-88 for
   facts corroborated by multiple independent sources (official-domain page + Wikipedia +
   at least one directory/aggregator agreeing). No score exceeds 88. Facts sourced only from an
   AI-generated WebSearch summary (rather than a directly quoted snippet) were capped lower
   (78-80) and flagged in notes.
5. Post-2022 Andhra Pradesh district reorganization (13 → 26 districts) was cross-checked via
   search so that `district` values reflect current district names (e.g., "NTR" for Vijayawada,
   "Eluru" for Eluru, "Kakinada" for Kakinada, "Tirupati" for Tirupati city, "East Godavari" for
   Rajahmundry/Rajamahendravaram) rather than pre-reorg names, where this could be confirmed.

## Sources Consulted (representative, not exhaustive — full list is in each row's source_url)

- Telangana Vaidya Vidhana Parishad — https://vvp.telangana.gov.in/ (content pages only surfaced as search snippets; direct fetch blocked)
- Telangana Directorate of Medical Education — https://dme.telangana.gov.in/
- District portals (telangana.gov.in subdomains): karimnagar, kothagudem, mahabubabad, kamareddy, jangaon, adilabad, vikarabad, suryapet
- Individual GMC/teaching-hospital sites: gmcnzb.org, gmckothagudem.org, gmcmancherial.org, rimsadilabad.org, gmcsiddipet.org, gmcyadadri.org, gmcvikarabad.ac.in, gmcnagarkurnool.org, gmckhammam.org, gmcsecunderabad.org, kmcwgl.com (Kakatiya Medical College / MGM Hospital)
- Andhra Pradesh Health, Medical & Family Welfare Dept — https://hmfw.ap.gov.in/
- AP Vaidya Vidhana Parishad — https://apvvp.ap.gov.in/, https://apvvp.nic.in/
- AP Directorate of Medical Education — https://dme.ap.nic.in/
- District portals (ap.gov.in subdomains): west godavari, krishna, chittoor, tirupati, srikakulam, spsnellore, vizianagaram
- Individual GMC/teaching-hospital sites: gunturmedicalcollege.edu.in, kurnoolmedicalcollege.ac.in, amc.edu.in (Andhra Medical College/KGH), rims-kadapa.in, gmcvizianagaram.ap.gov.in, gmcrajamahendravaram.ap.gov.in, gmceluru.ap.gov.in, gmcongole.org, rmckakinada.com
- Wikipedia articles (used only as secondary cross-check per instructions, and only via search
  snippets since direct fetch is blocked): Osmania General Hospital, Gandhi Medical College and
  Hospital, Niloufer Hospital, Telangana Vaidya Vidhana Parishad, Andhra Pradesh Vaidya Vidhana
  Parishad, King George Hospital Visakhapatnam, Sri Venkateswara Ramnarain Ruia Government
  General Hospital, Kurnool Medical College, Guntur Medical College, Rangaraya Medical College,
  Siddhartha Medical College, Government Medical College Anantapur/Kadapa/Sangareddy, Rajiv
  Gandhi Institute of Medical Sciences Adilabad, List of districts of Andhra Pradesh
- Secondary aggregators (used only to cross-check, never as sole source for a fact where
  avoidable): Medindia hospital directories, Mappls/Justdial listings, mbbscouncil.com,
  moksh16.com, careers360.com and similar medical-college-admission aggregator sites

## Key Structural Findings

- **Telangana**: TVVP (Telangana Vaidya Vidhana Parishad) manages ~175 secondary-level
  hospitals statewide (8 District Hospitals + 103 Area Hospitals, per TVVP's own published
  figures found in search results), while the Directorate of Medical Education (DME) manages
  medical colleges and their attached teaching hospitals separately. TG has rapidly expanded
  from a handful of teaching hospitals (Osmania, Gandhi, Kakatiya/MGM) to ~19+ Government
  Medical Colleges by opening one per district since ~2018, converting former District/Area
  Hospitals into GMC-attached teaching hospitals (Mahabubnagar, Siddipet, Nalgonda, Suryapet,
  Nagarkurnool, Jagtial, Sangareddy, Vikarabad, Mancherial, Kothagudem, Khammam, Yadadri, etc).
  This means several TG "District/Area Hospital" names from older sources now refer to
  facilities that have since been reclassified as Teaching Hospitals — this dataset reflects
  the current (2024-2026) teaching status where confirmable.
- **Andhra Pradesh**: APVVP manages 228 hospitals (20 District Hospitals, 56 Area Hospitals, 117
  CHCs, 10 Speciality Hospitals, 25 Civil Dispensaries — CHCs and below out of scope here), per
  APVVP's own published figures. AP's DME similarly oversees medical colleges + teaching
  hospitals; the state has pursued a "medical college in every district" expansion (e.g. Eluru
  GMC est. 2023, Rajahmundry District Hospital upgraded to teaching status 01-06-2022).
  Several formerly independent "RIMS" (Rajiv Gandhi Institute of Medical Sciences) autonomous
  institutes (Kadapa, Ongole, Srikakulam, Adilabad in TG) have since been folded into the
  "Government Medical College, X" naming/administrative convention.

## Conflicting Information Found (and how it was handled)

1. **Bed counts**: Nearly every large teaching hospital had 2-4 different bed-count figures
   across sources (e.g., Guntur GGH: 1038 vs 1170 vs 1500; KGH Visakhapatnam: 1037 vs 1562 vs
   2000; Kakinada GGH: 1200 vs 1462 vs 1800; GMC Kadapa: 650 vs 715 vs 750). In each case the
   `bed_capacity` field records the range/conflict explicitly rather than picking one number
   silently, and `notes` flags it.
2. **Mahabubabad Area Hospital address**: `mahabubabad.telangana.gov.in` itself returns two
   different addresses on different pages ("Area Hospital" page vs "Area Govt. Hospital" page),
   and a third-party aggregator gives a third location description. Not resolved — recorded as
   a conflict in the row's notes; may represent two physically distinct facilities (main town
   hospital vs a mandal-level sub-facility) rather than a data error.
3. **Chittoor district hospital naming**: Search results surfaced at least four differently
   named facilities for Chittoor town ("Chittoor Government Hospital," "Government District
   Hospital," "Government General Hospital," "Government Area Hospital"), at two different
   addresses (Church Street/Thotapalyam vs Thenabanda Dargah/Kongareddy Palli). Likely a mix of
   the current main facility plus an older/renamed predecessor, but not disambiguated with the
   search-only access available this session. Flagged in notes; only one row included to avoid
   probable duplication.
4. **Nellore hospital naming**: "ACSR Government General Hospital," "DSR District Hospital,"
   and "DSR Headquarters Hospital" all appear in Nellore-district search results with different
   bed counts (750 / 553 / 350). These may be the same physical campus under different
   historical names, or distinct facilities. Only the ACSR GGH row (clearly the current teaching
   hospital of ACSR Government Medical College) was included; the DSR-named entries were not
   added as separate rows to avoid unverified duplication.
5. **Jagtial**: an older "Area Hospital, Jagtial" (Medindia listing) and the newer "Government
   General Hospital, Jagtial" (GMC teaching hospital) may be the same site pre/post upgrade, or
   distinct facilities. Only the current GMC-affiliated teaching hospital was included as a row;
   flagged in notes.

## Districts / Hospitals That Could NOT Be Verified (Explicit Gap List)

Given the strict scope (verifiable District/Area/Teaching Hospitals only, skip if unconfirmable)
and search-only access, the following are **known gaps** — districts or hospitals not
represented in the CSV because no reasonably reliable name/detail could be confirmed in the time
available, rather than because none exist:

**Telangana** — no verified row for: Warangal Rural, Hanumakonda (separate from Warangal
Urban/MGM), Rangareddy, Medchal-Malkajgiri, Vikarabad-adjacent CHCs, Medak, Kamareddy's exact
District Hospital address/beds (name confirmed, details PENDING), Rajanna Sircilla, Jayashankar
Bhupalpally, Mulugu, Komaram Bheem Asifabad, Peddapalli, Jogulamba Gadwal, Wanaparthy, Nirmal
(exact address/beds), and the full TVVP roster beyond the ~8 district-level facilities plus the
Bhadradri Kothagudem cluster and a handful of others explicitly named in search snippets. TVVP's
own site (`vvp.telangana.gov.in/content.php?U=2`, the "district-wise list of area hospitals")
was identified as the authoritative master list but its actual table content never appeared in
any search snippet (only the page title/link), and direct fetch is blocked — this is the single
biggest gap in TG coverage.

**Andhra Pradesh** — no verified row for: Anakapalli, Alluri Sitharama Raju, Parvathipuram
Manyam, Palnadu, Bapatla, Nandyal, Sri Sathya Sai, Annamayya, Dr. B.R. Ambedkar Konaseema
(most of these are newer 2022-reorg districts whose standalone District/Area Hospital, if any,
could not be confirmed by name in the time available). APVVP's own master list of all 20
District Hospitals and 56 Area Hospitals (referenced generically via `apvvp.ap.gov.in` /
`apvvp.nic.in`) was likewise never returned as page content in search snippets — only summary
counts. This is the single biggest gap in AP coverage.

In both states, the master facility-list pages exist and were located (TVVP's
`content.php?U=2`, APVVP's home domains) but their tabular content could not be extracted
because WebFetch to `.gov.in` domains is blocked in this session and WebSearch only returns
short snippets/AI summaries rather than full page contents.

## Known Limitations

1. **No direct page fetches.** All facts derive from WebSearch result snippets/summaries, not
   from directly read source documents. This is inherently less reliable than reading a primary
   document in full — a snippet can omit context, and the search tool's own summarization step
   introduces a small risk of transcription drift. Confidence scores were capped conservatively
   (max 88) to reflect this.
2. **Master hospital-list pages (TVVP, APVVP) were never actually read**, only referenced by
   URL and by aggregate counts (e.g. "175 TVVP hospitals," "228 APVVP hospitals") mentioned in
   other pages/summaries. This is why district coverage is uneven — well-covered where a
   government medical college (with its own marketing-heavy web presence, easily surfaced by
   search) exists, thinner where only a plain District/Area Hospital exists with minimal web
   footprint.
3. **Bed counts and some addresses are frequently inconsistent** across secondary/aggregator
   sources (see "Conflicting Information" above); where this occurs it is disclosed in-row
   rather than silently resolved.
4. **Category churn**: Telangana in particular has been actively converting former
   District/Area Hospitals into GMC-affiliated Teaching Hospitals over the past 5-8 years. Some
   sources describing a facility as a plain "District Hospital" may be outdated relative to its
   current (2025-2026) teaching status, or vice versa. Rows reflect the most recent status found
   in search results, but given the pace of change some may already be stale by the time this is
   read.
5. **No independent confirmation of `managing_organization` per hospital.** The
   Teaching-Hospital rows' `managing_organization` value ("Directorate of Medical Education,
   Telangana/Andhra Pradesh") reflects the *general, confirmed administrative convention*
   (DME administers medical colleges + attached teaching hospitals; TVVP/APVVP administers
   standalone District/Area Hospitals) rather than a hospital-by-hospital confirmation. This
   convention itself was corroborated via DME's own site descriptions in both states, but should
   still be treated as a structural inference, not a per-row primary-source fact.
6. **Row count (49)** is below the upper end of the 40-70 target range specifically because
   several partially-identified hospitals (Jagtial's older Area Hospital, Nellore's DSR-named
   facilities, one of the two Chittoor addresses) were deliberately **excluded** rather than
   added as probably-duplicate or unverifiable rows, per the "quality over count" instruction.
