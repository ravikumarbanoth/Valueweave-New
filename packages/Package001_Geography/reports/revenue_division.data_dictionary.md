# Data Dictionary — `revenue_division_telangana.csv` / `revenue_division_andhra_pradesh.csv`

| Column | Type | Description | Mandatory | Example | Validation | Foreign Key |
|---|---|---|---|---|---|---|
| `revenue_division_id` | UUID | Primary key | Yes | — | UUID v4 | — |
| `revenue_division_ref` | TEXT | ValueWeave code: `{STATE}-{DISTRICT_REF}-RD-{SEQ}` | Yes | `TG-MDK-RD-1` | Unique | — |
| `revenue_division_name` | TEXT | Official revenue division name | Yes | Medak | Unique within `dist_ref` | — |
| `district_name` | TEXT | Parent district's official name (denormalized for readability) | Yes | Medak | Must match `district.district_name` | — |
| `dist_ref` | TEXT | Parent district's ValueWeave ref code | Yes | MDK | Must exist in `district.dist_ref` | `district.dist_ref` |
| `state_code` | TEXT | TG or AP | Yes | TG | Must exist in `state.state_code` | `state.state_code` |
| `divisional_headquarters` | TEXT | HQ town of the division | Yes | Medak | Defaults to division name per convention — see Collection Report §5 | — |
| `mandal_count` | INTEGER/TEXT | Number of mandals under this division | No | 8 or `PENDING_VERIFICATION` | ≥ 0 where populated | — |
| `mandal_count_source_detail` | TEXT | Whether/how `mandal_count` was independently verified | Yes | — | — | — |
| `lgd_code` | TEXT | LGD-issued code for this division | No | `PENDING_VERIFICATION` | — | — |
| `latitude` / `longitude` | TEXT | Divisional HQ coordinates | No | `PENDING_GEOCODING` | — | — |
| `data_source` / `source_url` / `collection_date` / `last_verified_date` / `confidence_score` / `verification_status` / `reviewer` / `version` / `license` / `attribution` | — | Provenance columns, per this run's per-row requirement | Yes | — | — | — |
| `created_by` / `created_at` / `updated_at` / `is_active` | — | Standard system columns | Yes | — | — | — |

**Duplicate detection method:** composite uniqueness on (`dist_ref`, `revenue_division_name`) — division names can repeat across different districts nationally, so district-scoped uniqueness is the correct rule (same pattern as Mandal).
