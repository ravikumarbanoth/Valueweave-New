# Collection Report: Training Centres (ITIs, PMKKs, Polytechnics, Skill Development Centres)

**Package:** ValueWeave Package006_Skills_and_Training v1.0.0
**Collection date:** 2026-07-24
**Output file:** `datasets/training_centres.csv` (22 data rows)

## 1. Methodology

The goal was to identify genuine, named, district-level skill-training centres —
Government Industrial Training Institutes (ITIs), Pradhan Mantri Kaushal
Kendras (PMKKs), Government Polytechnics, and government-backed skill
development centres — in Telangana and Andhra Pradesh, and to record only
verifiable facts about each, cross-referenced to Package001_Geography's
district UUIDs. Per the task's explicit instruction, no centre was invented to
pad geographic coverage; the dataset intentionally covers 17 of 61 districts
because that is what could genuinely be sourced and cross-checked in this
research pass.

**Tooling constraints encountered:**
- **WebFetch to `.gov.in` / `.ac.in` / `.nic.in` domains is blocked** in this
  environment (confirmed policy in the task brief). This means official ITI
  portals (`iti.telangana.gov.in`), the Directorate of Technical Education
  (`dte.telangana.gov.in`), and the Directorate General of Employment
  (`dge.gov.in`) could never be fetched and read directly — only their
  existence and snippet content as surfaced by `WebSearch` results could be
  used. Confidence scores were kept below the 85-95 "direct official fetch"
  band throughout as a result, consistent with the precedent set in this
  project's Package002_Education universities report.
- **The session's WebSearch call budget (200 calls) was exhausted mid-research**,
  before two planned follow-up queries (S.V. Government Polytechnic, Tirupati
  detail; Government Polytechnic Kalikiri detail) could be run. The Kalikiri
  row was still populated adequately from an earlier batched query that had
  already returned good detail (including the institution's own domain,
  `govtpolykalikiri.ac.in`). The Tirupati row could not be enriched beyond
  confirming the institution's name and general existence via a single
  search-result title, and is flagged as the weakest-sourced row in the
  dataset (confidence 50, most fields `PENDING_VERIFICATION`).

**Process per centre:**
1. Ran targeted `WebSearch` queries combining a district or city name with
   "Government ITI," "Government Polytechnic," "PMKK," or "APSSDC skill
   development centre," prioritizing the ten districts named in the task
   brief as most likely to have documented centre-level detail (Hyderabad,
   Ranga Reddy, Warangal, Karimnagar, Nizamabad; Visakhapatnam, Krishna/NTR,
   Guntur, Kurnool, Chittoor), then extended to Khammam, Nalgonda, Adilabad,
   Mahbubnagar, and Kakinada/East Godavari as additional real, well-documented
   candidates surfaced.
2. For each candidate, cross-checked the centre's name, address, and trades/
   courses against at least two independent search-result snippets where
   possible (a mix of the institution's own domain when it appeared directly
   in results — e.g. `mbtsgovtpolyguntur.ac.in`, `govtpolyvisakhapatnam.in`,
   `govtpolykalikiri.ac.in`, `sdivisakh.in` — and third-party aggregators such
   as `iti.directory`, Shikshan.org, Careers360, Shiksha, CollegeDunia, and
   the Directorate General of Employment's (`dge.gov.in`) district employment
   exchange node listings).
3. Where a fact (trades list, exact street address, official website,
   founding year) could not be found with a clear, corroborated source, the
   field was set to the literal string `PENDING_VERIFICATION` rather than
   guessed, and an explanation was appended to `notes` in the required
   `[field_name]: explanation` format.
4. Each centre was mapped to a `district_id` from the exact UUID list supplied
   in the task. Several centres required a judgment call because Telangana
   (2016) and Andhra Pradesh (2022) both underwent district reorganizations
   after these institutions were established — see Section 3 below.

## 2. Sources consulted (representative)

- Institution's own domains surfaced directly in search results (treated as
  the strongest available signal, though never independently fetched):
  `mbtsgovtpolyguntur.ac.in`, `govtpolyvisakhapatnam.in`,
  `govtpolykalikiri.ac.in`, `sdivisakh.in`
