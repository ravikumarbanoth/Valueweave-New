# Data Dictionary — msme_entrepreneurship_support_schemes (v1.0.0-RC1)

Records: 18

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| name | string | Current official name; superseded names (e.g. TS-iPASS, TSIIC) cross-referenced in notes |
| type | enum | Allowed values: Central Scheme, State Scheme, Support Body/Corporation, Incubator/Skill Body. |
| jurisdiction | enum | Allowed values: National, Telangana, Andhra Pradesh. |
| administering_body | string |  |
| target_beneficiaries | string |  |
| support_offered_summary | string |  |
| eligibility_summary | string |  |
| official_website | string |  |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
