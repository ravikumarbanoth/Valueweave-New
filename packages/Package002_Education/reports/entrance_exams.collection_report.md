# Collection Report — Entrance Exams (Package002_Education v1.0.0)

Collection date: 2026-07-21
Researcher: Claude (web-search-based knowledge engineering)
Output file: `entrance_exams.csv` (28 rows)

## Methodology

1. Built a target list of exams from the task brief: 12 named national exams, 12 named
   Telangana/Andhra Pradesh state exams (6 categories x 2 states), plus a small number of
   additional genuine national exams (XAT, ICAR AIEEA-PG, GPAT) identified during research
   as commonly grouped with this exam set.
2. For every exam, ran targeted web searches combining the exam name, current year (2026),
   and terms "official website," "conducting body," and "eligibility." Searches were run in
   parallel batches by exam family (engineering/medical, law, management, state CETs).
3. Prioritized government/exam-authority domains when selecting `official_website` and
   `source_url`: `nta.ac.in` / `nta.nic.in` / `exams.nta.nic.in` subdomains, `natboard.edu.in`,
   `consortiumofnlus.ac.in`, `jeeadv.ac.in`, `ctet.nic.in`, `cets.apsche.ap.gov.in`,
   `*.tgche.ac.in`, `polycet.sbtet.telangana.gov.in`, `appolycet.nic.in`. Education portals
   (Careers360, Shiksha, Testbook, Collegedekho, etc.) were used only as secondary
   cross-checks or where an official page could not be directly confirmed to load.
4. Attempted direct `WebFetch` of two official pages (`gpat.nta.nic.in`, `exams.nta.nic.in/cuet-pg/`)
   to pull primary text; both returned HTTP 403 (likely bot-blocking), so those two rows rely on
   search-result excerpts of the same official domains plus portal corroboration rather than a
   direct fetch — reflected in slightly lower confidence scores than fully-fetched pages.
5. Assigned `exam_level` using the 4-value enum required by the schema (Undergraduate,
   Postgraduate, Diploma/Polytechnic, Doctoral/Fellowship). Two categories of exam did not map
   cleanly onto a single degree level (CTET, and the B.Ed entrance tests TG/AP EdCET); the
   judgment call made in each case is recorded in that row's `notes` field.
6. `confidence_score` was set per-row: 85-92 where an official government/exam-authority
   domain was directly identified and consistent across multiple sources; 72-80 where the fact
   was only obtainable via cross-checked education portals, where an official page could not be
   loaded directly, or where the fact concerns a forward-looking detail not yet officially
   notified (e.g., GATE 2027 host institute).
7. Generated `id` values as UUIDv4 via Python's `uuid` module. All rows use
   `collection_date = 2026-07-21` and `verification_status = VST-NEEDS_REVIEW` per instructions.
8. Validated the final CSV programmatically (Python `csv` module round-trip) to confirm exactly
   15 columns per row, no malformed rows, and unique `id` values.

## Sources consulted (representative)

**National exams**
- https://jeemain.nta.nic.in/ (JEE Main)
- https://jeeadv.ac.in/ and https://jeeadv.ac.in/eligibility.html (JEE Advanced)
- https://neet.nta.nic.in/ and https://neet.nta.nic.in/about-department/introduction/ (NEET UG)
- https://natboard.edu.in/ (NEET PG, GPAT, NEET SS)
- https://cuet.nta.nic.in/ (CUET UG)
- https://exams.nta.nic.in/cuet-pg/ (CUET PG)
- https://consortiumofnlus.ac.in/ and https://www.shiksha.com/law/articles/consortiumofnlus-ac-in-clat-official-website-blogId-188634 (CLAT)
- https://iimcat.ac.in/ (CAT)
- https://gate.iitm.ac.in/ and https://engineering.careers360.com/articles/which-iit-will-conduct-gate-2027-check-official-details (GATE)
- https://ugcnet.nta.nic.in/ (UGC NET)
- https://ctet.nic.in/ (CTET)
- https://xatonline.in/ (XAT)
- https://exams.nta.nic.in/icar/ (ICAR AIEEA PG)

**Telangana exams**
- https://eapcet.tgche.ac.in/ (TG EAPCET)
- https://icet.tgche.ac.in/ (TG ICET)
- https://edcet.tgche.ac.in/ (TG EdCET)
- https://pgecet.tgche.ac.in/ (TG PGECET)
- https://lawcet.tgche.ac.in/ (TG LAWCET / TG PGLCET)
- https://polycet.sbtet.telangana.gov.in/ (TG POLYCET)

**Andhra Pradesh exams**
- https://cets.apsche.ap.gov.in/EAPCET/, /ICET/, /EDCET/, /PGECET/, /LAWCET/ (AP CETS portal family)
- https://appolycet.nic.in/ and apsbtet.ap.gov.in (AP POLYCET)

Secondary/cross-check portals used throughout: Careers360 (and its engineering/medicine/law/mba
subdomains), Shiksha, Testbook, Collegedekho, Collegedunia, Manabadi, Sakshi Education, MBAUniverse,
PW Live.

## Conflicts found and resolution

1. **GPAT conducting body**: Older material and one stale URL (`gpat.nta.nic.in`) still show NTA
   as the conductor. Multiple 2026-dated news sources (India TV, Business Standard, Careers360)
   confirm GPAT was transferred to NBEMS (with PCI) starting the 2024 cycle. Resolved in favor of
   NBEMS/natboard.edu.in as current; noted the outdated NTA reference in `notes`.
