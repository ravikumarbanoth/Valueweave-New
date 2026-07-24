# Enrichment Report v2: Construction & Skilled Trade Services
Package004_Industries_and_Livelihoods — Business Opportunity Knowledge Base transformation

**Dataset file:** `construction_skilled_trade_services.csv` (11 rows, 36 columns)
**Enrichment date:** 2026-07-23
**Base version:** RC1 collection (`construction_skilled_trade_services.collection_report.md`, 2026-07-22, 18 columns)
**Method:** WebSearch only (WebFetch to .gov.in/.ac.in/.nic.in confirmed HTTP 403 this session, re-tested live). No row's `id` was changed; no RC1-verified fact was removed or degraded — RC1 fields were kept and, where a better source was found, improved in place. All new fields are grounded in a specific, named, citable source or explicitly marked `PENDING_VERIFICATION`; no field was filled with generic filler.

## 1. Schema change

Added 19 new fields (18 requested + retained `ideal_target_audience` rename/expansion), renamed `target_customers`→`ideal_target_audience`, `typical_investment_range_summary`→`investment_range_summary`, `training_availability_summary`→`training_providers_summary`. Final column count: 36 (was 18).

## 2. Fill-rate by new field (11 rows each)

| Field | Fully grounded | Grounded w/ caveat | Fully PENDING_VERIFICATION |
|---|---|---|---|
| ideal_target_audience | 8 | 3 | 0 |
| minimum_investment | 1 | 1 | 9 |
| working_capital_summary | 2 | 1 | 8 |
| machinery_equipment_summary | 11 | 0 | 0 |
| raw_materials_summary | 11 | 0 | 0 |
| supplier_ecosystem_summary | 11 | 0 | 0 |
| customer_segments_summary | 11 | 0 | 0 |
| marketing_channels_summary | 11 | 0 | 0 |
| online_selling_options_summary | 4 | 0 | 7 |
| estimated_setup_time_summary | 0 | 1 | 10 |
| typical_risks_summary | 6 | 0 | 5 |
| seasonal_factors_summary | 1 | 0 | 10 |
| ai_tools_summary | 2 | 1 | 8 |
| automation_opportunities_summary | 4 | 0 | 7 |
| sustainability_summary | 5 | 0 | 6 |
| future_demand_summary | 10 | 1 | 0 |
| related_businesses_summary | 11 | 0 | 0 |
| district_suitability_summary | 0 | 0 | 11 |
| success_stories_summary | 3 | 0 | 8 |

**Pattern:** fields tied to real, named, currently-operating commercial entities (equipment/materials/suppliers/customers/marketing channels, and general construction-sector demand) filled at or near 100%. Fields requiring a specific "typical cost" benchmark, an individually-verifiable named person's success story, or a district-level breakdown remained mostly `PENDING_VERIFICATION`, because no authoritative source exists for most of them in the public record — consistent with RC1's finding that "investment" was the weakest field type across this dataset.

## 3. Notable real findings

- **Borewell Drilling** (`minimum_investment`, previously fully PENDING): upgraded with real current commercial rig pricing — single-unit lorry from ~₹60 lakh+GST, double-unit ~₹1.3 crore+GST, DTH rigs ~₹18.5 lakh–₹1.08 crore (TradeIndia/IndiaMART/Ganesh Drillers Hyderabad), plus per-foot drilling costs (₹150–420/ft) and drill-bit replacement costs (₹8,000–15,000 every 300–500 ft in Hyderabad granite). Also grounded a nuanced, non-generic `future_demand_summary`: baseline demand is high (60%+ of Indian irrigation depends on borewells) but coexists with a documented groundwater-depletion crisis (NASA GRACE data) and tightening CGWA/state regulation — reported honestly as a mixed picture rather than simple growth.
- **Carpentry**: found a genuine, named, independently findable success story — Priti Ajay Hinge, the only woman carpenter in Wathoda village, Maharashtra (YourStory, 2022), running an 8-year-established furniture business. This is the strongest individual success story in the dataset and materially improves both `success_stories_summary` and `ideal_target_audience` (women/rural entrepreneurs).
- **Welding & Fabrication**: added peer-reviewed, India-specific occupational-hazard data (Vellore and Delhi studies via PMC) — cut/hand injuries 38%, arc-eye 17%, burns 14%, plus fume-related respiratory risk — the most specific `typical_risks_summary` in the dataset. Also named three real CNC/laser-cutting service bureaus (Fast Cutting India, Weldarc India, Cyclotron Industries) as a documented automation option.
- **Painting**: found a genuine India-specific AI tool — the "Colour with Asian Paints" app's AI Visualizer (real-time camera-based colour preview) — and strong seasonal data (Diwali festive quarter = ~30–35% of annual paint-sector sales; monsoon is the slack season).
- **POP/False Ceiling**: two real named founder stories — Ceiling Banao (Manoj Kumar Mishra, "India's first digital platform for the false ceiling industry") and MyCeiling Pvt Ltd (Bangalore, prefab ceiling-decor alternative).
- **Tiles Fixing**: Somany Ceramics' real, quantified CSR "Tile Master" programme (800 masons trained, documented 25% productivity gain / 50% wastage reduction) — noted explicitly that its covered states (Delhi, Haryana, UP, HP, Gujarat, Rajasthan) do **not** include Telangana/AP, so relevance to this dataset's geography is flagged, not overstated.
- **Electrical Services**: Barefoot College (Tilonia, Rajasthan) — 2,500+ women trained as solar engineers, 75,000+ households electrified — used to genuinely ground women-entrepreneur suitability rather than asserting it generically. EV-charging market growth (27,000+ public stations, 22–31% CAGR to 2030–2035) grounds `future_demand_summary`.
- **Submersible Pump**: PM-KUSUM (real, active, PIB-sourced scheme, up to 90% solar-pump subsidy, 20 lakh farmer target) used to ground both `government_schemes_summary` (as a demand-side driver) and `future_demand_summary`.

## 4. Explicitly declined for lack of verification

- `district_suitability_summary`: 0/11 filled — no Telangana/AP district-level demand or saturation data was found for any trade in this search; declined entirely rather than inferring from state-level data.
- `estimated_setup_time_summary`: 0/11 fully filled — "time to acquire the trade skill" (a documented figure) was consistently NOT the same as "time to set up a business," and no source addressed the latter directly; declined rather than conflating the two.
- `minimum_investment` / `working_capital_summary`: PENDING for most trades — RC1 already established that no authoritative "typical cost" study exists for most of these trades; this pass did not manufacture figures to fill the gap, and only upgraded the two rows (Carpentry via PM Vishwakarma, Borewell Drilling via real commercial rig pricing) where a genuine source existed.
- `ai_tools_summary`: mostly PENDING — international AI trade-management tools (ServiceTitan, Jobber, BuildOps) were found but explicitly caveated as US-market evidence with no confirmed India adoption, rather than presented as India-relevant.
- `success_stories_summary`: 8/11 PENDING — aggregate platform statistics (e.g., Urban Company average partner earnings) were deliberately NOT substituted for an individually verifiable named success story, per the strict-accuracy instruction.

## 5. Confidence scores

All scores capped at 85 (Carpentry, the strongest-sourced row, reached the cap). Increases from RC1 ranged +3 to +8, sized to the volume and quality of new corroboration found per row (largest increase, +8: Borewell Drilling). No score was inflated beyond what the added sourcing supports.
