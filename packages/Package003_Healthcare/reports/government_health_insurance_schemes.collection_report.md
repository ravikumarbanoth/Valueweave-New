# Collection Report — Government Health Insurance & Health Schemes
Package003_Healthcare v1.0.0 | Collection date: 2026-07-21 | Collector: Claude (research agent)

## Methodology

- Tooling: WebSearch only. WebFetch to .gov.in / .ac.in / Wikipedia domains is blocked by this
  session's organizational egress policy (HTTP 403 confirmed on retest), so no direct fetch of
  primary government pages was possible. All facts below are triangulated from **multiple
  independent secondary sources** returned by WebSearch (news outlets, insurer/aggregator
  explainer pages, and search-engine summaries that themselves cite official material).
- For every scheme, targeted searches were run for: (a) administering body, (b) target
  beneficiaries, (c) coverage amount, (d) empanelled hospital network, and (e) official
  portal/domain. A separate round of searches was run specifically to hunt for **scheme renames**,
  since state health-scheme names in India change with changes of government (the AP education
  scholarship precedent cited in the task brief is a known pattern that also applies to health
  schemes).
- Because no primary-source fetch was possible, every row is capped at confidence 80–85 (within
  the 82–88 ceiling given, erring toward the low-mid end where secondary sources showed any
  inconsistency) and marked `VST-NEEDS_REVIEW`, per instructions.
- Where a specific figure could not be corroborated with reasonable confidence, the field is
  explicitly marked `PENDING_VERIFICATION` in-text rather than guessed (see AP EHS row).

## Sources consulted (representative, not exhaustive — full list per row is in `source_url`)

- https://pmjay.gov.in and https://www.mohfw.gov.in/?q=en/pressrelease/update-ayushman-bharat-pradhan-mantri-jan-arogya-yojana-ab-pm-jay (PM-JAY / senior-citizen top-up)
- https://cghs.mohfw.gov.in/ (CGHS — current domain)
- https://esic.gov.in/ , https://esic.gov.in/coverage , https://esic.gov.in/benefits (ESIC)
- https://www.desw.gov.in/about-echs (ECHS, Dept of Ex-Servicemen Welfare, MoD)
- https://aarogyasri.telangana.gov.in/ (Telangana — Rajiv Aarogyasri)
- https://www.siasat.com/telangana-govt-launches-new-health-scheme-for-govt-employees-3508268/ ,
  https://www.thehansindia.com/telangana/new-employees-health-scheme-launched-1098559 ,
  https://www.socialnews.xyz/2026/07/17/telangana-launches-new-health-scheme-for-employees-pensioners/
  (Telangana — NEHS launch, 17 July 2026)
- https://drntrvaidyaseva.ap.gov.in/ , http://hmfw.ap.gov.in/ntr-aarogyaseva-org.aspx (AP — Dr. NTR Vaidya Seva)
- https://thesouthfirst.com/andhrapradesh/here-is-all-you-need-to-know-about-the-revamped-ysr-aarogyasri-scheme/ ,
  https://connectmyindia.com/news/aarogyasri-renamed-dr-ntr-vaidya-seva-trust--3985.html (AP rename history)
- https://ehs.ap.gov.in/ , https://www.adityabirlacapital.com/abc-of-money/employee-health-scheme-government-andhra-pradesh (AP EHS)
- Cross-cutting aggregator/insurer explainer sites used only to corroborate figures across ≥2
  independent sources: policybazaar.com, starhealth.in, acko.com, schemesinindia.in, joinditto.in,
  ibef.org, manipalcigna.com.

Note: several .gov.in URLs are listed above as they appeared in search results and are the
correct canonical sources — but they were **not directly fetched** this session (blocked); they
are cited as the target for a future direct-verification pass, not as fetched evidence.

## Conflicts found and resolution (scheme renames)

1. **CGHS domain change (April 2025)** — Multiple sources (some older, some current) disagree on
   whether the correct domain is `cghs.gov.in` or `cghs.mohfw.gov.in`. Resolution: newer sources
   confirm the legacy `cghs.gov.in` / `cghs.nic.in` domains were **deactivated on 28 April 2025**
   when a new unified CGHS Digital Platform/HMIS went live. Current canonical domain used in the
   CSV: `cghs.mohfw.gov.in`.

2. **Andhra Pradesh — Dr. YSR Aarogyasri → Dr. NTR Vaidya Seva (July 2024)** — This is the most
   significant rename found, directly analogous to the AP scholarship-scheme renames referenced
   in the task brief. The BPL/low-income health-assurance scheme has changed its brand name with
   almost every change of AP government since 2007: launched as "Rajiv Aarogyasri" (2007, YSR
   Congress founder), renamed "NTR Aarogya Seva"/"NTR Vaidya Seva" (from 2014, TDP), renamed
   "Dr. YSR Aarogyasri" (2019, YSRCP), then renamed again to **"Dr. NTR Vaidya Seva"** in **July
   2024** after the TDP-led NDA coalition (CM N. Chandrababu Naidu) took office. The administering
   trust followed the same rename, from "Dr. YSR Aarogyasri Health Care Trust" to **"Dr. NTR
   Vaidya Seva Trust"**. Resolution: CSV uses the current name and trust, with the historical
   chain documented in the row's `notes` field so downstream consumers understand this is a
   politically-recurring rename pattern, not a one-off.

