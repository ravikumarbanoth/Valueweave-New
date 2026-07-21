# Data Dictionary — universities_telangana_andhra_pradesh

Records: 61

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| name | string |  |
| university_type | enum | Allowed values: State University, Central University, Deemed University, Institute of National Importance, Private University. |
| state | enum | Allowed values: Telangana, Andhra Pradesh. |
| district | string |  |
| city | string |  |
| affiliation | string |  |
| established_year | string |  |
| official_website | string |  |
| naac_grade | string | NAAC accreditation grade, or PENDING_VERIFICATION |
| nirf_rank | string | NIRF rank/band, or PENDING_VERIFICATION |
| courses_offered_summary | string |  |
| vice_chancellor | string | Left PENDING_VERIFICATION package-wide due to appointment volatility |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
