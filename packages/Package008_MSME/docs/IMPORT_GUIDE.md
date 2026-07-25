# Import Guide — Package008_MSME v1.0.0

How to load these 18 CSVs without corrupting them — and without undoing the normalization the package exists to provide.

## 1. Load order

| # | Dataset | Depends on |
|---|---|---|
| 1 | `msme_categories.csv` | — |
| 2 | `business_models.csv` | — |
| 3 | `license_compliance.csv` | — |
| 4 | `financial_support.csv` | — |
| 5 | `market_channels.csv` | — |
| 6 | `ai_business_tools.csv` | — |
| 7 | `startup_ecosystem.csv` | — |
| 8 | `msme_businesses.csv` | `msme_categories.csv`, `business_models.csv` |
| 9 | `machinery_mapping.csv` | `msme_businesses.csv`, `Package005_Agriculture (cross-package)` |
| 10 | `raw_material_mapping.csv` | `msme_businesses.csv`, `Package005_Agriculture (cross-package)` |
| 11 | `scheme_mapping.csv` | `msme_businesses.csv`, `Package007_Government_Schemes (cross-package)` |
| 12 | `skill_mapping.csv` | `msme_businesses.csv`, `Package006_Skills_and_Training (cross-package)` |
| 13 | `industry_mapping.csv` | `msme_businesses.csv`, `Package004_Industries (cross-package)` |
| 14 | `agriculture_business_mapping.csv` | `msme_businesses.csv`, `Package005_Agriculture (cross-package)`, `Package005_Agriculture (cross-package)` |
| 15 | `education_support_mapping.csv` | `Package002_Education (cross-package)`, `Package006_Skills_and_Training (cross-package)` |
| 16 | `district_business_mapping.csv` | `msme_businesses.csv`, `Package001_Geography (cross-package)` |
| 17 | `export_opportunities.csv` | `msme_businesses.csv` |
| 18 | `investment_intelligence.csv` | `msme_businesses.csv` |

Independent reference taxonomies first, then `msme_businesses` (needs categories and models), then the eight mapping datasets, and `investment_intelligence` last.

Eight datasets carry foreign keys **outside** this package, into six upstream packages. Loading Package008 standalone works — treat those columns as unresolved text until the upstream packages are in the same schema.

## 2. Every column is text on ingest

```sql
CREATE TABLE stg_msme_businesses (
  business_id            TEXT,
  business_name          TEXT,
  category_id            TEXT,
  category_name          TEXT,
  business_model_id      TEXT,
  business_model_name    TEXT,
  description            TEXT,
  udyam_classification   TEXT,
  investment_range       TEXT,   -- sentinel on ALL 40 rows
  working_capital_need   TEXT,
  employment_generation  TEXT,   -- range string e.g. '6-15', not a number
  difficulty             TEXT,
  risk_level             TEXT,
  technology_level       TEXT,
  automation_level       TEXT,
  ai_readiness           TEXT,
  market_demand          TEXT,
  export_potential       TEXT,
  profitability_outlook  TEXT,
  district_suitability   TEXT,
  data_source            TEXT,
  source_url             TEXT,
  collection_date        TEXT,
  confidence_score       TEXT,
  verification_status    TEXT,
  notes                  TEXT
);
```

`confidence_score` needs no sentinel guard — V4 guarantees a plain integer everywhere. `investment_range` needs one on every row, because it is sentinelled on every row.

`employment_generation` is a range string. Split it if you need bounds:

```sql
SELECT business_id,
       SPLIT_PART(employment_generation, '-', 1)::INT AS emp_min,
       SPLIT_PART(employment_generation, '-', 2)::INT AS emp_max
FROM msme_businesses
WHERE employment_generation <> 'PENDING_VERIFICATION';
```

## 3. Columns that carry sentinels

| Dataset | Column | Sentinel rows |
|---|---|---|
| `machinery_mapping.csv` | `package005_machinery_id` | 54 / 64 |
| `machinery_mapping.csv` | `package005_machinery_name` | 54 / 64 |
| `msme_businesses.csv` | `investment_range` | 40 / 40 |
| `raw_material_mapping.csv` | `package005_crop_id` | 21 / 33 |
| `raw_material_mapping.csv` | `package005_crop_name` | 21 / 33 |
| `business_models.csv` | `typical_lead_time_to_revenue` | 15 / 15 |
| `market_channels.csv` | `typical_payment_cycle` | 11 / 11 |
| `education_support_mapping.csv` | `package002_institution_id` | 9 / 13 |
| `education_support_mapping.csv` | `package002_institution_name` | 9 / 13 |
| `market_channels.csv` | `official_portal` | 8 / 11 |
| `skill_mapping.csv` | `package006_skill_id` | 7 / 53 |
| `skill_mapping.csv` | `package006_skill_name` | 7 / 53 |
| `license_compliance.csv` | `official_portal` | 6 / 14 |
| `financial_support.csv` | `official_website` | 4 / 12 |
| `financial_support.csv` | `linked_package007_scheme_short_name` | 4 / 12 |
| `agriculture_business_mapping.csv` | `package005_crop_id` | 4 / 14 |
| `agriculture_business_mapping.csv` | `package005_crop_name` | 4 / 14 |
| `education_support_mapping.csv` | `package006_provider_id` | 4 / 13 |
| `education_support_mapping.csv` | `package006_provider_name` | 4 / 13 |
| `startup_ecosystem.csv` | `official_website` | 3 / 12 |

