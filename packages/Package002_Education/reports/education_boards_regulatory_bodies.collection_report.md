# Collection Report: Educational Boards & Regulatory Bodies
## ValueWeave Package002_Education v1.0.0

**Collection date:** 2026-07-21
**Collector:** Automated research agent (WebSearch-based)
**Output file:** `education_boards_regulatory_bodies.csv` (21 data rows, 16 columns)

---

## 1. Methodology

1. Compiled a target list of entities from the task brief: 13 national regulatory/testing/accreditation/statistics bodies (UGC, AICTE, NCTE, NCVET, NCERT, NIOS, CBSE, CISCE, NTA, NAAC, NBA, NIRF, AISHE) and 8 genuine state-level bodies for Telangana (SCERT-TG, BSE Telangana/SSC, TSBIE, TSCHE) and Andhra Pradesh (SCERT-AP, BSEAP, BIEAP, APSCHE).
2. For each entity, ran targeted `WebSearch` queries combining the entity name with "official website," "established year," "headquarters," and "ministry/department" to triangulate the four core verifiable facts.
3. Attempted `WebFetch` against primary official domains (`.gov.in`) and Wikipedia to directly confirm facts pulled from search snippets.
4. **Environment constraint discovered:** the session's outbound HTTPS proxy (`/root/.ccr/`) returned `403 connect_rejected` (organization policy denial, not a certificate/config issue) for essentially every direct `WebFetch` attempt in this session, including `bse.telangana.gov.in`, `ugc.gov.in`, `aicte-india.org`, `cbse.gov.in`, `naac.gov.in`, `tgche.ac.in`, `apscert.gov.in`, and `en.wikipedia.org`. Per the proxy README, policy-denial (403) responses are not to be retried or routed around. Consequently, **no fact in this dataset could be independently re-confirmed via direct page fetch** — all facts rely on `WebSearch` tool results, which do retrieve and synthesize live page content server-side but were the only channel available.
5. Because of (4), confidence scores were capped lower than they would be with direct-fetch confirmation: no row exceeds 88, and rows with conflicting source dates or unconfirmed canonical domains were scored 58-72.
6. Cross-checked each fact against at least two independent search results (official site snippet + at least one secondary portal or Wikipedia-derived summary via WebSearch) where possible.
7. Generated one UUID v4 per row programmatically (Python `uuid.uuid4()`), and validated the final CSV with Python's `csv` module (correct column count on every row, unique/valid UUIDs).

---

## 2. Sources Consulted

### National bodies
- https://www.ugc.gov.in/ and https://www.ugc.gov.in/Home/AboutUGC (UGC)
- https://www.education.gov.in/en/annual-reports/university-grants-commission-ugc (Ministry of Education)
- https://www.aicte-india.org/ and https://www.aicte-india.org/about-us/history (AICTE)
- https://ncte.gov.in/website/index.aspx and https://web.ncte.gov.in/ (NCTE)
- https://dsel.education.gov.in/en/ncte (Dept. of School Education & Literacy)
- https://ncvet.gov.in/ and https://ncvet.gov.in/about-ncvet/ (NCVET)
- https://www.msde.gov.in/ministry/our-organisation/details/national-council-for-vocational-education-and-training-ncvet (MSDE)
- https://ncert.nic.in/about-us.php?ln=en (NCERT)
- https://nios.ac.in/ (NIOS)
- https://www.cbse.gov.in/ and https://www.cbse.gov.in/cbsenew/history.html (CBSE)
- https://en.wikipedia.org/wiki/Council_for_the_Indian_School_Certificate_Examinations and https://www.asklaila.com listing (CISCE - secondary only, no official .gov.in equivalent since it is a private body)
- https://exams.nta.nic.in/about-us/ and https://nta.ac.in/about (NTA)
- https://www.ugc.gov.in/Aboutus/NAAC and http://naac.gov.in/ (NAAC)
- https://www.nbaind.org/ (NBA)
- https://www.nirfindia.org/Home/About (NIRF)
- https://aishe.gov.in/about-survey/ and https://aishe.gov.in/about-department/introduction/ (AISHE)

### Telangana
- https://scert.telangana.gov.in/ (SCERT Telangana)
- https://bse.telangana.gov.in/ and https://www.bsetelanganagov.in / https://www.bset.ac/ (BSE Telangana - domain conflict, see Section 3)
- https://tsbie.cgg.gov.in/home.do and https://tgbie.in/ (TSBIE - domain conflict, see Section 3)
- https://tgche.ac.in/history/ and https://tweb.telangana.gov.in/departments/higher-education-department/telangana-state-council-of-higher-education/ (TSCHE)

### Andhra Pradesh
- https://scert.ap.gov.in/SCERT/ and https://apscert.gov.in/ (SCERT AP - domain conflict, see Section 3); https://www.deccanchronicle.com/southern-states/andhra-pradesh/scert-office-relocated-to-atmakuru-1869864 (2025 office relocation, secondary news source)
- https://en.wikipedia.org/wiki/Andhra_Pradesh_Board_of_Secondary_Education (BSEAP - Wikipedia-derived only, no clean official-domain snippet located)
- https://en.wikipedia.org/wiki/Board_of_Intermediate_Education,_Andhra_Pradesh and https://www.schools360.in/ap-intermediate-board-new-address/ (BIEAP)
- https://apsche.ap.gov.in/ (APSCHE)

All URLs above were surfaced and read via the `WebSearch` tool (which fetches and summarizes page content server-side); none were independently re-verified with a direct `WebFetch`/`curl` due to the session-wide proxy policy denial described in Section 1, item 4.

---

## 3. Conflicting Information Found and How It Was Resolved