- Directorate General of Employment, Government of India — district
  employment exchange node listings (`dge.gov.in/dge/node/...`), surfaced via
  search snippet only (not directly fetched, per the `.gov.in` WebFetch block)
- Telangana ITI Directorate Annexure-I ITI list PDF
  (`iti.telangana.gov.in/assets/pdf2024/...` and `pdf2025/...`) — surfaced in
  search results but not fetched directly
- Third-party ITI/polytechnic directories and aggregators: `iti.directory`,
  Shikshan.org, Careers360, Shiksha, CollegeDunia, TargetStudy, JustDial,
  UniversityDunia, AmpleTrails
- Ministry of Petroleum & Natural Gas refining/skill-development page
  (`mopng.gov.in`) and National Skills Network (`nationalskillsnetwork.in`)
  for the Skill Development Institute, Visakhapatnam
- Business-listing pages (britishschooloflanguages.com, JustDial) for the
  one PMKK entry (Nizamabad)

## 3. District-mapping judgment calls (post-reorganization centres)

Telangana's 2016 district reorganization and Andhra Pradesh's 2022 district
reorganization both created new districts from parts of older, larger ones.
Several sourced centres are indexed by aggregators under the *old* district
name/grouping. These were re-mapped to the *current* district matching the
supplied UUID list, with the discrepancy flagged explicitly in each row's
`notes` field:

- **Government ITI, Peddapalli** — aggregator groups it under the old,
  undivided Karimnagar district directory; mapped to **Peddapalli** (a
  separate district since 2016).
- **Government ITI, Kothagudem** — aggregator groups it under the old Khammam
  district directory; mapped to **Bhadradri Kothagudem** (separate since 2016).
- **Government Residential ITI, Mannanur (Achampet)** — aggregator groups it
  under the old, undivided Mahbubnagar district directory; Achampet/Mannanur
  are administratively within **Nagarkurnool** district (formed 2016) and
  the row is mapped there, not to Mahabubnagar.
- **Government Industrial Training Institute, Vijayawada** — mapped to
  **NTR** district, since Vijayawada became the NTR district headquarters in
  AP's 2022 reorganization (carved out of the former Krishna district).
- **Andhra Polytechnic, Kakinada** and **Government Polytechnic for Women,
  Kakinada** — mapped to **Kakinada** district, formed in 2022 from the
  former East Godavari district (whose separate, smaller successor district
  also still exists in the supplied ID list and was *not* used for these two
  Kakinada-town institutions).
- **Government Polytechnic, Warangal** — Warangal city today straddles the
  Warangal and Hanumakonda districts (split 2019); mapped to **Warangal**
  district pending precise campus-side confirmation, and flagged in notes.

## 4. Conflicts found and resolution

- **Government ITI, Vijayawada address:** one aggregator (TargetStudy) gave a
  pin code (531116) that actually corresponds to the Tuni/East Godavari area,
  not Vijayawada — almost certainly a data error in that source. No precise
  street address is asserted for this row; the address field records only
  the city/district-level location, and the discrepancy is noted.
- **Government ITI, Nizamabad official website:** one aggregator mentioned a
  domain (`itibnzb.com`) that could not be independently confirmed as the
  institute's own official site (it has the appearance of a third-party
  listing page rather than a verified institutional domain), so
  `official_website` was left `PENDING_VERIFICATION` rather than asserted.
- **Skill Development Institute (SDI), Visakhapatnam centre_type:** SDI is a
  distinct Ministry of Skill Development & Entrepreneurship (MSDE) / PSU-
  consortium skill institute model (est. October 2016, promoted by 8 Ministry
  of Petroleum & Natural Gas PSUs led by HPCL), not a standard ITI, PMKK, or
  polytechnic. It was mapped to the closest available schema category, **"State
  Skill Development Centre,"** with a note flagging this as an imperfect fit
  worth a schema review.

## 5. Centres/districts considered but excluded (and why)

