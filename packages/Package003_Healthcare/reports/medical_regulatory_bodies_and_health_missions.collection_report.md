# Collection Report: Medical Regulatory Bodies & Health Missions
Package003_Healthcare v1.0.0 — Knowledge Engineering Research

**Collection date:** 2026-07-21
**Researcher session constraint:** WebFetch to .gov.in / .ac.in / Wikipedia domains returned HTTP 403 (blocked by organizational egress policy) on every retry this session. All research below was therefore performed via the WebSearch tool only, which surfaces snippet-level summaries of search results (including from .gov.in and Wikipedia sources) without a direct page fetch. No field was fabricated; any field not resolvable with reasonable confidence via WebSearch snippets is marked `PENDING_VERIFICATION` in the CSV.

## Methodology

1. Enumerated the target entity list from the task brief: 10 explicitly named national bodies (NMC, INC, PCI, DCI/NDC, ICMR, CDSCO, NHM, NABH, NABL, MoHFW), plus explicitly named Telangana and Andhra Pradesh bodies (TSMC, APMC, TVVP, APVVP, NHM-Telangana, NHM-AP), plus "any other genuine state regulatory/mission bodies" discovered during research.
2. Ran targeted WebSearch queries per entity for: official website, establishment year/legal instrument, headquarters, parent ministry/department, and current mandate.
3. Cross-checked each entity against at least one independent secondary source (Wikipedia, PIB press releases, or a second government portal reference) where available, to catch stale or ambiguous facts (this was especially important for the Dental Council of India, which search revealed had a very recent, active legal transition).
4. Added national entries beyond the initial list only where clearly in scope and genuinely active: National Health Authority (NHA) / Ayushman Bharat PM-JAY, since the brief's scope explicitly includes "Health Missions" and PM-JAY/NHA is a major, currently active national health assurance program parented by MoHFW.
5. Added state-level entries beyond the initial list where a genuine, currently active, verifiably distinct body was found: Telangana State Pharmacy Council, Telangana State Nurses & Midwives Council (TGNMC/TSNMC), Rajiv Aarogyasri Health Care Trust (Telangana), AP Pharmacy Council (APPC), AP Nurses/Midwives/ANM/Health Visitors Council (APNMC), and Dr. YSR Aarogyasri Health Care Trust (Andhra Pradesh) — these are the direct TG/AP counterparts of PCI/INC-type state councils and state health-assurance schemes, and are genuinely distinct, separately administered bodies post the 2014 AP–Telangana bifurcation.
6. Every row was assigned `verification_status = VST-NEEDS_REVIEW` and a `confidence_score` in the 80–85 range (capped per task instructions at 82–88, since no direct .gov.in fetch/render was possible this session to confirm live page content), reflecting reliance on WebSearch snippets rather than direct document verification.
7. `collection_date` fixed at 2026-07-21 for all rows per task instruction.

## Final entity count

23 rows total: 11 national, 6 Telangana, 6 Andhra Pradesh.

## Sources consulted (representative, not exhaustive — see `source_url` column per row for the specific sources backing each entity)

- https://www.nmc.org.in/ and https://www.nmc.org.in/about-nmc/introduction/ (NMC)
- https://en.wikipedia.org/wiki/National_Medical_Commission (secondary cross-check)
- https://www.indiannursingcouncil.org/ (INC)
- https://pci.gov.in/en/ and https://pci.gov.in/en/pharmacy-council-of-india/ (PCI)
- https://dciindia.gov.in/ (DCI/NDC — note: legacy DCI domain now serving as NDC's site)
- https://www.pib.gov.in/PressReleasePage.aspx?PRID=2242888&reg=48&lang=2 (NDC constitution, PIB press release)
- https://telanganatoday.com/centre-replaces-dental-council-of-india-with-national-dental-commission (secondary cross-check on DCI→NDC transition)
- https://www.icmr.gov.in/ and https://www.icmr.gov.in/history (ICMR)
- https://cdsco.gov.in/opencms/opencms/en/Home/ and https://dghs.mohfw.gov.in/cdsco.php (CDSCO)
- https://nhm.gov.in/ (NHM)
- https://nabh.co/ (NABH)
- https://nabl-india.org/ (NABL)
- https://qcin.org/ and https://nabcb.qci.org.in/about-qci/ (QCI parent-body context for NABH/NABL)
- https://main.mohfw.gov.in/ (MoHFW)
- https://nha.gov.in/ and https://nha.gov.in/PM-JAY (NHA/PM-JAY)
- https://onlinetsmc.in/ and https://onlinetsmc.in/about-us/our-history/ (TSMC)
- https://vvp.telangana.gov.in/ and https://en.wikipedia.org/wiki/Telangana_Vaidya_Vidhana_Parishad (TVVP)
- https://chfw.telangana.gov.in/ (NHM Telangana host department)
- https://pharmacycouncil.telangana.gov.in/ (Telangana State Pharmacy Council)
- https://hmis.telangana.gov.in/ (Telangana Nurses & Midwives Council)
- https://rajivaarogyasri.telangana.gov.in/ASRI2.0/ (Rajiv Aarogyasri Health Care Trust, Telangana)
- https://apmc.ap.gov.in/ and https://apmc.ap.gov.in/about.html (APMC)
- https://apvvp.ap.gov.in/ and https://en.wikipedia.org/wiki/Andhra_Pradesh_Vaidya_Vidhana_Parishad (APVVP)
- https://hmfw.ap.gov.in/nhm-org.aspx (NHM Andhra Pradesh)
- https://appharmacycouncil.gov.in/site/aboutus (AP Pharmacy Council)
- https://nmcouncil.ap.nic.in/ and https://hmis.ap.nic.in/ (AP Nurses/Midwives Council)
- https://www.ysraarogyasri.ap.gov.in/ and https://drntrvaidyaseva.ap.gov.in/about-us-dr.ysr-aarogyasri-health-care-trust (Dr. YSR Aarogyasri Health Care Trust)

