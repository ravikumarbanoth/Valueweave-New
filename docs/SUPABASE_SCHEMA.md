# Supabase Schema — `knowledge`

**Generated from `knowledge_sync/config.py`.** Regenerate after changing a spec;
`generate_migration.py --check` fails CI on drift.

DDL: `knowledge_sync/migrations/001_knowledge_schema.sql`

---

## 1. Why a schema and not `public`

`kg_skills`, `kg_schemes` and `kg_relationships` **already exist in `public`** as
admin-authored CMS tables with different columns and different RLS. The brief asks
for those three names *and* says not to touch existing application tables.

A dedicated schema satisfies both: the tables get their intended names, `public`
is never opened, and

```sql
drop schema knowledge cascade;
```

is a complete rollback that cannot reach user data. Full argument in
`SYNC_ARCHITECTURE.md` §2.

---

## 2. The eight tables

| Table | Rows | Columns | Source packages |
|---|---:|---:|---|
| `kg_entities` | 647 | 20 | knowledge_graph |
| `kg_relationships` | 865 | 19 | knowledge_graph |
| `kg_districts` | 61 | 30 | Package001_Geography |
| `kg_skills` | 45 | 29 | Package006_Skills_and_Training |
| `kg_schemes` | 40 | 34 | Package007_Government_Schemes |
| `kg_businesses` | 85 | 35 | Package004_Industries, Package008_MSME |
| `kg_industries` | 24 | 23 | Package008_MSME |
| `kg_agriculture` | 45 | 30 | Package005_Agriculture |
| **Total** | **1812** | | |

Plus `knowledge.sync_runs` — one row per sync run, admin-readable.

---

## 3. Columns every table carries

| Column | Type | Purpose |
|---|---|---|
| `sync_row_key` | `text` **PK** | Stable key. The source row id, or `dataset:id` where several datasets feed one table. |
| `sync_source_package` | `text` | Which package produced this row |
| `sync_source_dataset` | `text` | Which CSV |
| `sync_source_row_id` | `text` | Which row in that CSV |
| `sync_content_hash` | `text` | Change detection. **Excludes** the `sync_*` columns, so a re-sync is not a diff. |
| `sync_pending_fields` | `jsonb` | `{column: sentinel}` — which values are unknown and *why* |
| `sync_version` | `text` | The run that last wrote this row |
| `sync_synced_at` | `timestamptz` | When |
| `sync_deleted_at` | `timestamptz` | Soft delete. `null` = live. **Rows are never removed.** |

Every application query filters `sync_deleted_at is null`, which the RLS policy
enforces anyway.

### `sync_pending_fields` is the interesting one

```json
{"latitude": "PENDING_GEOCODING", "longitude": "PENDING_GEOCODING"}
```

Two sentinels exist across the packages — `PENDING_VERIFICATION` (2,456 cells)
and `PENDING_GEOCODING` (272 cells). Both become `NULL` in their column, because
zero would be a fabricated measurement and the literal string would make every
consumer re-implement the check. Recording *which* sentinel lets the UI say
"coordinates not yet resolved" rather than showing a blank.

---

## 4. Type mapping

| CSV content | Postgres | Rule |
|---|---|---|
| A sentinel | `NULL` | plus an entry in `sync_pending_fields` |
| Empty, numeric column | `NULL` | an empty number is not a value |
| Empty, text column | `''` | an empty text cell is a distinguishable value |
| `"42"` | `integer` | |
| `"12,00,000"` | **error** | coercing to `NULL` would discard a real figure |
| `"2026-07-26"` | `date` | |
| `collection_date` | `text` | 9 rows carry `"2026-07-22; 2026-07-24 (v2 enrichment)"` |
| `minimum_investment` | `text` | all 45 Package004 values are sourced prose |

The last two look like mistakes and are not. See `SYNC_ARCHITECTURE.md` §6.

---

## 5. Foreign keys are validated, not constrained

`kg_relationships.from_entity` and `.to_entity` reference `kg_entities`, and
validation check V4 fails the run on a dangling reference — but **no `references`
clause exists in the DDL**.

A database FK would make load order a hard dependency and turn a soft-deleted
entity into a constraint violation for every edge that touches it. Since a sync is
all-or-nothing and validation runs across all tables before any write, the
guarantee is already enforced upstream; a database constraint would add a failure
mode without adding a guarantee.

---

## 6. Indexes

Per table:

- `<table>_live_idx` on `(sync_row_key) where sync_deleted_at is null` — partial,
  because every application query wants live rows only
- `<table>_source_idx` on `(sync_source_package, sync_source_dataset)`
- one on each foreign key
- one on each name/type column a page filters by: `entity_type`,
  `canonical_name`, `relationship_type`, `district_name`, `skill_name`,
  `scheme_name`, `business_name`, `crop_name`, `category_name`, `business_kind`,
  `st_id`

