# Collection Report: Digital & Technology Livelihoods
## Package004_Industries_and_Livelihoods v1.0.0 — Telangana & Andhra Pradesh

**Collection date:** 2026-07-22
**Dataset:** `digital_technology_livelihoods.csv` (12 rows)

## Methodology

- Task scope: characterize digital/tech livelihood and small-business *categories* (not individual companies) as they exist for a person in Telangana (TG) or Andhra Pradesh (AP) — Software/IT Services (freelance/small firm), Web Development, App Development, Digital Marketing Agency, Social Media Management, Cloud Services Consulting, Cybersecurity Consulting, and Data Analytics Services.
- These 8 requested categories were expanded to 12 rows by splitting Software/IT Services and Web Development into freelance vs. small-registered-firm variants, splitting Digital Marketing into full-service agency vs. SEO/content-specific consulting, and adding one additional row (Rural IT-Enabled Service Center / BPO-KPO Operator) to explicitly capture Telangana's documented GRID/LEAP rural-decentralization policy, which is directly relevant to the rural/urban suitability dimension requested for this dataset.
- Tooling constraint: **WebFetch to .gov.in, .ac.in, and Wikipedia domains was blocked (HTTP 403) by this session's organizational egress policy**, confirmed via a live retest. All research was therefore done via **WebSearch only**, which returns search-engine snippets/summaries of pages (including .gov.in pages) rather than full primary-source text. This means government scheme references in this dataset are traceable to specific .gov.in / MeitY-linked URLs but were not independently confirmed by reading the full primary page — they should be treated as "sourced but not fully primary-verified," consistent with each row's `verification_status = VST-NEEDS_REVIEW`.
- Per the task's strict no-invention rule, **no `typical_investment_range_summary` field states a specific rupee figure** derived from an unverified source. Where only generic SEO/CA-firm blog estimates were found (e.g., digital marketing agency setup costs), these were explicitly flagged as `PENDING_VERIFICATION (portal estimates only, not government-verified)` rather than presented as fact. No revenue figures were included anywhere, per instructions.

## Sources Consulted

**Government / MeitY-linked (via WebSearch snippets, not directly fetched):**
- T-Hub — Government of Telangana incubator: https://it.telangana.gov.in/initiatives/t-hub/ , https://t-hub.co/programs , https://programs.t-hub.co/rubrix-cohort-4/
- WE-HUB — Telangana women entrepreneurs incubator (ITE&C Dept.): https://wehub.telangana.gov.in/ , https://it.telangana.gov.in/initiatives/wehub/
- TASK — Telangana Academy for Skill and Knowledge: https://it.telangana.gov.in/initiatives/task/
- APITA — Andhra Pradesh Information Technology Academy: https://apit.ap.gov.in/ (existence/full-form confirmed via fullformexpand.com/LinkedIn summaries, not fully re-verified against the primary apit.ap.gov.in page)
- AP ITE&C Department: https://apit.ap.gov.in/?page_id=1762
- Startup India / DPIIT: https://www.startupindia.gov.in
- Skill India Digital Hub (MSDE): https://www.skillindiadigital.gov.in/free-online-courses/
- NASSCOM FutureSkills Prime (MeitY-backed): https://www.futureskillsprime.in/ , https://www.digitalindia.gov.in/initiative/futureskills-prime/
- Telangana ICT Policy Framework 2016: https://invest.telangana.gov.in/wp-content/uploads/2024/07/Telangana-ICT-Policy-Framework-2016-1.pdf

**Portal / secondary sources (industry blogs, news, aggregators — used only for context, cost estimates flagged PENDING_VERIFICATION):**
- missiontelangana.com (GRID/LEAP rural IT policy summary)
- teamleaseregtech.com, telematicswire.net (AP Innovation & Startup Policy 4.0 summaries)
- upmetrics.co, digitalmarketingcoimbatore.co.in (digital marketing agency cost estimates — not used as fact)
- indiafilings.com, patronaccounting.com, kanakkupillai.com (GST/Udyam registration procedural guidance)

## Government-sourced vs. Portal-only Rows

| Row | Primary basis | Confidence |
|---|---|---|
| DTL001, DTL002 (Software/IT Services) | T-Hub, TASK, Startup India, FutureSkills Prime (.gov/.gov-linked) | 78 |
| DTL003, DTL004 (Web Development) | Skill India Digital Hub, TASK, T-Hub | 75 / 73 |
| DTL005 (App Development) | T-Hub RubriX, WE-HUB, FutureSkills Prime | 75 |
| DTL006 (Digital Marketing Agency) | Scheme refs gov-linked; cost/description leans on portal blogs | 68 |
| DTL007, DTL008 (Social Media Mgmt, SEO/Content) | No category-specific scheme found; general WE-HUB/skilling refs only | 65 |
| DTL009 (Cloud Services) | T-Hub RubriX ("Advanced Computing"), FutureSkills Prime, TASK | 75 |
| DTL010 (Cybersecurity Consulting) | T-Hub RubriX ("Cybersecurity & IT"), Skill India Digital Hub | 75 |
| DTL011 (Data Analytics) | TASK (AI/ML/Data Science partnerships), FutureSkills Prime | 73 |
| DTL012 (Rural IT-Enabled Center) | Telangana GRID/LEAP policy (via secondary summary), TASK Finishing School | 68 |

No row reached the 85 government-authoritative ceiling because none was confirmed against a fully-fetched primary .gov.in page (WebFetch to that TLD was blocked all session) — all are capped at 65–78 to reflect "sourced via search snippet, not primary-verified."

## Conflicts Found / Resolved

- **APITA naming ambiguity**: initial search returned both "APITA" (Andhra Pradesh Information Technology Academy) and "iTAAP" (Information Technology Association of Andhra Pradesh) as similarly-named but distinct bodies. Resolved by using APITA only where explicitly matching "Andhra Pradesh Information Technology Academy" and not conflating with iTAAP (an industry association).
- **No AP-specific equivalent to WE-HUB was found.** WE-HUB is confirmed Telangana-only (India's first state-led women-entrepreneur incubator). Rows reference WE-HUB only for Telangana; no AP women-specific tech scheme is claimed — this is flagged as a gap below rather than invented.
- **Digital marketing/App Store cost figures**: portal sources gave a wide, inconsistent range (₹10,000 to ₹20 lakh depending on model). Rather than pick one, the range was excluded from the CSV field content and replaced with PENDING_VERIFICATION, with the conflicting figures noted only in this report.

## Known Gaps

1. No verified capital/investment figures for any of the 12 livelihood categories from a government incubator costing guide or NASSCOM report — all marked PENDING_VERIFICATION as instructed.
2. No AP-specific women-in-tech entrepreneurship scheme was located (WE-HUB is Telangana-only); this is a genuine ecosystem asymmetry, not a research omission, but should be re-checked with primary AP ITE&C sources once .gov.in fetch access is restored.
3. Exact TG/AP state-specific Shops & Establishment / Professional Tax thresholds for small IT/digital freelancers were not verified.
4. RubriX Program Brief PDF (programs.t-hub.co) and the AP Innovation & Startup Policy 4.0 government order PDF (apit.ap.gov.in) were identified but not directly fetched this session (WebFetch blocked/not attempted for the AP PDF); recommended follow-up once primary-source access is available.
5. Skill India Digital Hub's current live course catalog for "big data/analytics" was referenced only via a secondary aggregator (shiksha.com) summary, not the primary platform listing.

All 12 rows are marked `verification_status = VST-NEEDS_REVIEW` per the package's standard workflow, and should be reviewed against primary .gov.in sources before promotion to a verified state.
