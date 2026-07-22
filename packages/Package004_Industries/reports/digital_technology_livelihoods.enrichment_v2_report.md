# Enrichment Report v2: Digital & Technology Livelihoods

## Package004_Industries_and_Livelihoods — Telangana & Andhra Pradesh

**Enrichment date:** 2026-07-23
**Base dataset (RC1):** `digital_technology_livelihoods.csv` (12 rows, 18 columns), collected 2026-07-22
**Enriched dataset (this pass):** same file, overwritten in place, now 36 columns
**Companion report:** `digital_technology_livelihoods.collection_report.md` (RC1 methodology, unchanged)

## Methodology

RC1's 12 rows and their verified fields (`name`, `category`, `sub_category`, `description`, `skill_level`, `licenses_required_summary`, `government_schemes_summary`, `rural_urban_suitability`) were preserved and, where new sourcing was found, extended rather than replaced. `target_customers` was renamed and expanded into `ideal_target_audience`. `typical_investment_range_summary` was renamed `investment_range_summary`; `training_availability_summary` was renamed `training_providers_summary`. Eighteen new fields were added per the task specification.

Research used WebSearch only (WebFetch to .gov.in/.ac.in/.nic.in domains remained blocked, HTTP 403, consistent with RC1). Roughly 25 targeted searches were run across five source tiers: NASSCOM (Strategic Review 2026, FutureSkills Prime, gig-economy/community reports), vendor/certification pricing pages (via aggregators), Tracxn/CBInsights startup-market data, Telangana state-news coverage (thenewsminute.com) of IT-tower operations, and named practitioner/company profiles (LinkedIn, YourStory-referencing directories). No field was filled with generic "AI helps efficiency"-type filler; every non-PENDING_VERIFICATION claim traces to a specific named source.

## Fill-Rate by New Field (12 rows each)

| Field | Status |
|---|---|
| `ideal_target_audience` | 12/12 filled — all rows expanded to address students, job seekers, self-employed, women entrepreneurs, MSMEs, rural entrepreneurs, investors, local businesses per category fit |
| `minimum_investment` | 0/12 as a single authoritative figure, but **5/12 carry real, named, current cost data** even though flagged PENDING_VERIFICATION for a single TG/AP-verified number: DTL003 (Wix/no-code builder pricing ~Rs 300-1,500/mo), DTL005 (Google Play $25 one-time / Apple $99/yr platform fees), DTL009 (AWS $100-150 / Azure Rs 3,700-4,800 certification fees), DTL010 (CEH cert cost range Rs 8,459-1,50,000+), DTL011 (Power BI Pro ~Rs 1,000-1,600/mo vs. Tableau Creator ~Rs 5,500/mo) |
| `investment_range_summary` | 1/12 with a genuinely verified figure: **DTL012** — Telangana's documented 50% fixed-capital-investment subsidy (capped Rs 40 lakh/unit, first 3 companies; 10%/Rs 8 lakh thereafter). Remaining 11/12 stay PENDING_VERIFICATION for a single authoritative figure (unchanged limitation from RC1: no government/NASSCOM costing guide exists for these categories) |
| `working_capital_summary` | 0/12 with a sourced figure — genuinely no authoritative source found for any row; all honestly marked PENDING_VERIFICATION with qualitative reasoning only |
| `machinery_equipment_summary` | 9/12 with real named tools/costs (VS Code, GitHub, Wix, Power BI, Azure/AWS accounts, etc.); 3/12 (DTL002, DTL004, DTL007) partially PENDING_VERIFICATION for specific pricing |
| `raw_materials_summary` | 12/12 — "Not Applicable" stated explicitly for all rows (digital/software services consume no physical raw materials) |
| `supplier_ecosystem_summary` | 12/12 — real named vendors throughout: GitHub, AWS/Azure/GCP, Upwork/Fiverr/Freelancer.com/Toptal, WordPress/Wix/Shopify, Power BI/Tableau, EC-Council |
| `customer_segments_summary` | 12/12 filled |
| `marketing_channels_summary` | 12/12 filled — LinkedIn, marketplace profiles, local networking, referrals, tailored per category |
| `online_selling_options_summary` | 12/12 filled (DTL012 explicitly notes marketplaces are not applicable to this B2B-tender category) |
| `estimated_setup_time_summary` | 0/12 — no authoritative timeline source found for any row; uniformly PENDING_VERIFICATION rather than invented |
| `typical_risks_summary` | 12/12 filled with real, sourced risks (platform price competition, AI commoditization stats, certification-cost barriers, algorithm-change risk, talent-retention risk) |
| `seasonal_factors_summary` | 0/12 — no TG/AP-specific seasonality data found; all PENDING_VERIFICATION (plausible patterns noted as unconfirmed, not stated as fact) |
| `ai_tools_summary` | 11/12 filled with real, named, currently-marketed tools; DTL012 (rural BPO center) explicitly PENDING_VERIFICATION — no category-specific AI-tool documentation found |
| `automation_opportunities_summary` | 11/12 filled; DTL012 PENDING_VERIFICATION |
| `sustainability_summary` | 0/12 with a quantified figure — all honestly PENDING_VERIFICATION; qualitative remote-work logic noted but not presented as verified fact |
| `future_demand_summary` | 7/12 with a real cited NASSCOM/industry figure; 5/12 PENDING_VERIFICATION for a category-specific number (though several still reference the broader NASSCOM Strategic Review 2026 industry forecast as context) |
| `related_businesses_summary` | 12/12 filled |
| `district_suitability_summary` | 12/12 filled; DTL012 notably upgraded with real named district data (Nizamabad, Warangal, Khammam) |
| `success_stories_summary` | 7/12 with a real, named, findable example; 5/12 (DTL002 uses a hedged ecosystem-level example rather than a literal match) honestly PENDING_VERIFICATION where no individual match was found |

