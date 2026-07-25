# Package008_MSME v1.0.0

**ValueWeave.in MSME and Entrepreneurship Intelligence Knowledge Base**

| | |
|---|---|
| **Version** | 1.0.0 (Stable) |
| **Release date** | 2026-07-25 |
| **Datasets** | 18 |
| **Records** | 477 |
| **Businesses catalogued** | 40 |
| **Validation** | PASS — 0 violations across 13 checks |
| **Cross-package FK sets** | 10, into 6 released packages, 0 unresolved |
| **Normalization (V13)** | PASS — enforced in code, not prose |
| **Confidence range** | 57–78 (policy ceiling 85) |
| **Sentinel rate** | 3.72% of cells (`PENDING_VERIFICATION`) |
| **Verification status** | `VST-NEEDS_REVIEW` — no human data-steward sign-off |

## Purpose

This is not an MSME directory. It is the **Business Intelligence Layer** of the knowledge base:
40 MSME business opportunities, each surrounded by what it actually takes to run one — machinery,
raw materials, licences, skills, finance, market channels, export routes, AI tooling and
investment characteristics — bound to six released packages **by reference rather than by
duplication**.

```
Entrepreneur → Business Idea → Skills → Education → Industry → Agriculture
   → Machinery → Finance → Government Scheme → Production → Market
   → Export → AI → Growth → Investment
```

## The normalization rule is the design

The brief required that Package008 **not duplicate** government schemes, skills, industries,
geography, education or agriculture. That is enforced by validation check **V13**, which fails the
build if any column name restates an attribute owned by an upstream entity.

| Upstream domain | Package008 holds | Package008 does NOT hold |
|---|---|---|
| Government schemes | 57 relationship rows: relevance, stage, support nature | Any benefit, eligibility, portal, ministry or amount |
| Skills | 53 relationship rows: role, criticality, who needs it | Any NSQF level, duration or training route |
| Crops | 22 crop references across two datasets | Any season, yield, soil type or water requirement |
| Districts | 32 suitability rows, each with a named documented basis | Any population, area, literacy or coordinate |
| Industries | 19 opportunity references with a typed relationship | Any Package004 investment or machinery detail |
| Institutions | 13 talent-flow rows | Any established year, affiliation or type |

**The cost of this discipline: Package008 is not independently useful.** Ask it what a scheme pays
and it cannot tell you — it can only tell you which scheme to look up. That is the right trade,
because one authoritative copy stays current where six copies drift. But it means any consumer
application must load the upstream packages too. See `docs/IMPORT_GUIDE.md` §5 for how to join
without re-materialising the duplication.

## The questions it answers

| Question | Query surface |
|---|---|
| Which MSME business can I start? | `msme_businesses`, filtered on any closed-domain column |
| How much investment is required? | `udyam_classification` (statutory band) — **no rupee figure exists** |
| Which machinery is needed? | `machinery_mapping` |
| Which raw materials, and how volatile? | `raw_material_mapping` |
| Which licences are required? | `license_compliance` |
| Which government schemes support it? | `scheme_mapping` → Package007 |
| Which skills are required? | `skill_mapping` → Package006 |
| Which district is suitable? | `district_business_mapping` → Package001 |
| Which banks finance it? | `financial_support` |
| Which markets can I sell to? | `market_channels` |
| Which export opportunities exist? | `export_opportunities` |
| Which AI tools improve productivity? | `ai_business_tools` |
| Which businesses have the highest potential? | `investment_intelligence` |

See `docs/USAGE.md` for the SQL.

## Datasets

Load in this order — it is the dependency order and `import_order` in `package_manifest.json`.

### Layer 1 — Reference taxonomies (no upstream dependency)

