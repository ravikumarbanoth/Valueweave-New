# Import Guide — Package007_Government_Schemes v1.0.0

How to load these 15 CSVs into a relational store without corrupting them.

## 1. Load order

Dependency order, also recorded as `import_order` in `package_manifest.json`.

| # | Dataset | Depends on |
|---|---|---|
| 1 | `scheme_categories.csv` | — |
| 2 | `required_documents.csv` | — |
| 3 | `implementing_agencies.csv` | — |
| 4 | `financial_institutions.csv` | — |
| 5 | `scheme_application_status.csv` | — |
| 6 | `government_schemes.csv` | `scheme_categories.csv` |
| 7 | `eligibility_criteria.csv` | `government_schemes.csv`, `required_documents.csv` |
| 8 | `scheme_benefits.csv` | `government_schemes.csv` |
| 9 | `application_process.csv` | `government_schemes.csv` |
| 10 | `education_scheme_mapping.csv` | `government_schemes.csv`, `Package002_Education (cross-package)` |
| 11 | `agriculture_scheme_mapping.csv` | `government_schemes.csv`, `Package005_Agriculture (cross-package)`, `Package005_Agriculture (cross-package)` |
| 12 | `skill_scheme_mapping.csv` | `government_schemes.csv`, `Package006_Skills_and_Training (cross-package)`, `Package006_Skills_and_Training (cross-package)`, `Package006_Skills_and_Training (cross-package)`, `Package006_Skills_and_Training (cross-package)` |
| 13 | `industry_scheme_mapping.csv` | `government_schemes.csv`, `Package004_Industries (cross-package)` |
| 14 | `district_scheme_mapping.csv` | `government_schemes.csv`, `Package001_Geography (cross-package)` |
| 15 | `scheme_ai_recommendations.csv` | `government_schemes.csv`, `government_schemes.csv`, `government_schemes.csv` |

Reference taxonomies load first, then `government_schemes` (the canonical registry), then its child datasets, then the five cross-package mappings, and `scheme_ai_recommendations` last because it references `government_schemes` three times — including a semicolon-delimited multi-value column.

Five of the mapping datasets carry foreign keys **outside** this package. Loading Package007 standalone is fine — treat those columns as unresolved text until the upstream packages are present in the same schema.

## 2. Every column is text on ingest

Load as `TEXT`/`VARCHAR`, then cast in a second pass. The sentinel occupies cells in otherwise-numeric columns, so a directly typed load fails or silently coerces.

```sql
CREATE TABLE stg_government_schemes (
  scheme_id            TEXT,
  scheme_name          TEXT,
  short_name           TEXT,
  category_id          TEXT,
  category_name        TEXT,
  ministry             TEXT,
  department           TEXT,
  government_level     TEXT,
  launch_year          TEXT,
  objective            TEXT,
  benefit_summary      TEXT,
  financial_assistance TEXT,   -- sentinel on nearly every row
  subsidy_component    TEXT,
  loan_support         TEXT,
  coverage             TEXT,
  application_mode     TEXT,
  official_portal      TEXT,
  status               TEXT,
  also_in_package      TEXT,   -- sentinel where the scheme is Package007-only
  data_source          TEXT,
  source_url           TEXT,
  collection_date      TEXT,
  confidence_score     TEXT,
  verification_status  TEXT,
  notes                TEXT
);
```

Promote with an explicit sentinel guard:

```sql
CREATE TABLE government_schemes AS
SELECT scheme_id, scheme_name, short_name, category_id,
       ministry, department, government_level,
       NULLIF(launch_year,          'PENDING_VERIFICATION')::INT AS launch_year,
       NULLIF(financial_assistance, 'PENDING_VERIFICATION')      AS financial_assistance,
       NULLIF(also_in_package,      'PENDING_VERIFICATION')      AS also_in_package,
       objective, benefit_summary, coverage, application_mode,
       official_portal, status,
       confidence_score::INT AS confidence_score,
       verification_status, notes
FROM stg_government_schemes;
```

`confidence_score` needs no guard — V4 guarantees a plain integer on every row of every dataset, never a sentinel.

## 3. Columns that carry sentinels

