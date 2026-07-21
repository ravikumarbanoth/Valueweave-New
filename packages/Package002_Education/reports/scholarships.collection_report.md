# Collection Report: Scholarships (Package002_Education v1.0.0)

**Collection date:** 2026-07-21
**Collector:** Automated research (WebSearch + WebFetch), ValueWeave knowledge engineering
**Output file:** `scholarships.csv` (25 rows, 16 columns, header validated with Python `csv` module)

## Methodology

1. Identified target scheme list from the task brief: major Central schemes (NMMSS, CSSS, PM-USP/PMSS, AICTE Pragati/Saksham, INSPIRE) plus category-wise Central fellowships/scholarships (SC/ST/OBC-EBC-DNT/Minority/Disability), plus Telangana ePASS family of schemes and Andhra Pradesh ePASS/Jagananna-successor schemes.
2. For each scheme, ran targeted `WebSearch` queries (2026-dated where possible) to find: administering body, current eligibility, current benefit amount, and the official application portal/website.
3. Attempted `WebFetch` on primary `.gov.in` / state-portal domains (education.gov.in, scholarships.gov.in, socialjustice.gov.in, telanganaepass.cgg.gov.in, jnanabhumi.ap.gov.in, myscheme.gov.in) to read primary content directly. **Nearly all direct fetches returned HTTP 403 (WAF/bot-blocking) or DNS timeout** (jnanabhumi.ap.gov.in). This is a known limitation of this environment against Indian government web infrastructure, not a data-quality choice. As a result, confidence scores for this dataset are generally in the 60-80 range rather than the 85-95 "official source, directly read" band — reflecting that verification relied on WebSearch snippets which *reference* official domains (visible in the search results list) plus multiple independent secondary/aggregator sources (buddy4study.com, teachersbadi.in, indiascholarships.in, careers360.com, schemesinindia.in, egovtschemes.com, etc.), rather than a direct read of the primary page.
4. Cross-checked every figure across at least two independent sources where possible. Where sources conflicted or a figure appeared only once (especially rupee amounts, which change yearly), the field was marked **PENDING_VERIFICATION** in `funding_benefit_summary` rather than guessing or averaging.
5. Specifically probed for Andhra Pradesh scheme renames, since the state government changed in mid-2024 (YSRCP → TDP-led NDA under N. Chandrababu Naidu), and prior scholarship schemes carried the previous CM's name/initials ("Jagananna", "YSR").

## Sources Consulted (representative, not exhaustive — full URL list is in the CSV `source_url` column)

- Official/government domains referenced in search results: education.gov.in, scholarships.gov.in (NSP), socialjustice.gov.in, tribal.nic.in / fellowship.tribal.gov.in, minorityaffairs.gov.in, dst.gov.in / online-inspire.gov.in, depwd.gov.in, ksb.gov.in, nosmsje.gov.in, tcs.dosje.gov.in, telanganaepass.cgg.gov.in, jnanabhumi.ap.gov.in, jnboverseas1.apcfss.in, myscheme.gov.in, india.gov.in, indiascienceandtechnology.gov.in (ISTI portal)
- News/secondary cross-checks: Deccan Chronicle ("Andhra Pradesh: Naidu government renames welfare schemes"), Careers360 (news.careers360.com, school.careers360.com), Yovizag, Gulte, Sakshi Education
- Scholarship aggregator/portal sites used only as secondary corroboration (never as sole source for a figure that went into the CSV without a caveat): buddy4study.com, indiascholarships.in, teachersbadi.in, schemesinindia.in, sabscholarship.com, egovtschemes.com, wemakescholars.com, studentcover.in

## Conflicts Found and Resolution

### 1. Andhra Pradesh scheme renaming (major finding)
Per **GO No. 4 dated 18 June 2024** (secretary K. Harshavardhan), the new AP government renamed several education welfare schemes to remove references to the previous CM:
- **Jagananna Vidya Deevena** (tuition fee reimbursement) → **Post Matric Scholarship (RTF)**
- **Jagananna Vasathi Deevena** (maintenance/hostel allowance) → **Post Matric Scholarship (MTF)**
- **Jagananna Videshi Vidya Deevena** (SC overseas component) → **Ambedkar Overseas Vidya Nidhi (AOVN)**
- The BC-category overseas component now appears under variants of **"NTR Videshi Vidyadharana"** (naming inconsistent across secondary sources — flagged for further verification)
- **YSR Vidyonnathi Scheme** (UPSC/competitive-exam coaching support) → **NTR Vidyonnathi Scheme**

Despite the 2024 rename, **many 2026-dated scholarship-aggregator pages still market these schemes under the old "Jagananna"/"YSR" names** — almost certainly stale SEO content rather than evidence the rename was reversed. The CSV rows use the new official names and note the old names explicitly in the `notes` field so the package is discoverable either way. This is the most important rename to flag for whoever consumes this dataset next, since assuming the old names are current would be a factual error.

I was **not able to directly read the original GO No. 4 text** (jnanabhumi.ap.gov.in was unreachable in this session; a Deccan Chronicle article citing the GO returned 403 on WebFetch). The rename is corroborated by multiple independent news write-ups (Deccan Chronicle, Yovizag, Telangana Tribune, m9.news) that agree on the GO number, date, and substance, so confidence is moderate (72) rather than the maximum, and I recommend a follow-up direct-GO check before this feeds a customer-facing product.

