# Data Dictionary — government_hospitals_telangana_andhra_pradesh (v1.0.0-RC2)

Records: 55

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| name | string |  |
| category | enum | Allowed values: District Hospital, Area Hospital, Teaching Hospital. |
| ownership | string | All rows are State Government by scope |
| managing_organization | string |  |
| district | string |  |
| state | enum | Allowed values: Telangana, Andhra Pradesh. |
| city | string |  |
| address | string | PENDING_VERIFICATION for many rows |
| official_website | string |  |
| contact_number | string | PENDING_VERIFICATION for many rows |
| email | string | Added in RC2. Official hospital email if publicly listed, else PENDING_VERIFICATION |
| bed_capacity | string | PENDING_VERIFICATION where sources conflicted or none found; ranges recorded in notes where sources disagreed |
| medical_college_affiliation | string | Free-text cross-reference; not an enforced FK into medical_colleges_telangana_andhra_pradesh |
| teaching_status | enum | Allowed values: Teaching, Non-Teaching. |
| specialties_summary | string | Added in RC2. Brief factual list of medical specialties/departments, else PENDING_VERIFICATION |
| available_services_summary | string | Added in RC2. Brief factual note on key services, else PENDING_VERIFICATION |
| government_scheme_coverage_summary | string | Added in RC2. Which government health insurance schemes this hospital accepts, else PENDING_VERIFICATION |
| emergency_services | string | "Yes" only where a specific confirming source was found, else PENDING_VERIFICATION |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
