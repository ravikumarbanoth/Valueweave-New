# Collection Report: Construction & Skilled Trade Services
Package004_Industries_and_Livelihoods v1.0.0 — Telangana & Andhra Pradesh

**Dataset file:** `construction_skilled_trade_services.csv` (11 rows)
**Collection date:** 2026-07-22
**Collector:** Automated research agent (WebSearch only; WebFetch to .gov.in/.ac.in/Wikipedia blocked by session egress policy — confirmed HTTP 403 on retest)

## 1. Methodology

- Scope: nine named trade categories (Plumbing, Electrical Services, Welding & Fabrication, Carpentry, Painting, Aluminium Fabrication, Borewell Services, Tiles Fixing, POP Works/False Ceiling), expanded to **11 rows** by splitting Electrical Services into a basic Wireman/Electrician tier and a higher Licensed Contractor/Supervisor tier, and splitting Borewell Services into Drilling and Submersible Pump Installation & Repair (distinct livelihood profiles within the same trade family).
- Each row was researched via a series of targeted WebSearch queries covering: (a) DGT/NCVT ITI trade curricula (Craftsman Training Scheme), (b) NSDC/PMKVY Qualification Packs and Sector Skill Council (CSDCI) course specs, (c) state-level licensing regulations (Telangana Electrical Licensing Board/SBTET, WALTA groundwater law), (d) government livelihood/credit schemes (PM Vishwakarma, PMEGP/KVIC, Pradhan Mantri Mudra Yojana), and (e) MSME/DIC model project-profile cost figures.
- No direct WebFetch of primary source documents was possible this session (org egress policy blocks .gov.in/.ac.in/Wikipedia); all facts are drawn from WebSearch result snippets/summaries, including snippets of secondary sites quoting or paraphrasing primary government documents. This is disclosed per-row in the `notes` field and reflected in capped confidence scores.
- Per the task's strict rule, any field lacking a traceable authoritative source was set to **PENDING_VERIFICATION** in-line within the relevant summary field (rather than silently guessing), with confidence capped at 65 for portal-estimate-only content and at most 85 for content traced to a government source (further reduced when the government document itself was only seen via a secondary summary, not a direct read).

## 2. Sources Consulted

**Skills/training (government-linked):**
- NSDC course pages: nsdcindia.org (Plumber (General), Assistant Electrician, Welding and Quality Technician, Mason Tiling)
- DGT/NCVT ITI trade syllabi: cstaricalcutta.gov.in, bharatskills.gov.in (Plumber, Electrician, Welder, Carpenter)
- CSDCI (Construction Skill Development Council of India) qualification packs: csdcindia.org (Painter, Tile Mason, False Ceiling & Drywall Installer)
- National Qualifications Register: nqr.gov.in (Tile Mason — Basic; Helper Construction Painter)
- ITI course aggregators (non-primary): targetstudy.com, syllabus.iti.directory, collegedekho.com (Pump Operator cum Mechanic)
- APSSDC (Andhra Pradesh State Skill Development Corporation): jobskills.apssdc.in

**Licensing (government-linked):**
- Telangana State Electrical Licensing Regulations, 2018 — accessed via indiankanoon.org (case-law repository hosting the regulation text) and secondary how-to summaries (electrical4u.net, wikiprocedure.com)
- Telangana Water, Land and Trees Act (WALTA), 2002 — accessed via indiacode.nic.in (official legislative repository) search snippet, plus secondary procedural summaries (wikiprocedure.com, svdrillers.com blog)
- Central Ground Water Authority (CGWA) — cgwa.mowr.gov.in (referenced, not directly fetched)

**Schemes/finance (government-linked):**
- PM Vishwakarma Yojana official trade list and benefits — pib.gov.in press release
- Pradhan Mantri Mudra Yojana (PMMY) — mudra.org.in FAQ
- PMEGP/KVIC common project profiles — kviconline.gov.in (Welding Workshop case example, Wooden Furniture profile, Aluminium Fabrication profile)
- MSME-DI Thrissur project profile on Aluminium Fabrication — msmedithrissur.gov.in

## 3. Government-Sourced vs. Portal-Only Rows