- **Ranga Reddy district** — no dedicated, clearly-real, centre-level ITI or
  PMKK could be distinguished from Hyderabad-proper listings in the searches
  run (one aggregator result appeared to conflate a Hyderabad Mallepally ITI
  campus with a "Rangareddy" tag). Rather than guess which real centre sits
  in present-day Ranga Reddy district, this district was left uncovered.
- **PMKK centres in Karimnagar and Warangal** — searched for explicitly; no
  named, address-confirmed PMKK surfaced for either district in this pass
  (only Nizamabad's PMKK was confirmed with a specific address).
- Numerous private/self-financing ITIs and polytechnics surfaced heavily in
  every district search (e.g., various "Industrial Training Centres" branded
  as private) were deliberately excluded — the task scope prioritizes
  government-run/government-affiliated centres (Government ITI, PMKK,
  Government Polytechnic, State Skill Development Centre), and private
  centres were only in scope as "Private/NSDC-Partner Training Centre" where
  a specific need arose; none were included in this pass to keep the dataset
  focused on the clearest government-backed cases.

## 6. Known gaps

- **Coverage is 17 of 61 districts.** This is an intentional, honest outcome
  per the task's explicit instruction not to fabricate centres to fill gaps.
  The 44 uncovered districts (e.g., all of Srikakulam, Vizianagaram,
  Anakapalli, East Godavari, Eluru, West Godavari, Palnadu, Bapatla,
  Prakasam, Nellore, Nandyal, Ananthapuramu, Sri Sathya Sai, YSR Kadapa,
  Annamayya, and most Telangana districts outside the ten prioritized by the
  task brief) were not researched in this pass at the same depth, and no
  centre is asserted for them.
- **`official_website` is `PENDING_VERIFICATION` for 12 of 22 rows** — a
  dedicated, independently-confirmed institutional domain (distinct from a
  government department listing page or a third-party aggregator) could not
  be found for these centres.
- **`skills_or_trades_offered` is `PENDING_VERIFICATION` for 6 of 22 rows**
  where no specific trade/course list was found for that exact campus, only
  for the district in general or a different nearby campus.
- **S.V. Government Polytechnic, Tirupati (row 22)** is the weakest-sourced
  row (confidence 50) — confirmed to exist via a single search-result title
  only; the planned enrichment query could not be run because this session's
  WebSearch call budget was exhausted. This row is a priority for a
  follow-up verification pass.
- **PMKK Nizamabad (SynchroServe)** was sourced only from third-party
  training-directory/business-listing pages, not the official NSDC PMKK
  locator (`nsdcindia.org/find-nsdc-training-centre-pmkk`), which could not
  be fetched directly. Downstream verification against that locator is
  recommended before treating this row as authoritative.
- **No page was directly fetched (WebFetch) in this entire pass** — every
  fact derives from `WebSearch` result snippets, consistent with the
  `.gov.in`/`.ac.in`/`.nic.in` WebFetch block described in the task brief.
  Confidence scores were calibrated conservatively (50-75 range) to reflect
  this, never exceeding the task's hard cap of 85.

## 7. Row count summary

- **Total rows:** 22
- **Districts covered:** 17 — Hyderabad (2), Karimnagar (1), Peddapalli (1),
  Nizamabad (2), Khammam (1), Bhadradri Kothagudem (1), Warangal (1),
  Nalgonda (1), Adilabad (2), Nagarkurnool (1), Visakhapatnam (2), NTR (1),
  Guntur (1), Kurnool (1), Kakinada (2), Chittoor (1), Tirupati (1)
- **By centre_type:** 12 Government ITI, 8 Government Polytechnic,
  1 Pradhan Mantri Kaushal Kendra (PMKK), 1 State Skill Development Centre
- **Confidence score range:** 50-75 (mean ~61.5); no row exceeds the 85 cap
- **`PENDING_VERIFICATION` cells:** 23 total across the dataset, all
  confirmed to be the exact bare string with no appended text
- **`verification_status`:** `VST-NEEDS_REVIEW` for all 22 rows
- **`collection_date`:** `2026-07-24` for all 22 rows
