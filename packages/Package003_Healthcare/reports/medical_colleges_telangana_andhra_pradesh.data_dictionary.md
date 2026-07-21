# Data Dictionary — medical_colleges_telangana_andhra_pradesh (v1.0.0)

Records: 58

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| name | string |  |
| ownership | enum | 3 rows carry a qualified label (ESIC-central, AIIMS-autonomous, deemed-university-private) noted in `notes` rather than forced into a plain binary Allowed values: Government, Private. |
| affiliation | string | Health sciences university affiliation |
| established_year | string |  |
| district | string |  |
| state | enum | Allowed values: Telangana, Andhra Pradesh. |
| city | string |  |
| official_website | string |  |
| email | string | Added in RC2. Official college/admissions email if publicly listed, else PENDING_VERIFICATION |
| mbbs_seats | string | Annual MBBS intake if verifiable, else PENDING_VERIFICATION |
| attached_teaching_hospital | string | Free-text cross-reference; not an enforced FK into government_hospitals_telangana_andhra_pradesh |
| departments_summary | string | Added in RC2. Brief factual list of major clinical departments/specialties, else PENDING_VERIFICATION |
| government_scheme_coverage_summary | string | Added in RC2. Whether the attached teaching hospital accepts government health schemes, else PENDING_VERIFICATION |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
