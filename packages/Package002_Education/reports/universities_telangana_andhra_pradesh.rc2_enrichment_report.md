# RC2 Enrichment Report: Universities in Telangana and Andhra Pradesh

**Package:** ValueWeave Package002_Education
**Base dataset (RC1):** `universities_telangana_andhra_pradesh.csv` (61 rows, 19 columns, collected 2026-07-21)
**Enriched dataset (RC2):** `universities_telangana_andhra_pradesh.csv` (66 rows, 22 columns, enriched 2026-07-22)
**Enrichment date:** 2026-07-22

## 1. Methodology and constraint (unchanged from RC1)

`WebFetch` to `.gov.in`/`.ac.in`/Wikipedia and other external domains remained
blocked by the session's org egress policy for this entire pass (confirmed
403 at the start of the task). All enrichment was therefore performed via
`WebSearch` only, the same constraint as the RC1 collection pass. Per the
task's instruction, confidence scores were raised **at most +10 per row**
where genuinely stronger/multiple-source corroboration was found, and were
**capped at 82** — the 85-95 "direct official fetch" band was never claimed,
since direct fetch access is still unavailable.

For each of the 61 existing rows, targeted `WebSearch` queries were run to
re-verify/find: current Vice-Chancellor (or Director, for institutes that use
that title), NAAC grade, NIRF rank, and — for the three new columns —
ownership category, official contact details, and hostel/library/sports
information. Where results were internally consistent and reasonably dated,
the field was filled. Where results conflicted sharply, were undated, or
could not be attributed to a credible/official-adjacent source, the field
was left `PENDING_VERIFICATION` and the conflict was documented in `notes`
rather than guessed.

## 2. Confidence-score improvements

- **61 of 61 existing rows** had their confidence score reviewed and, in every
  case, improved (no row was worse off).
- Average confidence across the 61 original rows rose from **68.92 → 76.05**
  (a mean increase of **+7.1 points**; increases ranged from +3 to +10 per
  row, capped at a ceiling of 82).
- No row was assigned a confidence in the 85-95 "direct source" band —
  consistent with the ongoing WebFetch outage.
- The 5 newly added rows (see §5) were scored conservatively in the
  58-62 range, reflecting lighter, more indirect corroboration than most of
  the original 61.

## 3. PENDING_VERIFICATION fields filled

| Field | Originally PENDING (of 61) | Filled in RC2 | Still PENDING |
|---|---|---|---|
| `vice_chancellor` | 61 | **49** | 12 |
| `naac_grade` | 48 | **30** | 18 |
| `nirf_rank` | 51 | **11** | 40 |

Notable cases left deliberately `PENDING_VERIFICATION` rather than guessed,
because sources conflicted too sharply or lacked a clear/dated
current-office-holder:
- Acharya Nagarjuna University VC (three differently-named candidates found,
  none clearly dominant/dated)
- Vikrama Simhapuri University VC (three-way conflict)
- Krishna University NAAC grade (A++ vs. B — too wide a gap to resolve by
  corroboration weight)
- NIT Andhra Pradesh Director (a search result named "B.S. Murty," which
  appears to be a conflation with the separately-confirmed Director of IIT
  Hyderabad — deliberately **not** adopted)
- NIT Warangal Director, JNTUK VC, JNTU-GV VC, Woxsen University VC, Anurag
  University VC, IISER Tirupati Director, Central Tribal University of AP VC
  (post apparently under active recruitment/vacant)

## 4. New columns (ownership, contact_details, student_services_summary)

| Column | Real value assigned | PENDING_VERIFICATION |
|---|---|---|
| `ownership` | **66 / 66** (100%) | 0 |
| `contact_details` | 5 / 66 | 61 |
| `student_services_summary` | 5 / 66 | 61 |

`ownership` was straightforward to determine for nearly every row directly
from `university_type` plus governance facts already on record (State
University / National Law University established by state act → **State
Government**; Central University / Institute of National Importance →
**Central Government**; Private University / Deemed University run by a
trust or educational society → **Private Trust/Society**). Breakdown across
the final 66 rows: **State Government 40, Central Government 11, Private
Trust/Society 15.** No row required `PENDING_VERIFICATION` for ownership.
One nuance: IIIT Hyderabad is recorded as Private Trust/Society (it is
registered as a not-for-profit society) but operates under an N-PPP
(Not-for-profit Public-Private Partnership) model with state and central
government co-funding — noted in its `notes` field as an approximation of a
genuinely mixed structure.

`contact_details` and `student_services_summary` were, as anticipated in the
task brief, filled only for the handful of flagship institutions where
official phone/email/hostel/library facts surfaced directly and consistently
in search snippets: **Osmania University, University of Hyderabad, IIT
Hyderabad, Andhra University, and NIT Warangal.** For the remaining 61 rows
these fields were left `PENDING_VERIFICATION` rather than inferring plausible
but unverified contact points or facilities — this is expected and matches
the task's guidance that most rows would legitimately stay pending here.

## 5. New rows added (5)

Following up on gaps explicitly flagged in the RC1 collection report and one
additional genuinely well-documented omission, 5 new rows were added (all in
Andhra Pradesh), each with a new UUID and the full 22-column schema:

1. **National Sanskrit University, Tirupati** (Central University; formerly
   Rashtriya Sanskrit Vidyapeetha, a deemed university since 1961, elevated to
   Central University status via the Central Sanskrit Universities Act, 2020)
   — a genuinely UGC/Parliament-established central university that was
   simply absent from the RC1 dataset.
