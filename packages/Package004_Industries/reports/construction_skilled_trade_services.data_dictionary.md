# Data Dictionary — construction_skilled_trade_services (v1.0.0-RC1)

Records: 11

| Column | Type | Description |
|---|---|---|
| id | uuid |  |
| name | string |  |
| category | enum | Allowed values: Construction & Skilled Trades. |
| sub_category | string | e.g. Plumbing, Electrical Services |
| description | string |  |
| target_customers | string |  |
| typical_investment_range_summary | string | Descriptive qualitative summary where no authoritative cost figure exists; PM Vishwakarma Yojana's Rs 15,000 toolkit figure is cited only for the 2 of 9 trades it actually covers (Carpenter), verified rather than assumed |
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
