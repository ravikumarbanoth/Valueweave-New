# Package004_Industries_and_Livelihoods v1.0.0-RC1 — Coverage Report

## Datasets Released

| Dataset | Records |
|---|---|
| msme_entrepreneurship_support_schemes | 18 |
| food_agro_processing_micro_enterprises | 13 |
| construction_skilled_trade_services | 11 |
| digital_technology_livelihoods | 12 |
| china_inspired_adapted_opportunities | 9 |

**Total records released in v1.0.0-RC1: 63**

## Domains Released vs. Full Task Scope

The package brief named roughly 150 sub-categories across 13 category groups (Manufacturing, Agriculture & Allied, Construction & Skilled Trades, Technology, Repair & Maintenance, Tourism & Hospitality, Retail & Local Commerce, Recycling & Circular Economy, Service Businesses, Education & Training, Health & Wellness, Local Entrepreneurship, and China-Inspired Opportunities), each with ~25 fields per entity. This release covers 5 datasets spanning a curated slice of that scope: MSME & Entrepreneurship Support Schemes (the regulatory/support layer), Food & Agro-Processing Micro-Enterprises and Construction & Skilled Trade Services (two well-documented livelihood-opportunity groups), Digital & Technology Livelihoods, and the explicitly-requested China-Inspired Adapted Opportunities. All other domains are tracked as BLOCKED or QUEUED in `acquisition_backlog.json` and `registry/dataset_registry.csv`, not shipped as unverified placeholders.

## Field Scope

The brief specified ~25 fields per entity including Estimated Monthly Revenue Range, Machinery, Raw Materials, Suppliers, Business Risks, Opportunities, AI Opportunities, Sustainability, Market Trends, Future Potential, Related Industries, and District Suitability. This release ships a smaller verifiable core per entity (identity, category, description, target customers, investment range where sourced, skill level, training, licenses, government schemes, and rural/urban suitability). Revenue-range was dropped entirely rather than descoped-with-gaps: there is no reliable public source for typical small-business monthly revenue, so attempting it would mean either 100% PENDING_VERIFICATION or fabrication risk. See docs/METHODOLOGY.md 'Field-Depth Scope Reduction' for the full rationale.