2. **GATE 2027 organizing institute**: Sources consistently reported IIT Madras as the incoming
   host for the 2027 cycle (following IIT Guwahati for 2026), but no official GATE notification/
   brochure had been published as of the collection date. Recorded IIT Madras as the reported
   institute but flagged it as unconfirmed and lowered confidence to 72 with an explicit
   re-verification note.
3. **AP EdCET conducting university**: One portal source suggested Dravidian University, Kuppam;
   the majority of sources, including the 2026 notification's convenor contact details
   ("Convenor AP EDCET-2026, Acharya Nagarjuna University"), point to Acharya Nagarjuna
   University, Guntur. Resolved in favor of Acharya Nagarjuna University; the alternative claim
   is recorded in `notes` for transparency.
4. **CUET PG / GPAT official domains blocked**: Direct WebFetch attempts on `exams.nta.nic.in/cuet-pg/`
   and `gpat.nta.nic.in` returned HTTP 403. Data for these rows is instead drawn from search-engine
   result snippets of the same official domains, cross-checked against multiple portals — treated
   as slightly lower-confidence than directly fetched pages.
5. **ICAR AIEEA UG vs PG**: Multiple sources confirmed ICAR discontinued the standalone AIEEA UG
   exam after 2022/2023, with UG admissions folded into CUET (ICAR-UG) conducted by NTA. Only the
   still-active AIEEA PG exam was included, to avoid presenting a discontinued exam as current;
   the discontinuation and replacement mechanism is documented in that row's `notes`.

## Exams considered but excluded, and why

- **ICAR AIEEA (UG)** — discontinued after 2022/2023; superseded by CUET (ICAR-UG). Excluded to
  avoid listing an inactive exam as active (see row notes on AIEEA PG for the replacement path).
- **NDA/NA (UPSC)** — genuine national entrance exam, but it is a defense-services commissioning
  exam rather than a general higher-education entrance exam, and sits outside the education-system
  scope of this package; excluded for scope reasons, not because it is inactive.
- **MAT (AIMA)** — a real, currently active national MBA entrance exam, but was excluded to keep
  the dataset within the ~20-28 row target once XAT was included as the flagship additional
  management exam; can be added in a follow-up pass if broader MBA-exam coverage is wanted.
- **NEET SS (super-speciality)** — verified as genuine and currently active (NBEMS, exam scheduled
  Dec 2026), but was cut from the final row set purely to keep total rows within the requested
  20-28 range, prioritizing the more foundational/high-volume exams (NEET UG/PG, GATE, CAT, etc.).
  It can be reinstated easily; verified facts are noted here for reference: official site
  natboard.edu.in / nbe.edu.in, admits to DM/MCh/DrNB, eligibility = MD/MS/DNB in relevant parent
  specialty.
- **TS/AP ECET** (diploma-to-degree lateral entry) — verified as genuine, active state exams
  (TG ECET via ecet.tgche.ac.in / JNTUH; AP ECET via JNTU Kakinada/APSCHE) but excluded from the
  final row set to stay within the row-count target, since LAWCET/PGLCET pairing was prioritized
  as more directly requested by the task's example list. Can be added in a follow-up collection
  pass.
- **AP/TS PECET** (Physical Education Common Entrance Test) — encountered incidentally
  (`cets.apsche.ap.gov.in/PECET/`) while researching AP EdCET; genuine and active but a narrower,
  less central exam not named in the task brief, so excluded to preserve scope discipline.

## Known gaps / items flagged for follow-up review

- **GATE 2027 conducting institute** (row: GATE) — reported as IIT Madras across secondary
  sources, but the official GATE notification/brochure was not yet published at collection time.
  Re-verify against the official brochure once released (expected end-July/August 2026) and
  update `conducting_body`, `official_website`, and `confidence_score` accordingly.
- **CTET and TG/AP EdCET `exam_level` classification** — the schema's 4-value enum does not have
  a clean bucket for teacher-eligibility certification tests or for Bachelor's-level programs that
  require a prior bachelor's degree for entry. Judgment calls are documented per-row; a reviewer
  with domain authority should confirm or override these classifications if Package002 has a more
  specific convention.
- **CUET PG and GPAT official pages returned HTTP 403 on direct fetch** — facts for these two rows
  rest on search-engine snippets of official domains rather than a directly rendered official page;
  a follow-up pass with authenticated/alternate fetch access could raise confidence further.
- **Frequency of UGC NET and CTET** — recorded as 2 cycles/year based on well-established recent
  patterns (UGC NET June/December; CTET has run twice yearly in recent cycles, e.g. Feb/Sept 2026),
  but neither search surfaced an explicit official statement guaranteeing exactly two cycles for
  every future year; treat as a moderately-confident pattern rather than a hard guarantee.
- **AP ICET official domain** — search results surfaced two different official-looking URLs
  (`cets.apsche.ap.gov.in/ICET/` and `icet-sche.aptonline.in`). `cets.apsche.ap.gov.in/ICET/` was
  used as the primary `official_website` for consistency with the other APSCHE CETS exams, but
  both are plausibly valid APSCHE-linked domains.
- No row in this dataset required use of the `PENDING_VERIFICATION` placeholder — every field
  across all 28 rows was resolved to a stated fact, though several (flagged above) carry moderate
  rather than high confidence and are recommended for a secondary human review pass given the
  fast-changing nature of exam administration (renamings, conducting-body transfers, annual
  rotation of host institutions).
