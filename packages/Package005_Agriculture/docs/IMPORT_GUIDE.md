# Import Guide — Package005_Agriculture v1.0.0

How to load these 16 CSVs into a relational store without corrupting them.

## 1. Load order

Dependency order. Also recorded as `import_order` in `package_manifest.json`.

| # | Dataset | Depends on |
|---|---|---|
| 1 | `crop_categories.csv` | — |
| 2 | `soil_types.csv` | — |
| 3 | `climate_zones.csv` | — |
| 4 | `crops.csv` | `crop_categories.csv` |
| 5 | `crop_soil_mapping.csv` | `crops.csv`, `soil_types.csv` |
| 6 | `crop_climate_mapping.csv` | `crops.csv`, `climate_zones.csv` |
| 7 | `farm_machinery.csv` | — |
| 8 | `agri_processing_opportunities.csv` | — |
| 9 | `farmer_producer_organizations.csv` | — |
| 10 | `agriculture_training.csv` | — |
| 11 | `agriculture_schemes.csv` | — |
| 12 | `crop_disease_management.csv` | — |
| 13 | `market_linkages.csv` | — |
| 14 | `export_opportunities.csv` | — |
| 15 | `ai_precision_agriculture.csv` | — |
| 16 | `agri_business_mapping.csv` | `crops.csv`, `agri_processing_opportunities.csv`, `Package004_Industries (cross-package)`, `Package006_Skills_and_Training (cross-package)` |

`agri_business_mapping` is last because two of its four foreign keys point **outside** this package (Package004_Industries, Package006_Skills_and_Training). Loading Package005 standalone is fine — treat those two columns as unresolved text until the other packages are present.

## 2. Every column is text on ingest

Load all columns as `TEXT`/`VARCHAR` first, then cast in a second pass. The reason is the sentinel: `PENDING_VERIFICATION` occupies cells in otherwise-numeric columns, so a direct typed load fails or silently coerces.

```sql
CREATE TABLE stg_crops (
  crop_id               TEXT,
  crop_name             TEXT,
  scientific_name       TEXT,
  category_id           TEXT,
  category_name         TEXT,
  season                TEXT,
  duration_days         TEXT,   -- sentinel on perennials
  water_requirement_mm  TEXT,
  soil_type_preferred   TEXT,
  rainfall_mm           TEXT,
  temperature_min_c     TEXT,
  temperature_max_c     TEXT,
  avg_yield_tons_per_ha TEXT,   -- sentinel on coconut, tulsi
  major_states          TEXT,
  major_districts       TEXT,   -- sentinel where no TG/AP footprint
  organic_possible      TEXT,
  export_potential      TEXT,
  processing_potential  TEXT,
  mechanization_level   TEXT,
  data_source           TEXT,
  source_url            TEXT,
  collection_date       TEXT,
  confidence_score      TEXT,
  verification_status   TEXT,
  notes                 TEXT
);
```

Then promote with an explicit sentinel guard:

```sql
CREATE TABLE crops AS
SELECT crop_id,
       crop_name,
       category_id,
       season,
       NULLIF(duration_days,         'PENDING_VERIFICATION')::INT     AS duration_days,
       NULLIF(avg_yield_tons_per_ha, 'PENDING_VERIFICATION')::NUMERIC AS avg_yield_tons_per_ha,
       NULLIF(major_districts,       'PENDING_VERIFICATION')          AS major_districts,
       confidence_score::INT AS confidence_score,
       verification_status,
       notes
FROM stg_crops;
```

`confidence_score` needs no guard — V4 guarantees it is a plain integer on every row of every dataset, never a sentinel.

## 3. Columns that carry sentinels

Guard exactly these. Everything else in the package is fully populated.

| Dataset | Column | Sentinel rows |
|---|---|---|
| `agri_processing_opportunities.csv` | `investment_band` | 17 / 17 |
| `agri_processing_opportunities.csv` | `capacity_indicative` | 17 / 17 |
| `farm_machinery.csv` | `investment_inr` | 16 / 16 |
| `farm_machinery.csv` | `annual_maintenance_inr` | 16 / 16 |
| `crops.csv` | `major_districts` | 14 / 45 |
| `agri_business_mapping.csv` | `package004_opportunity_name` | 13 / 30 |
| `farm_machinery.csv` | `power_hp` | 10 / 16 |
| `ai_precision_agriculture.csv` | `approximate_cost_inr` | 10 / 10 |
| `crops.csv` | `duration_days` | 9 / 45 |
| `farm_machinery.csv` | `capacity` | 7 / 16 |
| `crops.csv` | `avg_yield_tons_per_ha` | 2 / 45 |
| `farm_machinery.csv` | `subsidy_scheme` | 1 / 16 |

