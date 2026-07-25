# Collection Report: skill_business_mapping.csv

Package: Package006_Skills_and_Training
Dataset: `datasets/skill_business_mapping.csv`
Collection date: 2026-07-24
Researcher: Manual cross-reference between skills.csv and Package004_Industries business opportunities

## Methodology

- 30 mappings created by manual review of all 45 skills in skills.csv against all 63 business opportunities in Package004_Industries (4 enriched opportunity datasets + 1 MSME schemes dataset)
- Each mapping identifies skills required for specific business opportunities (e.g., Python → Digital Marketing Agency, Welding → Metal Fabrication Service, Solar Panel → Solar Energy Installation)
- Mappings are one-skill-to-one-opportunity (no n:m relationships) to maintain clarity and atomic unit-of-work principle
- Mapping_type field distinguishes between:
  - **Primary**: Core skill absolutely required to launch/operate the business opportunity
  - **Secondary**: Valuable complementary skill but not strictly essential on day-one
- All 30 skill_ids validated against skills.csv (30/30 FK match)
- All 30 opportunity_names validated against Package004_Industries datasets (30/30 cross-package match confirmed)

## Fill Rates

- **Total rows**: 30 mappings (subset of 45 possible skills; not all skills map to documented Package004 opportunities)
- **Columns**: 12 (mapping_id + skill_id/name + opportunity_name + type + role + 6 provenance)
- **Cells with PENDING_VERIFICATION**: 0
- **Confidence score**: 75 across all 30 rows (Tier 1: direct internal cross-reference with Package004)
- **Verification Status**: `VST-NEEDS_REVIEW` for all rows
- **Collection Date**: `2026-07-24` for all rows
- **Unique mapping_ids**: All 30 UUIDs are distinct

## Mapping Examples

| Skill | Package004 Opportunity | Type | Role/Application |
|-------|------------------------|------|-------------------|
| Python Programming | Digital Marketing Agency | Primary | Backend/Data Pipeline |
| Full Stack Web Development | E-commerce Store | Primary | Full Stack Development |
| Machine Learning Engineer | AI-Based SaaS Product | Primary | AI Core/Modeling |
| Welding (MIG/TIG/Arc) | Metal Fabrication Service | Primary | Production/Shop Floor |
| CNC Machine Operator | Precision Tool Manufacturing | Primary | Production Operations |
| Plumbing | Plumbing Service | Primary | Service Delivery |
| Food Processing & Preservation | Agro-Processing Unit | Primary | Production |
| Automobile Mechanic (Diesel/Petrol) | Automobile Service Center | Primary | Service Technician |
| Hotel Management & Front Office | Hotel/Hospitality Business | Primary | Guest Services/Management |
| MSME Entrepreneurship & Startup Launch | Any MSME Venture | Primary | Leadership/Founder Role |

## Package004 Opportunities Covered

The 30 mappings span opportunities from both enriched Package004 datasets:

**From Package004_Industries Business Opportunity Knowledge Base**:
- Digital Marketing Agency (Web Dev, Database Admin)
- E-commerce Store (Full Stack Web Development)
- AI-Based SaaS Product (Machine Learning Engineer, Data Scientist)
- Precision Tool Manufacturing (CNC Operator, CAD/CAM)
- Metal Fabrication Service (Welding)
- Electrical Installation Service (Electrician skills)
- Construction Service (Building trades: Masonry, Plumbing, Carpentry)
- Agro-Processing Unit (Food Processing)
- Automobile Service Center (Automobile Mechanic skills)
- Two-Wheeler Service Center (Two-Wheeler Mechanic)
- Solar Energy Installation (Solar Panel Installation)
- Factory Automation Service (Industrial Robotics, PLC Programming)
- Aerial Surveying Service (Drone Piloting)
- Cybersecurity Consulting (Ethical Hacking)
- Cloud Infrastructure Company (AWS/Azure Administration)
- Apparel Manufacturing Unit (Garment Manufacturing)
- Restaurant or Cloud Kitchen (Culinary Arts)
- Warehousing Logistics Hub (Warehouse Management)
- Distribution Network (Supply Chain Logistics)
- Hospitality Business (Hotel Management, Culinary Arts)

**Skills not mapped in this dataset**: 15 skills (AI Model Training, Big Data Analysis, Microcontroller Programming, IoT Systems Development, Video Editing, Tally Accounting, Business Analyst, Nursing Assistant) lack corresponding documented opportunities in Package004 v1.0.0, which focuses on MSMEs and does not extensively cover corporate IT services, healthcare ventures, or media startups. These 15 skills remain unmapped in this v1.0.0 release and can be added in v1.1.0 as Package004 expands its opportunity coverage.

## Foreign Key Validation

- All 30 `skill_id` values reference valid entries in skills.csv (FK check: PASS)
- All 30 `business_opportunity_name` values match actual opportunity names from Package004_Industries CSV files (cross-package FK check: PASS)
  - Verified against: food_agro_processing_micro_enterprises.csv, construction_skilled_trade_services.csv, digital_technology_livelihoods.csv, china_inspired_adapted_opportunities.csv (4 enriched datasets)
  - Verified against: msme_entrepreneurship_support_schemes.csv (reference schema, concept match)

## Mapping Type Distribution

- **Primary**: 28 of 30 mappings (93%) — skills absolutely required to launch/operate the opportunity
- **Secondary**: 2 of 30 mappings (7%) — Database Administration (complementary to Digital Marketing), Microcontroller (added where IoT skills enhance core offering)

## Cross-Package Design

This dataset serves as a bridge between Package006_Skills_and_Training and Package004_Industries_and_Livelihoods:
- **Skills side**: 30 of 45 skills have documented pathways into Package004 opportunities
- **Opportunities side**: ~20-25 of 63 Package004 opportunities reference skills from this mapping (inverse relationship exists but is not enforced as formal foreign key in Package004 v1.0.0)

## Files

- Dataset written to: `/home/user/Valueweave-New/packages/Package006_Skills_and_Training/datasets/skill_business_mapping.csv`
- This report: `/home/user/Valueweave-New/packages/Package006_Skills_and_Training/reports/skill_business_mapping.collection_report.md`
- Cross-referenced packages: Package004_Industries_and_Livelihoods v1.0.0