2. **Sri Venkateswara Institute of Medical Sciences (SVIMS), Tirupati**
   (State University, medical, est. 1995 by AP state act) — distinct from the
   already-listed Sri Venkateswara University and Sri Venkateswara Veterinary
   University.
3. **RGUKT RK Valley** (Kadapa district, AP) — the RC1 report explicitly
   flagged this campus as "not independently verified... excluded rather
   than guessed"; this pass fills that named gap.
4. **RGUKT Srikakulam** — likewise explicitly flagged as a gap in RC1; filled
   in this pass.
5. **RGUKT Dr. APJ Abdul Kalam IIIT Ongole Campus** — a fifth RGUKT campus
   located and corroborated during this pass (established 2016, alongside
   Srikakulam, under the same AP Act No. 18/2008 framework); added for
   consistency with the other RGUKT campuses already present (Basar, Nuzvid).

All 5 new rows carry confidence scores of 58-62 (below the original dataset's
average) and `verification_status = VST-NEEDS_REVIEW`, reflecting lighter,
WebSearch-only corroboration. A suspicious duplicate NIRF figure ("#43 among
Engineering colleges," which appeared verbatim for both RGUKT Basar and RGUKT
Ongole) was identified as a likely search-conflation artifact and was
deliberately **not** recorded for Ongole — its `nirf_rank` was left
`PENDING_VERIFICATION` instead.

No other candidate institutions met the bar for inclusion; the
previously-excluded ISB Hyderabad, IICT Hyderabad, and the "Andhra Pradesh
State Skill Development University" were re-checked and still could not be
corroborated as genuine UGC-recognized degree-granting universities (the
Skill Development University in particular returned no usable search
results at all) — they remain excluded.

## 6. Conflicts found and how they were resolved

- **Kakatiya University NAAC grade** — RESOLVED: RC1 recorded "A (3.02 CGPA)"
  with a flagged possible A+ discrepancy. Three independent 2023 press
  sources (Hans India, Deccan Chronicle, Telangana Today) converge on **A+**
  (accredited June 2023), which is adopted as better-corroborated.
- **Dr. B.R. Ambedkar Open University NAAC grade** — RESOLVED: of three
  conflicting claims (A++, A/CGPA 3.12 per an official NAAC certificate
  reference, B++), the certificate-sourced **A (3.12 CGPA)** was adopted.
- **Sri Venkateswara University VC vacancy** — RESOLVED: RC1 had explicitly
  left this PENDING due to a reported prolonged VC vacancy; this pass found a
  dedicated news report confirming **Dr. Tata Narasinga Rao** was appointed
  as regular VC after the ~14-month gap.
- **KL University / NAAC integrity caveat** — NOT silently resolved, flagged
  instead: the confirmed VC (Dr. G. Pardha Saradhi Varma) was separately
  reported to have been arrested in Feb 2025 in a CBI investigation into
  alleged bribery of NAAC inspection-committee members. The existing NAAC
  A++ grade was **retained** (not altered without cause) but the caveat is
  now recorded in `notes`, and confidence was raised only modestly (+3)
  despite the VC name being newly confirmed.
- **Sri Sathya Sai Institute of Higher Learning NAAC figure** — flagged, not
  resolved: sources give a CGPA of 2.90/4, which on the standard NAAC scale
  would normally correspond to a "B++" band, yet other sources label it
  "A++" — an internal inconsistency noted rather than picked.
- Several VC-name three-way conflicts (Acharya Nagarjuna University, Vikrama
  Simhapuri University) and grade conflicts (Krishna University NAAC A++ vs.
  B) were left `PENDING_VERIFICATION` per the no-guessing rule — see §3.
- **Dr. B.R. Ambedkar University, Srikakulam NAAC validity** — the cited B++
  grade's stated validity end-date (9 Apr 2026) falls before this
  enrichment's collection date (22 Jul 2026), suggesting the accreditation
  may already be due for renewal; flagged for a future pass rather than
  treated as still-current without qualification.

## 7. Remaining major gaps (for RC3 and beyond)

- 12 of 61 original rows still have no confirmed Vice-Chancellor/Director;
  18 still lack a NAAC grade; 40 still lack a NIRF rank — all deliberately
  left unguessed.
- `contact_details` and `student_services_summary` remain `PENDING_VERIFICATION`
  for 61 of 66 rows — these fields are genuinely hard to source reliably from
  WebSearch snippets alone and will likely require direct site fetches.
- The RGUKT-family rows (Basar, Nuzvid, RK Valley, Srikakulam, Ongole) still
  lack campus-specific NAAC grades in several cases (only system-wide RGUKT
  figures surfaced); NIRF figures for this family are inconsistent across
  sources and should be re-verified once direct fetch is available.
- The Potti Sreeramulu Telugu University possible-rename question (to
  "Suravaram Pratap Reddy Telugu University") remains unconfirmed.
- **The single largest remaining data-quality lever is still the WebFetch
  outage.** A follow-up pass with working direct access to `.ac.in`/`.gov.in`
  domains, the UGC master list, and the NAAC/NIRF official portals is
  strongly recommended before this dataset can be promoted past RC2 —
  several fields recorded here rest on a single WebSearch-summarized
  snippet and would benefit from primary-source confirmation.

## 8. Row count summary (post-enrichment)

- **Total rows:** 66 (61 original + 5 new)
- **Telangana:** 29 (unchanged)
- **Andhra Pradesh:** 37 (32 original + 5 new)
- **Ownership breakdown:** State Government 40, Central Government 11,
  Private Trust/Society 15