| Dataset | Column | Sentinel rows |
|---|---|---|
| `district_scheme_mapping.csv` | `district_specific_variation` | 305 / 305 |
| `scheme_benefits.csv` | `benefit_quantum` | 45 / 51 |
| `application_process.csv` | `typical_timeline` | 39 / 43 |
| `government_schemes.csv` | `financial_assistance` | 35 / 40 |
| `government_schemes.csv` | `also_in_package` | 18 / 40 |
| `scheme_ai_recommendations.csv` | `suggested_next_scheme_id` | 12 / 37 |
| `eligibility_criteria.csv` | `verification_document_hint` | 11 / 55 |
| `skill_scheme_mapping.csv` | `package006_provider_id` | 9 / 12 |
| `skill_scheme_mapping.csv` | `package006_provider_name` | 9 / 12 |
| `skill_scheme_mapping.csv` | `package006_certification_id` | 8 / 12 |
| `skill_scheme_mapping.csv` | `package006_certification_name` | 8 / 12 |
| `implementing_agencies.csv` | `official_website` | 6 / 20 |
| `financial_institutions.csv` | `official_website` | 4 / 12 |
| `education_scheme_mapping.csv` | `package002_dataset` | 3 / 7 |
| `education_scheme_mapping.csv` | `package002_record_id` | 3 / 7 |
| `education_scheme_mapping.csv` | `package002_record_name` | 3 / 7 |
| `skill_scheme_mapping.csv` | `package006_scheme_id` | 3 / 12 |
| `skill_scheme_mapping.csv` | `package006_scheme_name` | 3 / 12 |
| `agriculture_scheme_mapping.csv` | `package005_crop_id` | 2 / 14 |
| `agriculture_scheme_mapping.csv` | `package005_crop_name` | 2 / 14 |
| `agriculture_scheme_mapping.csv` | `package005_scheme_id` | 2 / 14 |
| `agriculture_scheme_mapping.csv` | `package005_scheme_name` | 2 / 14 |
| `skill_scheme_mapping.csv` | `package006_skill_id` | 1 / 12 |
| `skill_scheme_mapping.csv` | `package006_skill_name` | 1 / 12 |

Whole-column cases — a `NOT NULL` constraint on any of these will fail the load:

- `application_process.typical_timeline` — **all 43 rows**
- `district_scheme_mapping.district_specific_variation` — **all 305 rows**
- `scheme_benefits.benefit_quantum` — nearly every row
- `government_schemes.financial_assistance` — nearly every row

This is intentional (see `docs/METHODOLOGY.md` §2): scheme amounts and processing timelines are notification-driven and were not confirmable, so none is asserted.

## 4. Constraints to declare

```sql
ALTER TABLE scheme_categories   ADD PRIMARY KEY (category_id);
ALTER TABLE required_documents  ADD PRIMARY KEY (document_id);
ALTER TABLE government_schemes  ADD PRIMARY KEY (scheme_id);

ALTER TABLE government_schemes ADD FOREIGN KEY (category_id)
  REFERENCES scheme_categories(category_id);
ALTER TABLE eligibility_criteria ADD FOREIGN KEY (scheme_id)
  REFERENCES government_schemes(scheme_id);
ALTER TABLE scheme_benefits ADD FOREIGN KEY (scheme_id)
  REFERENCES government_schemes(scheme_id);
ALTER TABLE application_process ADD FOREIGN KEY (scheme_id)
  REFERENCES government_schemes(scheme_id);
-- and the same on all five *_scheme_mapping tables

ALTER TABLE government_schemes
  ADD CHECK (confidence_score BETWEEN 0 AND 85),
  ADD CHECK (verification_status IN ('VST-NEEDS_REVIEW','VST-VERIFIED')),
  ADD CHECK (government_level IN ('Central','State','Central-State','Local')),
  ADD CHECK (status IN ('Active','Closed','Subsumed','Revised'));
```

**Do not** declare foreign keys on the cross-package columns (`package001_dist_id`, `package002_record_id`, `package005_*`, `package006_*`, `package004_opportunity_name`) unless those packages are loaded in the same schema — several carry sentinels and will violate a naive FK.

`scheme_ai_recommendations.related_scheme_ids` is a **semicolon-delimited multi-value column**. Normalise it into a junction table rather than declaring an FK on it:

```sql
CREATE TABLE recommendation_related_scheme AS
SELECT recommendation_id,
       TRIM(UNNEST(STRING_TO_ARRAY(related_scheme_ids, ';'))) AS scheme_id
FROM scheme_ai_recommendations
WHERE related_scheme_ids <> 'PENDING_VERIFICATION';
```

## 5. Denormalised name columns

Child and mapping datasets carry `scheme_short_name` alongside `scheme_id` for readability, and the mapping datasets do the same for upstream names. V8 and V9 verify these agree with the referenced row — this is what caught a real short-name inconsistency during release (`SUI` in the registry versus `Stand-Up India` in five child datasets).

If you normalise on import, drop the name columns and join. If you keep them, re-run `validate.py` after any edit.

## 6. Post-load verification

| Table | Rows |
|---|---|
| `scheme_categories` | 24 |
| `required_documents` | 15 |
| `implementing_agencies` | 20 |
| `financial_institutions` | 12 |
| `scheme_application_status` | 8 |
| `government_schemes` | 40 |
| `eligibility_criteria` | 55 |
| `scheme_benefits` | 51 |
| `application_process` | 43 |
| `education_scheme_mapping` | 7 |
| `agriculture_scheme_mapping` | 14 |
| `skill_scheme_mapping` | 12 |
| `industry_scheme_mapping` | 12 |
| `district_scheme_mapping` | 305 |
| `scheme_ai_recommendations` | 37 |
| **total** | **655** |

Authoritative counts live in `registry/dataset_registry.csv` and `package_manifest.json`, both generated from the CSVs themselves.

## 7. Re-validating

```bash
cd packages/Package007_Government_Schemes
python3 validate.py      # exit 0 = clean
```

Run before any import and after any hand-edit.
