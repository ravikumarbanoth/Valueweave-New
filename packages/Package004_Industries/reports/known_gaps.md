# Package004_Industries_and_Livelihoods v1.0.0 — Known Gaps

See `acquisition_backlog.json` for the full structured list and
`reports/business_opportunity_enrichment_summary.md` for the exact per-field fill-rate table from the
v2 enrichment pass. Summary:

## Domain-level (roughly 145 of ~150 briefed sub-categories not researched)
This release covers 5 datasets: MSME & Entrepreneurship Support Schemes, Food & Agro-Processing
Micro-Enterprises, Construction & Skilled Trade Services, Digital & Technology Livelihoods, and
China-Inspired Adapted Opportunities. Textile & Garments, Retail & Local Commerce (general), and
Repair & Maintenance are marked BLOCKED (high fragmentation, no authoritative registry, or extremely
large category with no tractable narrow slice found); everything else (Pharmaceuticals, Electronics,
Construction Materials, Furniture, Plastics, Engineering Workshops, Mushroom/Nursery/Organic
Farming/Beekeeping, Dairy/Poultry/Fisheries, Tourism & Hospitality, Recycling, other Service
Businesses, Education & Training businesses, Health & Wellness businesses, Local Entrepreneurship
food/craft businesses, and all states/UTs beyond Telangana & Andhra Pradesh) is QUEUED.

## Field-level gaps (v1.0.0, post-enrichment)

320 of 1,890 fields (16.93%) across the 4 enriched datasets remain `PENDING_VERIFICATION`. The
weakest fields, in order, are: `minimum_investment` (86.7% pending), `estimated_setup_time_summary`
(84.4%), `seasonal_factors_summary` (77.8%), `working_capital_summary` and `sustainability_summary`
(73.3% each), `ai_tools_summary` (55.6%), `success_stories_summary` (53.3%), and
`district_suitability_summary` (42.2%) — no reliable public source was found for these, so they carry
the bare sentinel rather than a guess. See `reports/business_opportunity_enrichment_summary.md` for
the full field-by-field table.

Estimated Monthly Revenue Range remains dropped from the schema entirely (see `docs/METHODOLOGY.md`).

`msme_entrepreneurship_support_schemes` was intentionally NOT migrated to the 36-column Business
Opportunity schema — it characterizes support infrastructure, not opportunities a person starts.

## Environment constraint
WebFetch to .gov.in/.ac.in/.nic.in domains was blocked across both the RC1 collection pass and the
v2 enrichment pass (confirmed HTTP 403, re-tested live before each pass began). All data is
WebSearch-snippet-sourced (plus limited, explicitly-flagged Tier-5 qualitative sourcing in
`china_inspired_adapted_opportunities.csv`), with confidence capped at 85.