| Entity | Conflict | Resolution |
|---|---|---|
| AICTE | Founding year: 1945 (as advisory body) vs. 1987 (statutory status via Act of Parliament) | Recorded `established_year = 1945` (true founding date) and noted the 1987 statutory conversion in the `notes` field. |
| NCTE | Founding: 1973 (as non-statutory advisory body) vs. 1995 (statutory body under NCTE Act 1993, enforced 1 July 1995) | Recorded `established_year = 1995` since NCTE as a *regulatory* body (matching the "type" column) legally exists from that date; 1973 origin noted. |
| CISCE | Official domain: `cisce.org`, `cisceboard.org`, `cisce.net`, `csisce.org.in` all appear in search results, several looking like mirror/unofficial sites | Selected `cisce.org` based on matching registered-office contact email (`council@cisce.org`) found in a secondary source; confidence lowered to 62 and conflict flagged in `notes`. |
| BSE Telangana | Domain variants: `bse.telangana.gov.in`, `bsetelanganagov.in`, `bset.ac` | Selected `bse.telangana.gov.in` as the only `.gov.in` (government) domain among the variants; confidence lowered to 65 since it could not be fetch-confirmed. |
| BIEAP | Domain variants: `bie.ap.gov.in`, `bieap.gov.in`, `bieap-gov.org`, `bieap.apcfss.in` | Selected `bieap.gov.in`, matching the address given in the most detailed secondary source (schools360.in office-relocation article); flagged as unconfirmed in `notes`. |
| BSEAP (Andhra Pradesh) | Establishment year: some sources say 1953 (informal genesis at AP's formation as a linguistic state), others cite a Government Order dated 16-01-1969 | Recorded `established_year = 1969` as the more specific, citable, GO-documented date; 1953 origin claim noted; confidence lowered to 58 (lowest in the dataset) due to this unresolved conflict. |
| SCERT AP headquarters | Office relocated from Vijayawada to Atmakuru (Mangalagiri, Guntur District) around March 2025 per a Deccan Chronicle report | Used the post-relocation address since it is the most recent; flagged as sourced from a single secondary news report, not a government notification, so confidence is 68 rather than higher. |

---

## 4. Entities Considered but Excluded

- **Department of School Education & Literacy (DSEL)** and **Department of Higher Education (DHE)** — these are Ministry of Education *departments*, not boards/regulatory bodies in their own right; they appear as the `parent_ministry_or_department` value for multiple rows instead of being listed as standalone entities.
- **National Skill Development Agency (NSDA)** and erstwhile **National Council of Vocational Training (NCVT)** — both were formally subsumed into NCVET in 2018 and no longer operate as independent regulators; excluded as defunct/absorbed.
- **Indian Nursing Council, Bar Council of India, Medical Council of India/National Medical Commission, Pharmacy Council of India** — genuine national regulators, but for professional/vocational licensing rather than general school/higher-education regulation or accreditation as scoped by the task; excluded to stay within the requested focus.
- **Central Advisory Board of Education (CABE)** — an advisory/consultative forum rather than a regulatory or standards body; excluded for being out of scope (not a "board" in the school/university-regulation sense).
- **TREIS (Telangana Residential Educational Institutions Society)** and equivalent AP residential-school societies — these are institution-operating bodies, not regulatory/curriculum/examination boards; excluded as out of scope.
- **AP Board of Education (apbe.co.in)** — appeared in search results as a name similar to BSEAP, but could not confirm it is a genuine distinct government body rather than a private coaching/content portal; excluded rather than risk including a non-authoritative entity.

---

## 5. Known Gaps / PENDING_VERIFICATION Fields

- **1 field** explicitly marked `PENDING_VERIFICATION`: `headquarters_city` for **APSCHE** (Andhra Pradesh State Council of Higher Education) — search results confirmed the official domain (`apsche.ap.gov.in`) and the 1988 founding act, but no source located gave a specific current headquarters city/address (likely somewhere in the Vijayawada/Guntur/Amaravati administrative area post-2014, but this was not confirmed to the standard required to state it as fact).
- **No other field uses the literal `PENDING_VERIFICATION` string**, but several rows carry material uncertainty flagged in `notes` and reflected in lower `confidence_score` values (58-72) rather than being blanked out, specifically:
  - CISCE canonical website domain (confidence 62)
  - BSE Telangana canonical website domain (confidence 65)
  - BIEAP canonical website domain (confidence 62)
  - BSEAP establishment year conflict (confidence 58 — lowest in the dataset)
  - SCERT AP headquarters (relocation reported by a single secondary news source, confidence 68)
- **Systemic caveat:** every row in this dataset was sourced exclusively through the `WebSearch` tool. Direct `WebFetch` verification against primary `.gov.in` sources and Wikipedia was attempted for ~10 entities but blocked in every case by a `403 connect_rejected` organization policy denial at the session's egress proxy (confirmed via `curl $HTTPS_PROXY/__agentproxy/status`, which logs these as `policy denial or upstream failure`, not a fixable client-side certificate/config issue). No score in the dataset exceeds 88 as a result, and this constraint is recorded in the `notes` field of the affected rows. A governance reviewer with unrestricted network access should re-fetch primary sources for all rows before promoting any of them out of `VST-NEEDS_REVIEW`.

---

## 6. Summary Statistics

- **Total rows:** 21 (13 national + 4 Telangana + 4 Andhra Pradesh)
- **Distinct sources cited:** 25+ URLs across official `.gov.in`/institutional domains and secondary/cross-check sources (Wikipedia, education news portals)
- **Confidence score range:** 58-88 (mean ≈ 75)
- **Verification status:** all rows `VST-NEEDS_REVIEW` per task specification
- **PENDING_VERIFICATION fields:** 1 (APSCHE headquarters_city)
