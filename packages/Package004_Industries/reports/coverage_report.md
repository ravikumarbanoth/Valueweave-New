# Package004_Industries_and_Livelihoods v1.0.0 — Coverage Report

## Datasets Released

| Dataset | Records | Columns | Schema Tier |
|---|---|---|---|
| msme_entrepreneurship_support_schemes | 18 | 15 | Support-layer reference |
| food_agro_processing_micro_enterprises | 13 | 36 | Business Opportunity |
| construction_skilled_trade_services | 11 | 36 | Business Opportunity |
| digital_technology_livelihoods | 12 | 36 | Business Opportunity |
| china_inspired_adapted_opportunities | 9 | 36 | Business Opportunity |

**Total records in v1.0.0: 63** (unchanged from RC1 — this release deepened existing rows, it did not
add new ones)

## Domains Released vs. Full Task Scope

The package brief named roughly 150 sub-categories across 13 category groups (Manufacturing,
Agriculture & Allied, Construction & Skilled Trades, Technology, Repair & Maintenance, Tourism &
Hospitality, Retail & Local Commerce, Recycling & Circular Economy, Service Businesses, Education &
Training, Health & Wellness, Local Entrepreneurship, and China-Inspired Opportunities). This release
covers 5 datasets spanning a curated slice of that scope: MSME & Entrepreneurship Support Schemes (the
regulatory/support layer), Food & Agro-Processing Micro-Enterprises and Construction & Skilled Trade
Services (two well-documented livelihood-opportunity groups), Digital & Technology Livelihoods, and
the explicitly-requested China-Inspired Adapted Opportunities. All other domains are tracked as
BLOCKED or QUEUED in `acquisition_backlog.json` and `registry/dataset_registry.csv`, not shipped as
unverified placeholders.

## Field Scope — Evolved in v1.0.0

RC1 shipped a smaller verifiable core per opportunity entity (identity, category, description, target
customers, investment range where sourced, skill level, training, licenses, government schemes, and
rural/urban suitability — 18 columns). **v1.0.0's deep-enrichment pass expanded 4 of the 5 datasets to
36 columns**, adding the practical entrepreneurship fields requested to turn this from an "Industry
Classification Package" into a "Business Opportunity Knowledge Base": ideal target audience, minimum
investment, working capital, machinery/equipment, raw materials, supplier ecosystem, customer
segments, training providers, marketing channels, online selling options, estimated setup time,
typical risks, seasonal factors, AI tools, automation opportunities, sustainability, future demand,
related businesses, district suitability, and success stories.

Estimated Monthly Revenue Range remains dropped entirely — no reliable public source exists for
typical small-business monthly revenue in these categories; attempting it would mean either 100%
`PENDING_VERIFICATION` or fabrication risk. See `docs/METHODOLOGY.md`.

See `reports/business_opportunity_enrichment_summary.md` for the exact per-field fill-rate table.
