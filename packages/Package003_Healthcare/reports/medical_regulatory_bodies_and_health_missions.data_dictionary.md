# Data Dictionary — medical_regulatory_bodies_and_health_missions (v1.0.0-RC1)

Records: 23

| Column | Type | Description |
|---|---|---|
| id | uuid | Unique row identifier (UUIDv4) |
| name | string | Official name of the regulatory body/mission |
| type | string | e.g. Central Regulatory Body, State Medical Council, National Health Program, State Health Mission, Standards/Accreditation Body |
| jurisdiction | enum | Allowed values: National, Telangana, Andhra Pradesh. |
| parent_ministry_or_department | string |  |
| established_year | string | Year established, or PENDING_VERIFICATION |
| official_website | string |  |
| headquarters_city | string |  |
| headquarters_state | string |  |
| mandate_summary | string |  |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
