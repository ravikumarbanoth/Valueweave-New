# Enrichment Report v2: Food & Agro-Processing Micro-Enterprises
Package004_Industries_and_Livelihoods — Business Opportunity Knowledge Base transformation

**Dataset file:** `food_agro_processing_micro_enterprises.csv` (13 rows, 36 columns)
**Enrichment date:** 2026-07-24
**Base version:** RC1 collection (`food_agro_processing_micro_enterprises.collection_report.md`, 2026-07-22, 18 columns)
**Method:** WebSearch only (WebFetch to .gov.in/.ac.in/.nic.in/Wikipedia confirmed blocked this session, consistent with prior packages). No row's `id`, `name`, `category`, `sub_category` or `description` was changed; no RC1-verified fact was removed or degraded — RC1 fields were kept and, where a better source was found, improved in place. All new fields are grounded in a specific, named, citable source or set to the exact bare string `PENDING_VERIFICATION`; no field was filled with generic filler.

## 1. Schema change

Added 19 new fields (18 requested + `ideal_target_audience`), renamed `target_customers`→`ideal_target_audience`/`customer_segments_summary` (split across both, per the target schema), `typical_investment_range_summary`→`investment_range_summary`, `training_availability_summary`→`training_providers_summary`. Final column count: 36 (was 18), header order verified to match `construction_skilled_trade_services.csv` exactly.

## 2. A data-integrity bug caught and fixed before delivery

