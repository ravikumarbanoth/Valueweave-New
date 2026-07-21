# Package004_Industries_and_Livelihoods v1.0.0-RC1 — Usage Guide

## What's in this package

Five CSV datasets under `datasets/`, each independently loadable (no inter-dataset foreign keys):

| File | Rows | Covers |
|---|---|---|
| `msme_entrepreneurship_support_schemes.csv` | 18 | National + Telangana + Andhra Pradesh MSME/entrepreneurship schemes, corporations, and support bodies |
| `food_agro_processing_micro_enterprises.csv` | 13 | Small-scale food/agro-processing livelihood opportunities (spice processing, pickles, oils, millets, seeds) |
| `construction_skilled_trade_services.csv` | 11 | Skilled-trade livelihood opportunities (plumbing, electrical, welding, carpentry, etc.) |
| `digital_technology_livelihoods.csv` | 12 | IT/software, web/app development, digital marketing livelihood opportunities |
| `china_inspired_adapted_opportunities.csv` | 9 | Real Indian/Telugu-state adaptations of the China-inspired business models named in the brief |

## Before treating any row as fact-checked

Every row's `verification_status` is `VST-NEEDS_REVIEW`. Nothing in this release has been promoted to
`VST-VERIFIED`. Confidence scores range 48-82 (lower than Package001-003's ceilings — see
`docs/METHODOLOGY.md` for why this package's typical confidence band is more conservative).

## The most important field to handle carefully: `typical_investment_range_summary`

This field is **not** a reliable numeric range you can parse and trust uniformly across rows:
- In `food_agro_processing_micro_enterprises.csv` and `digital_technology_livelihoods.csv`, it is the
  literal sentinel `PENDING_VERIFICATION` wherever no government-sourced figure was found (8 of 13
  rows, and all 12 rows, respectively) — the qualitative context researchers found is in `notes`
  instead, prefixed `[typical_investment_range_summary]:`.
- In `construction_skilled_trade_services.csv` and `china_inspired_adapted_opportunities.csv`, it is
  a **descriptive qualitative summary** (e.g. "core cost is a smartphone and product photography")
  rather than a hard number, since that's genuinely more informative than a bare sentinel when no
  number exists but real qualitative context does.

Do not treat this field as a structured numeric range in downstream code — parse it as free text, and
check `confidence_score` before surfacing it as anything more than a general orientation.

## Estimated Monthly Revenue Range is NOT in this package

The brief asked for it "if publicly available." No reliable source was found for any row, so the
field was dropped from the schema entirely rather than shipped as an empty/pending column — see
`docs/METHODOLOGY.md`.

## Where to look for provenance

- `metadata/*.metadata.json` — per-dataset stats, confidence calibration, collection method.
- `evidence/*.evidence_manifest.json` — full cited-source list + the WebFetch-block explanation.
- `raw_sources/*.source_inventory.md` — human-readable source list per dataset.
- `reports/*.collection_report.md` — full research methodology, conflicts found/resolved, exclusions.

## What's NOT in this package yet

See `acquisition_backlog.json` and `registry/dataset_registry.csv` for the ~145 remaining
sub-categories from the brief (Textile & Garments, most of Manufacturing beyond food-processing,
most of Agriculture & Allied beyond processing, Tourism & Hospitality general, Repair & Maintenance,
Retail & Local Commerce general, Recycling, other Service Businesses, Education & Training
businesses, Health & Wellness businesses, Local Entrepreneurship food/craft businesses) and all
non-TG/AP states — each marked `BLOCKED` or `QUEUED` with a specific reason and unblock path.
