# Data Dictionary — digital_technology_livelihoods (v1.0.0-RC1)

Records: 12

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| name | string |  |
| category | enum | Allowed values: Technology. |
| sub_category | string | e.g. Web Development, Digital Marketing Agency |
| description | string |  |
| target_customers | string |  |
| typical_investment_range_summary | string | PENDING_VERIFICATION for all rows in this dataset -- no credible government/NASSCOM costing source with a specific figure was found; see notes for the qualitative context each row's researcher found |
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