During self-validation (required by the task's critical rule 2), an earlier draft of this enrichment was found to have **26 cells** where `PENDING_VERIFICATION` had explanatory text concatenated directly onto it (e.g. `PENDING_VERIFICATION (only machinery-cost components are sourced...)`) — the exact recurring bug flagged in the task instructions. Every such cell was corrected programmatically: the cell was reset to the exact bare string `PENDING_VERIFICATION`, and the explanation was moved into the `notes` column as `[field_name]: explanation`. A stricter follow-up pass distinguished this true bug pattern (cell *starts with* `PENDING_VERIFICATION` plus appended text) from legitimate narrative cells that merely *reference* the phrase mid-sentence inside a substantive, sourced paragraph (e.g. `investment_range_summary` text like "...the underlying KVIC project-profile sourcing and PENDING_VERIFICATION investment caveat are identical to the Andhra-Style Pickle row" — a real narrative sentence in the same style already used in the accepted `construction_skilled_trade_services.csv` reference dataset). Those legitimate narrative cells were left untouched. Final automated validation confirms **zero** remaining cells where `PENDING_VERIFICATION` is not the exact, complete cell value.

## 3. Fill-rate by new field (13 rows each)

| Field | Filled with sourced content | Pending |
|---|---|---|
| ideal_target_audience | 13 | 0 |
| minimum_investment | 3 | 10 |
| investment_range_summary | 13 | 0 |
| working_capital_summary | 2 | 11 |
| machinery_equipment_summary | 10 | 3 |
| raw_materials_summary | 13 | 0 |
| supplier_ecosystem_summary | 9 | 4 |
| customer_segments_summary | 13 | 0 |
| training_providers_summary | 13 | 0 |
| marketing_channels_summary | 5 | 8 |
| online_selling_options_summary | 8 | 5 |
| estimated_setup_time_summary | 0 | 13 |
| typical_risks_summary | 11 | 2 |
| seasonal_factors_summary | 1 | 12 |
| ai_tools_summary | 0 | 13 |
| automation_opportunities_summary | 6 | 7 |
| sustainability_summary | 1 | 12 |
| future_demand_summary | 8 | 5 |
| related_businesses_summary | 13 | 0 |
| district_suitability_summary | 6 | 7 |
| success_stories_summary | 5 | 8 |

**Pattern:** fields tied to real, named, currently-operating commercial entities (machinery/equipment brands and prices, raw-material sourcing, customer segments, training providers, related businesses) filled at or near 100%. Fields requiring a confirmed government total-project-cost figure, a formal "AI tool adoption in this exact Indian micro-enterprise category" study, or a granular seasonal-demand study were mostly `PENDING_VERIFICATION` — consistent with the pattern already established in the construction dataset, where "investment," "AI tools" and "seasonal factors" were similarly the weakest field types.

## 4. Notable real findings

- **Turmeric Processing (Nizamabad)**: the **National Turmeric Board** was inaugurated in Nizamabad in 2025 (PIB/DD News/Agro Spectrum India), targeting $1 billion in turmeric exports by 2030 — a concrete, government-backed, region-specific institutional finding that materially strengthens `future_demand_summary` and `district_suitability_summary`. Real named machinery suppliers (Confider Industries LLP, Vilnesh International, Bharath Industrial Works) with specific prices (~Rs 4.9–7.8 lakh for 500 kg/hr semi-automatic lines) were also sourced.
- **Chilli Processing (Guntur)**: sourced real export-value data (~$640 million from Guntur district alone in 2019-20, per ThePrint), a real PMFME Chilli Incubation Centre at RARS Warangal extending institutional support into Telangana, named D2C brands (Guntur Farmlands, Umadi Foods), and a specific, real FSSAI compliance event — Patanjali Foods' 2025 recall of 4 tonnes of red chilli powder over a pesticide-residue finding.
- **Masala Powder (Small & Medium)**: these rows already carried the strongest government-DPR sourcing in RC1 (KVIC/PMEGP total project costs of Rs 3.5 lakh and Rs 8 lakh respectively); this pass added a real, verifiable success story — **Badshah Masala**, founded 1958 as a home-based Mumbai spice business selling from a bicycle, later acquired by Dabur India — illustrating this exact business model's growth ceiling (not Telangana/AP-specific, flagged as such).
- **Andhra-Style Pickle**: found a strong, specific, regionally-matched success story — **Bhogaraju Foods** (Andhra Pradesh), where founder Vasudha Bhogaraju turned her mother's loss-making home pickle business into a Rs 2 crore/year enterprise selling 29 varieties to 13 countries after completing a digital-marketing course and launching an e-commerce site in 2017 (30stades.com). The same source also documents a real, named risk pattern (pricing/positioning failure in the original home business) used directly in `typical_risks_summary`.
- **Cold-Pressed Groundnut/Sesame Oil**: found multiple real, named D2C brands validating the category (Tata Simply Better — a large-FMCG entrant — Earthen Story, Little Farmer India, KachiGhaani.com), a peer-reviewed source on groundnut oil-cake as a sustainable cattle-feed by-product, and sourced Anantapur/Rayalaseema district groundnut-production data (including a real supply-side risk: reported production decline from rainfall deficit and labour costs, per Deccan Chronicle).
- **Millet Processing (Telangana)**: sourced two genuine, named, Hyderabad-headquartered millet-food success stories — **Troo Good** (founder Raju Bhupati, scaled from 1,000 to 90,000 school parathas/month) and **Health Sutra** (founder Sai Krishna Popuri, ~Rs 4 crore annual revenue from a Rs 5 lakh start) — plus formal market-research demand data (India's millet market projected at 13.4–15.8% CAGR through 2036, Future Market Insights/6Wresearch/Ken Research).
- **FPO-Level Millet Processing (AP)**: found a real, named, ICAR-documented facility — the **Dhimsa FPO Millet Processing Unit-cum-Custom Hiring Centre** at Killoguda village, Alluri Sitarama Raju district, AP, serving small/marginal tribal farmers — used for both `district_suitability_summary` and `success_stories_summary`, a substantial upgrade from RC1's generic PIB-only sourcing.
- **Seed Processing**: sourced real, named, priced seed-cleaning/grading machinery (Prince Agro Industries ~Rs 21.6 lakh; Agro Asian Industries Rs 8.5–17.5 lakh by capacity tier) and concrete TSSDCL operational data (~5,700 contracted farmers across ~45,000 acres; a Central Quality Control Laboratory operating in Hyderabad since 1983).

## 5. Explicitly declined for lack of verification

- `ai_tools_summary`: 0/13 filled — no India-specific evidence of AI tool adoption (demand forecasting, quality-control machine vision, etc.) at the food/agro-processing *micro-enterprise* scale was found; academic machine-vision spice-quality research exists but is not a deployed tool for this dataset's entrepreneur profile, so it was not substituted in.
- `estimated_setup_time_summary`: 0/13 filled — no source distinguished "business setup time" from "training/certification duration" for any row in this dataset, mirroring the same gap identified in the construction dataset.
- `sustainability_summary` / `seasonal_factors_summary`: mostly PENDING except where a specific, sourced claim existed (cold-press vs. solvent-extraction energy/chemical profile; groundnut oil-cake as feed; turmeric's Feb–May harvest-arrival price pattern) — generic "sustainability is good" or "seasonality exists" claims were deliberately not invented for rows lacking a real citation.
- `minimum_investment` / `working_capital_summary`: PENDING for most rows — RC1 already established that most sub-categories lack a single confirmable total-project-cost figure; this pass only filled these fields where a government KVIC/PMEGP/PMFME project-profile line-item breakdown was directly traceable (Masala Small/Medium, Flour Milling's machinery-cost component, Cold-Pressed Groundnut/Sesame Oil's KVIC total).
- `success_stories_summary`: 8/13 PENDING — several real named D2C brands were found (Tata Simply Better, Coco Soul/ITC, etc.) but explicitly **not** used as claimed regional success stories because none were confirmed as Telangana/AP-based or micro-enterprise-scale; they were instead cited under `marketing_channels_summary`/`online_selling_options_summary` context where their relevance is accurate without overreach. A vague web-search reference to "an entrepreneur building a Rs 150-crore chilli business" could not be traced to a named individual or citable article and was explicitly not used.

## 6. Source conflicts encountered

- **Turmeric/Chilli investment figures**: portal-sourced numeric ranges (Rs 5–19 lakh for turmeric; Rs 6.5–25 lakh for chilli) could not be reconciled with a single confirmed government DPR total-cost line despite locating the exact official KVIC/PMEGP and PMFME document titles/URLs — both rows retain `investment_range_summary` narrative explaining this gap rather than picking one portal figure.
- **Millet Processing (Telangana)**: two investment data points for meaningfully different scales were not reconciled — the official PMFME Model DPR (~Rs 81.83 lakh, a 5 MT/day institutional facility) versus the real Chelpur/Bhupalpally SHG unit (~Rs 10 lakh, a news-portal figure, not a project-profile document). Both are retained side-by-side in `investment_range_summary` with the scale mismatch flagged explicitly rather than averaged or collapsed into one number.
- **Pickle Making (Andhra-style vs. Telangana-style)**: the strongest new success story (Bhogaraju Foods) is Andhra Pradesh-specific; it was used fully for the Andhra-Style Pickle row but only referenced as cross-row context (not claimed as a Telangana example) for the General/Telangana-Style Pickle row, which received a smaller confidence increase (+4) as a result.

## 7. Confidence scores

Range: 55–83 (post-enrichment), up from 48–78 (RC1). All increases fall within the +8-per-row cap and no score was lowered. Increases were sized to the volume and quality of new corroboration found per row: the largest increases (+8, at the cap) went to Turmeric, Chilli, Andhra-Style Pickle, Cold-Pressed Groundnut/Sesame Oil, Cold-Pressed Coconut Oil, Small-Scale Millet Processing, FPO-Level Millet Processing, and Seed Processing — each of which gained a genuinely new, named, verifiable institutional fact or success story. The Small-Scale Multi-Product Food Processing row (too broad a category for any single confirming source) was left unchanged at 55. `verification_status` remains `VST-NEEDS_REVIEW` for all 13 rows as instructed.