| Row | Training data | Licensing data | Investment data |
|---|---|---|---|
| Plumbing | Gov-sourced (DGT/NSDC) | N/A (verified no license needed) | Portal-estimate only |
| Electrical Services (Wireman) | Gov-sourced (DGT/NSDC/SBTET) | Gov-sourced (TS Electrical Licensing Regs 2018, via secondary summary) | Portal-estimate only |
| Electrical Contracting (Supervisor/Contractor) | Gov-sourced (SBTET) | Gov-sourced (via secondary summary) | Portal-estimate only |
| Welding & Fabrication | Gov-sourced (DGT/NSDC/APSSDC) | N/A (verified no license needed) | PMEGP case example (gov-linked, single case) |
| Carpentry | Gov-sourced (DGT/PM Vishwakarma) | N/A (verified no license needed) | **Gov-sourced** (PM Vishwakarma Rs 15,000 toolkit — strongest figure in dataset) |
| Painting | Gov-sourced (CSDCI/NSDC/NQR) | N/A (verified no license needed) | Portal-estimate only |
| Aluminium Fabrication | Not found (flagged PENDING_VERIFICATION) | N/A (verified no license needed) | Gov document (MSME/KVIC) but only seen via search snippet — lower confidence |
| Borewell Drilling | Not found (flagged PENDING_VERIFICATION) | Gov-sourced (WALTA Act 2002, via snippet) | Portal-estimate only |
| Submersible Pump Repair | Third-party aggregator only (not primary DGT fetch) | N/A (verified no license needed) | Portal-estimate only |
| Tiles Fixing | Gov-sourced (CSDCI/NQR) | N/A (verified no license needed) | Portal-estimate only; PM Vishwakarma applicability explicitly flagged uncertain |
| POP/False Ceiling | Gov-sourced (CSDCI/NSDC) | N/A (verified no license needed) | Portal-estimate only |

Overall: **6 of 11 rows** have government-sourced training data with reasonable confidence (70-82); **2 rows** (Electrical Services variants) have a verifiable, named state licensing requirement; **1 row** (Carpentry) has a fully government-benchmarked investment figure (PM Vishwakarma toolkit). No row has all three fields (training + license + investment) fully government-verified simultaneously — investment is the weakest field across the whole dataset, consistent with the general absence of authoritative "typical cost to become an independent tradesperson" studies in the public record.

## 4. Conflicts Found / Resolved

- **PM Vishwakarma trade coverage**: initial assumption might have been that all "traditional trades" are covered by PM Vishwakarma. Cross-checked the official 18-trade list (PIB) and confirmed only **Carpenter** and **Mason (Rajmistri)** among our nine categories are explicitly listed — Plumber, Electrician, Welder, Painter, Aluminium Fabricator, Tile Mason, and POP/False Ceiling installer are **not** named trades under the scheme. This was resolved by explicitly stating non-applicability in each affected row rather than assuming eligibility, and by flagging "Tile Mason" as an open question relative to the broader "Mason" trade rather than conflating the two.
- **Multiple CSDCI False-Ceiling QP code versions** (CON/Q1103, CON/Q1104, CON/Q1107, CON/Q1111) appeared across different document years — resolved by treating the code as indicative of a qualification *family* rather than asserting one definitive current code, and disclosing the version drift in the row's notes.
- **Aluminium fabrication investment figures** varied widely across different KVIC/MSME document snippets (Rs 2.65 lakh to Rs 17.56 lakh) — resolved by presenting the full observed range with an explicit caveat that these are multiple distinct illustrative model profiles, not one official number, and flagging for direct-document re-verification.

## 5. Known Gaps

1. **No direct primary-document verification** was possible for any .gov.in/.nic.in source this session due to the organizational WebFetch block; all "government-sourced" facts were obtained via WebSearch snippets of either the primary document or a secondary site quoting it. Recommend a follow-up pass with direct fetch access to confirm: Telangana State Electrical Licensing Regulations 2018 (full text), WALTA Act 2002 current drilling-rig rules, and the KVIC/MSME project profile PDFs in full.
2. **No authoritative "typical investment" figures** exist for Plumbing, Electrical Services (both tiers), Painting, Borewell Drilling, Submersible Pump Repair, Tiles Fixing, or POP/False Ceiling — these remain PENDING_VERIFICATION/portal-estimate-only. Only Carpentry (PM Vishwakarma) has a solid government benchmark; Welding & Aluminium Fabrication have single-case PMEGP/MSME examples rather than a generalized range.
3. **No named formal training body/course** was identified for Aluminium Fabrication or Borewell Drilling — both trades appear to be learned primarily through informal apprenticeship in the Indian context, and this absence is reported rather than filled with an invented training program.
4. **AP-specific equivalents** to Telangana's Electrical Licensing Board / SBTET wireman-supervisor certificate process were not independently located in this pass — the electrical licensing rows are Telangana-specific; Andhra Pradesh's parallel regulatory framework (likely under its own Electrical Inspectorate) should be researched separately before assuming identical rules apply.
5. **Tile Mason's relationship to PM Vishwakarma's "Mason (Rajmistri)" trade** is unresolved — it is plausible but unconfirmed that tile-fixing specialists can register under the broader Mason trade; this is flagged rather than assumed in the dataset.