Two whole-column cases are worth calling out because a `NOT NULL` constraint on them will fail the load outright:

- `farm_machinery.investment_inr` and `annual_maintenance_inr` — **all 16 rows** sentinelled
- `ai_precision_agriculture.approximate_cost_inr` — **all 10 rows** sentinelled
- `agri_processing_opportunities.investment_band` and `capacity_indicative` — **all 17 rows** sentinelled

This is intentional (see `docs/METHODOLOGY.md` §2): no official public cost figure exists for this equipment, so none is asserted.

## 4. Constraints to declare

```sql
-- Primary keys (V2 guarantees these hold)
ALTER TABLE crop_categories ADD PRIMARY KEY (category_id);
ALTER TABLE soil_types      ADD PRIMARY KEY (soil_id);
ALTER TABLE climate_zones   ADD PRIMARY KEY (climate_zone_id);
ALTER TABLE crops           ADD PRIMARY KEY (crop_id);

-- In-package foreign keys (V8 guarantees these resolve)
ALTER TABLE crops ADD FOREIGN KEY (category_id)
  REFERENCES crop_categories(category_id);
ALTER TABLE crop_soil_mapping ADD FOREIGN KEY (crop_id) REFERENCES crops(crop_id);
ALTER TABLE crop_soil_mapping ADD FOREIGN KEY (soil_id) REFERENCES soil_types(soil_id);
ALTER TABLE crop_climate_mapping ADD FOREIGN KEY (crop_id) REFERENCES crops(crop_id);
ALTER TABLE crop_climate_mapping ADD FOREIGN KEY (climate_zone_id)
  REFERENCES climate_zones(climate_zone_id);
ALTER TABLE agri_business_mapping ADD FOREIGN KEY (crop_id) REFERENCES crops(crop_id);
ALTER TABLE agri_business_mapping ADD FOREIGN KEY (processing_opportunity_id)
  REFERENCES agri_processing_opportunities(opportunity_id);

-- Check constraints mirroring validation policy
ALTER TABLE crops ADD CHECK (confidence_score BETWEEN 0 AND 85);
ALTER TABLE crops ADD CHECK (verification_status IN ('VST-NEEDS_REVIEW','VST-VERIFIED'));
```

**Do not** declare a foreign key on `agri_business_mapping.package006_skill_id` or `package004_opportunity_name` unless those packages are loaded in the same schema. 13 of 30 `package004_opportunity_name` values are the sentinel and will violate a naive FK.

## 5. Denormalised name columns

Mapping tables carry both an ID and its name (`crop_id` + `crop_name`, `soil_id` + `soil_name`, `climate_zone_id` + `climate_zone_name`) for readability. Validation check V8 verifies the name agrees with the referenced row.

If you normalise on import, **drop the name columns and join** — do not keep both, or the next hand-edit will desynchronise them. If you keep them, re-run `validate.py` after any edit; V8 is what caught the `crop_id` renumbering during this release.

## 6. Post-load verification

Confirm the load matches the release:

```sql
SELECT 'crops' t, COUNT(*) n FROM crops
UNION ALL SELECT 'crop_categories', COUNT(*) FROM crop_categories
UNION ALL SELECT 'crop_soil_mapping', COUNT(*) FROM crop_soil_mapping
UNION ALL SELECT 'crop_climate_mapping', COUNT(*) FROM crop_climate_mapping
UNION ALL SELECT 'agri_business_mapping', COUNT(*) FROM agri_business_mapping;
```

Expected:

| Table | Rows |
|---|---|
| `crop_categories` | 24 |
| `soil_types` | 10 |
| `climate_zones` | 8 |
| `crops` | 45 |
| `crop_soil_mapping` | 90 |
| `crop_climate_mapping` | 90 |
| `farm_machinery` | 16 |
| `agri_processing_opportunities` | 17 |
| `farmer_producer_organizations` | 5 |
| `agriculture_training` | 7 |
| `agriculture_schemes` | 12 |
| `crop_disease_management` | 10 |
| `market_linkages` | 6 |
| `export_opportunities` | 8 |
| `ai_precision_agriculture` | 10 |
| `agri_business_mapping` | 30 |
| **total** | **388** |

Authoritative counts live in `registry/dataset_registry.csv` and `package_manifest.json`, both generated from the CSVs themselves.

## 7. Re-validating the source files

```bash
cd packages/Package005_Agriculture
python3 validate.py      # exit 0 = clean
```

Run this before any import, and again after any hand-edit to a CSV.