### 2. Conflicting fellowship stipend rates (SC vs ST vs disability fellowships)
NFSC (SC, JRF/SRF ₹37,000/₹42,000 per month) reflects the 2023 UGC fellowship revision. A search for the analogous ST fellowship (NFST) returned an apparently pre-revision figure (₹25,000/₹28,000), and the disability fellowship (NFPwD) returned yet another figure (₹31,000/₹35,500, labeled "2025-26" by the source). These three fellowships are typically expected to track the same UGC JRF/SRF pay scale, so at least two of the three numbers found are likely stale. Rather than pick one, I reported each figure **as found, with an explicit note flagging the cross-scheme inconsistency**, and marked the ST figure PENDING_VERIFICATION.

### 3. AP overseas-scholarship eligibility income ceiling
Sources gave both "≤ ₹5 lakh" and "≤ ₹6 lakh" for different AP overseas schemes without a consistent pattern; recorded as reported per scheme with a verification flag rather than reconciled.

### 4. Minority scholarship benefit amounts (Central)
One secondary source claimed a flat "up to ₹10,000/year" for the Central Post-Matric Scholarship for Minorities, which is inconsistent with this scheme's known fee-reimbursement + tiered-maintenance-allowance structure. Treated as unreliable; recorded PENDING_VERIFICATION instead of the unverified single-source figure.

### 5. National Overseas Scholarship (NOS) benefit amount
A "$15,400 annually" figure appeared only in a search-result **title**, not corroborated in body text. Not used as a hard figure; funding summary describes the benefit qualitatively (tuition + maintenance + airfare) with PENDING_VERIFICATION for the exact current rate.

## Schemes Considered but Excluded

- **UGC-NET/CSIR-NET JRF (general, non-category)** — not a "scholarship scheme" targeted at students by category/state welfare; out of scope for this package's SC/ST/BC/EBC/Minority/general-merit welfare-scholarship focus.
- **Private/CSR scholarships** (e.g., Reliance Foundation, Tata scholarships) — excluded per task scope, which is government/state schemes only.
- **State schemes for other states** (Karnataka MCM renewal rules turned up in search noise) — out of scope; this package is India-national + Telangana + Andhra Pradesh only.
- **AP "EBC Nestham"** — appears to be a women/OC-EBC livelihood support scheme rather than a student scholarship; excluded as out-of-category, though it surfaced in AP scholarship searches.
- **Older/renamed AP overseas scheme names** (Jagananna Videshi Vidya Deevena as a single umbrella scheme) — superseded in the CSV by the three current category-specific successor rows (Ambedkar Overseas Vidya Nidhi for SC, NTR Videshi Vidyadharana for BC, and the AP EWS/general component was not clearly verifiable and was left out rather than guessed).
- **A hypothesized "AP general/EWS overseas scholarship" (non-SC, non-BC, non-minority)** — search did not surface a clearly verifiable current scheme of this type; not included rather than guessed.

## Known Gaps / Items Flagged for Follow-Up Verification

- **Direct primary-source access was blocked** for essentially every `.gov.in` and state-portal domain attempted via `WebFetch` in this session (HTTP 403 or DNS timeout). All findings rest on `WebSearch` result snippets (which do index official-domain content) plus secondary aggregator corroboration. Recommend a follow-up pass with authenticated/allow-listed access to `scholarships.gov.in`, `telanganaepass.cgg.gov.in`, and `jnanabhumi.ap.gov.in` to convert PENDING_VERIFICATION fields to confirmed figures.
- **AP Pre-Matric Scholarship** (row `12d3acee-...`) is the weakest-verified row in the dataset (confidence 60) — could not confirm the current official AP-specific scheme name or a specific benefit amount distinct from the generic Central pre-matric scheme description.
- **NTR Videshi Vidyadharana** naming is inconsistent across sources (also seen as "AP Videshi Vidyadharana" / "Overseas Vidya Nidhi (BC)") — flagged for GO-level confirmation of the single correct current name.
- **Telangana overseas scheme income ceilings and exact current amounts** (Ambedkar Overseas Vidya Nidhi, Mahatma Jyotiba Phule BC Overseas Vidya Nidhi, CM's Overseas Scholarship for Minorities) vary slightly across secondary sources; the ₹20 lakh cap and airfare component were consistent, but income ceilings need a GO-level check.
- **All rupee/dollar benefit amounts are point-in-time as reported by 2026-dated web sources** and are explicitly subject to annual government revision — this dataset should not be treated as authoritative for exact current-year disbursement amounts without a follow-up direct-portal check close to publication time.
- No scheme in this dataset was found to be discontinued outright; all 25 included schemes returned 2026-cycle application information (deadlines, portals, or NSP references), supporting that they are currently active. The AP renames are name changes with continuity of substance, not discontinuations.

## Row Count Summary

- Central/National schemes: 15
- Telangana state schemes: 5
- Andhra Pradesh state schemes: 5
- **Total: 25 rows**, all `verification_status = VST-NEEDS_REVIEW`, confidence scores ranging 60-80 (median ~72), reflecting reliance on search-snippet + secondary-source corroboration rather than direct primary-document reads.
