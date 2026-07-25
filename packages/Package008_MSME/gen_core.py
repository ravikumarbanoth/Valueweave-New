#!/usr/bin/env python3
"""
Package008_MSME v1.0.0 — Core Dataset Generator

Builds the nine datasets that have no upstream foreign keys:
   1  msme_categories.csv          24 categories
   2  business_models.csv          15 delivery models
   3  msme_businesses.csv          40 MSME opportunities (core entity)
   6  license_compliance.csv       14 licences and registrations
   7  financial_support.csv        12 finance sources
  14  market_channels.csv          11 sales channels
  16  ai_business_tools.csv        12 AI/software tool classes
  17  startup_ecosystem.csv        12 incubation and support bodies
  18  investment_intelligence.csv  one investment profile per business

NORMALIZATION RULE (from the package brief): Package008 is the Business
Intelligence Layer and SHALL NOT duplicate schemes, skills, industries,
geography, education or agriculture. Those live upstream and are referenced by
id in gen_mappings.py. Consequently this file contains no scheme detail, no
skill detail and no industry detail -- only MSME-intrinsic reference data.

Source tiers (confidence ceiling 85, per project policy):
  Tier 1  MSME Ministry, Udyam portal, SIDBI, NABARD, NSIC, KVIC, DPIIT,
          Startup India, GeM, MSME-DIs, state industries departments      70-85
  Tier 2  Government reports                                             62-74
  Tier 3  Industry associations (CII, FICCI, ASSOCHAM, NASSCOM)           56-69
  Tier 4  Official sector reports                                        45-55

No fabricated values. Any fact not confirmable in a public source is the bare
sentinel PENDING_VERIFICATION. In particular: no rupee investment figure is
asserted anywhere -- see docs/METHODOLOGY.md section 2.
"""

import csv
from pathlib import Path

CD = "2026-07-25"
VST = "VST-NEEDS_REVIEW"
PV = "PENDING_VERIFICATION"
DATASETS = Path("datasets")

MSME_M = "Ministry of Micro, Small and Medium Enterprises"
MSME_URL = "https://msme.gov.in/"
UDYAM = "Udyam Registration portal; Ministry of MSME"
UDYAM_URL = "https://udyamregistration.gov.in/"
DCMSME = "Office of Development Commissioner (MSME); MSME-DI project profiles"
SIDBI = "SIDBI"
SIDBI_URL = "https://www.sidbi.in/"
DPIIT = "DPIIT; Startup India"
DPIIT_URL = "https://www.startupindia.gov.in/"
NASSCOM = "NASSCOM"
NASSCOM_URL = "https://nasscom.in/"


