# Data Dictionary — universities_telangana_andhra_pradesh (v1.0.0-RC2)

Records: 66

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
| vice_chancellor | string | Filled for 49/66 rows as of RC2 where a clearly-dated appointment source was found; remainder PENDING_VERIFICATION |
| ownership | enum | Added in RC2. Populated for all 66 rows — determinable from existing type/governance facts. Allowed values: State Government, Central Government, Private Trust/Society, Government-Aided. |
| contact_details | string | Added in RC2. Official phone/email if publicly listed; populated for 5 flagship rows only as of RC2, PENDING_VERIFICATION elsewhere. |
| student_services_summary | string | Added in RC2. Brief factual note on hostel/library/sports-complex presence; populated for 5 flagship rows only as of RC2, PENDING_VERIFICATION elsewhere. |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
