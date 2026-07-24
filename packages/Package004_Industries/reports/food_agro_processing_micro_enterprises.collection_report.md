# Collection Report: Food & Agro-Processing Micro-Enterprises
Package004_Industries_and_Livelihoods v1.0.0 — Telangana & Andhra Pradesh

Collection date: 2026-07-22
Rows produced: 13 (target was 12-20)

## Methodology

1. Scope: seven livelihood/industry categories were researched as *opportunity types* (not
   individual companies): Food Processing (general), Spice Processing, Pickle Making, Masala
   Powder Manufacturing, Cold Pressed Oil Extraction, Millet Processing, Seed Processing.
2. Tooling constraint: WebFetch to `.gov.in` / `.ac.in` / Wikipedia domains was blocked (HTTP 403)
   for this session, as pre-confirmed. All research was therefore done via **WebSearch only** —
   search-engine snippets and AI-summarized excerpts of government PDFs, never a direct fetch/read
   of the source PDF text. This is an important limitation flagged throughout the CSV: numbers
   that "look" government-sourced (i.e., they came from a URL on kviconline.gov.in, niftem.ac.in,
   pmfme.mofpi.gov.in, a state government portal, etc.) were still only *seen* through WebSearch's
   synthesized answer text, not independently verified character-for-character. Confidence scores
   were capped accordingly (max 78, never the full 85 ceiling) even where a specific government
   project-profile document was identified by exact title and URL.
