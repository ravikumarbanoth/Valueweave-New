# Package004_Industries_and_Livelihoods — Business Opportunity Enrichment Summary (v1.0.0)

This report documents the v2 deep-enrichment pass (2026-07-24) that evolved this package from an
**Industry Classification Package** (RC1, 18 columns per opportunity) into a **Business Opportunity
Knowledge Base** (v1.0.0, 36 columns per opportunity), per explicit instruction. It supplements —
does not replace — each dataset's own `reports/<dataset>.enrichment_v2_report.md`.

## What changed

| Dataset | RC1 columns | v1.0.0 columns | RC1 confidence avg | v1.0.0 confidence avg |
|---|---|---|---|---|
| food_agro_processing_micro_enterprises | 18 | 36 | 60.2 | 66.5 |
| construction_skilled_trade_services | 18 | 36 | 69.7 | 75.1 |
| digital_technology_livelihoods | 18 | 36 | 72.3 | 76.9 |
| china_inspired_adapted_opportunities | 15 | 36 | 70.0 | 75.2 |
| msme_entrepreneurship_support_schemes | 15 | 15 (unchanged) | 77.5 | 77.5 |

`msme_entrepreneurship_support_schemes` was deliberately left at its original schema — see "Why one
dataset wasn't enriched" below.

Row counts, primary keys, and original identity fields (`id`, `name`/`original_china_concept`+
`adapted_indian_concept`, `category`, `sub_category`, `description`) were preserved unchanged across
the enrichment pass in all 4 opportunity datasets — no rows were added, removed, or re-identified.

## The 24 new fields (per opportunity dataset)

Every enriched dataset gained: `ideal_target_audience`, `minimum_investment`,
`working_capital_summary`, `machinery_equipment_summary`, `raw_materials_summary`,
`supplier_ecosystem_summary`, `customer_segments_summary`, `training_providers_summary` (renamed
from `training_availability_summary`), `marketing_channels_summary`, `online_selling_options_summary`,
`estimated_setup_time_summary`, `typical_risks_summary`, `seasonal_factors_summary`,
`ai_tools_summary`, `automation_opportunities_summary`, `sustainability_summary`,
`future_demand_summary`, `related_businesses_summary`, `district_suitability_summary`, and
`success_stories_summary`. `china_inspired_adapted_opportunities` additionally carries
`skills_needed_summary` in place of `skill_level`, reflecting that "China-inspired adaptation" is
less a fixed skill tier and more a platform/channel competency.

## Per-field fill rate (across all 45 rows in the 4 enriched datasets)

| Field | Sourced | Pending | Fill rate |
|---|---|---|---|
| ideal_target_audience | 45 | 0 | 100% |
| raw_materials_summary | 45 | 0 | 100% |
| customer_segments_summary | 45 | 0 | 100% |
| licenses_required_summary | 45 | 0 | 100% |
| government_schemes_summary | 45 | 0 | 100% |
| related_businesses_summary | 45 | 0 | 100% |
| skills_needed_summary (china_inspired only, n=9) | 9 | 0 | 100% |
| machinery_equipment_summary | 42 | 3 | 93.3% |
| supplier_ecosystem_summary | 41 | 4 | 91.1% |
| training_providers_summary | 41 | 4 | 91.1% |
| typical_risks_summary | 38 | 7 | 84.4% |
| marketing_channels_summary | 37 | 8 | 82.2% |
| future_demand_summary | 35 | 10 | 77.8% |
| investment_range_summary | 34 | 11 | 75.6% |
| online_selling_options_summary | 33 | 12 | 73.3% |
| automation_opportunities_summary | 30 | 15 | 66.7% |
| district_suitability_summary | 26 | 19 | 57.8% |
| success_stories_summary | 21 | 24 | 46.7% |
| ai_tools_summary | 20 | 25 | 44.4% |
| working_capital_summary | 12 | 33 | 26.7% |
| sustainability_summary | 12 | 33 | 26.7% |
| seasonal_factors_summary | 10 | 35 | 22.2% |
| estimated_setup_time_summary | 7 | 38 | 15.6% |
| minimum_investment | 6 | 39 | 13.3% |

**Interpretation**: the fields that answer "what do I need and who buys it" (raw materials, customers,
licenses, schemes, related businesses, target audience, machinery, suppliers, training) filled
strongly — 91-100% sourced. The fields that require either a single hard number
(`minimum_investment`, `estimated_setup_time_summary`) or genuinely thin public documentation
(`seasonal_factors_summary`, `working_capital_summary`, `sustainability_summary`) filled weakly —
13-27% sourced — because no reliable public source exists for most rows, not because research effort
was skipped. Every unsourced cell carries the bare `PENDING_VERIFICATION` sentinel, never a guess.

## Confidence score discipline

Every confidence-score increase during enrichment was capped at +8 over the RC1 value and required a
genuinely new, stronger corroborating source — never raised on the basis of the new fields alone.
No score was ever lowered. Package-wide range moved from 48-82 (RC1) to 55-85 (v1.0.0); package-wide
average moved from 70.5 to 74.4.

## Tier-5 (qualitative/community) sourcing — used once, disclosed explicitly

Per the enrichment brief, Tier-5 sources (founder interviews, business communities, forums, Reddit,
YouTube creators) were permitted for qualitative color, but only in
`china_inspired_adapted_opportunities.csv` — the dataset the brief itself frames around adaptation
patterns rather than institutional facts. 4 of its 9 rows/fields explicitly flag Tier-5 provenance in
`notes` (e.g. a Dukaan seller profiled via Quartz, a YouTube creator profiled via a single industry
blog) and those rows' confidence scores are capped lower than government/news-corroborated rows in
the same dataset. No other dataset in this package draws on Tier-5 sources for any field.

## Why one dataset wasn't enriched: msme_entrepreneurship_support_schemes

This dataset catalogues schemes and support bodies (PMEGP, WE-HUB, T-IDEA, etc.) — the
support-layer infrastructure that opportunities draw on, not opportunities themselves. The user's
Business Opportunity brief (using "Mushroom Cultivation" as the worked example) describes fields that
only make sense for something a person *starts* (machinery, raw materials, minimum investment,
target customers). Forcing this dataset into the same 36-column shape would mean either leaving 20+
columns entirely empty for every row, or fabricating opportunity-shaped facts about a scheme, neither
of which serves the stated goal. It remains at its original 15-column schema and is cross-referenced
conceptually (not via enforced FK) from every enriched dataset's `government_schemes_summary` field.

## What this pass did NOT do

- Did not re-verify any RC1 fact against a primary source (WebFetch to `.gov.in`/`.ac.in`/`.nic.in`
  remained blocked throughout this pass — same constraint as RC1).
- Did not add, remove, or re-order rows in any dataset.
- Did not promote any row to `VST-VERIFIED` — every row remains `VST-NEEDS_REVIEW`.
- Did not populate any field with a plausible-sounding but unsourced figure — the 320
  `PENDING_VERIFICATION` cells package-wide are the honest record of what public information doesn't
  exist yet for these opportunities, not a to-do list to quietly guess through.
