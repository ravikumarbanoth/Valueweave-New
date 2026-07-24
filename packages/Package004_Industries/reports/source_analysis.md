# Package004_Industries_and_Livelihoods v1.0.0 — Source Analysis

## Collection Method

Every fact in this release was collected via the WebSearch tool, across both the RC1 collection pass
(2026-07-22) and the v2 deep-enrichment pass (2026-07-24). Direct WebFetch to primary .gov.in / .ac.in
/ .nic.in pages was blocked throughout both passes (confirmed HTTP 403 policy denial, re-tested live
before each pass began). No page was directly fetched and re-read for any dataset in this release;
all facts are search-snippet-sourced and cited by URL. `china_inspired_adapted_opportunities.csv`
additionally draws on a small number of explicitly-flagged Tier-5 qualitative sources (forums,
YouTube creator content) for color, per the enrichment brief.

## Distinct Sources Cited Per Dataset (post-enrichment)

| Dataset | Distinct Source URLs | Total Rows | Enriched in v2? |
|---|---|---|---|
| msme_entrepreneurship_support_schemes | 37 | 18 | No (unchanged from RC1) |
| food_agro_processing_micro_enterprises | 74 | 13 | Yes |
| construction_skilled_trade_services | 82 | 11 | Yes |
| digital_technology_livelihoods | 12 | 12 | Yes |
| china_inspired_adapted_opportunities | 75 | 9 | Yes (incl. disclosed Tier-5 sources) |

**Sum across datasets: 280** (not globally deduplicated — some government portal URLs are cited by
more than one dataset, e.g. Telangana/AP MSME and IT department pages).

The 3 enriched datasets with the largest jump in cited sources (food_agro, construction, china_inspired)
reflect the v2 pass's requirement to independently source each of ~20 new fields per row, each
potentially citing a distinct URL; `digital_technology_livelihoods` added comparatively fewer new
distinct URLs because several of its new fields (e.g. `ai_tools_summary` for named tools like GitHub
Copilot) drew on facts already covered by sources cited for other fields in the same row.

Full per-source listings for the RC1-era baseline are in `raw_sources/*.source_inventory.md` (see the
v1.0.0 note at the top of each enriched dataset's file); full evidence manifests (including the
WebFetch-block note) are in `evidence/*.evidence_manifest.json`. The CSV files themselves are
canonical for the complete post-enrichment `source_url` list per row.