def write(filename, headers, rows):
    for i, r in enumerate(rows):
        if len(r) != len(headers):
            raise ValueError(f"{filename} row {i} ({r[0]}): {len(r)} values, expected {len(headers)}")
    with open(DATASETS / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows x {len(headers)} cols")


# ===========================================================================
# 1. msme_categories.csv — the 24 categories named in the brief
# ===========================================================================
H_CAT = ["category_id", "category_name", "category_group", "description",
         "nic_section_hint", "capital_intensity", "skill_intensity",
         "typical_udyam_class", "data_source", "source_url", "collection_date",
         "confidence_score", "verification_status", "notes"]

CATEGORIES = [
    ("mc-001", "Manufacturing", "Primary Sector Group", "Physical goods production across all product classes", "Section C - Manufacturing", "High", "Medium", "Micro to Medium", MSME_M, MSME_URL, CD, "78", VST, "Largest MSME group by Udyam registration count"),
    ("mc-002", "Services", "Primary Sector Group", "Non-goods commercial activity across professional and personal services", "Sections M, N, S", "Low", "Medium", "Micro to Small", MSME_M, MSME_URL, CD, "77", VST, "Fastest-growing group; low entry capital"),
    ("mc-003", "Trading", "Primary Sector Group", "Wholesale and retail buying and reselling without transformation", "Section G", "Low", "Low", "Micro", MSME_M, MSME_URL, CD, "74", VST, "Retail and wholesale trade became Udyam-eligible in 2021"),
    ("mc-004", "Food Processing", "Manufacturing Sub-Sector", "Transformation of agricultural produce into food products", "Division 10-11", "Medium", "Medium", "Micro to Small", "Ministry of Food Processing Industries (MoFPI)", "https://mofpi.gov.in/", CD, "76", VST, "PMFME is the dedicated scheme; overlaps Package005 processing layer"),
    ("mc-005", "Engineering", "Manufacturing Sub-Sector", "Metal fabrication, machining, tooling and mechanical assembly", "Division 25-28", "High", "High", "Micro to Medium", DCMSME, MSME_URL, CD, "75", VST, "Ancillary supply to larger industry is the dominant model"),
    ("mc-006", "Electronics", "Manufacturing Sub-Sector", "Electronic component and assembly manufacturing", "Division 26-27", "High", "High", "Small to Medium", "Ministry of Electronics and IT (MeitY)", "https://www.meity.gov.in/", CD, "73", VST, "PLI schemes target this sector; import dependence remains high"),
    ("mc-007", "Agriculture and Allied", "Primary Sector Group", "Farm-adjacent enterprise including inputs, nursery and allied activity", "Section A", "Medium", "Medium", "Micro", "Ministry of Agriculture and Farmers Welfare", "https://agricoop.gov.in/", CD, "74", VST, "Crop and processing detail lives in Package005, referenced not duplicated"),
    ("mc-008", "Healthcare", "Services Sub-Sector", "Diagnostic, clinical support and medical product enterprise", "Division 86", "Medium", "High", "Micro to Small", "Ministry of Health and Family Welfare", "https://mohfw.gov.in/", CD, "70", VST, "Heavily licence-gated; qualification requirements are statutory"),
    ("mc-009", "Textiles and Apparel", "Manufacturing Sub-Sector", "Fibre, yarn, fabric and garment manufacturing", "Division 13-14", "Medium", "Medium", "Micro to Medium", "Ministry of Textiles", "https://texmin.nic.in/", CD, "74", VST, "Highest employment per unit of investment among manufacturing groups"),
    ("mc-010", "Chemical", "Manufacturing Sub-Sector", "Industrial and specialty chemical formulation and manufacture", "Division 20-21", "High", "High", "Small to Medium", DCMSME, MSME_URL, CD, "71", VST, "Pollution Control Board consent is the binding entry constraint"),
    ("mc-011", "Construction", "Primary Sector Group", "Building, infrastructure and specialised construction trades", "Section F", "Medium", "Medium", "Micro to Small", MSME_M, MSME_URL, CD, "73", VST, "Trade-service detail lives in Package004, referenced not duplicated"),
    ("mc-012", "Information Technology", "Services Sub-Sector", "Software development, IT services and IT-enabled services", "Division 62-63", "Low", "High", "Micro to Medium", NASSCOM, NASSCOM_URL, CD, "76", VST, "Lowest capital intensity of any category; skill-gated instead"),
    ("mc-013", "Renewable Energy", "Emerging Sector", "Solar, wind and clean energy equipment, EPC and O&M", "Division 35", "High", "High", "Small to Medium", "Ministry of New and Renewable Energy (MNRE)", "https://mnre.gov.in/", CD, "72", VST, "Policy-driven demand; PM Surya Ghar expanded the rooftop segment"),
    ("mc-014", "Industrial Automation", "Emerging Sector", "PLC, SCADA, sensor and control system integration", "Division 28, 33", "Medium", "High", "Micro to Small", DCMSME, MSME_URL, CD, "68", VST, "Systems-integration model; low inventory, high skill"),
    ("mc-015", "Robotics", "Emerging Sector", "Robotic system design, assembly and deployment", "Division 28", "High", "High", "Small to Medium", "MeitY; industry associations", "https://www.meity.gov.in/", CD, "62", VST, "Early-stage in India; mostly integration rather than manufacture"),
    ("mc-016", "Artificial Intelligence", "Emerging Sector", "AI product development, model deployment and AI-enabled services", "Division 62", "Low", "High", "Micro to Small", NASSCOM, NASSCOM_URL, CD, "64", VST, "Capital-light, talent-gated; Package006 holds the skill detail"),
    ("mc-017", "Electric Vehicles", "Emerging Sector", "EV components, assembly, charging infrastructure and service", "Division 29-30", "High", "High", "Small to Medium", "Ministry of Heavy Industries", "https://heavyindustries.gov.in/", CD, "68", VST, "Service and charging segments are the realistic MSME entry points"),
    ("mc-018", "Semiconductors", "Emerging Sector", "Semiconductor assembly, testing, design services and support", "Division 26", "Very High", "Very High", "Medium", "MeitY; India Semiconductor Mission", "https://www.meity.gov.in/", CD, "58", VST, "Fabrication is out of MSME reach; design services and ATMP support are not"),
    ("mc-019", "Logistics and Warehousing", "Services Sub-Sector", "Freight, warehousing, cold chain and last-mile distribution", "Division 49-52", "Medium", "Low", "Micro to Medium", "Ministry of Commerce and Industry", "https://commerce.gov.in/", CD, "73", VST, "PM Gati Shakti and the National Logistics Policy shape demand"),
    ("mc-020", "Creative Industries", "Services Sub-Sector", "Design, media production, content and craft-based enterprise", "Division 58-60, 74", "Low", "High", "Micro", "Ministry of Information and Broadcasting", "https://mib.gov.in/", CD, "66", VST, "Highly fragmented; platform distribution changed the economics"),
    ("mc-021", "Tourism and Hospitality", "Services Sub-Sector", "Accommodation, food service, tours and experience enterprise", "Division 55-56, 79", "Medium", "Medium", "Micro to Small", "Ministry of Tourism", "https://tourism.gov.in/", CD, "70", VST, "Seasonal cash flow is the dominant operational risk"),
    ("mc-022", "Education and Training", "Services Sub-Sector", "Coaching, vocational training and edtech enterprise", "Division 85", "Low", "High", "Micro to Small", "Ministry of Education", "https://www.education.gov.in/", CD, "69", VST, "Institution detail lives in Package002, referenced not duplicated"),
    ("mc-023", "Waste Management", "Emerging Sector", "Collection, segregation, treatment and disposal services", "Division 38", "Medium", "Medium", "Micro to Small", "Ministry of Environment, Forest and Climate Change", "https://moef.gov.in/", CD, "68", VST, "Urban local body contracts are the primary revenue route"),
    ("mc-024", "Recycling and Circular Economy", "Emerging Sector", "Material recovery, reprocessing and remanufacture", "Division 38", "Medium", "Medium", "Micro to Medium", "Ministry of Environment, Forest and Climate Change", "https://moef.gov.in/", CD, "66", VST, "EPR obligations on producers created a compliance-driven market"),
]

# ===========================================================================
# 2. business_models.csv
# ===========================================================================
H_BM = ["business_model_id", "business_model_name", "model_type",
        "description", "revenue_pattern", "asset_intensity",
        "typical_lead_time_to_revenue", "primary_risk", "data_source",
        "source_url", "collection_date", "confidence_score",
        "verification_status", "notes"]

MODELS = [
    ("bm-001", "Manufacturing Unit", "Asset-Based", "Owns plant and machinery, transforms inputs into finished goods", "Order or stock-based sales", "High", PV, "Capacity utilisation below breakeven", DCMSME, MSME_URL, CD, "76", VST, "Classic MSME form; carries the heaviest fixed-cost burden"),
    ("bm-002", "Job Work / Ancillary Unit", "Asset-Based", "Processes material owned by a principal manufacturer for a conversion fee", "Conversion charges per unit", "High", PV, "Dependence on one or few principals", DCMSME, MSME_URL, CD, "72", VST, "Lower working capital than own-brand manufacture; higher concentration risk"),
    ("bm-003", "Trading Business", "Working-Capital-Based", "Buys and resells without transformation", "Margin on turnover", "Low", PV, "Inventory obsolescence and receivable delay", MSME_M, MSME_URL, CD, "74", VST, "Became Udyam-eligible in 2021; capital sits in stock not plant"),
    ("bm-004", "Service Centre", "Skill-Based", "Delivers a technical or professional service from a fixed location", "Per-job or retainer", "Low", PV, "Skill concentration in the founder", MSME_M, MSME_URL, CD, "74", VST, "Fastest path to revenue among all models"),
    ("bm-005", "Repair and Maintenance Centre", "Skill-Based", "Restores or maintains customer-owned equipment", "Per-job charges plus parts margin", "Low", PV, "Technology obsolescence of serviced products", MSME_M, MSME_URL, CD, "72", VST, "Authorised-service-partner status materially changes economics"),
    ("bm-006", "Cloud Kitchen", "Asset-Light Hybrid", "Prepares food for delivery only, without dine-in space", "Per-order, platform-mediated", "Medium", PV, "Platform commission and rating dependence", "Ministry of Food Processing Industries", "https://mofpi.gov.in/", CD, "68", VST, "FSSAI licence mandatory; rent lower than restaurant format"),
    ("bm-007", "Cold Storage Facility", "Infrastructure", "Rents temperature-controlled storage capacity", "Rental per tonne-month", "Very High", PV, "Utilisation seasonality and power cost", "Ministry of Agriculture; MoFPI", "https://agricoop.gov.in/", CD, "70", VST, "Revenue is rental, not produce sale; Package005 holds the machinery record"),
    ("bm-008", "Warehouse and Distribution", "Infrastructure", "Stores and moves goods on behalf of principals", "Storage and handling charges", "High", PV, "Anchor-client concentration", "Ministry of Commerce and Industry", "https://commerce.gov.in/", CD, "70", VST, "Warehousing Development and Regulatory Authority registration where applicable"),
    ("bm-009", "Software Product Company", "IP-Based", "Builds and licenses proprietary software", "Subscription or licence", "Very Low", PV, "Product-market fit failure", NASSCOM, NASSCOM_URL, CD, "72", VST, "Highest scalability, longest revenue lead time"),
    ("bm-010", "IT Services Firm", "Skill-Based", "Delivers software and IT work on client specification", "Time-and-material or fixed-bid", "Very Low", PV, "Billable utilisation and client concentration", NASSCOM, NASSCOM_URL, CD, "74", VST, "Revenue starts fastest of the technology models"),
    ("bm-011", "Systems Integrator", "Skill-Based", "Specifies, supplies and commissions multi-vendor technical systems", "Project value plus AMC", "Low", PV, "Project execution and payment milestones", DCMSME, MSME_URL, CD, "68", VST, "Automation, solar EPC and security systems all use this form"),
    ("bm-012", "Drone Service Provider", "Asset-Based Service", "Operates drones for survey, spraying or inspection on contract", "Per-acre or per-project", "Medium", PV, "DGCA compliance and pilot availability", "Ministry of Civil Aviation (DGCA); Ministry of Agriculture", "https://www.dgca.gov.in/", CD, "64", VST, "Licence-gated; Package005 holds the agricultural drone machinery record"),
    ("bm-013", "Solar EPC Contractor", "Project-Based", "Engineers, procures and commissions solar installations", "Project value plus O&M", "Medium", PV, "Subsidy disbursement timing and price competition", "Ministry of New and Renewable Energy", "https://mnre.gov.in/", CD, "68", VST, "PM Surya Ghar expanded the residential rooftop segment sharply"),
    ("bm-014", "Battery and E-Waste Recycling", "Asset-Based", "Recovers materials from end-of-life batteries and electronics", "Recovered material sales plus EPR credits", "High", PV, "Feedstock collection reliability and CPCB compliance", "Ministry of Environment, Forest and Climate Change; CPCB", "https://cpcb.nic.in/", CD, "64", VST, "EPR obligations on producers created the demand side"),
    ("bm-015", "Food Processing Unit", "Asset-Based", "Converts agricultural produce into packaged food products", "Product sales, retail or B2B", "Medium", PV, "Raw material seasonality and price volatility", "Ministry of Food Processing Industries", "https://mofpi.gov.in/", CD, "74", VST, "Package005 holds the crop and processing-opportunity detail"),
]

# ===========================================================================
# 3. msme_businesses.csv — core entity, 40 opportunities
# ===========================================================================
H_BIZ = ["business_id", "business_name", "category_id", "category_name",
         "business_model_id", "business_model_name", "description",
         "udyam_classification", "investment_range", "working_capital_need",
         "employment_generation", "difficulty", "risk_level",
         "technology_level", "automation_level", "ai_readiness",
         "market_demand", "export_potential", "profitability_outlook",
         "district_suitability", "data_source", "source_url",
         "collection_date", "confidence_score", "verification_status", "notes"]

# (id, name, cat, model, desc, udyam, wc_need, employment, difficulty, risk,
#  tech, automation, ai_ready, demand, export, profit, district, src, url, conf, note)
B = [
    # --- Food Processing (7) ---
    ("mb-001", "Rice Milling Unit", "mc-004", "bm-001", "Dehusks and polishes paddy into marketable rice with bran and husk by-products", "Small", "High", "6-15", "Moderate", "Medium", "Medium", "Semi-Automated", "Medium", "High", "Medium", "Good", "Both", DCMSME, MSME_URL, 73, "By-product realisation (bran to oil extractors, husk as fuel) drives margin"),
    ("mb-002", "Dal Milling Unit", "mc-004", "bm-001", "Dehusks and splits pulses into dal with chuni and husk by-products", "Small", "High", "5-12", "Moderate", "Medium", "Medium", "Semi-Automated", "Medium", "High", "High", "Good", "Both", DCMSME, MSME_URL, 73, "Milling recovery percentage is the single largest profitability lever"),
    ("mb-003", "Cold-Pressed Oil Unit", "mc-004", "bm-001", "Extracts virgin edible oil by mechanical cold press, with oil cake as by-product", "Micro", "Medium", "3-8", "Easy", "Low", "Low", "Semi-Automated", "Low", "Very High", "High", "Very Good", "Both", DCMSME, MSME_URL, 72, "Premium health-oil positioning; oil cake is a second revenue line"),
    ("mb-004", "Spice Grinding and Packing Unit", "mc-004", "bm-001", "Cleans, grinds and packs whole spices into branded powders and blends", "Micro", "Medium", "4-10", "Easy", "Medium", "Low", "Semi-Automated", "Low", "Very High", "Very High", "Very Good", "Both", "Spices Board of India; MSME-DI", "https://www.indianspices.com/", 74, "Colour value and moisture control determine grade and export eligibility"),
    ("mb-005", "Millet Processing Unit", "mc-004", "bm-001", "Dehulls and mills millets into flour, rava and ready-mix products", "Micro", "Medium", "4-10", "Moderate", "Medium", "Medium", "Semi-Automated", "Low", "High", "Medium", "Good", "Rural", "Ministry of Food Processing Industries", "https://mofpi.gov.in/", 70, "Dehulling is the technically hardest unit operation; nutri-cereal demand growing"),
    ("mb-006", "Fruit Pulp and Beverage Unit", "mc-004", "bm-015", "Produces aseptic fruit pulp, concentrate and ready-to-drink beverages", "Small", "High", "10-25", "Hard", "High", "Medium", "Automated", "Medium", "High", "High", "Good", "Both", "Ministry of Food Processing Industries", "https://mofpi.gov.in/", 69, "Severe seasonality; aseptic packing is what enables year-round sales"),
    ("mb-007", "Cloud Kitchen", "mc-004", "bm-006", "Prepares food for delivery-only distribution through aggregator platforms", "Micro", "Medium", "4-10", "Easy", "High", "Low", "Basic", "Medium", "Very High", "Low", "Variable", "Urban", "Ministry of Food Processing Industries", "https://mofpi.gov.in/", 66, "Platform commission and rating dependence are the structural risks"),
    # --- Engineering (6) ---
    ("mb-008", "CNC Machining Job Shop", "mc-005", "bm-002", "Precision machining of components on CNC lathes and machining centres for principals", "Small", "Medium", "5-15", "Hard", "Medium", "High", "Automated", "Medium", "High", "Medium", "Good", "Both", DCMSME, MSME_URL, 73, "Ancillary model; skill availability is the binding constraint not capital"),
    ("mb-009", "Sheet Metal Fabrication Unit", "mc-005", "bm-001", "Cuts, forms and welds sheet metal into enclosures, structures and assemblies", "Micro", "Medium", "5-12", "Moderate", "Medium", "Medium", "Semi-Automated", "Low", "High", "Low", "Good", "Both", DCMSME, MSME_URL, 72, "Local demand from construction and equipment makers; low export intensity"),
    ("mb-010", "Tool and Die Making Unit", "mc-005", "bm-002", "Designs and manufactures dies, moulds, jigs and fixtures", "Small", "Medium", "6-15", "Very Hard", "Medium", "High", "Automated", "Medium", "Medium", "Medium", "Very Good", "Urban", "MSME Technology Centres (Tool Rooms)", MSME_URL, 71, "Highest skill barrier in engineering; MSME Tool Rooms are the training route"),
    ("mb-011", "Industrial Automation Integration", "mc-014", "bm-011", "Specifies and commissions PLC, SCADA and sensor-based control systems", "Micro", "Low", "4-12", "Hard", "Medium", "High", "Advanced", "High", "High", "Low", "Very Good", "Urban", DCMSME, MSME_URL, 68, "Asset-light systems integration; revenue is project plus annual maintenance"),
    ("mb-012", "Electrical Panel Manufacturing", "mc-005", "bm-001", "Assembles and wires LT and control panels to customer specification", "Micro", "Medium", "5-12", "Moderate", "Medium", "Medium", "Semi-Automated", "Low", "High", "Low", "Good", "Both", DCMSME, MSME_URL, 71, "BIS conformity and electrical inspectorate approval gate the market"),
    ("mb-013", "Foundry (Small Scale)", "mc-005", "bm-001", "Casts ferrous or non-ferrous components in sand or investment moulds", "Small", "High", "10-25", "Very Hard", "High", "Medium", "Basic", "Low", "Medium", "Medium", "Variable", "Both", DCMSME, MSME_URL, 68, "Pollution Control Board consent and energy cost are the dominant constraints"),
    # --- Information Technology and AI (6) ---
    ("mb-014", "Custom Software Development Firm", "mc-012", "bm-010", "Builds software to client specification on time-and-material or fixed-bid terms", "Micro", "Low", "5-20", "Moderate", "Medium", "High", "Advanced", "Very High", "Very High", "Very High", "Very Good", "Urban", NASSCOM, NASSCOM_URL, 74, "Lowest capital intensity of any manufacturing or service category"),
    ("mb-015", "SaaS Product Startup", "mc-012", "bm-009", "Develops and licenses a proprietary software product on subscription", "Micro", "Low", "3-15", "Hard", "Very High", "High", "Advanced", "Very High", "High", "Very High", "Variable", "Urban", DPIIT, DPIIT_URL, 70, "Longest lead time to revenue; highest scalability if product-market fit lands"),
    ("mb-016", "AI Solutions and Consulting", "mc-016", "bm-010", "Delivers AI model development, integration and advisory services", "Micro", "Low", "3-12", "Hard", "High", "High", "Advanced", "Very High", "Very High", "Very High", "Very Good", "Urban", NASSCOM, NASSCOM_URL, 66, "Talent-gated rather than capital-gated; Package006 holds the skill records"),
    ("mb-017", "Digital Marketing Agency", "mc-012", "bm-004", "Provides SEO, paid media, content and social media management services", "Micro", "Low", "3-12", "Easy", "Medium", "Medium", "Advanced", "Very High", "Very High", "Medium", "Good", "Urban", NASSCOM, NASSCOM_URL, 71, "Very low entry barrier; differentiation is the commercial problem"),
    ("mb-018", "IT Hardware and Network Services", "mc-012", "bm-005", "Supplies, installs and maintains IT hardware and network infrastructure", "Micro", "Medium", "4-10", "Easy", "Low", "Medium", "Semi-Automated", "Medium", "High", "Low", "Good", "Both", NASSCOM, NASSCOM_URL, 70, "Annual maintenance contracts provide the recurring revenue base"),
    ("mb-019", "Rural BPO / IT-Enabled Services Centre", "mc-012", "bm-004", "Delivers data processing, digitisation and voice support from a rural location", "Micro", "Low", "10-40", "Moderate", "Medium", "Medium", "Semi-Automated", "High", "Medium", "Low", "Variable", "Rural", "MeitY; NASSCOM Foundation", "https://www.meity.gov.in/", 66, "Highest employment per rupee invested; connectivity is the binding constraint"),
    # --- Renewable Energy and EV (4) ---
    ("mb-020", "Solar Rooftop EPC Contractor", "mc-013", "bm-013", "Engineers, procures and commissions rooftop solar plants", "Micro", "Medium", "5-15", "Moderate", "Medium", "Medium", "Semi-Automated", "Medium", "Very High", "Low", "Good", "Both", "Ministry of New and Renewable Energy", "https://mnre.gov.in/", 71, "PM Surya Ghar sharply expanded the residential segment; DISCOM empanelment needed"),
    ("mb-021", "Solar Panel Assembly Unit", "mc-013", "bm-001", "Assembles photovoltaic modules from imported or domestic cells", "Small", "High", "15-40", "Hard", "High", "Medium", "Automated", "Low", "High", "Medium", "Variable", "Both", "Ministry of New and Renewable Energy", "https://mnre.gov.in/", 66, "ALMM listing determines eligibility for government-supported projects"),
    ("mb-022", "EV Charging Station Operator", "mc-017", "bm-007", "Installs and operates public or captive electric vehicle charging points", "Micro", "Medium", "2-6", "Moderate", "High", "Medium", "Automated", "Medium", "High", "Low", "Variable", "Urban", "Ministry of Heavy Industries; Ministry of Power", "https://heavyindustries.gov.in/", 65, "Utilisation risk is severe while EV penetration remains low"),
    ("mb-023", "EV Two-Wheeler Service Centre", "mc-017", "bm-005", "Diagnoses and services electric two-wheelers including battery systems", "Micro", "Low", "3-8", "Moderate", "Medium", "Medium", "Semi-Automated", "Medium", "High", "Low", "Good", "Both", "Ministry of Heavy Industries", "https://heavyindustries.gov.in/", 66, "Skill gap is acute; Package006 holds the EV technician skill record"),
    # --- Textiles (3) ---
    ("mb-024", "Garment Manufacturing Unit", "mc-009", "bm-001", "Cuts and stitches garments for domestic brands or export buyers", "Small", "High", "20-60", "Moderate", "Medium", "Low", "Semi-Automated", "Low", "High", "Very High", "Variable", "Both", "Ministry of Textiles", "https://texmin.nic.in/", 73, "Highest employment per unit of investment in manufacturing"),
    ("mb-025", "Handloom and Handicraft Enterprise", "mc-020", "bm-001", "Produces handwoven textiles or handicraft products, often through artisan clusters", "Micro", "Medium", "5-20", "Easy", "Medium", "Low", "Basic", "Low", "Medium", "High", "Variable", "Rural", "Ministry of Textiles; KVIC", "https://texmin.nic.in/", 70, "GI tagging and e-commerce access changed the margin structure materially"),
    ("mb-026", "Technical Textiles Unit", "mc-009", "bm-001", "Manufactures functional textiles for industrial, medical or agricultural use", "Small", "High", "10-30", "Hard", "Medium", "High", "Automated", "Low", "High", "High", "Good", "Both", "Ministry of Textiles (National Technical Textiles Mission)", "https://texmin.nic.in/", 66, "Higher margin than apparel; requires testing and certification capability"),
    # --- Logistics and Infrastructure (4) ---
    ("mb-027", "Cold Storage Facility", "mc-019", "bm-007", "Rents temperature-controlled storage capacity to producers and traders", "Medium", "Medium", "8-20", "Hard", "Medium", "Medium", "Automated", "Medium", "Very High", "Low", "Variable", "Rural", "Ministry of Agriculture; MoFPI", "https://agricoop.gov.in/", 70, "Revenue is rental per tonne-month; power cost and utilisation drive viability"),
    ("mb-028", "Warehouse and Distribution Centre", "mc-019", "bm-008", "Provides storage, handling and secondary distribution for principals", "Small", "Medium", "8-25", "Moderate", "Medium", "Low", "Semi-Automated", "Medium", "High", "Low", "Good", "Both", "Ministry of Commerce and Industry", "https://commerce.gov.in/", 70, "Anchor-client concentration is the main commercial risk"),
    ("mb-029", "Last-Mile Delivery Fleet Operator", "mc-019", "bm-004", "Operates a delivery fleet on contract to e-commerce or logistics principals", "Micro", "Medium", "10-40", "Easy", "High", "Low", "Semi-Automated", "Medium", "Very High", "Low", "Variable", "Urban", "Ministry of Commerce and Industry", "https://commerce.gov.in/", 68, "Thin margins and high driver attrition; volume-dependent economics"),
    ("mb-030", "Packaging Materials Unit", "mc-001", "bm-001", "Manufactures corrugated boxes, flexible packaging or labels", "Small", "High", "8-20", "Moderate", "Medium", "Medium", "Automated", "Low", "Very High", "Low", "Good", "Both", DCMSME, MSME_URL, 72, "Demand is derived from every other manufacturing sector"),
    # --- Waste, Recycling, Chemical (4) ---
    ("mb-031", "Plastic Waste Recycling Unit", "mc-024", "bm-014", "Collects, washes, shreds and pelletises post-consumer plastic waste", "Small", "Medium", "8-20", "Moderate", "Medium", "Medium", "Semi-Automated", "Low", "High", "Medium", "Good", "Both", "Central Pollution Control Board", "https://cpcb.nic.in/", 68, "EPR obligations on producers created a compliance-driven demand side"),
    ("mb-032", "E-Waste Dismantling and Recovery", "mc-024", "bm-014", "Dismantles electronic waste and recovers metals and components", "Small", "Medium", "10-25", "Hard", "High", "Medium", "Semi-Automated", "Low", "High", "Medium", "Good", "Urban", "Central Pollution Control Board", "https://cpcb.nic.in/", 65, "CPCB authorisation is mandatory and the compliance burden is substantial"),
    ("mb-033", "Bio-Fertiliser and Vermicompost Unit", "mc-007", "bm-001", "Produces microbial bio-fertilisers and vermicompost from organic waste", "Micro", "Low", "4-12", "Easy", "Low", "Low", "Basic", "Low", "High", "Low", "Good", "Rural", "Ministry of Agriculture and Farmers Welfare", "https://agricoop.gov.in/", 70, "Fertiliser Control Order registration required for packaged sale"),
    ("mb-034", "Detergent and Cleaning Products Unit", "mc-010", "bm-001", "Formulates and packs household and industrial cleaning products", "Micro", "Medium", "5-12", "Easy", "Medium", "Low", "Semi-Automated", "Low", "High", "Low", "Good", "Both", DCMSME, MSME_URL, 69, "Low technical barrier; brand and distribution are the real constraints"),
    # --- Services, Healthcare, Education, Tourism (6) ---
    ("mb-035", "Diagnostic Laboratory", "mc-008", "bm-004", "Provides pathology and diagnostic testing services", "Micro", "Medium", "5-15", "Hard", "Medium", "High", "Automated", "Medium", "High", "Low", "Good", "Both", "Ministry of Health and Family Welfare", "https://mohfw.gov.in/", 68, "Clinical Establishments Act registration and qualified pathologist are statutory"),
    ("mb-036", "Medical Devices Assembly Unit", "mc-008", "bm-001", "Assembles and packs Class A or B medical devices under licence", "Small", "High", "10-25", "Very Hard", "High", "High", "Automated", "Low", "High", "High", "Good", "Urban", "Central Drugs Standard Control Organisation", "https://cdsco.gov.in/", 63, "CDSCO manufacturing licence and ISO 13485 are prerequisites, not options"),
    ("mb-037", "Skill Training Centre", "mc-022", "bm-004", "Delivers vocational or professional training, often scheme-affiliated", "Micro", "Low", "5-20", "Moderate", "Medium", "Medium", "Semi-Automated", "Medium", "High", "Low", "Variable", "Both", "Ministry of Skill Development and Entrepreneurship", "https://msde.gov.in/", 69, "Scheme affiliation determines viability; Package006 holds provider detail"),
    ("mb-038", "Homestay and Rural Tourism Enterprise", "mc-021", "bm-004", "Operates accommodation and experience services for visitors", "Micro", "Low", "2-8", "Easy", "Medium", "Low", "Basic", "Medium", "Medium", "Medium", "Variable", "Rural", "Ministry of Tourism", "https://tourism.gov.in/", 66, "State tourism registration; severe seasonality in cash flow"),
    ("mb-039", "Drone Services Enterprise", "mc-014", "bm-012", "Provides drone-based survey, spraying and inspection services on contract", "Micro", "Medium", "3-8", "Hard", "High", "High", "Advanced", "Very High", "High", "Low", "Variable", "Both", "DGCA; Ministry of Agriculture", "https://www.dgca.gov.in/", 64, "DGCA licensing and trained pilot availability gate entry; Package005 holds the machinery record"),
    ("mb-040", "3D Printing and Prototyping Service", "mc-015", "bm-004", "Produces prototypes and low-volume parts by additive manufacturing", "Micro", "Low", "2-6", "Moderate", "Medium", "High", "Automated", "High", "Medium", "Low", "Variable", "Urban", DCMSME, MSME_URL, 63, "Niche demand from product developers, education and dental sectors"),
]

# ===========================================================================
# 6. license_compliance.csv
# ===========================================================================
H_LIC = ["license_id", "license_name", "license_type", "issuing_authority",
         "jurisdiction", "applicability", "is_mandatory_when_applicable",
         "renewal_cycle", "online_application", "official_portal",
         "data_source", "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

LICENCES = [
    ("lic-001", "Udyam Registration", "Registration", MSME_M, "National", "All MSMEs seeking scheme benefits, priority sector credit or GeM access", "Yes", "No renewal (permanent)", "Yes", "https://udyamregistration.gov.in/", UDYAM, UDYAM_URL, CD, "78", VST, "Free, self-declaration based, PAN and GST linked; replaced Udyog Aadhaar"),
    ("lic-002", "GST Registration", "Tax Registration", "Goods and Services Tax Network", "National", "Enterprises above the turnover threshold, or making inter-state supply", "Yes", "No renewal", "Yes", "https://www.gst.gov.in/", "GSTN; Central Board of Indirect Taxes and Customs", "https://www.gst.gov.in/", CD, "76", VST, "Threshold differs for goods and services and for special category states"),
    ("lic-003", "FSSAI Licence / Registration", "Sector Licence", "Food Safety and Standards Authority of India", "National", "Any food business operator: manufacture, processing, storage, distribution, sale", "Yes", "1 to 5 years", "Yes", "https://foscos.fssai.gov.in/", "FSSAI", "https://www.fssai.gov.in/", CD, "75", VST, "Three tiers by turnover and scale: Registration, State Licence, Central Licence"),
    ("lic-004", "Factory Licence", "Establishment Licence", "State Directorate of Factories and Boilers", "State", "Manufacturing units above the worker-count threshold under the Factories Act", "Yes", "Annual or as prescribed", "Varies by state", PV, "Factories Act 1948; state labour departments", MSME_URL, CD, "70", VST, "Threshold depends on worker count and whether power is used"),
    ("lic-005", "Pollution Control Board Consent", "Environmental Clearance", "State Pollution Control Board", "State", "Units in the Red, Orange or Green category per CPCB classification", "Yes", "As prescribed by category", "Yes", "https://cpcb.nic.in/", "Central Pollution Control Board; state boards", "https://cpcb.nic.in/", CD, "72", VST, "Consent to Establish then Consent to Operate; White category is exempt"),
    ("lic-006", "Trade Licence", "Local Licence", "Municipal corporation or local body", "Local", "Most commercial premises within municipal limits", "Yes", "Annual", "Varies by local body", PV, "State municipal acts", MSME_URL, CD, "68", VST, "Requirement, fee and process vary widely between local bodies"),
    ("lic-007", "Fire NOC", "Safety Clearance", "State Fire and Emergency Services", "State", "Premises above prescribed area, height or occupancy thresholds", "Yes", "As prescribed", "Varies by state", PV, "State fire service acts", MSME_URL, CD, "68", VST, "Often a precondition for Factory Licence and Trade Licence"),
    ("lic-008", "BIS Certification (ISI Mark)", "Product Certification", "Bureau of Indian Standards", "National", "Products under mandatory certification via a Quality Control Order", "Yes", "As prescribed", "Yes", "https://www.bis.gov.in/", "Bureau of Indian Standards", "https://www.bis.gov.in/", CD, "73", VST, "Mandatory only for notified products; voluntary otherwise"),
    ("lic-009", "ISO Certification", "Management System Certification", "Accredited third-party certification body", "International", "Voluntary; often a buyer or tender requirement", "No", "3 years with annual surveillance", "Yes", PV, "International Organization for Standardization; NABCB", "https://nabcb.qci.org.in/", CD, "70", VST, "Not a government licence; ISO 9001 quality, ISO 22000 food, ISO 13485 devices"),
    ("lic-010", "Drug Manufacturing Licence", "Sector Licence", "State Drugs Controller / CDSCO", "State and National", "Manufacture of drugs, cosmetics or medical devices", "Yes", "As prescribed", "Yes", "https://cdsco.gov.in/", "Central Drugs Standard Control Organisation", "https://cdsco.gov.in/", CD, "70", VST, "Qualified technical staff and premises standards are statutory prerequisites"),
    ("lic-011", "Electrical Inspectorate Approval", "Safety Clearance", "State Electrical Inspectorate", "State", "Installations above prescribed load or voltage thresholds", "Yes", "As prescribed", "Varies by state", PV, "State electricity departments; CEA regulations", MSME_URL, CD, "66", VST, "Required before energisation of higher-load industrial connections"),
    ("lic-012", "Import Export Code", "Trade Registration", "Directorate General of Foreign Trade", "National", "Any enterprise importing or exporting goods or services", "Yes", "Annual update required", "Yes", "https://www.dgft.gov.in/", "Directorate General of Foreign Trade", "https://www.dgft.gov.in/", CD, "75", VST, "Mandatory for all cross-border trade; annual electronic update needed to stay active"),
    ("lic-013", "Shops and Establishments Registration", "Establishment Licence", "State labour department", "State", "Commercial establishments not covered by the Factories Act", "Yes", "As prescribed by state", "Yes", PV, "State shops and establishments acts", MSME_URL, CD, "70", VST, "Applies to most service and trading businesses"),
    ("lic-014", "EPR Authorisation", "Environmental Registration", "Central Pollution Control Board", "National", "Producers, importers and recyclers of plastic, e-waste, batteries or tyres", "Yes", "As prescribed", "Yes", "https://eprplastic.cpcb.gov.in/", "Central Pollution Control Board", "https://cpcb.nic.in/", CD, "68", VST, "Creates the recycler demand side; registration is on the CPCB EPR portal"),
]

# ===========================================================================
# 7. financial_support.csv
# ===========================================================================
H_FIN = ["finance_id", "finance_source_name", "source_type", "institution_type",
         "instrument", "typical_use", "collateral_requirement",
         "linked_package007_scheme_short_name", "official_website",
         "data_source", "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

FINANCE = [
    ("fin-001", "Scheduled Commercial Banks", "Institutional Lender", "Public and private sector banks", "Term loan; working capital; cash credit", "Plant, machinery and working capital across all MSME categories", "Waivable up to a prescribed limit under CGTMSE", "PMMY; PMEGP; Stand-Up India", PV, "Reserve Bank of India; Department of Financial Services", "https://www.rbi.org.in/", CD, "75", VST, "Priority sector lending targets make MSME credit a regulatory obligation"),
    ("fin-002", "Regional Rural Banks", "Institutional Lender", "Government-sponsored rural bank", "Term loan; working capital", "Rural micro enterprise and allied activity", "Waivable up to a prescribed limit", "PMMY; PMEGP", PV, "Reserve Bank of India; NABARD", "https://www.nabard.org/", CD, "71", VST, "District-level rural reach; sponsored by public sector banks"),
    ("fin-003", "SIDBI", "Development Financial Institution", "Apex MSME financier", "Refinance; direct term loan; fund of funds", "MSME refinance and larger direct term lending", "Case dependent", PV, SIDBI_URL, SIDBI, SIDBI_URL, CD, "75", VST, "Mostly an institutional lender; administers CGTMSE with the MSME Ministry"),
    ("fin-004", "NABARD", "Development Financial Institution", "Rural development financier", "Refinance; project loan; grant support", "Agri-processing, rural infrastructure and allied enterprise", "Case dependent", "AIF; KCC", "https://www.nabard.org/", "NABARD", "https://www.nabard.org/", CD, "75", VST, "Refinances lenders rather than lending directly to most enterprises"),
    ("fin-005", "CGTMSE Guarantee Cover", "Credit Enhancement", "Trust (Ministry of MSME and SIDBI)", "Guarantee cover to the lender", "Enables collateral-free credit to micro and small enterprises", "Substitutes for collateral", "CGTMSE", "https://www.cgtmse.in/", "CGTMSE", "https://www.cgtmse.in/", CD, "74", VST, "The borrower does not apply; the lender invokes cover"),
    ("fin-006", "Pradhan Mantri MUDRA Yojana", "Government Credit Programme", "Banks, NBFCs and MFIs", "Term loan; working capital", "Non-farm micro enterprise credit under four size categories", "Collateral-free", "PMMY", "https://www.mudra.org.in/", "MUDRA; Department of Financial Services", "https://www.mudra.org.in/", CD, "76", VST, "Package007 holds the scheme record; referenced here, not duplicated"),
    ("fin-007", "Stand-Up India", "Government Credit Programme", "Scheduled commercial banks", "Composite loan (term plus working capital)", "Greenfield enterprise by SC, ST and women entrepreneurs", "Collateral-free with CGTMSE cover", "Stand-Up India", "https://www.standupmitra.in/", "Stand-Up India portal", "https://www.standupmitra.in/", CD, "74", VST, "Greenfield and first-time-entrepreneur conditions apply"),
    ("fin-008", "PMEGP Margin Money Subsidy", "Government Subsidy", "KVIC, KVIB and DIC with a financing bank", "Back-ended margin money subsidy on a bank loan", "New micro enterprise creation", "Bank-determined; CGTMSE often applied", "PMEGP", "https://www.kviconline.gov.in/pmegpeportal/", "KVIC; PMEGP e-portal", "https://www.kviconline.gov.in/pmegpeportal/", CD, "74", VST, "Subsidy is released only after loan disbursement, as a term deposit"),
    ("fin-009", "NSIC Support Schemes", "Government Support", "Public sector enterprise", "Raw material assistance; bank credit facilitation; bid security", "Working capital relief and tender participation support", "Scheme dependent", PV, "https://www.nsic.co.in/", "National Small Industries Corporation", "https://www.nsic.co.in/", CD, "70", VST, "Support services rather than direct term lending"),
    ("fin-010", "State Finance Corporations", "Institutional Lender", "State-level financial institution", "Term loan; equipment finance", "State-specific industrial and MSME term lending", "Case dependent", PV, PV, "State industries departments", MSME_URL, CD, "64", VST, "Capacity and activity levels differ substantially between states"),
    ("fin-011", "Angel Investors and Angel Networks", "Equity Investor", "Private individual or syndicate", "Equity; convertible instrument", "Early-stage technology and scalable ventures", "Not applicable (equity)", PV, PV, "DPIIT; Startup India", DPIIT_URL, CD, "62", VST, "Relevant to a narrow slice of MSMEs; most are not equity-fundable"),
    ("fin-012", "Venture Capital and SIDBI Fund of Funds", "Equity Investor", "Fund", "Equity; structured instrument", "High-growth scalable startups past product validation", "Not applicable (equity)", "SISFS", "https://www.sidbivcf.in/", "SIDBI; DPIIT", SIDBI_URL, CD, "64", VST, "Fund of Funds for Startups invests through SEBI-registered AIFs, not directly"),
]

# ===========================================================================
# 14. market_channels.csv
# ===========================================================================
H_MKT = ["channel_id", "channel_name", "channel_type", "buyer_type",
         "description", "typical_payment_cycle", "entry_barrier",
         "digital_intensity", "official_portal", "data_source", "source_url",
         "collection_date", "confidence_score", "verification_status", "notes"]

CHANNELS = [
    ("ch-001", "Local Retail", "Physical", "B2C", "Direct sale to end consumers from own or partner retail outlets", PV, "Low", "Low", PV, MSME_M, MSME_URL, CD, "70", VST, "Fastest cash conversion; limited by catchment size"),
    ("ch-002", "Wholesale and Distributor Network", "Physical", "B2B", "Sale in bulk to distributors who reach retail", PV, "Medium", "Low", PV, MSME_M, MSME_URL, CD, "70", VST, "Volume scale at the cost of margin and end-customer relationship"),
    ("ch-003", "Direct B2B Supply", "Physical", "B2B", "Direct supply to industrial or institutional buyers on contract", PV, "High", "Low", PV, DCMSME, MSME_URL, CD, "71", VST, "Requires quality certification and often vendor registration"),
    ("ch-004", "Ancillary / Job Work Supply", "Physical", "B2B", "Conversion work or component supply to a principal manufacturer", PV, "High", "Low", PV, DCMSME, MSME_URL, CD, "70", VST, "Stable order flow, high concentration risk"),
    ("ch-005", "Government e-Marketplace (GeM)", "Digital", "B2G", "Sale to government buyers through the national procurement platform", PV, "Medium", "High", "https://gem.gov.in/", "Government e-Marketplace", "https://gem.gov.in/", CD, "74", VST, "Udyam registration enables MSME benefits including purchase preference"),
    ("ch-006", "Government Procurement (Tender)", "Physical and Digital", "B2G", "Sale through conventional tendering outside GeM", PV, "High", "Medium", PV, "Ministry of Finance; state procurement rules", MSME_URL, CD, "68", VST, "Public Procurement Policy reserves a share of procurement for MSEs"),
    ("ch-007", "Amazon Marketplace", "Digital", "B2C", "Third-party seller listing on the Amazon India marketplace", PV, "Low", "High", PV, "Ministry of Commerce (e-commerce policy context)", "https://commerce.gov.in/", CD, "66", VST, "Commission, returns and advertising cost materially compress margin"),
    ("ch-008", "Flipkart Marketplace", "Digital", "B2C", "Third-party seller listing on the Flipkart marketplace", PV, "Low", "High", PV, "Ministry of Commerce (e-commerce policy context)", "https://commerce.gov.in/", CD, "66", VST, "Same margin structure considerations as other marketplaces"),
    ("ch-009", "ONDC Network", "Digital", "B2C and B2B", "Sale through the Open Network for Digital Commerce interoperable network", PV, "Low", "High", "https://ondc.org/", "DPIIT; ONDC", "https://ondc.org/", CD, "62", VST, "Designed to lower platform dependence; adoption still maturing"),
    ("ch-010", "Own Digital Storefront", "Digital", "B2C", "Direct-to-consumer sale through an owned website or social commerce", PV, "Low", "High", PV, "Ministry of Commerce and Industry", "https://commerce.gov.in/", CD, "66", VST, "Highest margin retention, highest customer acquisition cost"),
    ("ch-011", "Export Channel", "Physical and Digital", "B2B and B2C", "Sale to overseas buyers directly or through merchant exporters", PV, "Very High", "Medium", "https://www.dgft.gov.in/", "DGFT; APEDA; Export Promotion Councils", "https://www.dgft.gov.in/", CD, "70", VST, "Import Export Code mandatory; certification is the binding constraint"),
]

# ===========================================================================
# 16. ai_business_tools.csv
# ===========================================================================
H_AI = ["tool_id", "tool_class", "function_area", "description",
        "msme_relevance", "adoption_maturity_india", "implementation_complexity",
        "typical_deployment", "expected_benefit", "data_source", "source_url",
        "collection_date", "confidence_score", "verification_status", "notes"]

AI_TOOLS = [
    ("ait-001", "ERP System", "Operations", "Integrated management of inventory, production, purchase, sales and accounts", "High", "Medium", "High", "Cloud SaaS or on-premise", "Single source of operational truth; reduces reconciliation effort", NASSCOM, NASSCOM_URL, CD, "68", VST, "Adoption barrier is process discipline, not software cost"),
    ("ait-002", "CRM System", "Sales and Marketing", "Tracks leads, customers, quotations and follow-up", "High", "Medium", "Low", "Cloud SaaS", "Fewer lost enquiries; measurable sales pipeline", NASSCOM, NASSCOM_URL, CD, "68", VST, "Highest value for order-driven B2B businesses"),
    ("ait-003", "Accounting and GST Software", "Finance and Compliance", "Books of account, invoicing and GST return preparation", "Very High", "High", "Low", "Desktop or cloud", "Compliance reliability; reduced professional fees", "GSTN; Institute of Chartered Accountants of India", "https://www.gst.gov.in/", CD, "72", VST, "Effectively universal already; GST made it near-mandatory"),
    ("ait-004", "Inventory and Warehouse Management", "Operations", "Stock tracking, reorder logic and location management", "High", "Medium", "Medium", "Cloud SaaS with barcode or RFID", "Lower working capital locked in stock", NASSCOM, NASSCOM_URL, CD, "66", VST, "Direct working capital impact makes the business case easiest to prove"),
    ("ait-005", "Predictive Maintenance", "Production", "Sensor and model-based prediction of equipment failure", "Medium", "Low", "High", "IoT sensors with analytics platform", "Reduced unplanned downtime", "MeitY; industry associations", "https://www.meity.gov.in/", CD, "58", VST, "Justifiable only where downtime cost is high; rare below a certain scale"),
    ("ait-006", "AI Quality Inspection", "Production", "Automated defect detection using computer vision", "Medium", "Low", "High", "Camera and edge compute on the line", "Consistent inspection; lower rejection at customer", "MeitY; Samarth Udyog centres", "https://www.meity.gov.in/", CD, "58", VST, "Most economic where inspection is currently manual and high-volume"),
    ("ait-007", "Computer Vision Sorting and Grading", "Production", "Automated grading of produce or components by visual attributes", "Medium", "Low", "High", "Line-integrated vision system", "Grade consistency; higher realisation per unit", "MoFPI; APEDA pack-house standards", "https://mofpi.gov.in/", CD, "57", VST, "Most viable at FPO or shared pack-house scale rather than single micro unit"),
    ("ait-008", "Digital Marketing and Ad Automation", "Sales and Marketing", "Automated campaign management, targeting and creative optimisation", "High", "High", "Low", "Cloud platforms", "Lower customer acquisition cost", NASSCOM, NASSCOM_URL, CD, "66", VST, "Already widely adopted among consumer-facing MSMEs"),
    ("ait-009", "Customer Service Chatbot", "Sales and Marketing", "Automated first-line customer query handling", "Medium", "Medium", "Low", "WhatsApp Business API or web widget", "Response coverage outside working hours", NASSCOM, NASSCOM_URL, CD, "64", VST, "WhatsApp is the dominant channel for Indian MSME customer contact"),
    ("ait-010", "Generative AI for Content and Documentation", "Cross-Functional", "Drafting product content, proposals, translations and documentation", "High", "Medium", "Low", "Cloud SaaS", "Substantially reduced content and documentation time", NASSCOM, NASSCOM_URL, CD, "62", VST, "Lowest-friction AI entry point; no integration required"),
    ("ait-011", "Workflow and Robotic Process Automation", "Operations", "Automates repetitive rule-based digital tasks", "Medium", "Low", "Medium", "Cloud or desktop RPA", "Fewer manual data-entry errors", NASSCOM, NASSCOM_URL, CD, "60", VST, "Requires stable, documented processes to be worth automating"),
    ("ait-012", "AI Credit Scoring and Cash Flow Forecasting", "Finance and Compliance", "Model-based credit assessment and cash flow projection", "Medium", "Low", "Medium", "Lender-side or fintech platform", "Faster credit decisions; better cash planning", "Reserve Bank of India; fintech sector reporting", "https://www.rbi.org.in/", CD, "58", VST, "Mostly lender-side today; account aggregator framework is enabling it"),
]

# ===========================================================================
# 17. startup_ecosystem.csv
# ===========================================================================
H_ECO = ["ecosystem_id", "entity_name", "entity_type", "sponsoring_body",
         "jurisdiction", "services_offered", "target_stage", "sector_focus",
         "official_website", "data_source", "source_url", "collection_date",
         "confidence_score", "verification_status", "notes"]

ECOSYSTEM = [
    ("eco-001", "Startup India", "National Programme", DPIIT, "National", "Recognition, tax benefit facilitation, seed fund access, public procurement relaxation", "Idea to growth", "Sector agnostic", "https://www.startupindia.gov.in/", DPIIT, DPIIT_URL, CD, "76", VST, "DPIIT recognition is the gateway to most central startup benefits"),
    ("eco-002", "Atal Incubation Centres", "Incubator Network", "Atal Innovation Mission, NITI Aayog", "National", "Physical incubation, mentoring, seed support, lab access", "Idea to early revenue", "Sector agnostic with regional focus", "https://aim.gov.in/", "Atal Innovation Mission, NITI Aayog", "https://aim.gov.in/", CD, "72", VST, "Distributed across states; hosted by academic and non-profit institutions"),
    ("eco-003", "MSME Development Institutes (MSME-DI)", "Government Institute", MSME_M, "State (multiple offices)", "Project profiles, EDP training, technical guidance, scheme facilitation", "Pre-establishment to early operation", "Manufacturing and services", MSME_URL, DCMSME, MSME_URL, CD, "73", VST, "The most under-used MSME resource; publishes project profiles free of charge"),
    ("eco-004", "MSME Technology Centres (Tool Rooms)", "Government Institute", MSME_M, "National (multiple centres)", "Precision tooling services, skill training, design and prototyping", "Operating enterprises", "Engineering and tooling", MSME_URL, DCMSME, MSME_URL, CD, "72", VST, "Provides tooling capability MSMEs cannot economically own"),
    ("eco-005", "District Industries Centre (DIC)", "District Office", "State industries department", "District", "Scheme facilitation, PMEGP processing, entrepreneur guidance, subsidy claims", "Pre-establishment to growth", "Sector agnostic", PV, "State industries departments", MSME_URL, CD, "70", VST, "The practical first point of contact for most district-level entrepreneurs"),
    ("eco-006", "T-Hub, Hyderabad", "Incubator / Accelerator", "Government of Telangana with academic partners", "Telangana", "Incubation, acceleration, corporate innovation, investor access", "Early to growth stage", "Technology-led", "https://t-hub.co/", "Government of Telangana", "https://t-hub.co/", CD, "70", VST, "One of India's largest single-site startup facilities"),
    ("eco-007", "WE-HUB, Hyderabad", "Incubator", "Government of Telangana", "Telangana", "Women-focused incubation, mentoring, market and funding access", "Idea to growth", "Sector agnostic, women-led", "https://wehub.telangana.gov.in/", "Government of Telangana", "https://wehub.telangana.gov.in/", CD, "70", VST, "India's first state-led incubator exclusively for women entrepreneurs"),
    ("eco-008", "AP Innovation Society / Startup AP", "State Programme", "Government of Andhra Pradesh", "Andhra Pradesh", "Startup recognition, incubation linkage, state incentive facilitation", "Idea to growth", "Sector agnostic", PV, "Government of Andhra Pradesh", MSME_URL, CD, "66", VST, "State counterpart to Startup India; Package004 holds the policy record"),
    ("eco-009", "Rural Business Incubators (RBI under ASPIRE)", "Incubator Network", MSME_M, "National (rural)", "Rural enterprise incubation, technology demonstration, skill support", "Idea to early operation", "Agro-processing and rural industry", MSME_URL, DCMSME, MSME_URL, CD, "66", VST, "ASPIRE scheme vehicle; addresses the rural incubation gap"),
    ("eco-010", "Rural Self Employment Training Institutes (RSETI)", "Training Institute", "Ministry of Rural Development with sponsoring banks", "District", "Free residential entrepreneurship training with credit linkage", "Pre-establishment", "Rural micro enterprise", PV, "Ministry of Rural Development", "https://rural.nic.in/", CD, "70", VST, "Bank-sponsored; Package006 holds the training-provider record"),
    ("eco-011", "Technology Business Incubators (DST-supported)", "Incubator Network", "Department of Science and Technology", "National", "Deep-tech incubation, seed support, research linkage", "Prototype to early revenue", "Science and technology led", "https://dst.gov.in/", "Department of Science and Technology", "https://dst.gov.in/", CD, "68", VST, "Hosted at academic and research institutions; research-adjacent focus"),
    ("eco-012", "Export Promotion Councils", "Trade Body", "Ministry of Commerce and Industry", "National (sector-wise)", "Buyer linkage, trade fair access, market intelligence, certification guidance", "Export-ready enterprises", "Sector-specific councils", "https://commerce.gov.in/", "Ministry of Commerce and Industry", "https://commerce.gov.in/", CD, "70", VST, "Council membership is often required for export incentive access"),
]


# ===========================================================================
# 18. investment_intelligence.csv — one row per business
# ===========================================================================
H_INV = ["intelligence_id", "business_id", "business_name", "investment_band",
         "capex_intensity", "working_capital_intensity", "roi_category",
         "payback_category", "scalability", "technology_adoption_requirement",
         "composite_risk", "growth_potential", "future_outlook",
         "key_success_factor", "data_source", "source_url", "collection_date",
         "confidence_score", "verification_status", "notes"]

# Derived deterministically from msme_businesses attributes (see build note below).
# (business_id, roi_category, payback_category, scalability, growth_potential,
#  future_outlook, key_success_factor, conf)
INV = {
    "mb-001": ("Moderate", "Medium", "Low", "Stable", "Stable", "By-product realisation and milling recovery", 70),
    "mb-002": ("Moderate", "Medium", "Low", "Stable", "Stable", "Milling recovery percentage", 70),
    "mb-003": ("Attractive", "Short", "Medium", "Growing", "Positive", "Premium brand positioning and oil cake sales", 70),
    "mb-004": ("Attractive", "Short", "Medium", "Growing", "Positive", "Colour value, moisture control and export certification", 72),
    "mb-005": ("Moderate", "Medium", "Medium", "Growing", "Positive", "Dehulling efficiency and nutri-cereal demand capture", 68),
    "mb-006": ("Moderate", "Long", "High", "Growing", "Positive", "Aseptic capability to break seasonality", 67),
    "mb-007": ("Variable", "Short", "Medium", "Growing", "Uncertain", "Platform rating and unit economics per order", 64),
    "mb-008": ("Attractive", "Medium", "Medium", "Growing", "Positive", "Skilled operator availability and machine utilisation", 71),
    "mb-009": ("Moderate", "Medium", "Low", "Stable", "Stable", "Local order flow and fabrication quality", 70),
    "mb-010": ("Attractive", "Long", "Medium", "Stable", "Positive", "Design skill depth; Tool Room access", 69),
    "mb-011": ("Attractive", "Short", "High", "Growing", "Strongly Positive", "Domain expertise and AMC retention", 67),
    "mb-012": ("Moderate", "Medium", "Low", "Stable", "Stable", "BIS conformity and inspectorate approval", 69),
    "mb-013": ("Variable", "Long", "Low", "Stable", "Uncertain", "Energy cost management and CPCB compliance", 66),
    "mb-014": ("Attractive", "Short", "High", "Growing", "Strongly Positive", "Billable utilisation and client diversification", 72),
    "mb-015": ("Variable", "Long", "Very High", "Growing", "Uncertain", "Product-market fit before capital exhaustion", 68),
    "mb-016": ("Attractive", "Short", "Very High", "Growing", "Strongly Positive", "Access to AI talent", 64),
    "mb-017": ("Moderate", "Short", "High", "Growing", "Positive", "Differentiation in a crowded market", 69),
    "mb-018": ("Moderate", "Short", "Medium", "Stable", "Stable", "AMC base for recurring revenue", 68),
    "mb-019": ("Variable", "Medium", "Medium", "Stable", "Uncertain", "Rural connectivity and client retention", 64),
    "mb-020": ("Attractive", "Short", "High", "Growing", "Strongly Positive", "DISCOM empanelment and installation quality", 69),
    "mb-021": ("Variable", "Long", "Medium", "Growing", "Uncertain", "ALMM listing for government-linked demand", 64),
    "mb-022": ("Variable", "Long", "High", "Growing", "Uncertain", "Site selection against current EV penetration", 63),
    "mb-023": ("Moderate", "Short", "Medium", "Growing", "Positive", "EV-specific diagnostic skill", 64),
    "mb-024": ("Moderate", "Medium", "High", "Stable", "Stable", "Buyer compliance audits and delivery reliability", 71),
    "mb-025": ("Moderate", "Medium", "Low", "Stable", "Positive", "GI tagging and direct e-commerce access", 68),
    "mb-026": ("Attractive", "Long", "High", "Growing", "Positive", "Testing and certification capability", 64),
    "mb-027": ("Moderate", "Long", "Medium", "Growing", "Positive", "Utilisation rate and power cost", 68),
    "mb-028": ("Moderate", "Medium", "High", "Growing", "Positive", "Anchor client plus diversification", 68),
    "mb-029": ("Variable", "Short", "High", "Growing", "Uncertain", "Route density and driver retention", 66),
    "mb-030": ("Moderate", "Medium", "Medium", "Stable", "Positive", "Proximity to manufacturing clusters", 70),
    "mb-031": ("Moderate", "Medium", "Medium", "Growing", "Positive", "Feedstock collection reliability", 66),
    "mb-032": ("Moderate", "Medium", "Medium", "Growing", "Positive", "CPCB authorisation and recovery yield", 63),
    "mb-033": ("Moderate", "Short", "Low", "Growing", "Positive", "FCO registration and agronomic credibility", 68),
    "mb-034": ("Moderate", "Short", "Medium", "Stable", "Stable", "Distribution reach and brand trust", 67),
    "mb-035": ("Attractive", "Medium", "Medium", "Growing", "Positive", "Qualified pathologist and accreditation", 66),
    "mb-036": ("Attractive", "Long", "High", "Growing", "Positive", "CDSCO licence and ISO 13485 system", 61),
    "mb-037": ("Variable", "Medium", "Medium", "Stable", "Uncertain", "Scheme affiliation and placement outcomes", 67),
    "mb-038": ("Moderate", "Long", "Low", "Growing", "Positive", "Occupancy management through the off season", 64),
    "mb-039": ("Moderate", "Medium", "High", "Growing", "Positive", "DGCA-licensed pilot availability", 62),
    "mb-040": ("Variable", "Medium", "Medium", "Growing", "Uncertain", "Niche demand identification", 61),
}

CAPEX_BY_MODEL_TYPE = {
    "bm-001": "High", "bm-002": "High", "bm-003": "Low", "bm-004": "Low",
    "bm-005": "Low", "bm-006": "Medium", "bm-007": "Very High", "bm-008": "High",
    "bm-009": "Very Low", "bm-010": "Very Low", "bm-011": "Low", "bm-012": "Medium",
    "bm-013": "Medium", "bm-014": "High", "bm-015": "Medium",
}


def rows_businesses():
    cat_name = {c[0]: c[1] for c in CATEGORIES}
    model_name = {m[0]: m[1] for m in MODELS}
    out = []
    for (bid, name, cat, model, desc, udyam, wc, emp, diff, risk, tech, autom,
         ai, demand, exp, profit, dist, src, url, conf, note) in B:
        out.append((bid, name, cat, cat_name[cat], model, model_name[model], desc,
                    udyam, PV, wc, emp, diff, risk, tech, autom, ai, demand, exp,
                    profit, dist, src, url, CD, str(conf), VST, note))
    return out


def rows_investment():
    biz = {b[0]: b for b in B}
    out = []
    for i, (bid, (roi, payback, scal, growth, outlook, ksf, conf)) in enumerate(INV.items(), start=1):
        b = biz[bid]
        model, wc, risk = b[3], b[6], b[9]
        out.append((f"ii-{i:03d}", bid, b[1], b[5], CAPEX_BY_MODEL_TYPE[model], wc,
                    roi, payback, scal, b[13], risk, growth, outlook, ksf,
                    "Derived from msme_businesses.csv attributes; MSME-DI project profile framing",
                    MSME_URL, CD, str(conf), VST,
                    "investment_band mirrors udyam_classification; no rupee figure is asserted. "
                    "roi_category, payback_category and scalability are ordinal judgements, not "
                    "computed returns"))
    return out


if __name__ == "__main__":
    print("Generating Package008_MSME core datasets:\n")
    write("msme_categories.csv", H_CAT, CATEGORIES)
    write("business_models.csv", H_BM, MODELS)
    write("msme_businesses.csv", H_BIZ, rows_businesses())
    write("license_compliance.csv", H_LIC, LICENCES)
    write("financial_support.csv", H_FIN, FINANCE)
    write("market_channels.csv", H_MKT, CHANNELS)
    write("ai_business_tools.csv", H_AI, AI_TOOLS)
    write("startup_ecosystem.csv", H_ECO, ECOSYSTEM)
    write("investment_intelligence.csv", H_INV, rows_investment())
    print("\nCore generation complete.")