At 1812 rows these exist for query *shape*, not volume.

---

## 7. Row level security

```sql
alter table knowledge.<table> enable row level security;

create policy "<table> public read"
  on knowledge.<table> for select
  using (sync_deleted_at is null);
```

**There is no insert, update or delete policy on any table, deliberately.** With
RLS enabled and no write policy, `anon` and `authenticated` cannot write here at
all. The sync uses the service role, which bypasses RLS.

*"Never edit package data inside Supabase"* is therefore enforced by the **absence
of a policy** rather than by convention — the strongest form available, because
there is nothing to misconfigure.

`sync_runs` is admin-read-only via `public.is_valueweave_admin()`.

---

## 8. Grants

```sql
grant usage on schema knowledge to anon, authenticated;
grant select on all tables in schema knowledge to anon, authenticated;
alter default privileges in schema knowledge
  grant select on tables to anon, authenticated;
```

`select` only. No write grant is issued to any role.

---

## 9. Table reference

### `knowledge.kg_entities`

Global entity registry — every node in the knowledge graph.

**647 rows** · owner `knowledge_graph`

**Sources**

- `knowledge_graph/entities.csv` (key `global_entity_id`)

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `global_entity_id` | `text` | **not null** |
| `entity_type` | `text` | **not null** |
| `canonical_name` | `text` | **not null** |
| `source_package` | `text` | **not null** |
| `package_local_id` | `text` |  |
| `status` | `text` |  |
| `lifecycle_state` | `text` |  |
| `created_at` | `date` |  |
| `updated_at` | `date` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_relationships`

Typed, provenance-carrying edges between entities.

**865 rows** · owner `knowledge_graph`

**Sources**

- `knowledge_graph/relationships.csv` (key `relationship_id`)

**Foreign keys**

- `from_entity` → `knowledge.kg_entities.global_entity_id` (validated at sync time, not a database constraint — see §5)
- `to_entity` → `knowledge.kg_entities.global_entity_id` (validated at sync time, not a database constraint — see §5)

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `relationship_id` | `text` | **not null** |
| `from_entity` | `text` | **not null** |
| `relationship_type` | `text` | **not null** |
| `to_entity` | `text` | **not null** |
| `confidence` | `integer` |  |
| `provenance_package` | `text` | **not null** |
| `provenance_dataset` | `text` | **not null** |
| `provenance_row_id` | `text` | **not null** |
| `derived_at` | `date` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_districts`

Districts of Telangana and Andhra Pradesh.

**61 rows** · owner `Package001_Geography`

**Sources**

- `Package001_Geography/district.csv` (key `dist_id`)

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `dist_id` | `text` | **not null** |
| `district_name` | `text` | **not null** |
| `st_id` | `text` | **not null** |
| `district_headquarters` | `text` |  |
| `area_sq_km` | `numeric` |  |
| `population` | `integer` |  |
| `mandal_count` | `integer` |  |
| `density_per_sq_km` | `numeric` |  |
| `urban_pct` | `numeric` |  |
| `literacy_rate_pct` | `numeric` |  |
| `sex_ratio` | `numeric` |  |
| `latitude` | `numeric` |  |
| `longitude` | `numeric` |  |
| `govt_district_code` | `text` |  |
| `lgd_district_code` | `text` |  |
| `data_source` | `text` |  |
| `source_url` | `text` |  |
| `collection_date` | `text` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_skills`

Skills with NSQF level, demand and automation risk.

**45 rows** · owner `Package006_Skills_and_Training`

**Sources**

- `Package006_Skills_and_Training/skills.csv` (key `skill_id`)

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `skill_id` | `text` | **not null** |
| `skill_name` | `text` | **not null** |
| `category_id` | `text` |  |
| `category_name` | `text` |  |
| `description` | `text` |  |
| `difficulty_level` | `text` |  |
| `nsqf_level` | `integer` |  |
| `learning_duration` | `text` |  |
| `demand_level` | `text` |  |
| `automation_risk` | `text` |  |
| `ai_augmentation_level` | `text` |  |
| `future_demand` | `text` |  |
| `self_employment_score` | `integer` |  |
| `startup_opportunity` | `text` |  |
| `data_source` | `text` |  |
| `source_url` | `text` |  |
| `collection_date` | `text` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_schemes`

Government schemes — Package007 is the authoritative owner (ADR-003).

**40 rows** · owner `Package007_Government_Schemes`

**Sources**

