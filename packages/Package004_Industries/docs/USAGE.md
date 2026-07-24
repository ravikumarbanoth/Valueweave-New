# Package004_Industries_and_Livelihoods v1.0.0 — Usage Guide (Business Opportunity Knowledge Base)

## What's in this package

Five CSV datasets under `datasets/`, each independently loadable (no inter-dataset foreign keys). Four
carry the full 36-column Business Opportunity schema; one (the scheme/support-body reference dataset)
retains its original 15-column schema:

| File | Rows | Columns | Covers |
|---|---|---|---|
| `msme_entrepreneurship_support_schemes.csv` | 18 | 15 | National + Telangana + Andhra Pradesh MSME/entrepreneurship schemes, corporations, and support bodies |
| `food_agro_processing_micro_enterprises.csv` | 13 | 36 | Small-scale food/agro-processing business opportunities (spice processing, pickles, oils, millets, seeds) |
| `construction_skilled_trade_services.csv` | 11 | 36 | Skilled-trade business opportunities (plumbing, electrical, welding, carpentry, etc.) |
| `digital_technology_livelihoods.csv` | 12 | 36 | IT/software, web/app development, digital marketing business opportunities |
| `china_inspired_adapted_opportunities.csv` | 9 | 36 | Real Indian/Telugu-state adaptations of the China-inspired business models named in the brief |

## Before treating any row as fact-checked

Every row's `verification_status` is `VST-NEEDS_REVIEW`. Nothing in this release has been promoted to
`VST-VERIFIED`. Confidence scores range 55-85 (lower than Package001-003's ceilings — see
`docs/METHODOLOGY.md` for why this package's typical confidence band is more conservative).

## The 36-column Business Opportunity schema (4 of 5 datasets)

Each row answers the practical questions a student, job seeker, self-employed professional, woman
entrepreneur, MSME, rural entrepreneur, investor, or local business would ask before pursuing an
opportunity. Every `*_summary` column is a short sourced free-text summary — parse as free text, not
as a structured sub-schema:

| Field | What it answers |
|---|---|
| `ideal_target_audience` | Who realistically starts this (students/women/rural youth/professionals) |
| `minimum_investment` | A specific rupee figure, or `PENDING_VERIFICATION` |
| `investment_range_summary` | Broader cost range/description |
| `working_capital_summary` | Ongoing operating capital needs |
| `machinery_equipment_summary` | What equipment is needed |
| `raw_materials_summary` | What inputs, sourced how |
| `supplier_ecosystem_summary` | Where to source from |
| `customer_segments_summary` | Who buys |
| `training_providers_summary` | Where to learn the skill |
| `licenses_required_summary` | What registrations/licenses apply |
| `government_schemes_summary` | Which schemes support this opportunity |
| `marketing_channels_summary` | How to reach customers |
| `online_selling_options_summary` | Which platforms (WhatsApp Business, Meesho, Flipkart, ONDC, etc.) |
| `estimated_setup_time_summary` | How long to get running |
| `typical_risks_summary` | What commonly goes wrong |
| `seasonal_factors_summary` | Seasonality considerations |
| `ai_tools_summary` | Real, currently-available AI tools relevant to this opportunity |
| `automation_opportunities_summary` | What can be automated |
| `sustainability_summary` | Environmental/sustainability considerations |
| `future_demand_summary` | Outlook |
| `related_businesses_summary` | Adjacent opportunities |
| `district_suitability_summary` | Telangana/AP districts known for this activity (free text, not a structured `district_id`) |
| `rural_urban_suitability` | Rural / Urban / Both (enum) |
| `success_stories_summary` | Named real examples, where independently found |

`china_inspired_adapted_opportunities.csv` additionally carries `key_platforms_or_channels` and
`skills_needed_summary` in place of `skill_level`, and uses `original_china_concept` /
`adapted_indian_concept` instead of a single `name` column.

## `PENDING_VERIFICATION` is common in this release — that's disclosed, not a defect

320 of 1,890 fields (16.93%) across the 4 enriched datasets are the bare `PENDING_VERIFICATION`
sentinel — most concentrated in `minimum_investment`, `estimated_setup_time_summary`,
`seasonal_factors_summary`, `working_capital_summary`, `sustainability_summary`, and
`ai_tools_summary`. See `reports/business_opportunity_enrichment_summary.md` for the exact per-field
fill-rate table. **Do not treat `PENDING_VERIFICATION` as an empty string or null** — it is an
explicit "known unknown," distinct from missing data, and any explanatory context researchers found is
in that row's `notes` column, prefixed `[field_name]:`.

## `minimum_investment` vs. `investment_range_summary`

- `minimum_investment` is a single rupee figure, populated **only** when traced to a specific
  government DIC/MSME/PMFME/KVIC project-profile document — 86.7% of rows across the enriched
  datasets are `PENDING_VERIFICATION` here.
- `investment_range_summary` is a broader descriptive summary that may include qualitative cost
  drivers even when no hard number exists — more often populated (75.6% fill rate) but still not a
  structured numeric range you can parse uniformly. Check `confidence_score` before surfacing either
  field as more than a general orientation.

## Estimated Monthly Revenue Range is NOT in this package

No reliable source was found for any row across either the RC1 or v2 pass, so the field was dropped
from the schema entirely rather than shipped as an empty/pending column — see `docs/METHODOLOGY.md`.

## Where to look for provenance

- `metadata/*.metadata.json` — per-dataset stats, confidence calibration, collection method (both
  RC1 and v2 passes documented).
- `evidence/*.evidence_manifest.json` — full cited-source list + the WebFetch-block explanation.
- `raw_sources/*.source_inventory.md` — human-readable source list per dataset.
- `reports/*.collection_report.md` — RC1 research methodology, conflicts found/resolved, exclusions.
- `reports/*.enrichment_v2_report.md` — v2 deep-enrichment methodology and findings, per dataset.
- `reports/business_opportunity_enrichment_summary.md` — the package-wide enrichment summary and
  per-field fill-rate table.

## What's NOT in this package yet

See `acquisition_backlog.json` and `registry/dataset_registry.csv` for the ~145 remaining
sub-categories from the brief (Textile & Garments, most of Manufacturing beyond food-processing,
most of Agriculture & Allied beyond processing, Tourism & Hospitality general, Repair & Maintenance,
Retail & Local Commerce general, Recycling, other Service Businesses, Education & Training
businesses, Health & Wellness businesses, Local Entrepreneurship food/craft businesses) and all
non-TG/AP states — each marked `BLOCKED` or `QUEUED` with a specific reason and unblock path.
