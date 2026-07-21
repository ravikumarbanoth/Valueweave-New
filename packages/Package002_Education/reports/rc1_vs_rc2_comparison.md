# Package002_Education — RC1 vs RC2 Comparison

RC1: 2026-07-21 (initial collection). RC2: 2026-07-22 (enrichment pass). Neither has been merged to
`main` — this comparison exists to inform that merge decision, per the requester's instruction.

## 1. New Records Added

| Dataset | RC1 | RC2 | New Records |
|---|---|---|---|
| education_boards_regulatory_bodies | 21 | 21 | 0 |
| universities_telangana_andhra_pradesh | 61 | 66 | **5** |
| entrance_exams | 28 | 29 | **1** |
| scholarships | 25 | 25 | 0 |
| **Total** | **135** | **141** | **6** |

New rows added (all newly-verified, not padding):
- **National Sanskrit University, Tirupati** (Andhra Pradesh, Central University)
- **SVIMS Tirupati** (Andhra Pradesh)
- **RGUKT RK Valley**, **RGUKT Srikakulam**, **RGUKT Ongole** (Andhra Pradesh) — these three were explicitly named as gaps in the RC1 collection report and are now included
- **NEET SS** (National, entrance exam) — excluded from RC1 only to stay within the row-count target, now freshly re-verified

## 2. Fields Enriched

### New columns added (universities dataset only, 66 rows each)
| Column | Filled in RC2 | Notes |
|---|---|---|
| `ownership` | 66/66 (100%) | Determinable from existing type/governance facts for every row |
| `contact_details` | 5/66 (7.6%) | Only the 5 flagship universities (Osmania, University of Hyderabad, IIT Hyderabad, Andhra University, NIT Warangal) |
| `student_services_summary` | 5/66 (7.6%) | Same 5 flagship universities |

### Existing PENDING_VERIFICATION fields filled (within RC1's original 61 university rows)
| Column | RC1 filled | RC2 filled | Newly filled in RC2 |
|---|---|---|---|
| `vice_chancellor` | 0/61 | 49/61 | **+49** |
| `naac_grade` | 13/61 | 43/61 | **+30** |
| `nirf_rank` | 10/61 | 21/61 | **+11** |

### Boards/exams/scholarships
| Dataset | Field filled |
|---|---|
| education_boards_regulatory_bodies | APSCHE `headquarters_city` — the sole RC1 PENDING_VERIFICATION field — filled as **Mangalagiri (Guntur District)** |
| entrance_exams | No RC1 pending fields existed |
| scholarships | No RC1 pending fields existed |

## 3. Confidence Improvements

| Dataset | RC1 Avg | RC2 Avg | Delta | RC1 Range | RC2 Range |
|---|---|---|---|---|---|
| education_boards_regulatory_bodies | 74.6 | 79.1 | +4.5 | 58-85 | 63-88 |
| universities_telangana_andhra_pradesh | 68.9 | 74.8 | +5.9 | 58-75 | 58-82 |
| entrance_exams | 84.6 | 85.0 | +0.4 | 72-92 | 78-92 |
| scholarships | 72.0 | 76.8 | +4.8 | 60-80 | 60-88 |
| **Package overall** | **75.0** | **77.9** | **+2.9** | 58-92 | 58-92 |

No row in either RC1 or RC2 claims the 85-95 "direct official fetch" confidence band, since WebFetch
to `.gov.in`/`.ac.in`/Wikipedia domains remained blocked by this session's organizational egress
policy in both passes (re-confirmed via a live test fetch before RC2 began). The improvement reflects
stronger *multi-source WebSearch corroboration*, not a change in fetch method.

## 4. Conflicts Resolved in RC2

- **GATE 2027 host institute**: confirmed as IIT Madras via an official notification released
  20-Jul-2026 (confidence 72→80).
- **AP ICET conducting body/domain**: corroborated (78→86).
- **NOS overseas maintenance figures**: confirmed at USD 15,400 / GBP 9,900.
- **NFST JRF/SRF stipend rate**: confirmed at ₹31,000/₹35,000.
- **NFSC/NFST/NFPwD stipend "inconsistency"**: identified as three genuinely different, currently-valid
  pay scales rather than stale/conflicting data.
- **Telangana overseas scholarships' ₹5L income ceiling**: confirmed.
- **AP NTR Videshi Vidyadharana ₹6L ceiling**: confirmed via a government-linked document.
- **Kakatiya University NAAC grade**: A → A+ (3-source corroboration).
- **BRAOU NAAC grade**: A / 3.12, certificate-sourced, adopted over conflicting claims.
- **Sri Venkateswara University VC vacancy**: resolved — Dr. Tata Narasinga Rao appointed.
- **APSCHE headquarters city**: Mangalagiri, Guntur District.

## 5. Conflicts Explicitly NOT Resolved (left as PENDING_VERIFICATION / flagged, not guessed)

- **BSEAP founding year**: 1953 vs 1969 — still conflicting; confidence nudged only +5 rather than
  resolved.
- **AP Ambedkar Overseas Vidya Nidhi (SC) and NTR Vidyonnathi income ceilings**: still genuinely
  conflicting after a dedicated re-check.
- **Krishna University NAAC grade**: A++ vs B conflict — left PENDING_VERIFICATION rather than
  guessed.
- **Acharya Nagarjuna University and NIT Andhra Pradesh leadership**: left PENDING_VERIFICATION; a
  likely search-result conflation with IIT Hyderabad's director was explicitly identified and
  rejected rather than adopted.

## 6. Integrity Disclosure Added in RC2

**KL University**: its Vice-Chancellor was reportedly arrested in a CBI probe into alleged
NAAC-inspector bribery. The NAAC grade is retained in the dataset (removing verified accreditation
data because of an unrelated controversy would itself be a form of unverified editorializing), but
this is flagged explicitly in the row's `notes` field, and confidence was raised only modestly rather
than to the full extent the underlying NAAC source would otherwise support.

## 7. Remaining Gaps After RC2

- 36 of 40 briefed education domains remain entirely un-researched (BLOCKED/QUEUED in
  `acquisition_backlog.json`), unchanged from RC1 — RC2 was an enrichment pass on the existing 4
  domains, not an expansion.
- `contact_details` and `student_services_summary` remain PENDING_VERIFICATION for 61 of 66
  university rows.
- No row in the package (0 of 141) has been promoted to `VST-VERIFIED`.
- Field depth per institution is still short of the ~33 fields named in the original brief (fee
  structure, lat/long, labs, facilities, research, incubation, student intake, approval, departments
  remain unaddressed).
- Latitude/longitude remains 0% populated package-wide.
- The BSEAP founding-year and two AP scholarship income-ceiling conflicts remain open.

## 8. Recommendation Inputs for the Merge Decision

RC2 improved confidence (+2.9 avg), filled 90 previously-pending fields across the 3 volatile
university columns, added 3 new columns with real (if partial) population, added 6 new verified
records, and resolved 11 source conflicts while explicitly declining to guess on 4 more. It did not
change the package's structural health/AI-readiness score (59/100, see `package_health_report.md`),
since that rubric measures provenance/identifiers/geo/cross-gov-ID/FK-integrity — none of which RC2
targeted. Whether this level of improvement clears the bar for canonical release is a decision for
the requester, not this report.