- `Package007_Government_Schemes/government_schemes.csv` (key `scheme_id`)

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `scheme_id` | `text` | **not null** |
| `scheme_name` | `text` | **not null** |
| `short_name` | `text` |  |
| `category_id` | `text` |  |
| `category_name` | `text` |  |
| `ministry` | `text` |  |
| `department` | `text` |  |
| `government_level` | `text` |  |
| `launch_year` | `integer` |  |
| `objective` | `text` |  |
| `benefit_summary` | `text` |  |
| `financial_assistance` | `text` |  |
| `subsidy_component` | `text` |  |
| `loan_support` | `text` |  |
| `coverage` | `text` |  |
| `application_mode` | `text` |  |
| `official_portal` | `text` |  |
| `status` | `text` |  |
| `also_in_package` | `text` |  |
| `data_source` | `text` |  |
| `source_url` | `text` |  |
| `collection_date` | `text` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_businesses`

MSME businesses and business opportunities. Unions Package008's researched MSMEs with Package004's four opportunity datasets.

**85 rows** · owner `Package008_MSME`

**Sources**

- `Package008_MSME/msme_businesses.csv` (key `business_id`) — tagged `business_kind=MSME`
- `Package004_Industries/food_agro_processing_micro_enterprises.csv` (key `id`) — tagged `business_kind=BusinessOpportunity`
- `Package004_Industries/construction_skilled_trade_services.csv` (key `id`) — tagged `business_kind=BusinessOpportunity`
- `Package004_Industries/digital_technology_livelihoods.csv` (key `id`) — tagged `business_kind=BusinessOpportunity`
- `Package004_Industries/china_inspired_adapted_opportunities.csv` (key `id`) — tagged `business_kind=BusinessOpportunity`

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `business_id` | `text` |  |
| `id` | `text` |  |
| `business_kind` | `text` | **not null** |
| `business_name` | `text` |  |
| `name` | `text` |  |
| `category_id` | `text` |  |
| `category_name` | `text` |  |
| `description` | `text` |  |
| `udyam_classification` | `text` |  |
| `investment_range` | `text` |  |
| `minimum_investment` | `text` |  |
| `working_capital_need` | `text` |  |
| `employment_generation` | `text` |  |
| `difficulty` | `text` |  |
| `risk_level` | `text` |  |
| `technology_level` | `text` |  |
| `automation_level` | `text` |  |
| `ai_readiness` | `text` |  |
| `profitability_outlook` | `text` |  |
| `ideal_target_audience` | `text` |  |
| `data_source` | `text` |  |
| `source_url` | `text` |  |
| `collection_date` | `text` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_industries`

MSME sector taxonomy. Package004 has no standalone industry dataset — its industries are embedded in opportunity rows — so the graph's 78 Industry nodes stay in kg_entities and this table is the browsable sector list.

**24 rows** · owner `Package008_MSME`

**Sources**

- `Package008_MSME/msme_categories.csv` (key `category_id`)

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `category_id` | `text` | **not null** |
| `category_name` | `text` | **not null** |
| `category_group` | `text` |  |
| `description` | `text` |  |
| `nic_section_hint` | `text` |  |
| `capital_intensity` | `text` |  |
| `skill_intensity` | `text` |  |
| `typical_udyam_class` | `text` |  |
| `data_source` | `text` |  |
| `source_url` | `text` |  |
| `collection_date` | `text` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.
### `knowledge.kg_agriculture`

Crops with agronomic attributes (Package005).

**45 rows** · owner `Package005_Agriculture`

**Sources**

- `Package005_Agriculture/crops.csv` (key `crop_id`)

**Foreign keys**

_none_

| Column | Type | |
|---|---|---|
| `sync_row_key` | `text` | **primary key** |
| `crop_id` | `text` | **not null** |
| `crop_name` | `text` | **not null** |
| `scientific_name` | `text` |  |
| `category_id` | `text` |  |
| `category_name` | `text` |  |
| `season` | `text` |  |
| `duration_days` | `integer` |  |
| `water_requirement_mm` | `integer` |  |
| `soil_type_preferred` | `text` |  |
| `rainfall_mm` | `integer` |  |
| `temperature_min_c` | `numeric` |  |
| `temperature_max_c` | `numeric` |  |
| `avg_yield_tons_per_ha` | `numeric` |  |
| `major_states` | `text` |  |
| `major_districts` | `text` |  |
| `data_source` | `text` |  |
| `source_url` | `text` |  |
| `collection_date` | `text` |  |
| `confidence_score` | `integer` |  |
| `verification_status` | `text` |  |
| `notes` | `text` |  |

Plus the eight `sync_*` columns described in §3.

---

## 10. Applying and rolling back

```bash
# apply
psql "$DATABASE_URL" -f knowledge_sync/migrations/001_knowledge_schema.sql

# verify
psql "$DATABASE_URL" -c "\dt knowledge.*"

# roll back — complete, and cannot reach application data
psql "$DATABASE_URL" -c "drop schema knowledge cascade;"
```

The migration is `create ... if not exists` throughout, so it is re-runnable.

**Not yet applied to any database.** No Supabase credentials exist in this
environment; the DDL is generated and tested, not executed. See
`OPERATIONS_GUIDE.md` §First run.
