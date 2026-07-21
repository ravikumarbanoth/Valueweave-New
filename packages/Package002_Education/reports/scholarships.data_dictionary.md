# Data Dictionary — scholarships (v1.0.0)

Records: 25

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| scheme_name | string | Current official scheme name at collection time; superseded names cross-referenced in notes |
| scheme_type | enum | Allowed values: Central Scheme, State Scheme. |
| jurisdiction | enum | Allowed values: National, Telangana, Andhra Pradesh. |
| administering_body | string |  |
| target_beneficiaries | string |  |
| eligibility_summary | string |  |
| funding_benefit_summary | string |  |
| application_portal | string |  |
| official_website | string |  |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
