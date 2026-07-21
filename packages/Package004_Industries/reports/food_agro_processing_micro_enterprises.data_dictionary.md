# Data Dictionary — food_agro_processing_micro_enterprises (v1.0.0-RC1)

Records: 13

| Column | Type | Description |
|---|---|---|
| id | uuid | Unique row identifier (UUIDv4) |
| name | string | Livelihood/business-type name |
| category | enum | Allowed values: Manufacturing, Agriculture & Allied. |
| sub_category | string | e.g. Spice Processing, Pickle Making |
| description | string |  |
| target_customers | string |  |
| typical_investment_range_summary | string | PENDING_VERIFICATION unless traced to a specific government DIC/MSME/PMFME/KVIC project profile; portal-only estimates are described qualitatively in this field with a capped confidence score rather than presented as a solid figure |
| skill_level | enum | Allowed values: Unskilled, Semi-skilled, Skilled, Professional/Technical. |
| training_availability_summary | string |  |
| licenses_required_summary | string |  |
| government_schemes_summary | string |  |
| rural_urban_suitability | enum | Allowed values: Rural, Urban, Both. |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