Whole-column cases — a `NOT NULL` constraint on any of these fails the load:

- `msme_businesses.investment_range` — **all 40 rows**
- `business_models.typical_lead_time_to_revenue` — **all 15 rows**
- `market_channels.typical_payment_cycle` — **all 11 rows**

## 4. Constraints to declare

```sql
ALTER TABLE msme_categories ADD PRIMARY KEY (category_id);
ALTER TABLE business_models ADD PRIMARY KEY (business_model_id);
ALTER TABLE msme_businesses ADD PRIMARY KEY (business_id);

ALTER TABLE msme_businesses
  ADD FOREIGN KEY (category_id)       REFERENCES msme_categories(category_id),
  ADD FOREIGN KEY (business_model_id) REFERENCES business_models(business_model_id);

-- repeat on every mapping table, export_opportunities and investment_intelligence
ALTER TABLE scheme_mapping ADD FOREIGN KEY (business_id)
  REFERENCES msme_businesses(business_id);

-- investment_intelligence is strictly 1:1 (V11 enforces exactly one row per business)
ALTER TABLE investment_intelligence ADD UNIQUE (business_id);

ALTER TABLE msme_businesses
  ADD CHECK (confidence_score BETWEEN 0 AND 85),
  ADD CHECK (verification_status IN ('VST-NEEDS_REVIEW','VST-VERIFIED')),
  ADD CHECK (udyam_classification IN ('Micro','Small','Medium')),
  ADD CHECK (difficulty IN ('Easy','Moderate','Hard','Very Hard')),
  ADD CHECK (district_suitability IN ('Rural','Urban','Both','Variable'));
```

**Do not** declare foreign keys on the `package0NN_*` columns unless those packages are in the same schema — several carry sentinels and will violate a naive FK.

## 5. Do not re-denormalise upstream attributes

This is the import rule specific to Package008, and the most important one here.

The package deliberately holds no scheme benefit, no skill NSQF level, no crop agronomy and no district demographics. Those are reached by joining on the referenced id. Validation check **V13** fails the build if such a column appears in Package008 itself.

V13 cannot police your schema. If you materialise a convenience join, keep it a **view**:

```sql
-- Correct: a view
CREATE VIEW v_business_scheme_detail AS
SELECT b.business_id, b.business_name,
       s.relevance, s.applicable_stage, s.support_nature,
       p7.scheme_name, p7.benefit_summary, p7.official_portal   -- lives in Package007
FROM msme_businesses b
JOIN scheme_mapping s USING (business_id)
JOIN package007.government_schemes p7 ON p7.scheme_id = s.package007_scheme_id;
```

Persisting those Package007 columns into a Package008 table recreates exactly the duplication the package structure prevents. The next Package007 release will then silently diverge from your copy, and nothing will tell you.

## 6. Post-load verification

| Table | Rows |
|---|---|
| `msme_categories` | 24 |
| `business_models` | 15 |
| `license_compliance` | 14 |
| `financial_support` | 12 |
| `market_channels` | 11 |
| `ai_business_tools` | 12 |
| `startup_ecosystem` | 12 |
| `msme_businesses` | 40 |
| `machinery_mapping` | 64 |
| `raw_material_mapping` | 33 |
| `scheme_mapping` | 57 |
| `skill_mapping` | 53 |
| `industry_mapping` | 19 |
| `agriculture_business_mapping` | 14 |
| `education_support_mapping` | 13 |
| `district_business_mapping` | 32 |
| `export_opportunities` | 12 |
| `investment_intelligence` | 40 |
| **total** | **477** |

Authoritative counts live in `registry/dataset_registry.csv` and `package_manifest.json`, both generated from the CSVs.

## 7. Re-validating

```bash
cd packages/Package008_MSME
python3 validate.py      # exit 0 = clean; 13 checks including V13 normalization
```
