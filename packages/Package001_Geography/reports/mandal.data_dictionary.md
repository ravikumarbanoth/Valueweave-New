# Data Dictionary — `mandal.csv`

| Column | Type | Description | Mandatory | Example | Validation | Foreign Key |
|---|---|---|---|---|---|---|
| `mandal_id` | UUID | Primary key | Yes | — | UUID v4 | — |
| `mandal_ref` | TEXT | ValueWeave code: `{STATE}-{DISTRICT}-{MNEMONIC}` | Yes | `TG-MDK-NKD` | Unique | — |
| `mandal_name` | TEXT | Official mandal/tehsil name | Yes | Narayankhed | Unique within `dist_id` | — |
| `dist_id` | UUID | Parent district | Yes | — | Must exist in `district.dist_id` | `district.dist_id` |
| `revenue_division_name` | TEXT | Parent revenue division (intermediate tier between District and Mandal — see Collection Report §0 Schema Evolution Note) | No | Sangareddy | Free text pending its own lookup/entity if usage grows | — |
| `lgd_subdistrict_code` | TEXT | LGD-issued numeric sub-district code | No | `PENDING_VERIFICATION` | Must match LGD registry once populated | — |
| `village_count` | INTEGER | Number of villages in the mandal | No | `PENDING_VERIFICATION` | ≥ 0 | — |
| `mandal_population` | INTEGER | Population per cited Census/Survey year | No | `PENDING_VERIFICATION` | ≥ 0 | — |
| `population_source_detail` | TEXT | Which source/year the population figure is from | No | `PENDING_VERIFICATION` | — | — |
| `is_rural` | BOOLEAN | Predominantly rural flag | Yes | `PENDING_VERIFICATION` | TRUE/FALSE | — |
| `latitude` / `longitude` | TEXT | Mandal HQ coordinates | No | `PENDING_GEOCODING` | — | — |
| `data_source` / `source_url` / `collection_date` / `last_verified_date` / `confidence_score` / `verification_status` / `reviewer` / `version` | — | Provenance columns, per collection-run requirements | Yes | — | — | — |
| `license` | TEXT | License governing the source data for this row | Yes | `PENDING_VERIFICATION` | Must match a recognized license type | — |
| `attribution` | TEXT | Required attribution text, where the license mandates it | No | `PENDING_VERIFICATION` | — | — |
| `created_by` / `created_at` / `updated_at` / `is_active` | — | Standard system columns | Yes | — | — | — |

**Note:** `license` and `attribution` are new columns added at this stage (not present in the original CSV Schema Reference) to satisfy this collection run's explicit per-row requirement. Recommend back-porting these two columns to `state.csv`/`district.csv` in a follow-up schema-alignment pass so all three Geography Foundation datasets are structurally consistent.
