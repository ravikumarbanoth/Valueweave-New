# Package004_Industries_and_Livelihoods v1.0.0-RC1 — Known Gaps

See `acquisition_backlog.json` for the full structured list. Summary:

## Domain-level (roughly 145 of ~150 briefed sub-categories not researched)
This release covers 5 datasets: MSME & Entrepreneurship Support Schemes, Food & Agro-Processing Micro-Enterprises, Construction & Skilled Trade Services, Digital & Technology Livelihoods, and China-Inspired Adapted Opportunities. Textile & Garments and Retail & Local Commerce (general) and Repair & Maintenance are marked BLOCKED (high fragmentation, no authoritative registry, or extremely large category with no tractable narrow slice found this session); everything else (Pharmaceuticals, Electronics, Construction Materials, Furniture, Plastics, Engineering Workshops, Mushroom/Nursery/Organic Farming/Beekeeping, Dairy/Poultry/Fisheries, Tourism & Hospitality, Recycling, other Service Businesses, Education & Training businesses, Health & Wellness businesses, Local Entrepreneurship food/craft businesses, and all states/UTs beyond Telangana & Andhra Pradesh) is QUEUED.

## Field-level gaps
- `typical_investment_range_summary` is PENDING_VERIFICATION for all 12 digital/technology rows and 8 of 13 food/agro-processing rows — no government/authoritative costing source with a specific figure was found.
- Estimated Monthly Revenue Range was dropped from the schema entirely (see docs/METHODOLOGY.md).
- Machinery, Raw Materials, Suppliers, Business Risks, AI Opportunities, Sustainability, Market Trends, Future Potential, Related Industries, and District Suitability (the remaining ~10 fields named in the brief) are not populated in this release — see docs/METHODOLOGY.md 'Field-Depth Scope Reduction'.

## Environment constraint
WebFetch to .gov.in/.ac.in/.nic.in domains was blocked all session (confirmed HTTP 403, re-tested live before collection began). All data is WebSearch-snippet-sourced with confidence capped at 85.