3. **Andhra Pradesh EHS — name vs. trust nuance** — The employee-facing "Employee Health Scheme
   (EHS)" brand name itself does **not** appear to have been renamed in 2024, but its
   administering trust was (same rename as #2, since both schemes share the trust). Several
   aggregator sources still reference the pre-2024 trust name ("Dr. YSR Aarogyasri Health Care
   Trust"), which is flagged in the row as a lag in secondary sources rather than a live fact
   conflict.

4. **Telangana — Aarogyasri → Rajiv Aarogyasri (December 2023) + coverage increase** — After the
   Congress-led government under CM A. Revanth Reddy took office (Dec 2023), the state's BPL
   health scheme was relaunched as "Rajiv Aarogyasri" with coverage doubled from Rs 5 lakh to
   Rs 10 lakh, effective 9 December 2023. In July 2024, 163 additional procedures were added,
   split between AB-PMJAY-funded (98) and state-funded (65) — evidence of active convergence
   between the state scheme and the national PM-JAY scheme rather than the two operating in
   isolation.

5. **Telangana — EHS → NEHS (17 July 2026) — very recent, found mid-research** — The Telangana
   state-employee health scheme was relaunched as the "New Employees Health Scheme (NEHS)" on
   17 July 2026, just four days before this collection date, with a newly constituted "Employees
   Health Care Trust (EHCT)" (distinct from the Aarogyasri Health Care Trust that had previously
   administered the employee scheme's hospital network) and a new portal (nehs.telangana.gov.in).
   Because this happened so recently, only launch-week news coverage was available to corroborate
   it — no settled secondary-source consensus yet exists. Confidence was capped at 82 for this row
   specifically because of that recency, and the row's notes flag it for re-verification in a
   future collection cycle once more independent sources have caught up.

## Schemes excluded and why

- **Rashtriya Swasthya Bima Yojana (RSBY)** — Confirmed discontinued/subsumed into AB PM-JAY on
  23 September 2018; no longer exists as a standalone scheme. Excluded as not currently active.
- **Pradhan Mantri Suraksha Bima Yojana (PMSBY)** — This is an accidental-death/disability
  insurance scheme (Ministry of Finance/insurance-company administered), not a health/medical
  hospitalization scheme. Excluded per the task's instruction to focus on health insurance /
  financial-coverage-for-healthcare specifically rather than every GoI insurance product.
- **National Health Mission (NHM) programmes** (e.g., Janani Suraksha Yojana, Janani Shishu
  Suraksha Karyakram) — These are service-delivery/cash-incentive programmes for specific health
  events (institutional delivery, maternal/child care), not general-purpose health insurance or
  financial-coverage schemes with a defined per-family sum insured. Excluded per task instruction
  to focus on insurance/financial-coverage schemes, not general health programmes.
- **State Chief Minister's Relief Fund medical-assistance grants (TG/AP)** — These are
  discretionary, case-by-case ex-gratia grants, not a structured insurance scheme with defined
  eligibility/coverage rules. Excluded as not a "scheme" in the required sense.
- **Universal Health Insurance Scheme (UHIS)** — Legacy central scheme, effectively defunct/
  superseded; excluded as not currently active.

## Known gaps / items for future direct-verification pass

- **AP EHS current per-family coverage ceiling** — Secondary sources are inconsistent or omit a
  specific current rupee figure for the employee scheme (as distinct from the well-documented
  Rs 25 lakh figure for the BPL-facing Dr. NTR Vaidya Seva scheme). Marked
  `PENDING_VERIFICATION` in the CSV rather than guessed.
- **ECHS one-time subscription/contribution amount by rank** — Not independently verified this
  session; the scheme's *benefit* structure (no ceiling on treatment cost) is well corroborated,
  but the *contribution* amount was not confirmed.
- **Exact current empanelled-hospital counts** for PM-JAY (30,000+, order-of-magnitude only),
  Rajiv Aarogyasri (Telangana), and Dr. NTR Vaidya Seva (AP) — all cited as approximate; hospital
  networks are added/removed continuously and should be re-pulled from the live NHA/state-trust
  dashboards when direct fetch access is available.
- **CGHS current beneficiary count** — sources ranged 42–50 lakh depending on publication date;
  not resolved to a single authoritative figure this session.
- **No direct primary-source (.gov.in) fetch was performed this session** for any row — every
  fact is secondary-source-triangulated. A follow-up pass with .gov.in fetch access should
  directly confirm figures on: pmjay.gov.in, cghs.mohfw.gov.in, esic.gov.in, desw.gov.in,
  aarogyasri.telangana.gov.in, nehs.telangana.gov.in, drntrvaidyaseva.ap.gov.in, and ehs.ap.gov.in.

## Row count summary

8 rows delivered (4 Central Scheme / National, 2 Telangana State Scheme, 2 Andhra Pradesh State
Scheme). This is within the requested "roughly 8–15" range at the lower/higher-confidence end;
the collector prioritized verifying every included scheme is genuinely active under its current
name over padding the count with borderline or stale entries (see exclusions above).