## Conflicts found and how they were resolved

- **NABH founding year:** sources split between 2005 (formation of the accreditation scheme within QCI) and 2006 (launch of the accreditation program itself). Recorded 2006 as the primary figure and flagged both years in the `notes` field rather than silently picking one.
- **NABL founding year:** most sources say 1999; a minority reference 1998 or 2000. Recorded 1999 with the ambiguity flagged in `notes`.
- **MoHFW domain:** multiple mirrored/legacy domains surfaced (`main.mohfw.gov.in`, `mohfw.nic.in`, `mohfw.gov.in`, `mohfw-dohfw.gov.in`). Treated `mohfw.gov.in` as the canonical current domain and noted the mirrors.
- **APMC headquarters address:** one source cited "Dr. NTR University of Health Sciences, Gunadala, Vijayawada" and another cited "Dr. Y.S.R. University of Health Sciences, Vijayawada" for the same building/complex — both point to the same campus in Gunadala, Vijayawada (the university has been renamed over time); resolved to Vijayawada as headquarters city with the naming discrepancy noted.
- **DCI vs. NDC transition timing:** this is a live, very recent regulatory transition — the National Dental Commission Act was passed by Parliament in 2023 but the National Dental Commission was only formally notified/constituted on 19 March 2026, dissolving the Dental Council of India (in continuous operation since 1949). Both dates are recorded distinctly in `notes` to avoid conflating Act-passage year with operational-establishment year. Given how recent this is, the entity is flagged for re-verification once official documentation stabilizes.
- **NHM Telangana / NHM AP dedicated domains:** the task brief's phrasing implied possible dedicated domains (e.g., `nhm.telangana.gov.in`, `nhm.ap.gov.in`); search did not surface such domains. Instead, both states run NHM as a wing of their Commissionerate/Department of Health & Family Welfare (`chfw.telangana.gov.in`, `hmfw.ap.gov.in`). This was resolved by recording the actual department portal as the official website and noting the absence of a separate NHM-specific state domain.

## Entities considered and excluded (with reasons)

- **AYUSH regulatory bodies** (National Commission for Indian System of Medicine / NCISM, National Commission for Homoeopathy / NCH, and their predecessors CCIM/CCH): genuine, active, verifiable national bodies, but they sit under the Ministry of AYUSH rather than the Ministry of Health & Family Welfare and were not named in the task's explicit entity list. Excluded to keep the package focused per the task's stated scope; flagged here in case a future "AYUSH & Traditional Medicine Regulatory Bodies" package is planned.
- **FSSAI (Food Safety and Standards Authority of India)** and **National Pharmaceutical Pricing Authority (NPPA)**: genuine national bodies adjacent to healthcare (food safety, drug pricing) but not primarily medical-practice/health-system regulators or health missions; excluded as out of scope for this specific package.
- **State Drug Control Administrations (Telangana/AP Drugs Control Administration)**: these regulate drug licensing/manufacturing rather than medical practice or health missions per se; excluded to avoid scope creep, though they are legitimate adjacent bodies worth a future "Pharmaceutical Regulation" package.
- **District-level Commissionerates/DCHS offices**: numerous district-level health offices surfaced in search (e.g., DCHS Vizianagaram) — these are administrative sub-units, not standalone regulatory/mission bodies, and were excluded.

## Known gaps / fields marked PENDING_VERIFICATION

- **CDSCO established_year**: could not confirm a precise founding year for the organization in its current form via WebSearch snippets; marked `PENDING_VERIFICATION`.
- **NHM Telangana established_year** and **NHM Andhra Pradesh established_year**: the state-specific NHM administrative units' formal establishment dates (as distinct from the pan-India NRHM 2005 / NHM 2013 launch dates) were not independently confirmed; marked `PENDING_VERIFICATION`.
- **Telangana State Pharmacy Council established_year** and **AP Pharmacy Council established_year**: both operate under the national Pharmacy Act, 1948, but their specific state-level constitution dates were not confirmed; marked `PENDING_VERIFICATION`.
- **Rajiv Aarogyasri Health Care Trust (Telangana) established_year**: the scheme itself dates to 2007 (pre-bifurcation, undivided AP), but the date of separate constitution of a Telangana-specific Trust post-2014 was not confirmed; marked `PENDING_VERIFICATION`.
- **AP Nurses/Midwives Council (APNMC) headquarters_city**: multiple portals (`nmcouncil.ap.nic.in`, `hmis.ap.nic.in`) surfaced without a clearly stated single headquarters city; marked `PENDING_VERIFICATION`. Also note: search results indicated APNMC online services were reported suspended from 16 March 2026 for a portal migration — operational status should be re-checked before this record is used downstream.
- **National Dental Commission (NDC)**: this is an extremely recent transition (notified 19 March 2026, roughly four months before this collection date). The website, governance structure and even the domain (still the legacy `dciindia.gov.in`) may change as the transition settles; flagged for near-term re-verification.
- No direct .gov.in page render was possible this session (WebFetch blocked, confirmed 403). All facts trace to WebSearch result snippets, which themselves often quote or summarize .gov.in / Wikipedia content but were not independently rendered and inspected in full. Recommend a follow-up pass with direct WebFetch access (or a different network egress path) to raise confidence scores above the 80–85 range currently recorded.