## Notable Real Findings

- **NASSCOM Technology Sector in India: Strategic Review 2026** — Indian tech industry revenue forecast at $315B in FY26 (+6.1% YoY), IT services ~$149B, AI-related revenue $10-12B, GCC expansion as a growth driver, mid-tier firms "outpacing top-tier peers." Used across `future_demand_summary` for DTL001, DTL002, DTL009, DTL011.
- **NASSCOM/FutureSkills Prime**: Digital Marketing + AI programme enrollments grew 3.1x since Q3 2024 — a directly relevant, quantified demand signal for DTL006/DTL008.
- **Empiezo IT Solutions** (DTL011) — real, named, multiply-corroborated (Tracxn, CBInsights, LinkedIn) Hyderabad data-analytics/AI firm, founded 2016 by Sirisha Kasinadhuni, backed by WE-Hub and Atal Incubation Centre-CCMB. Strongest success-story match found this pass.
- **Rakesh Bandari ("Rakesh Ranks")** (DTL003, DTL006, DTL008) — named Hyderabad freelance web/SEO/digital-marketing consultant, YourStory-featured, documented 90% organic-traffic increase for a retail client.
- **Khammam/Warangal/Nizamabad IT towers** (DTL012) — 75 companies operating, ~12,500 youth employed; Khammam hub specifically credited to NRI entrepreneur Lax Chepuri's coordination with the state government; Warangal tower houses Tech Mahindra, Cyient, Genpact. Real Telangana GRID/LEAP subsidy structure (50%/Rs 40 lakh cap, tapering to 10%/Rs 8 lakh) also confirmed.
- **Hyderabad cybersecurity market** (DTL010) — Tracxn data: 86 companies, 18 funded, $26.6M raised, 4 Series A+; named funded firms Equal, Tanla Platforms, Visiontek, Ensurity, PeopleLink.
- **Named AI tools** grounded per category: GitHub Copilot/ChatGPT (developer adoption, 49%/64% globally, 84% using AI tools in 2026 per index.dev); Power BI Copilot (Microsoft); Azure Copilot; PentestGPT/BurpGPT/Simbian (AI pentesting); Semrush/SurferSEO (AI SEO); Canva/Jasper/Buffer AI Assistant/Hootsuite OwlyWriter AI (social/content); Wix AI Website Builder/Durable/Framer AI (AI site builders).
- **Udyam registration confirmed genuinely free** (Rs 0 government fee via udyamregistration.gov.in) — applied consistently across `licenses_required_summary` where relevant.

## What Was Explicitly Declined (Not Fabricated)

- No single authoritative rupee figure exists for `investment_range_summary`/`minimum_investment` in 11 of 12 rows — despite extensive searching, no NASSCOM or incubator costing guide was found; portal/vendor price points are cited as real data points but not conflated with a verified "the cost is X" claim.
- `working_capital_summary`, `estimated_setup_time_summary`, and `seasonal_factors_summary` are 0/12 filled with sourced figures across the entire dataset — a genuine, consistent gap rather than an oversight in specific rows.
- DTL012's `ai_tools_summary` and `automation_opportunities_summary` were left PENDING_VERIFICATION rather than assuming general BPO-industry AI/RPA trends apply locally without confirmation.
- DTL004, DTL005, DTL007, and DTL009's `success_stories_summary` were left PENDING_VERIFICATION rather than stretching found T-Hub aggregate ecosystem statistics (e.g., "$2B raised across 2,500 startups") into a false single-example match.

## Remaining Major Gaps (carried forward / new)

1. No government-verified investment/setup-cost figure exists for any of the 12 categories — the single largest recurring gap, unchanged in kind from RC1 but now partially offset by real vendor/certification price points in 5 rows.
2. `working_capital_summary`, `estimated_setup_time_summary`, `seasonal_factors_summary`, and `sustainability_summary` remain entirely unsourced across all 12 rows — a genuine research frontier for a future pass (would likely require primary incubator/NASSCOM costing guides not accessible under the current WebFetch restriction).
3. Individual named success stories are missing for freelance/small-firm software services (DTL001, DTL002 use hedged ecosystem examples), web dev agency (DTL004), mobile app development (DTL005), and cloud consulting (DTL009).
4. WebFetch to .gov.in/.ac.in/.nic.in remains blocked; all government-linked findings (including the new Telangana rural-subsidy figures and GSEC cybersecurity-hub announcement) are search-snippet sourced, not primary-page-verified, consistent with the dataset-wide `VST-NEEDS_REVIEW` status.
5. No AP-specific (as opposed to Telangana-only WE-HUB) women-in-tech scheme was found this pass either — this asymmetry, flagged in RC1, persists.
