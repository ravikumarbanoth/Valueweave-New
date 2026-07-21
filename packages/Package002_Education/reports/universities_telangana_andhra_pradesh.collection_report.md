# Collection Report: Universities in Telangana and Andhra Pradesh

**Package:** ValueWeave Package002_Education v1.0.0
**Collection date:** 2026-07-21
**Output file:** `universities_telangana_andhra_pradesh.csv` (61 data rows)

## 1. Methodology

The goal was to identify genuine, degree-granting, university-level institutions
(state universities, central universities, deemed universities, Institutes of
National Importance, and well-documented private universities) located in
Telangana (TG) and Andhra Pradesh (AP), and to record verifiable facts about
each — never inventing or guessing a value.

**Tooling constraint encountered:** The `WebFetch` tool was non-functional for
the entire session — every attempted fetch (including to `osmania.ac.in`,
`en.wikipedia.org`, and even `google.com`) returned an HTTP 403 from the
session's egress proxy (`connect_rejected: gateway answered 403 to CONNECT
(policy denial or upstream failure)`, per `/root/.ccr/__agentproxy/status`).
This means no page was directly fetched and read in full during this research
pass. All facts below were instead assembled from `WebSearch` result snippets,
which return AI-summarized excerpts of multiple search results (typically
Wikipedia, university sites reflected in secondary aggregators, and education
portals such as Careers360, Shiksha, Collegedunia, CollegeDekho, and
Grokipedia). Search snippets in most cases explicitly cited or quoted content
sourced from official `.ac.in`/`.edu.in` domains (e.g., establishment year,
address, official website URL), but because the underlying page itself could
not be independently fetched and verified in this session, **confidence
scores throughout this dataset were kept in the 58–75 range** (i.e., treated
as portal/secondary-sourced or search-snippet-sourced, per the task's
guidance that only directly-fetched official sources warrant the 85–95 band).
This is a conservative, honest calibration given the tooling failure, not a
reflection of doubt about the institutions' existence.

**Process per institution:**
1. Identify candidate university via UGC/Wikipedia list searches and general
   knowledge of the two states' higher-education landscape.
2. Run a targeted `WebSearch` query combining the university name with
   "established year," "official website," and "NAAC grade" or "NIRF rank."
3. Cross-check establishment year, location, and website against at least
   two independent snippets (typically Wikipedia + a portal, or Wikipedia +
   the institution's own about page as quoted in the snippet).
4. Where NAAC grade, NIRF rank, or Vice-Chancellor name could not be found
   with a clearly current, reliable source in the search results, the field
   was set to the literal string `PENDING_VERIFICATION` rather than guessed.
5. Vice-Chancellor names were **not** populated for any row in this pass —
   no search was run specifically to find current VC names (a volatile,
   frequently-changing field), and per the task's instruction this field is
   left `PENDING_VERIFICATION` for all 61 rows to avoid reporting stale or
   unverified appointments.

## 2. Sources consulted

Representative sources referenced across the ~45 WebSearch queries run
(full per-row citations are in each row's `source_url` field):

- Wikipedia articles for individual universities (e.g.,
  https://en.wikipedia.org/wiki/Osmania_University,
  https://en.wikipedia.org/wiki/Andhra_University,
  https://en.wikipedia.org/wiki/Central_University_of_Andhra_Pradesh)
- Official university domains as referenced/quoted within search snippets
  (e.g., osmania.ac.in, jntuh.ac.in, uohyd.ac.in, andhrauniversity.edu.in,
  gitam.edu, kluniversity.in, rgukt.ac.in, cuap.ac.in, ctuap.ac.in)
- UGC-related search results (ugc.gov.in consolidated university lists,
  surfaced in search but not independently fetched)
- Telangana district government portals (e.g., mahabubnagar.telangana.gov.in,
  karimnagar.telangana.gov.in) and AP district portals (srikakulam.ap.gov.in,
  spsnellore.ap.gov.in) for a subset of state universities
- Education portals used for ranking/accreditation cross-checks: Careers360,
  Shiksha, Collegedunia, CollegeDekho, Grokipedia, UniversityGuru
- News coverage of NIRF 2025 rankings: Telangana Today
  (telanganatoday.com), Sakshi Education (education.sakshi.com),
  Deccan Chronicle

## 3. Conflicts found and resolution

- **Kakatiya University NAAC grade:** search snippets disagreed between "A"
  (3.02 CGPA, 2023 cycle) and "A+" (an earlier or differently-sourced claim).
  Recorded the more specific, dated figure (A, 3.02 CGPA, 2023) and flagged
  the discrepancy explicitly in the `notes` field.
- **Potti Sreeramulu Telugu University name:** current sources show it may
  now be referred to as "Suravaram Pratap Reddy Telugu University." Kept the
  historically dominant name as the primary `name` field and flagged the
  rename in `notes` for downstream verification against the state gazette.
- **Sreenidhi University establishment year:** sources conflict between 2021,
  2022, and 2024 for when the university (as distinct from its parent
  Sreenidhi Institute of Science & Technology, est. 1997) was formally
  constituted. Recorded 2022 with the conflict explicitly noted; confidence
  score lowered to 58 (the lowest in the dataset) to reflect this.
- **Dr. NTR University of Health Sciences naming:** the university's name
  reportedly reverted from "NTR University of Health Sciences" back to
  "Dr. NTR University of Health Sciences" in July 2024 — noted for downstream
  awareness.
- **JNTU-GV (Vizianagaram) vs. its constituent college:** the constituent
  College of Engineering Vizianagaram (est. 2007, later under JNTUK) is
  distinct from the independent university JNTU-GV, which was only
  constituted in January 2022. Both dates are recorded in `notes` to avoid
  confusing the two.
- **RGUKT as a multi-campus system:** RGUKT operates linked but administratively
  distinct campuses — Basar (Telangana) and Nuzvid, RK Valley, and Srikakulam
  (Andhra Pradesh). Only Basar (TG) and Nuzvid (AP) were independently
  verified and included as separate rows; RK Valley and Srikakulam campuses
  were not separately researched/verified in this pass (see Gaps below).

## 4. Universities considered but excluded (and why)

- **Indian School of Business (ISB), Hyderabad** — not a UGC-recognized
  degree-granting university; operates autonomous PGP diploma programs, not
  a university in the sense required by this task.
- **RGUKT RK Valley and RGUKT Srikakulam (AP campuses)** — plausible
  additional rows, but not independently verified with a dedicated search in
  this pass; excluded rather than guessed. Flagged as a gap below.
- **Indian Institute of Chemical Technology (IICT), Hyderabad** — a CSIR
  research laboratory, not a degree-granting university.
- Numerous small/obscure private "universities" and skill-development
  institutions surfaced in search results (e.g., various single-campus
  private engineering colleges not yet elevated to university status, or
  very recently notified private universities with minimal independent
  corroboration) were deliberately excluded to keep the dataset to
  genuinely well-documented, verifiable institutions rather than inflating
  row count with unverifiable entries, per the task's explicit guidance.
- **Andhra Pradesh State Skill Development University** and similar very
  newly notified institutions were not included — insufficient independent
  corroboration was found in the searches performed.

## 5. Known gaps

- **Vice-Chancellor names are `PENDING_VERIFICATION` for all 61 rows.** This
  is intentional: VC appointments change frequently, no dedicated
  current-VC search was performed for any institution in this pass, and the
  task explicitly instructs against filling this field without a clearly
  current, reliable source.
- **NAAC grade and NIRF rank are `PENDING_VERIFICATION` for the majority of
  rows** — these were only populated where a search snippet gave an
  explicit, clearly-dated figure (mostly the largest/most prominent
  universities: Osmania, Andhra University, Acharya Nagarjuna University,
  Sri Venkateswara University, University of Hyderabad, IIT Hyderabad, NIT
  Warangal, GITAM, KL University, VIT-AP, Anurag University, JNTUK, RGUKT
  Basar). Smaller state universities and most of the agricultural/
  veterinary/health-sciences universities had no reliable current
  NAAC/NIRF figures surfaced in search.
- **WebFetch tool was unavailable for the entire session** (organization
  egress policy blocked outbound HTTPS CONNECT to all tested external
  hosts, including google.com). No page was directly fetched and read in
  full; all data is derived from WebSearch's summarized snippets. This
  should be treated as a data-quality caveat for the whole dataset —
  confidence scores were deliberately capped below the 85–95 "direct
  official source" band as a result. A follow-up pass with working direct
  fetch access to `.ac.in`/`.gov.in` domains and the UGC university portal
  is recommended to raise confidence and fill the PENDING_VERIFICATION
  fields.
- **UGC master list was not directly cross-checked row-by-row** — the
  UGC consolidated PDF list of universities (ugc.gov.in) was surfaced in
  search results but not fetched/parsed directly; the dataset instead relies
  on convergent Wikipedia/portal/official-site-snippet identification. A
  formal cross-check against the current UGC list is recommended.
- **Affiliated/constituent colleges were intentionally excluded** per task
  scope — only apex, degree-granting university bodies are included.
- Some very small or newly upgraded state universities in AP/TG (e.g.,
  any additional universities created since 2023 not surfaced in this
  research pass) may be missing; the list targets ~35-60 well-documented
  institutions rather than being exhaustive.

## 6. Row count summary

- **Total rows:** 61
- **Telangana:** 29 — 15 State University, 3 Central University,
  3 Deemed University, 6 Private University, 2 Institute of National
  Importance
- **Andhra Pradesh:** 32 — 21 State University (including specialized
  agricultural/veterinary/horticultural/health-sciences/law/women's
  universities), 2 Central University, 4 Deemed University,
  2 Private University, 3 Institute of National Importance