| Dataset | Rows | PK |
|---|---|---|
| `msme_categories.csv` | 24 | `category_id` |
| `business_models.csv` | 15 | `business_model_id` |
| `license_compliance.csv` | 14 | `license_id` |
| `financial_support.csv` | 12 | `finance_id` |
| `market_channels.csv` | 11 | `channel_id` |
| `ai_business_tools.csv` | 12 | `tool_id` |
| `startup_ecosystem.csv` | 12 | `ecosystem_id` |

### Layer 2 — Core entity

| Dataset | Rows | PK |
|---|---|---|
| `msme_businesses.csv` | 40 | `business_id` |

### Layers 3–6 — Requirements and cross-package mappings

| Dataset | Rows | Links to |
|---|---|---|
| `machinery_mapping.csv` | 64 | Package005 `farm_machinery` (where the machine exists there) |
| `raw_material_mapping.csv` | 33 | Package005 `crops` (where the input is a crop) |
| `scheme_mapping.csv` | 57 | Package007 `government_schemes` |
| `skill_mapping.csv` | 53 | Package006 `skills` |
| `industry_mapping.csv` | 19 | Package004 opportunity `id` |
| `agriculture_business_mapping.csv` | 14 | Package005 `crops` + `agri_processing_opportunities` |
| `education_support_mapping.csv` | 13 | Package002 `universities` + Package006 `training_providers` |
| `district_business_mapping.csv` | 32 | Package001 `district` |

### Layers 8 & 11 — Market and investment

| Dataset | Rows | PK |
|---|---|---|
| `export_opportunities.csv` | 12 | `opportunity_id` |
| `investment_intelligence.csv` | 40 | `intelligence_id` |

## Cross-package integration

Ten foreign key sets into six released packages — the widest surface in the knowledge base. Every
id was resolved against the upstream CSV **at generation time**; the generator aborts rather than
write an unresolvable reference, and V9 re-checks on every validation run.

| Upstream | Foreign key | Resolved | Sentinel |
|---|---|---|---|
| Package007 | `scheme_mapping.package007_scheme_id` | 57 | 0 |
| Package006 | `skill_mapping.package006_skill_id` | 46 | 7 |
| Package006 | `education_support_mapping.package006_provider_id` | 9 | 4 |
| Package005 | `raw_material_mapping.package005_crop_id` | 12 | 21 |
| Package005 | `agriculture_business_mapping.package005_crop_id` | 10 | 4 |
| Package005 | `machinery_mapping.package005_machinery_id` | 10 | 54 |
| Package005 | `agriculture_business_mapping.package005_processing_opportunity_id` | 14 | 0 |
| Package004 | `industry_mapping.package004_opportunity_id` | 19 | 0 |
| Package002 | `education_support_mapping.package002_institution_id` | 4 | 9 |
| Package001 | `district_business_mapping.package001_dist_id` | 32 | 0 |

**Zero unresolved.** Sentinels here mean the upstream package holds no counterpart record — a
statement about upstream coverage, not about the relationship being unknown. Each case is
explained in `validation_report.md`.

**Package003_Healthcare** has no foreign key: healthcare appears as MSME category `mc-008`, but
Package003 holds institutions and insurance schemes, not enterprise opportunities, so there is no
counterpart record type to reference.

## What this package does not assert

- **No rupee figure, anywhere.** `investment_range` is the sentinel on all 40 businesses. A
  per-business project cost depends on capacity, location, degree of automation and whether
  premises are owned — the MSMED Act thresholds are official, a project cost is not.
  `udyam_classification` carries the statutory Micro/Small/Medium signal instead.
- **No computed return.** `investment_intelligence` has no percentage, no payback period, no IRR.
  Every field is ordinal, because computing any of them would need the figures above. Use it to
  compare businesses against each other, never to underwrite a decision.
- **No machinery cost, payment cycle or lead time to revenue.** All sentinelled.
- **No exhaustive district guidance.** 32 rows, not 2,440 — suitability is asserted only where a
  documented district characteristic drives it, and every row names that characteristic.
- **No state MSME incentive policies.** Package004 holds the Telangana and Andhra Pradesh records.

## Provenance model

