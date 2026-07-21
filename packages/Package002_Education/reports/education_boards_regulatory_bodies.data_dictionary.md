# Data Dictionary — education_boards_regulatory_bodies (v1.0.0-RC2)

Records: 21

| Column | Type | Description |
|---|---|---|
| id | uuid | Unique row identifier (UUIDv4) |
| name | string | Official name of the board/regulatory body |
| type | string | Category, e.g. Central Regulatory Body, State Board - Secondary, Accreditation Body |
| jurisdiction | enum | Scope of authority Allowed values: National, Telangana, Andhra Pradesh. |
| parent_ministry_or_department | string | Governing ministry/department, if applicable |
| established_year | string | Year established (or PENDING_VERIFICATION) |
| official_website | string | Official website URL |
| headquarters_city | string |  |
| headquarters_state | string |  |
| mandate_summary | string | Brief factual description of the body's mandate |
| data_source | string | Human-readable source label |
| source_url | string | URL of the specific source used |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
