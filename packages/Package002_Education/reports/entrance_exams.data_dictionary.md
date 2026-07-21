# Data Dictionary — entrance_exams (v1.0.0-RC2)

Records: 29

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| exam_name | string |  |
| exam_level | enum | Allowed values: Undergraduate, Postgraduate, Diploma/Polytechnic, Doctoral/Fellowship. |
| jurisdiction | enum | Allowed values: National, Telangana, Andhra Pradesh. |
| conducting_body | string |  |
| frequency_per_year | string |  |
| purpose | string |  |
| official_website | string |  |
| eligibility_summary | string |  |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