Six mandatory provenance columns on every row of every dataset:

| Column | Meaning |
|---|---|
| `data_source` | Ministry, authority or association the row is attributed to |
| `source_url` | Public URL for that body |
| `collection_date` | `2026-07-25`, uniform package-wide |
| `confidence_score` | Integer 0–100, capped at 85 |
| `verification_status` | `VST-NEEDS_REVIEW` |
| `notes` | Caveats and sourcing remarks |

### Confidence bands

| Band | Tier |
|---|---|
| 70–85 | Tier 1 — Ministry of MSME, Udyam portal, SIDBI, NABARD, NSIC, KVIC, DPIIT, GeM, MSME-DIs |
| 62–69 | Tier 2 — government reports and programme literature |
| 56–61 | Tier 3 — industry associations (CII, FICCI, ASSOCHAM, NASSCOM) |
| 45–55 | Tier 4 — official sector reports |

The 85 ceiling records that WebFetch to `.gov.in` / `.nic.in` / `.ac.in` is blocked in this
environment, so no row rests on a primary-source page read — the same constraint that applied to
Package004 through Package007. Observed range is 57–78. The floor of 57 appears on rows recording a
genuine upstream absence, where the low score is the signal.

## Validation

```bash
cd packages/Package008_MSME
python3 validate.py
```

Thirteen checks:

| Check | Enforces |
|---|---|
| V1 | Structural — row length matches header |
| V2 | Primary key unique and non-empty |
| V3 | All six provenance columns present |
| V4 | `confidence_score` integer, 0–100, ≤ 85 |
| V5 | Bare-sentinel discipline |
| V6 | `verification_status` enum |
| V7 | Uniform `collection_date` |
| V8 | In-package FKs resolve; denormalised names agree |
| V9 | Cross-package FKs resolve upstream; upstream names agree |
| V10 | No silently blank cells |
| V11 | Every business has ≥1 scheme, skill and machinery row, and exactly 1 investment row |
| V12 | Closed enum domains on 11 classification columns |
| **V13** | **Normalization — no column restates an upstream-owned attribute** |

Exit 0 = release-clean. Five defect classes were caught before release, including ten district
refs that were plausible guesses and did not exist, and three skill names that did not match
Package006's actual values. Detail in `validation_report.md`.

## Repository layout

```
Package008_MSME/
├── datasets/                    18 released CSVs
├── metadata/                    18 per-dataset metadata JSON files
├── reports/                     18 per-dataset collection reports
├── schemas/schema_catalog.json  canonical PK/FK/column reference
├── registry/dataset_registry.csv
├── docs/
│   ├── METHODOLOGY.md           how the data was collected and scored
│   ├── USAGE.md                 query recipes and traps
│   ├── DATA_DICTIONARY.md       every column, with observed domains
│   └── IMPORT_GUIDE.md          load order, DDL, join discipline
├── package_manifest.json
├── validation_report.md         validation_summary.json
├── quality_report.md            what this is and is not fit for
├── VERSION_HISTORY.md           RELEASE_NOTES.md  CHANGELOG.md  VERSION
├── codex_handoff.md
├── validate.py                  13-check validation engine
└── gen_core.py  gen_mappings.py  build_artifacts.py  build_docs.py
```

Full rebuild — order matters, because both builders read the validation summary:

```bash
python3 gen_core.py && python3 gen_mappings.py \
  && python3 validate.py && python3 build_artifacts.py && python3 build_docs.py
```

Every count in the manifest, registry, schema catalog, collection reports and docs is derived from
the CSVs rather than hand-maintained, so they cannot drift.

## Versioning

Released versions are immutable. Changes ship as new versions under
`Package008_MSME_vMAJOR.MINOR.PATCH`. See `VERSION_HISTORY.md` for lineage and the upstream
versions this release was built against, `CHANGELOG.md` for detail, and
`package_manifest.json` → `planned_next_release` for the v1.1.0 target.
