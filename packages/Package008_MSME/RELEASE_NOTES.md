# Release Notes — Package008_MSME v1.0.0

**Released 2026-07-25 · Stable · validation PASS (0 violations across 13 checks)**

The final package in the ValueWeave knowledge base programme, and the one that binds the rest
together.

## What this is

The Business Intelligence Layer: 40 MSME business opportunities profiled across
classification, difficulty, risk, technology and market, surrounded by their machinery and raw
material requirements, licence obligations, finance sources, market and export routes, AI tool
adoption profile, startup ecosystem support and per-business investment intelligence.

18 datasets · 477 records · 7770 cells.

## The questions it answers

| Question | Where |
|---|---|
| Which MSME business can I start? | `msme_businesses` filtered by category, difficulty, udyam class |
| Which machinery is needed? | `machinery_mapping` |
| Which raw materials, and how volatile? | `raw_material_mapping` |
| Which licences apply? | `license_compliance` |
| Which schemes support it? | `scheme_mapping` -> Package007 |
| Which skills are required? | `skill_mapping` -> Package006 |
| Which district suits it? | `district_business_mapping` -> Package001 |
| Which banks finance it? | `financial_support` |
| Which markets can I sell to? | `market_channels` |
| Which export opportunities exist? | `export_opportunities` |
| Which AI tools improve productivity? | `ai_business_tools` |
| Which businesses have the highest potential? | `investment_intelligence` |

## Normalization: the defining constraint

The brief required that Package008 not duplicate schemes, skills, industries, geography, education
or agriculture. **This is enforced in code, not prose.** Validation check V13 fails the build if
any column name restates an attribute owned by an upstream entity — a scheme's benefit, a skill's
NSQF level, a crop's season, a district's population.

Ten foreign key sets into six packages: **213 resolved, 99 sentinel, 0 unresolved.**

| Upstream | Resolved | Sentinel |
|---|---|---|
| Package007 `government_schemes.scheme_id` | 57 | 0 |
| Package006 `skills.skill_id` | 46 | 7 |
| Package006 `training_providers.provider_id` | 9 | 4 |
| Package005 `crops.crop_id` (raw material) | 12 | 21 |
| Package005 `crops.crop_id` (agri business) | 10 | 4 |
| Package005 `farm_machinery.machinery_id` | 10 | 54 |
| Package005 `agri_processing_opportunities.opportunity_id` | 14 | 0 |
| Package004 opportunity `id` | 19 | 0 |
| Package002 `universities.id` | 4 | 9 |
| Package001 `district.dist_id` | 32 | 0 |

**The trade-off:** Package008 is not independently useful. Ask it what a scheme pays and it cannot
tell you — only which scheme to look up. That is correct (one authoritative copy beats six that
drift) but it means consumers must load the upstream packages. `docs/IMPORT_GUIDE.md` section 5
shows how to join without re-materialising the duplication.

## Read this before using the data

**No rupee figure exists anywhere in this package.** `investment_range` is the sentinel on all
40 rows. A per-business investment requirement depends on capacity, location, automation and
whether premises are owned — the MSMED Act thresholds are official, but a project cost is not.
`udyam_classification` carries the statutory Micro/Small/Medium signal instead.

**`investment_intelligence` contains no computed return.** No percentage, no payback period, no
IRR. Every field is ordinal, because computing any of them would need the figures above. Use it to
compare businesses against each other, never to underwrite a decision.

**Nothing has had human review.** All 477 rows are `VST-NEEDS_REVIEW`.

## Scope boundaries

- **18 of 24 categories have businesses.** Semiconductors, robotics and
  creative industries have one each; several categories have none.
- **`district_business_mapping` is 32 rows, not 2,440.** Suitability is asserted only where a
  documented district characteristic drives it.
- **`industry_mapping` covers 19 of 40 businesses.** The rest have no Package004 counterpart.
- **No Package003_Healthcare foreign key.** Healthcare is an MSME category here, but Package003
  holds institutions and insurance schemes, not enterprise opportunities.
- **No state MSME incentive policies.** Package004 holds the Telangana and Andhra Pradesh records.

## Defects caught before release

Five classes, all by validation. Two worth naming because they generalise:

**Guessing an id format is not reading it.** Ten district refs (`AP-GNT`, `TG-SGR`, …) were
plausible and wrong; the real ones are `AP-GUN`, `TG-SNG`. Every one would have broken a join.

**Package006 has seven skill gaps this package now documents.** Foundry casting, handloom weaving,
corrugation operation, plastic reprocessing, chemical formulation, data entry, training delivery —
no Package006 record exists. Each is an explicit sentinel row with the requirement stated, which is
a concrete request back to Package006 rather than a silent approximation.

Full detail in `validation_report.md`.

## Files

```
Package008_MSME/
├── datasets/              18 released CSVs
├── metadata/              18 per-dataset metadata JSON files
├── reports/               18 per-dataset collection reports
├── schemas/               schema_catalog.json
├── registry/              dataset_registry.csv
├── docs/                  METHODOLOGY, USAGE, DATA_DICTIONARY, IMPORT_GUIDE
├── package_manifest.json
├── validation_report.md   validation_summary.json
├── quality_report.md
├── VERSION_HISTORY.md     RELEASE_NOTES.md  CHANGELOG.md  VERSION
├── codex_handoff.md
├── validate.py            13-check validation engine (V13 = normalization)
└── gen_core.py  gen_mappings.py  build_artifacts.py  build_docs.py
```
