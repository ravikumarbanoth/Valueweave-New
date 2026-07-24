# Data Dictionary — food_agro_processing_micro_enterprises (v1.0.0)

Records: 13

| Column | Type | Description |
|---|---|---|
| id | uuid | Unique row identifier (UUIDv4) |
| name | string | Opportunity/business-type name |
| category | enum | Allowed values: Manufacturing, Agriculture & Allied. |
| sub_category | string | e.g. Spice Processing, Pickle Making |
| description | string |  |
| ideal_target_audience | string | Who realistically starts this opportunity (students/women/rural youth/professionals/etc.) |
| minimum_investment | string | A specific rupee figure ONLY if traceable to a government DIC/MSME/PMFME/KVIC project-profile document; otherwise the bare PENDING_VERIFICATION sentinel |
| investment_range_summary | string |  |
| working_capital_summary | string |  |
| machinery_equipment_summary | string |  |
| raw_materials_summary | string |  |
| supplier_ecosystem_summary | string |  |
| customer_segments_summary | string |  |
| skill_level | enum | Allowed values: Unskilled, Semi-skilled, Skilled, Professional/Technical. |
| training_providers_summary | string |  |
| licenses_required_summary | string |  |
| government_schemes_summary | string |  |
| marketing_channels_summary | string |  |
| online_selling_options_summary | string |  |
| estimated_setup_time_summary | string |  |
| typical_risks_summary | string |  |
| seasonal_factors_summary | string |  |
| ai_tools_summary | string |  |
| automation_opportunities_summary | string |  |
| sustainability_summary | string |  |
| future_demand_summary | string |  |
| related_businesses_summary | string |  |
| district_suitability_summary | string | Telangana/AP districts known for this activity |
| rural_urban_suitability | enum | Allowed values: Rural, Urban, Both. |
| success_stories_summary | string | Named real examples ONLY where independently found via search; PENDING_VERIFICATION otherwise |
| data_source | string |  |
| source_url | string |  |
| collection_date | date |  |
| confidence_score | integer |  |
| verification_status | enum | Allowed values: VST-NEEDS_REVIEW, VST-VERIFIED. |
| notes | string |  |
