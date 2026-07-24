# Package004_Industries_and_Livelihoods v1.0.0 — Confidence Analysis

Updated after the v2 deep-enrichment pass (2026-07-24). Confidence scores in this release reflect two
source tiers: rows traced to a specific government DIC/MSME/PMFME/KVIC project-profile document or an
equivalent authoritative source score 70-85; rows where only portal/blog/community estimates were
found (no government backing) are capped at 55-65 even where the qualitative description is
informative. During enrichment, a row's score could rise by at most +8 over its RC1 value, and only
when genuinely new corroborating sources were found — no score was ever lowered, and no row exceeds
85 since no direct page fetch was possible this session (WebFetch to .gov.in/.ac.in was blocked,
re-confirmed live before both the RC1 and v2 passes).

| Dataset | Min | Max | Average | RC1 Average | Change |
|---|---|---|---|---|---|
| msme_entrepreneurship_support_schemes | 70 | 82 | 77.5 | 77.5 | unchanged (not enriched) |
| food_agro_processing_micro_enterprises | 55 | 83 | 66.5 | 60.2 | +6.3 |
| construction_skilled_trade_services | 64 | 85 | 75.1 | 69.7 | +5.4 |
| digital_technology_livelihoods | 70 | 82 | 76.9 | 72.3 | +4.6 |
| china_inspired_adapted_opportunities | 63 | 85 | 75.2 | 70.0 | +5.2 |
| **Package-wide** | **55** | **85** | **74.4** | **70.5** | **+3.9** |

## Interpretation

No row in this package should be treated as `VST-VERIFIED` — every row starts at `VST-NEEDS_REVIEW`.
The food/agro-processing dataset retains the lowest average confidence (66.5) even after enrichment,
because most of its investment-range and setup-cost claims could only be portal-sourced rather than
traced to a government project profile — this is disclosed in `docs/METHODOLOGY.md` and
`reports/business_opportunity_enrichment_summary.md`, not hidden. `china_inspired_adapted_opportunities`
carries a small number of rows with Tier-5 (community/forum/YouTube) sourcing for qualitative color;
those specific rows/fields are capped toward the lower end of the range and explicitly flagged in
`notes`, distinct from the government/news-corroborated majority of that dataset.