3. Priority source classes searched, in order of evidentiary weight:
   - KVIC / PMEGP (Prime Minister's Employment Generation Programme) official "common project
     profiles" hosted at `kviconline.gov.in/pmegp/pmegpweb/docs/commonprojectprofile/` — these are
     the closest thing to a DIC/MSME project-profile-grade source available for this space.
   - PMFME (Pradhan Mantri Formalisation of Micro Food Processing Enterprises) official "Model
     Detailed Project Reports (DPRs)" hosted by NIFTEM/NIFTEM-T and mirrored on several state PMFME
     Special Purpose Vehicle (SPV) websites (e.g. `pmfmersamb.rajasthan.gov.in`, `pmfmeap.org`).
   - MSME-DI Hyderabad "Brief/District Industrial Profile" documents (covers both Telangana and
     Andhra Pradesh, since MSME-DI Hyderabad is the joint development institute for both states).
   - State policy documents: Government of Telangana MSME Policy Order / Compendium of MSME
     Schemes; Andhra Pradesh Food Processing Policy 4.0 (2024-29).
   - MIDH (Mission for Integrated Development of Horticulture) scheme pages (for seed processing).
   - Secondary/portal sources (NIIR, imarcgroup, agrijob.in, upmsme, various business-loan blogs)
     were used ONLY to cross-check plausibility of a number, never as the primary cited basis for
     a confidence score above 65, per the task's strict rule.
4. Every row's `typical_investment_range_summary` states explicitly whether the figure traces to
   a named government project profile/DPR, or is PENDING_VERIFICATION because no such document's
   internal cost table could be confirmed this session.

## Rows with government-project-profile-grade investment figures (confidence 65-78)

| Row | Sub-category | Figure | Source doc |
|---|---|---|---|
| Masala Powder Manufacturing (Small) | Masala Powder Manufacturing | Total project cost Rs 3.5 lakh (structured line-item breakdown: workshed, equipment, working capital) | KVIC/PMEGP "MASALA MAKING UNIT (SMALL).pdf" |
| Masala Powder Manufacturing (Medium) | Masala Powder Manufacturing | Total project cost Rs 8 lakh | KVIC/PMEGP "MASALA MAKING UNIT (MEDIUM).pdf" |
| Cold-Pressed Groundnut/Sesame Oil (Kachi Ghani) Unit | Cold Pressed Oil Extraction | Total project cost ~Rs 19.5 lakh | KVIC/PMEGP "PROJECT PROFILE ON GROUNDNUT OIL AND OIL CAKE MANUFACTURING.pdf" |
| Small-Scale Flour/Atta Milling Unit | Food Processing (General) | Machinery cost Rs 10.82 lakh (maize) / Rs 24.40 lakh (wheat) — machinery component only, not full total | PMFME Model DPRs (maize flour mill, wheat flour mill), niftem.ac.in / state PMFME mirrors |
| Small-Scale Millet Processing Unit | Millet Processing | Total project cost ~Rs 81.83 lakh (5 MT/day capacity — larger-than-micro scale) | PMFME Model DPR, Ragi/Small Millets Processing Unit |

These five rows are the strongest in the dataset. Even so, none were pushed to the 85-point
ceiling, because the underlying PDF text was never directly fetched/verified this session — only
surfaced via WebSearch's synthesized answer.

## Rows that are portal-estimate-only or PENDING_VERIFICATION (confidence ≤ 65)

| Row | Why capped |
|---|---|
| Turmeric Processing & Powder-Making Unit (TG) | Named KVIC profiles located by URL (Spice Grinding Unit, Cumin Powder) but internal cost table not confirmed; numeric range (Rs 5-25 lakh) came from a mix of portal sources. Confidence 58. |
| Chilli Processing, Grading & Powder-Making Unit (AP) | Same issue — KVIC "Red Chilli Powder Production Unit" and PMFME "Byadgi Chilli" DPR located by exact URL, cost table not confirmed. Confidence 58. |
| Andhra-Style Pickle Making Unit | KVIC profiles (Handmade Pickle, Lime Pickle, Tomato Products and Pickles) located by URL; cost tables not confirmed; portal estimates too widely spread (Rs 5 lakh to Rs 127 lakh depending on scale) to compress responsibly. Investment set to PENDING_VERIFICATION. Confidence 52. |
| General/Telangana-Style Pickle Making Unit | Same basis as above, split out mainly for TG-specific scheme percentages. Confidence 52. |
| Cold-Pressed Coconut Oil Unit | No government project profile found at all for coconut cold-pressing specifically; only generic blog estimates (Rs 5-12 lakh). Investment PENDING_VERIFICATION. Confidence 50. |
| FPO-Level Primary Millet Processing Unit (AP) | IIMR's FPO support is confirmed via a PIB release, but no AP-specific investment figure was found. Investment PENDING_VERIFICATION. Confidence 48. |
| Agricultural Seed Cleaning, Grading & Processing Unit | Only the MIDH subsidy CAP (50% up to Rs 100 lakh) is government-confirmed; no confirmed total-project-cost figure for a typical TG/AP-scale unit was found. Investment PENDING_VERIFICATION. Confidence 48. |
| Small-Scale Multi-Product Food Processing Unit (general) | Deliberately left investment as PENDING_VERIFICATION because the category is too broad to cite one figure responsibly (spans everything from a Rs 3.5 lakh masala unit to a Rs 50 lakh PMEGP ceiling project). Confidence 55. |

**Summary count: 5 of 13 rows carry a genuine government project-profile/DPR-derived investment
figure (though WebSearch-mediated, not directly fetched); 8 of 13 rows have investment set to
PENDING_VERIFICATION or are explicitly flagged portal-only**, in line with the task's strict
verification rule.

## Conflicting information found and how it was resolved

- **Millet processing scale mismatch**: the only government DPR found (PMFME Model DPR for
  Ragi/Small Millets) sizes a unit at 5 MT/day and ~Rs 81.83 lakh — well above what a first-time
  individual micro-entrepreneur would typically build. A real, much smaller example (a Rs 10 lakh
  unit at Chelpur, Bhupalpally, Telangana) was found via a Telangana Today news article. Rather
  than picking one, both figures are presented side-by-side in the row with the scale difference
  and sourcing-quality difference explicitly called out, and confidence was capped at 65 (not
  higher) to reflect that the lower, more "micro-scale-relevant" figure is news/portal-sourced.
- **Pickle investment spread**: portal sources quoted anywhere from Rs 5 lakh (a very small
  home-based unit) to Rs 127.23 lakh (a 1,058 MT/year industrial-scale plant) for "pickle
  manufacturing." Given the enormous spread and the inability to confirm which scale the official
  KVIC profiles (Handmade Pickle, Lime Pickle) actually specify, the investment field was set to
  PENDING_VERIFICATION rather than picking an arbitrary midpoint.
- **"Seed Processing" ambiguity**: this term could mean (a) processing agricultural/crop seeds
  for sowing (cleaning, grading, treating — an agri-input/certification-linked activity), or (b)
  processing food seeds like sesame/chia for consumption (KVIC does have "Chia Seeds Processing
  Unit" and "Sesame Seed Processing Unit" PMEGP profiles). Given the package's framing around
  "industries, trades, and livelihoods" and the presence of a dedicated Seed Village
  Programme/seed-certification ecosystem in Telangana (TSSOCA) and AP, this row was resolved
  toward interpretation (a) — crop seed processing — and categorized as "Agriculture & Allied"
  rather than "Manufacturing." This choice is documented in the row's notes field so a reviewer
  can redirect it if interpretation (b) was actually intended.

## Category/state-split decisions (documented per task's "use judgment" instruction)

- **Spice Processing** was split into a Telangana row (turmeric, citing Telangana's status as
  India's largest turmeric producer per MSME-DI Hyderabad) and an Andhra Pradesh row (chilli,
  citing the Guntur belt) because the raw-material base and regional market context genuinely
  differ, even though the underlying KVIC/PMEGP scheme mechanics are the same.
- **Masala Powder Manufacturing** was split into Small and Medium scale because the KVIC/PMEGP
  portal hosts two distinct, cleanly sourced project profiles with different total-cost figures
  (Rs 3.5 lakh vs Rs 8 lakh) — a genuine scale distinction worth preserving rather than collapsing
  into one imprecise range.
- **Pickle Making** was split into an Andhra-style row (leveraging AP's specific food-processing
  policy subsidy rates and the region's renown for avakaya/gongura pickles) and a general/
  Telangana row (leveraging Telangana's MSME policy rates) — the product/technology base is
  nearly identical, so this split is scheme/state-policy-driven rather than product-driven.
- **Cold Pressed Oil Extraction** was split into groundnut/sesame (kachi ghani — the one with a
  confirmed KVIC cost figure) and coconut (relevant to coastal AP, but with no confirmed
  government figure) rather than merging them, since merging would have falsely implied the
  weaker coconut data point was as well-sourced as the groundnut one.
- **Millet Processing** was split into a Telangana row (where the concrete PMFME DPR + Millet
  Incubation Centre + Chelpur example all exist) and an AP row (where only the IIMR FPO-support
  fact was found, with no investment figure) to avoid overstating how much is known for AP
  specifically.
- **Food Processing (general)** was split into a true "general/umbrella" row (investment
  intentionally left PENDING_VERIFICATION because the category is too broad) and a more concrete
  "Flour/Atta Milling" row, since flour milling is one of the most commonly cited entry-level food
  processing livelihoods in TG/AP and had a genuine PMFME Model DPR machinery-cost figure to
  anchor it.

## Known gaps / recommended follow-up (for a session with unrestricted WebFetch)

1. **Direct PDF verification needed** for all KVIC/PMEGP "common project profile" PDFs cited
   (Masala Making Unit Small/Medium, Groundnut Oil and Oil Cake, Spice Grinding Unit, Cumin
   Powder, Handmade Pickle, Lime Pickle, Tomato Products and Pickles, Red Chilli Powder Production
   Unit, Oil Crusher/Expeller) and all PMFME Model DPR PDFs (maize/wheat flour mill, ragi/millet
   processing, turmeric powder, byadgi chilli) — a session with unblocked `.gov.in`/`.ac.in`
   WebFetch access should re-fetch these directly and confirm exact total-project-cost figures
   line-by-line, which would allow several confidence scores to rise into the 80-85 band.
2. **No confirmed government project profile was found at all** for: coconut cold-pressed oil
   specifically, agricultural seed processing units at TG/AP-relevant scale, and AP-specific
   millet processing unit costs. These three areas are the weakest in the dataset and should be
   prioritized for follow-up research (e.g., checking NABARD's Model Bankable Projects portal
   directly, Coconut Development Board scheme documents, and AP-specific PMFME SPV DPR archives
   at pmfmeap.org/model-micro-dprs, which was identified but not fully explored this session).
3. **PMFME AP-specific DPR archive** (`pmfmeap.org/model-micro-dprs`) was located but not
   exhaustively mined — it likely contains additional AP-specific model DPRs (the search surfaced
   "Bakery" and "Banana Powder" examples in passing) that could sharpen several rows above,
   particularly the general Food Processing and Spice Processing (chilli) rows.
4. **Training availability** claims (RSETI's "Papad, Pickle and Masala Powder Making" batches,
   MSME-DI EDP programmes, PMFME DRP handholding) are reasonably well-established as *general*
   government-training mechanisms, but district-level availability specifically within Telangana/
   AP districts was not individually confirmed for every district.

## Sources consulted (representative list; full set of URLs also appears per-row in the CSV)

- KVIC/PMEGP common project profiles — https://www.kviconline.gov.in/pmegp/pmegpweb/docs/commonprojectprofile/ (various filenames, see CSV `source_url` column)
- PMEGP guidelines (margin money/subsidy rates) — https://www.kviconline.gov.in/pmegpeportal/dashboard/notification/PMEGP_Guidelines_Certified_2022_3.pdf
- PMFME scheme (national) — https://pmfme.mofpi.gov.in/
- PMFME Model DPRs (NIFTEM/NIFTEM-T) — https://niftem.ac.in/newsite/pmfme/... and https://niftem-t.ac.in/pmfme/...
- PMFME AP State Nodal Agency — https://www.pmfmeap.org/ and https://www.pmfmeap.org/model-micro-dprs
- PMFME Rajasthan SNA (mirrors national model DPR for wheat flour mill) — https://pmfmersamb.rajasthan.gov.in/
- MSME-DI Hyderabad (covers both TG & AP) — https://msmedihyderabad.gov.in/
- Government of Telangana MSME Policy Order / Compendium of Schemes — https://rich.telangana.gov.in/assets/pdfs/Resources/Compendium-of-MSME-Schemes-050922.pdf
- Andhra Pradesh Food Processing Policy 4.0 (2024-29) — https://www.apexports.ap.gov.in/assets/gallery/AP%20Food%20Processing%20Policy%20(4.0)%20%202024-29.pdf
- Government of Telangana Horticulture / MIDH scheme page — https://shm.tg.nic.in/Scheme.html
- TSSOCA (Telangana State Seed & Organic Certification Authority) — https://tssoca.telangana.gov.in/indian-seed-processing-units/
- seednet.gov.in (Dept. of Agriculture & Farmers Welfare) — https://seednet.gov.in/material/prog-schemes.htm
- PIB press releases (IIMR millet FPO support, RSETI courses) — https://www.pib.gov.in/
- Agro Spectrum India (Telangana Millet Incubation Centre) — https://agrospectrumindia.com/2023/09/17/telangana-inaugurates-the-first-of-its-kind-millet-incubation-centre-at-hyderabad.html
- Telangana Today (Chelpur/Bhupalpally millet unit) — https://telanganatoday.com/telangana-bhupalpally-swears-by-millets-as-farmers-turn-to-cereal-grains

Note: this session's WebFetch tool was blocked from directly retrieving any of the above
`.gov.in`/`.ac.in` URLs (confirmed HTTP 403 per task instructions); all information from these
domains was obtained exclusively through WebSearch's returned snippets/summaries.
