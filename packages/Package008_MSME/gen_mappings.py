#!/usr/bin/env python3
"""
Package008_MSME v1.0.0 — Mapping Dataset Generator

Builds the nine datasets that carry upstream foreign keys:
   4  machinery_mapping.csv             -> Package005 farm_machinery where the machine exists there
   5  raw_material_mapping.csv          -> Package005 crops where the input is a crop
   8  scheme_mapping.csv                -> Package007 scheme_id (scheme detail NOT duplicated)
   9  skill_mapping.csv                 -> Package006 skill_id (skill detail NOT duplicated)
  10  industry_mapping.csv              -> Package004 opportunity id (industry detail NOT duplicated)
  11  agriculture_business_mapping.csv  -> Package005 crop_id + agri_processing_opportunities
  12  education_support_mapping.csv     -> Package002 university id + Package006 provider_id
  13  district_business_mapping.csv     -> Package001 dist_id
  15  export_opportunities.csv          (business -> market; no upstream FK)

THE NORMALIZATION RULE, enforced here rather than merely stated:
Package008 is the Business Intelligence Layer. It stores the RELATIONSHIP between an
MSME business and an upstream entity, plus attributes of that relationship, and nothing
else. It does not restate the scheme's benefit, the skill's NSQF level, the crop's
agronomy or the district's population -- those belong to their owning package and are
reachable by joining on the id.

Every upstream id is resolved against the released CSV AT GENERATION TIME. An id that
does not exist upstream aborts the build rather than shipping a broken reference.
Where no genuine upstream counterpart exists, the bare sentinel PENDING_VERIFICATION is
written instead of an invented one.
"""

import csv
import sys
from pathlib import Path

CD = "2026-07-25"
VST = "VST-NEEDS_REVIEW"
PV = "PENDING_VERIFICATION"

PKG = Path(__file__).resolve().parent
DATASETS = PKG / "datasets"
PACKAGES = PKG.parent

MSME_M = "Ministry of Micro, Small and Medium Enterprises"
MSME_URL = "https://msme.gov.in/"
DCMSME = "Office of Development Commissioner (MSME); MSME-DI project profiles"


def read(rel):
    p = PACKAGES / rel
    if not p.exists():
        sys.exit(f"FATAL: upstream dataset missing: {rel}")
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def local(name):
    with open(DATASETS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(filename, headers, rows):
    for i, r in enumerate(rows):
        if len(r) != len(headers):
            raise ValueError(f"{filename} row {i} ({r[0]}): {len(r)} values, expected {len(headers)}")
    with open(DATASETS / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows x {len(headers)} cols")


# ------------------------------------------------------------- upstream loads
P001_DIST = read("Package001_Geography/datasets/district.csv")
P002_UNIV = read("Package002_Education/datasets/universities_telangana_andhra_pradesh.csv")
P004 = {
    "food_agro_processing_micro_enterprises": read("Package004_Industries/datasets/food_agro_processing_micro_enterprises.csv"),
    "construction_skilled_trade_services": read("Package004_Industries/datasets/construction_skilled_trade_services.csv"),
    "digital_technology_livelihoods": read("Package004_Industries/datasets/digital_technology_livelihoods.csv"),
    "china_inspired_adapted_opportunities": read("Package004_Industries/datasets/china_inspired_adapted_opportunities.csv"),
}
P005_CROPS = read("Package005_Agriculture/datasets/crops.csv")
P005_MACH = read("Package005_Agriculture/datasets/farm_machinery.csv")
P005_PROC = read("Package005_Agriculture/datasets/agri_processing_opportunities.csv")
P006_SKILLS = read("Package006_Skills_and_Training/datasets/skills.csv")
P006_PROV = read("Package006_Skills_and_Training/datasets/training_providers.csv")
P007_SCH = read("Package007_Government_Schemes/datasets/government_schemes.csv")

BIZ = local("msme_businesses.csv")
BIZ_NAME = {r["business_id"]: r["business_name"] for r in BIZ}


def resolve(rows, key, needle, idcol, label):
    hits = [r for r in rows if needle.lower() in r[key].lower()]
    if len(hits) != 1:
        sys.exit(f"FATAL: {label!r} matched {len(hits)} upstream rows via {key}~{needle!r}")
    return hits[0][idcol], hits[0][key]


# ===========================================================================
# 4. machinery_mapping.csv
# ===========================================================================
H_MACH = ["mapping_id", "business_id", "business_name", "machinery_name",
          "machinery_role", "package005_machinery_id", "package005_machinery_name",
          "investment_category", "automation_level", "is_essential",
          "data_source", "source_url", "collection_date", "confidence_score",
          "verification_status", "notes"]

# (business_id, machinery_name, role, P005 machinery needle | None, invest_cat, automation, essential, conf)
MACHINERY = [
    ("mb-001", "Rice Mill (Mini)", "Primary processing", "Rice Mill (Mini)", "Core Plant", "Semi-Automated", "Yes", 72),
    ("mb-001", "Paddy Cleaner and Destoner", "Pre-cleaning", None, "Core Plant", "Semi-Automated", "Yes", 68),
    ("mb-001", "Packaging Machine (Form-Fill-Seal)", "Packing", "Packaging Machine", "Ancillary", "Automated", "No", 68),
    ("mb-002", "Dal Mill (Mini)", "Primary processing", "Dal Mill (Mini)", "Core Plant", "Semi-Automated", "Yes", 72),
    ("mb-002", "Grader and Polisher", "Finishing", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-003", "Oil Expeller (Cold Press)", "Extraction", "Oil Expeller (Cold Press)", "Core Plant", "Semi-Automated", "Yes", 72),
    ("mb-003", "Filter Press", "Clarification", None, "Core Plant", "Mechanical", "Yes", 66),
    ("mb-003", "Bottling and Capping Line", "Packing", None, "Ancillary", "Semi-Automated", "No", 65),
    ("mb-004", "Pulveriser / Impact Mill", "Grinding", None, "Core Plant", "Semi-Automated", "Yes", 68),
    ("mb-004", "Solar Dryer", "Pre-drying", "Solar Dryer", "Ancillary", "Automated", "No", 67),
    ("mb-004", "Packaging Machine (Form-Fill-Seal)", "Packing", "Packaging Machine", "Core Plant", "Automated", "Yes", 68),
    ("mb-005", "Millet Dehuller", "Dehulling", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-005", "Flour Mill / Rava Unit", "Milling", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-006", "Fruit Pulper and Deseeder", "Pulping", None, "Core Plant", "Automated", "Yes", 66),
    ("mb-006", "Aseptic Filling Line", "Preservation and filling", None, "Core Plant", "Automated", "Yes", 64),
    ("mb-006", "Cold Storage Unit", "Raw material holding", "Cold Storage Unit", "Ancillary", "Automated", "No", 67),
    ("mb-007", "Commercial Kitchen Equipment Set", "Food preparation", None, "Core Plant", "Basic", "Yes", 64),
    ("mb-008", "CNC Turning Centre", "Machining", None, "Core Plant", "Automated", "Yes", 70),
    ("mb-008", "CNC Vertical Machining Centre", "Machining", None, "Core Plant", "Automated", "Yes", 70),
    ("mb-008", "Coordinate Measuring Machine", "Quality inspection", None, "Ancillary", "Automated", "No", 66),
    ("mb-009", "CNC Press Brake", "Forming", None, "Core Plant", "Automated", "Yes", 69),
    ("mb-009", "Laser or Plasma Cutting Machine", "Cutting", None, "Core Plant", "Automated", "Yes", 69),
    ("mb-009", "Welding Equipment (MIG/TIG)", "Joining", None, "Core Plant", "Mechanical", "Yes", 70),
    ("mb-010", "EDM (Electrical Discharge Machine)", "Die sinking", None, "Core Plant", "Automated", "Yes", 67),
    ("mb-010", "Surface and Cylindrical Grinder", "Finishing", None, "Core Plant", "Mechanical", "Yes", 67),
    ("mb-011", "PLC and HMI Development Kit", "Engineering and testing", None, "Tooling", "Digital", "Yes", 65),
    ("mb-012", "Busbar Bending and Punching Machine", "Panel fabrication", None, "Core Plant", "Semi-Automated", "Yes", 67),
    ("mb-013", "Induction Melting Furnace", "Melting", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-013", "Sand Mixer and Moulding Line", "Moulding", None, "Core Plant", "Semi-Automated", "Yes", 65),
    ("mb-014", "Developer Workstations and Cloud Infrastructure", "Development", None, "IT Infrastructure", "Digital", "Yes", 70),
    ("mb-015", "Developer Workstations and Cloud Infrastructure", "Product development", None, "IT Infrastructure", "Digital", "Yes", 68),
    ("mb-017", "Workstations and Creative Software Licences", "Content production", None, "IT Infrastructure", "Digital", "Yes", 67),
    ("mb-019", "Workstations, Connectivity and UPS Backup", "Service delivery", None, "IT Infrastructure", "Digital", "Yes", 65),
    ("mb-038", "Guest Room Furnishing and Kitchen Equipment", "Guest service", None, "Premises", "Basic", "Yes", 64),
    ("mb-016", "GPU Compute (owned or cloud)", "Model training and inference", None, "IT Infrastructure", "Digital", "Yes", 64),
    ("mb-018", "Diagnostic and Networking Toolkit", "Service delivery", None, "Tooling", "Basic", "Yes", 67),
    ("mb-020", "Installation Tools and Safety Equipment", "Installation", None, "Tooling", "Basic", "Yes", 68),
    ("mb-021", "Solar Module Laminator", "Lamination", None, "Core Plant", "Automated", "Yes", 64),
    ("mb-021", "Cell Stringer / Tabber", "Cell interconnection", None, "Core Plant", "Automated", "Yes", 63),
    ("mb-022", "AC and DC Charging Units", "Charging delivery", None, "Core Plant", "Automated", "Yes", 64),
    ("mb-023", "Battery Diagnostic and Balancing Equipment", "Diagnostics", None, "Tooling", "Semi-Automated", "Yes", 64),
    ("mb-024", "Industrial Sewing Machines (lockstitch, overlock)", "Stitching", None, "Core Plant", "Semi-Automated", "Yes", 71),
    ("mb-024", "Fabric Cutting Machine", "Cutting", None, "Core Plant", "Semi-Automated", "Yes", 70),
    ("mb-024", "Steam Press and Finishing Unit", "Finishing", None, "Ancillary", "Semi-Automated", "Yes", 69),
    ("mb-025", "Handloom / Artisan Toolset", "Production", None, "Tooling", "Basic", "Yes", 68),
    ("mb-026", "Nonwoven or Coating Line", "Functional finishing", None, "Core Plant", "Automated", "Yes", 62),
    ("mb-027", "Cold Storage Unit", "Storage", "Cold Storage Unit", "Core Plant", "Automated", "Yes", 70),
    ("mb-027", "Cold Chain / Reefer Transport", "Outbound movement", "Cold Chain / Reefer Transport", "Ancillary", "Automated", "No", 66),
    ("mb-028", "Forklift and Material Handling Equipment", "Handling", None, "Core Plant", "Mechanical", "Yes", 68),
    ("mb-028", "Racking and WMS Barcode Infrastructure", "Storage and tracking", None, "Core Plant", "Digital", "Yes", 66),
    ("mb-029", "Delivery Vehicle Fleet", "Transport", None, "Core Plant", "Basic", "Yes", 67),
    ("mb-030", "Corrugation and Box Making Line", "Converting", None, "Core Plant", "Automated", "Yes", 69),
    ("mb-030", "Flexographic Printing Machine", "Printing", None, "Core Plant", "Automated", "No", 67),
    ("mb-031", "Plastic Shredder and Washing Line", "Size reduction and cleaning", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-031", "Pelletiser / Extruder", "Reprocessing", None, "Core Plant", "Automated", "Yes", 66),
    ("mb-032", "Dismantling Workstations and Shredder", "Dismantling", None, "Core Plant", "Semi-Automated", "Yes", 63),
    ("mb-033", "Vermibed Infrastructure and Shredder", "Composting", None, "Core Plant", "Basic", "Yes", 67),
    ("mb-034", "Mixing and Blending Tanks", "Formulation", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-034", "Filling and Sealing Line", "Packing", None, "Core Plant", "Semi-Automated", "Yes", 66),
    ("mb-035", "Biochemistry and Haematology Analysers", "Testing", None, "Core Plant", "Automated", "Yes", 66),
    ("mb-036", "Cleanroom and Assembly Fixtures", "Assembly", None, "Core Plant", "Automated", "Yes", 61),
    ("mb-037", "Training Lab Equipment and Computers", "Training delivery", None, "Core Plant", "Basic", "Yes", 66),
    ("mb-039", "Agricultural Drone", "Aerial operation", "Agricultural Drone", "Core Plant", "Advanced", "Yes", 66),
    ("mb-040", "FDM and Resin 3D Printers", "Additive manufacturing", None, "Core Plant", "Automated", "Yes", 62),
]

# ===========================================================================
# 5. raw_material_mapping.csv
# ===========================================================================
H_RAW = ["mapping_id", "business_id", "business_name", "raw_material_name",
         "material_class", "package005_crop_id", "package005_crop_name",
         "supplier_type", "availability", "seasonality", "price_volatility",
         "data_source", "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

# (business_id, material, class, crop needle | None, supplier_type, availability, seasonality, volatility, conf)
RAW = [
    ("mb-001", "Paddy", "Agricultural Produce", "Rice", "Farmer / FPO / APMC mandi", "High", "Seasonal (kharif peak)", "Medium", 72),
    ("mb-002", "Pigeon Pea (Toor)", "Agricultural Produce", "Pigeon Pea", "Farmer / FPO / APMC mandi", "Medium", "Seasonal (kharif)", "High", 70),
    ("mb-002", "Chickpea", "Agricultural Produce", "Chickpea", "Farmer / FPO / APMC mandi", "Medium", "Seasonal (rabi)", "High", 70),
    ("mb-003", "Groundnut", "Agricultural Produce", "Groundnut", "Farmer / FPO / APMC mandi", "High", "Seasonal (kharif)", "High", 71),
    ("mb-003", "Sesame", "Agricultural Produce", None, "Farmer / trader", "Medium", "Seasonal", "High", 64),
    ("mb-004", "Turmeric (dry fingers)", "Agricultural Produce", "Turmeric", "Farmer / FPO / spice mandi", "High", "Seasonal (post-harvest)", "High", 72),
    ("mb-004", "Dry Chilli", "Agricultural Produce", "Chilli", "Farmer / FPO / Guntur mandi", "High", "Seasonal (rabi harvest)", "Very High", 72),
    ("mb-004", "Coriander Seed", "Agricultural Produce", "Coriander", "Farmer / trader", "Medium", "Seasonal (rabi)", "High", 68),
    ("mb-005", "Pearl Millet", "Agricultural Produce", "Pearl Millet", "Farmer / FPO", "Medium", "Seasonal (kharif)", "Medium", 68),
    ("mb-005", "Finger Millet", "Agricultural Produce", "Finger Millet", "Farmer / FPO", "Medium", "Seasonal (kharif)", "Medium", 66),
    ("mb-006", "Mango", "Agricultural Produce", "Mango", "Farmer / orchard / mandi", "Medium", "Highly seasonal", "High", 69),
    ("mb-006", "Tomato", "Agricultural Produce", "Tomato", "Farmer / mandi", "High", "Multi-season", "Very High", 68),
    ("mb-007", "Vegetables and Provisions", "Agricultural Produce", None, "Local wholesale market", "High", "Multi-season", "High", 62),
    ("mb-008", "Alloy Steel and Aluminium Bar Stock", "Metal", None, "Steel distributor / principal-supplied", "High", "Year-round", "High", 69),
    ("mb-009", "MS and GI Sheet", "Metal", None, "Steel distributor", "High", "Year-round", "High", 69),
    ("mb-010", "Tool Steel (D2, H13)", "Metal", None, "Specialist steel distributor / import", "Medium", "Year-round", "Medium", 66),
    ("mb-011", "PLC, Drives, Sensors and Cabling", "Electronic Component", None, "OEM authorised distributor", "Medium", "Year-round", "Medium", 65),
    ("mb-012", "Switchgear, Busbar and Enclosures", "Electrical Component", None, "OEM authorised distributor", "High", "Year-round", "Medium", 67),
    ("mb-013", "Pig Iron and Foundry Scrap", "Metal", None, "Scrap dealer / mini steel plant", "High", "Year-round", "Very High", 65),
    ("mb-021", "Solar Cells, Glass, EVA and Backsheet", "Electronic Component", None, "Import / domestic cell maker", "Medium", "Year-round", "High", 63),
    ("mb-022", "Charging Hardware and Transformer", "Electrical Component", None, "OEM / EPC supplier", "Medium", "Year-round", "Medium", 63),
    ("mb-023", "Battery Modules and Spare Parts", "Electronic Component", None, "OEM authorised channel", "Low", "Year-round", "Medium", 62),
    ("mb-024", "Fabric and Trims", "Textile", None, "Fabric market / buyer-nominated mill", "High", "Year-round", "Medium", 70),
    ("mb-025", "Cotton and Silk Yarn", "Textile", "Cotton", "Yarn dealer / cooperative", "Medium", "Year-round", "Medium", 67),
    ("mb-026", "Technical Fibre and Coating Chemicals", "Textile", None, "Specialist supplier / import", "Low", "Year-round", "Medium", 61),
    ("mb-030", "Kraft Paper and Ink", "Paper and Chemical", None, "Paper mill / distributor", "High", "Year-round", "High", 68),
    ("mb-031", "Post-Consumer Plastic Waste", "Recovered Material", None, "Aggregator / urban local body / EPR channel", "Medium", "Year-round", "High", 65),
    ("mb-032", "End-of-Life Electronics", "Recovered Material", None, "Aggregator / bulk consumer / EPR channel", "Medium", "Year-round", "High", 63),
    ("mb-033", "Cattle Dung and Farm Waste", "Agricultural Residue", None, "Local farmer / dairy", "High", "Year-round", "Low", 67),
    ("mb-034", "Surfactants, Builders and Fragrance", "Chemical", None, "Chemical distributor", "High", "Year-round", "Medium", 66),
    ("mb-035", "Reagents and Consumables", "Chemical", None, "Diagnostic reagent distributor", "High", "Year-round", "Low", 65),
    ("mb-036", "Device Components and Sterile Packaging", "Electronic Component", None, "Qualified vendor / import", "Medium", "Year-round", "Medium", 60),
    ("mb-040", "PLA, ABS Filament and Photopolymer Resin", "Polymer", None, "Specialist distributor / import", "Medium", "Year-round", "Medium", 61),
]

# ===========================================================================
# 8. scheme_mapping.csv  -> Package007 ONLY (no scheme detail duplicated)
# ===========================================================================
H_SCHM = ["mapping_id", "business_id", "business_name", "package007_scheme_id",
          "package007_scheme_short_name", "relevance", "applicable_stage",
          "support_nature", "data_source", "source_url", "collection_date",
          "confidence_score", "verification_status", "notes"]

# (business_id, P007 short_name, relevance, stage, support_nature, conf)
SCHEME_LINKS = [
    ("mb-001", "PMFME", "Primary", "Establishment", "Credit-linked capital subsidy", 72),
    ("mb-001", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 72),
    ("mb-001", "CGTMSE", "Secondary", "Establishment", "Collateral-free credit enablement", 70),
    ("mb-002", "PMFME", "Primary", "Establishment", "Credit-linked capital subsidy", 72),
    ("mb-002", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 71),
    ("mb-003", "PMFME", "Primary", "Establishment", "Credit-linked capital subsidy", 72),
    ("mb-003", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 71),
    ("mb-004", "PMFME", "Primary", "Establishment", "Credit-linked capital subsidy with ODOP focus", 73),
    ("mb-004", "PMMY", "Secondary", "Working capital", "Collateral-free micro credit", 70),
    ("mb-005", "PMFME", "Primary", "Establishment", "Credit-linked capital subsidy with ODOP focus", 71),
    ("mb-006", "PMFME", "Primary", "Establishment", "Credit-linked capital subsidy", 70),
    ("mb-006", "AIF", "Secondary", "Expansion", "Interest subvention on post-harvest infrastructure", 68),
    ("mb-007", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 68),
    ("mb-007", "PMFME", "Secondary", "Establishment", "Applies where the unit is a micro food processor", 66),
    ("mb-008", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 71),
    ("mb-008", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 70),
    ("mb-009", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 71),
    ("mb-009", "PMMY", "Secondary", "Working capital", "Collateral-free micro credit", 69),
    ("mb-010", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 69),
    ("mb-011", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 67),
    ("mb-012", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 69),
    ("mb-013", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 67),
    ("mb-014", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 70),
    ("mb-015", "SISFS", "Primary", "Ideation to prototype", "Grant and convertible instrument via incubator", 70),
    ("mb-016", "SISFS", "Primary", "Ideation to prototype", "Grant and convertible instrument via incubator", 66),
    ("mb-017", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 68),
    ("mb-018", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 68),
    ("mb-019", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 66),
    ("mb-020", "PM Surya Ghar", "Primary", "Operation", "Demand-side subsidy driving installation volume", 70),
    ("mb-020", "PMMY", "Secondary", "Working capital", "Collateral-free micro credit", 68),
    ("mb-021", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 64),
    ("mb-022", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 64),
    ("mb-023", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 65),
    ("mb-023", "PM Vishwakarma", "Secondary", "Skill and toolkit", "Applies where the operator is a traditional-trade artisan", 62),
    ("mb-024", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 71),
    ("mb-024", "CGTMSE", "Secondary", "Establishment", "Collateral-free credit enablement", 69),
    ("mb-025", "PM Vishwakarma", "Primary", "Skill, toolkit and credit", "Artisan-focused end-to-end support", 70),
    ("mb-025", "PMEGP", "Secondary", "Establishment", "Margin money subsidy on bank loan", 68),
    ("mb-026", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 63),
    ("mb-027", "AIF", "Primary", "Establishment", "Interest subvention on post-harvest infrastructure", 70),
    ("mb-027", "PMKSY", "Secondary", "Establishment", "Applies where the facility serves an irrigation command area", 62),
    ("mb-028", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 68),
    ("mb-029", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 67),
    ("mb-030", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 69),
    ("mb-031", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 66),
    ("mb-032", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 64),
    ("mb-033", "PKVY", "Primary", "Operation", "Demand-side support through organic cluster conversion", 68),
    ("mb-033", "PMEGP", "Secondary", "Establishment", "Margin money subsidy on bank loan", 67),
    ("mb-034", "PMEGP", "Primary", "Establishment", "Margin money subsidy on bank loan", 67),
    ("mb-035", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 65),
    ("mb-036", "CGTMSE", "Primary", "Establishment", "Collateral-free credit enablement", 61),
    ("mb-037", "PMKVY 4.0", "Primary", "Operation", "Scheme affiliation is the revenue basis for the centre", 68),
    ("mb-037", "DDU-GKY", "Secondary", "Operation", "Placement-linked rural training projects", 66),
    ("mb-038", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 64),
    ("mb-039", "SMAM", "Primary", "Operation", "Drone component supports custom-hiring service demand", 66),
    ("mb-039", "PMMY", "Secondary", "Establishment", "Collateral-free micro credit", 64),
    ("mb-040", "PMMY", "Primary", "Establishment", "Collateral-free micro credit", 62),
]

# ===========================================================================
# 9. skill_mapping.csv  -> Package006 ONLY (no skill detail duplicated)
# ===========================================================================
H_SKM = ["mapping_id", "business_id", "business_name", "package006_skill_id",
         "package006_skill_name", "skill_role", "criticality",
         "who_needs_it", "data_source", "source_url", "collection_date",
         "confidence_score", "verification_status", "notes"]

SKILL_LINKS = [
    ("mb-001", "Food Processing & Preservation", "Process operation and quality control", "Essential", "Operator and supervisor", 71),
    ("mb-002", "Food Processing & Preservation", "Milling operation and grading", "Essential", "Operator and supervisor", 71),
    ("mb-003", "Food Processing & Preservation", "Extraction, filtration and packing", "Essential", "Operator", 71),
    ("mb-004", "Food Processing & Preservation", "Grinding, blending and packing", "Essential", "Operator", 71),
    ("mb-005", "Food Processing & Preservation", "Dehulling and milling operation", "Essential", "Operator", 69),
    ("mb-006", "Food Processing & Preservation", "Thermal processing and aseptic handling", "Essential", "Technician and supervisor", 68),
    ("mb-007", "Food Service & Culinary Arts", "Food preparation and kitchen operation", "Essential", "Chef and kitchen staff", 68),
    ("mb-008", "CNC Machine Operator", "Machine setting, programming and operation", "Essential", "Operator", 72),
    ("mb-008", "CAD/CAM Design", "Part programming and drawing interpretation", "Essential", "Programmer", 70),
    ("mb-009", "Welding (MIG/TIG/Arc)", "Joining and structural fabrication", "Essential", "Fabricator", 72),
    ("mb-010", "CAD/CAM Design", "Die and mould design", "Essential", "Designer", 69),
    ("mb-010", "CNC Machine Operator", "Precision machining of tooling", "Essential", "Machinist", 69),
    ("mb-011", "PLC Programming & Control Systems", "Control logic development and commissioning", "Essential", "Automation engineer", 68),
    ("mb-011", "Industrial Robotics", "Robotic cell integration where applicable", "Useful", "Automation engineer", 64),
    ("mb-012", "Industrial Electrician", "Panel wiring and testing", "Essential", "Electrician", 70),
    ("mb-014", "Full Stack Web Development", "Application development", "Essential", "Developer", 72),
    ("mb-014", "Python Programming", "Backend and automation development", "Essential", "Developer", 72),
    ("mb-014", "Database Administration", "Data layer design and operation", "Useful", "Developer", 68),
    ("mb-015", "Full Stack Web Development", "Product development", "Essential", "Founding engineer", 70),
    ("mb-015", "AWS/Azure Cloud Administration", "Deployment and scaling", "Essential", "Engineer", 68),
    ("mb-016", "Machine Learning Engineer", "Model development and deployment", "Essential", "ML engineer", 66),
    ("mb-016", "Data Scientist", "Problem framing and analysis", "Essential", "Data scientist", 66),
    ("mb-016", "Python Programming", "Implementation language", "Essential", "Engineer", 68),
    ("mb-017", "Video Editing & Content Creation", "Creative production", "Essential", "Creative staff", 67),
    ("mb-018", "Electronics Repair", "Hardware diagnosis and repair", "Essential", "Technician", 68),
    ("mb-018", "AWS/Azure Cloud Administration", "Network and cloud service configuration", "Useful", "Engineer", 65),
    ("mb-019", None, "Data processing and digitisation", "Essential", "Operator", 58),
    ("mb-020", "Solar Panel Installation", "Rooftop installation and commissioning", "Essential", "Installer", 70),
    ("mb-020", "Electrician (Domestic Wiring)", "Electrical connection and safety", "Essential", "Electrician", 69),
    ("mb-021", "PCB Assembly & Soldering", "Cell interconnection and module assembly", "Essential", "Assembly operator", 63),
    ("mb-022", "Industrial Electrician", "Charger installation and electrical works", "Essential", "Electrician", 64),
    ("mb-023", "EV Technician", "EV and battery system diagnosis", "Essential", "Technician", 66),
    ("mb-023", "Two-Wheeler Mechanic", "Mechanical service of two-wheelers", "Essential", "Mechanic", 66),
    ("mb-024", "Garment Manufacturing (Stitching)", "Cutting, stitching and finishing", "Essential", "Operator", 72),
    ("mb-026", "Garment Manufacturing (Stitching)", "Fabric handling and conversion", "Useful", "Operator", 62),
    ("mb-027", "Warehouse Management", "Storage operation and stock control", "Essential", "Supervisor", 68),
    ("mb-028", "Warehouse Management", "Inventory and dispatch operation", "Essential", "Supervisor", 70),
    ("mb-028", "Supply Chain Logistics", "Network planning and coordination", "Essential", "Manager", 69),
    ("mb-029", "Supply Chain Logistics", "Route planning and fleet coordination", "Essential", "Coordinator", 67),
    ("mb-033", "Organic Farming", "Composting and bio-input production", "Essential", "Supervisor", 68),
    ("mb-035", "Nursing Assistant", "Sample collection and patient handling", "Essential", "Phlebotomist and assistant", 65),
    ("mb-036", "PCB Assembly & Soldering", "Device assembly under controlled conditions", "Essential", "Assembly operator", 61),
    ("mb-037", None, "Instruction delivery", "Essential", "Trainer", 58),
    ("mb-039", "Drone Piloting & Operations", "Flight operation and mission planning", "Essential", "Pilot", 68),
    ("mb-039", "Precision Agriculture & IoT", "Agronomic application of drone data", "Useful", "Agronomy advisor", 64),
    ("mb-013", None, "Melting, moulding and casting operation", "Essential", "Foundry operator", 57),
    ("mb-025", None, "Handloom weaving and craft production", "Essential", "Artisan weaver", 57),
    ("mb-030", None, "Corrugation and converting machine operation", "Essential", "Machine operator", 57),
    ("mb-031", None, "Plastic sorting, washing and extrusion operation", "Essential", "Plant operator", 57),
    ("mb-032", "Electronics Repair", "Component identification during dismantling", "Useful", "Dismantling technician", 62),
    ("mb-034", None, "Chemical formulation and blending", "Essential", "Formulation operator", 57),
    ("mb-038", "Hotel Management & Front Office", "Guest handling and property operation", "Essential", "Owner-operator", 66),
    ("mb-040", "CAD/CAM Design", "Model preparation and slicing", "Essential", "Designer", 63),
]

# ===========================================================================
# 10. industry_mapping.csv  -> Package004 ONLY
# ===========================================================================
H_IND = ["mapping_id", "business_id", "business_name", "package004_dataset",
         "package004_opportunity_id", "package004_opportunity_name",
         "relationship", "data_source", "source_url", "collection_date",
         "confidence_score", "verification_status", "notes"]

# (business_id, P004 dataset, needle, relationship, conf, note)
IND_LINKS = [
    ("mb-001", "food_agro_processing_micro_enterprises", "Small-Scale Flour/Atta Milling Unit", "Adjacent", 66, "Closest Package004 milling counterpart; Package004 covers flour rather than paddy"),
    ("mb-002", "food_agro_processing_micro_enterprises", "Small-Scale Multi-Product Food Processing Unit", "Adjacent", 64, "No dedicated dal-milling opportunity in Package004 v1.0.0"),
    ("mb-003", "food_agro_processing_micro_enterprises", "Cold-Pressed Groundnut/Sesame Oil", "Same opportunity", 74, "Exact one-to-one counterpart"),
    ("mb-004", "food_agro_processing_micro_enterprises", "Turmeric Processing & Powder-Making Unit", "Same opportunity", 74, "Exact counterpart for the turmeric variant"),
    ("mb-004", "food_agro_processing_micro_enterprises", "Chilli Processing, Grading & Powder-Making Unit", "Same opportunity", 74, "Exact counterpart for the chilli variant"),
    ("mb-004", "food_agro_processing_micro_enterprises", "Masala Powder Manufacturing Unit (Small Scale)", "Same opportunity", 72, "Exact counterpart for the blended-masala variant"),
    ("mb-005", "food_agro_processing_micro_enterprises", "Small-Scale Millet Processing Unit", "Same opportunity", 73, "Exact one-to-one counterpart"),
    ("mb-006", "food_agro_processing_micro_enterprises", "Small-Scale Multi-Product Food Processing Unit", "Broader Package004 record", 66, "Fruit pulp falls inside the multi-product scope"),
    ("mb-009", "construction_skilled_trade_services", "Welding & Metal Fabrication", "Same opportunity", 72, "Exact one-to-one counterpart"),
    ("mb-012", "construction_skilled_trade_services", "Electrical Contracting", "Adjacent", 66, "Package004 covers contracting service; this is panel manufacture"),
    ("mb-014", "digital_technology_livelihoods", "Small IT Services Firm / Software Development Startup", "Same opportunity", 73, "Exact one-to-one counterpart"),
    ("mb-015", "digital_technology_livelihoods", "Small IT Services Firm / Software Development Startup", "Adjacent", 66, "Package004 does not separate product from services model"),
    ("mb-016", "digital_technology_livelihoods", "Data Analytics Services", "Adjacent", 64, "Closest Package004 counterpart; no dedicated AI opportunity exists there"),
    ("mb-017", "digital_technology_livelihoods", "Digital Marketing Agency", "Same opportunity", 73, "Exact one-to-one counterpart"),
    ("mb-018", "digital_technology_livelihoods", "Cloud Services Consulting", "Adjacent", 63, "Closest counterpart; Package004 has no hardware-service opportunity"),
    ("mb-019", "digital_technology_livelihoods", "Rural IT-Enabled Service Center / BPO-KPO Operator", "Same opportunity", 72, "Exact one-to-one counterpart"),
    ("mb-025", "china_inspired_adapted_opportunities", "Instagram Shopping / WhatsApp Business", "Channel counterpart", 62, "Package004 records the social-commerce channel used by artisan enterprises"),
    ("mb-029", "china_inspired_adapted_opportunities", "WhatsApp Group Buying", "Channel counterpart", 60, "Package004 records the community-order channel that drives last-mile volume"),
    ("mb-038", "china_inspired_adapted_opportunities", "Telangana Homestays", "Same opportunity", 70, "Exact one-to-one counterpart"),
]

# ===========================================================================
# 11. agriculture_business_mapping.csv  -> Package005
# ===========================================================================
H_AGB = ["mapping_id", "business_id", "business_name", "package005_crop_id",
         "package005_crop_name", "package005_processing_opportunity_id",
         "package005_processing_opportunity_name", "value_add_stage",
         "data_source", "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

# (business_id, crop needle | None, P005 processing needle | None, stage, conf, note)
AGB_LINKS = [
    ("mb-001", "Rice", "Rice Mill", "Primary Processing", 73, "Direct counterpart on both the crop and processing side"),
    ("mb-002", "Pigeon Pea", "Dal Mill", "Primary Processing", 72, "Toor is the principal dal-milling feedstock"),
    ("mb-002", "Chickpea", "Dal Mill", "Primary Processing", 71, "Chana dal is the second major line"),
    ("mb-003", "Groundnut", "Cold-Pressed Oil Unit", "Primary Processing", 73, "Direct counterpart on both sides"),
    ("mb-004", "Turmeric", "Turmeric Powder Unit", "Secondary Processing", 74, "Direct counterpart on both sides"),
    ("mb-004", "Chilli", "Chilli Powder Unit", "Secondary Processing", 74, "Direct counterpart on both sides"),
    ("mb-005", "Pearl Millet", "Millet Processing Unit", "Primary Processing", 71, "Direct counterpart on both sides"),
    ("mb-005", "Finger Millet", "Millet Processing Unit", "Primary Processing", 69, "Second millet line in the same unit"),
    ("mb-006", "Mango", "Fruit Pulp Unit", "Secondary Processing", 70, "Direct counterpart on both sides"),
    ("mb-006", "Tomato", "Fruit Pulp Unit", "Secondary Processing", 68, "Tomato paste runs on the same pulping line"),
    ("mb-027", None, "Cold Storage Facility", "Post-Harvest Infrastructure", 70, "Crop-agnostic infrastructure; serves multiple crops"),
    ("mb-030", None, "Food Packaging Unit", "Packaging", 68, "Crop-agnostic; packaging serves all processed food lines"),
    ("mb-033", None, "Vermicompost Unit", "Input Manufacturing", 69, "Crop-agnostic agricultural input"),
    ("mb-039", None, "Rice Mill", "Service to Production", 58, "Weak link: drone services support cultivation, not milling; retained to record the agriculture adjacency"),
]

# ===========================================================================
# 12. education_support_mapping.csv  -> Package002 + Package006
# ===========================================================================
H_EDU = ["mapping_id", "support_entity_type", "entity_name",
         "package002_institution_id", "package002_institution_name",
         "package006_provider_id", "package006_provider_name",
         "supports_business_categories", "support_nature", "data_source",
         "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

# (entity_type, entity_name, P002 needle|None, P006 needle|None, categories, nature, conf, note)
EDU_LINKS = [
    ("Technical University", "Jawaharlal Nehru Technological University Hyderabad", "Jawaharlal Nehru Technological University Hyderabad", None, "Engineering; Electronics; Industrial Automation", "Technical talent pipeline; incubation and innovation cell", 70, "Affiliating body for a large share of Telangana engineering colleges"),
    ("Central University", "University of Hyderabad", "University of Hyderabad", None, "Artificial Intelligence; Information Technology", "Research talent; entrepreneurship cell", 68, "Research-led rather than industry-facing"),
    ("State University", "Osmania University", "Osmania University", None, "Information Technology; Creative Industries; Education and Training", "Graduate talent pipeline", 66, "Largest general-education intake in Telangana"),
    ("State University", "Kakatiya University", "Kakatiya University", None, "Food Processing; Agriculture and Allied", "Regional graduate pipeline in north Telangana", 64, "Serves the Warangal industrial and agricultural belt"),
    ("ITI Network", "Industrial Training Institutes (ITI) -- Telangana", None, "Industrial Training Institutes (ITI) -- Telangana", "Engineering; Construction; Electric Vehicles", "Trade-certified shop-floor workforce", 70, "Package006 holds the provider record and its trade detail"),
    ("ITI Network", "Industrial Training Institutes (ITI) -- Andhra Pradesh", None, "Industrial Training Institutes (ITI) -- Andhra Pradesh", "Engineering; Construction; Electric Vehicles", "Trade-certified shop-floor workforce", 70, "Package006 holds the provider record and its trade detail"),
    ("Polytechnic Network", "Polytechnic Colleges (SBTET) -- Telangana", None, "Polytechnic Colleges (SBTET) -- Telangana", "Engineering; Electronics; Industrial Automation", "Diploma-level technician pipeline", 69, "Diploma holders are the standard supervisory intake for MSME manufacturing"),
    ("Polytechnic Network", "Polytechnic Colleges (SBTET) -- Andhra Pradesh", None, "Polytechnic Colleges (SBTET) -- Andhra Pradesh", "Engineering; Electronics; Industrial Automation", "Diploma-level technician pipeline", 69, "Diploma holders are the standard supervisory intake for MSME manufacturing"),
    ("Skill Institute", "National Skill Training Institutes (NSTI)", None, "National Skill Training Institutes (NSTI)", "Engineering; Textiles and Apparel", "Instructor training and advanced trade skills", 66, "Trains the trainers for the ITI network"),
    ("Skill Mission", "TASK -- Telangana Academy for Skill and Knowledge", None, "TASK -- Telangana Academy for Skill and Knowledge", "Information Technology; Artificial Intelligence", "Industry-aligned finishing programmes", 66, "Bridges the graduate-to-employable gap for technology roles"),
    ("Skill Corporation", "APSSDC -- Andhra Pradesh State Skill Development Corporation", None, "APSSDC -- Andhra Pradesh State Skill Development Corporation", "Engineering; Industrial Automation; Electric Vehicles", "State skilling delivery and industry partnership", 66, "Operates Siemens Centres of Excellence in Andhra Pradesh"),
    ("Construction Academy", "National Academy of Construction (NAC), Hyderabad", None, "National Academy of Construction (NAC), Hyderabad", "Construction", "Construction trade and supervisory training", 66, "Sector-specific; supports the construction MSME workforce"),
    ("IT Institute", "NIELIT -- Hyderabad Centre", None, "NIELIT -- Hyderabad Centre", "Information Technology; Electronics", "IT and electronics certification", 66, "Government IT-certification route for MSME staff"),
]

# ===========================================================================
# 13. district_business_mapping.csv  -> Package001
# ===========================================================================
H_DBM = ["mapping_id", "package001_dist_id", "dist_ref", "district_name",
         "state", "business_id", "business_name", "suitability_basis",
         "resource_strength", "market_access_score", "data_source",
         "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

# District-business suitability is asserted ONLY where a documented district
# characteristic drives it. Every row names that characteristic in
# suitability_basis. No blanket district x business cross-product is generated.
# (dist_ref, business_id, basis, resource_strength, market_access, conf)
DISTRICT_LINKS = [
    ("TG-NZB", "mb-004", "Nizamabad is a benchmark turmeric market yard; Package005 records it as a major turmeric district", "Very High", "High", 71),
    ("TG-NZB", "mb-001", "Major paddy-growing district with established milling activity", "High", "High", 69),
    ("AP-GUN", "mb-004", "Guntur hosts Asia's largest chilli market yard; Package005 records it as a major chilli district", "Very High", "Very High", 72),
    ("AP-GUN", "mb-002", "Significant pulse acreage in the district and adjoining belt", "High", "High", 67),
    ("AP-ATP", "mb-003", "Anantapur is India's largest groundnut district by area; Package005 records it", "Very High", "Medium", 71),
    ("AP-KUR", "mb-002", "Kurnool has substantial chickpea and pulse acreage per Package005", "High", "Medium", 68),
    ("AP-KUR", "mb-004", "Chilli and coriander acreage supports spice processing", "High", "Medium", 66),
    ("TG-KRM", "mb-001", "Karimnagar is a major paddy district with dense milling clusters", "Very High", "High", 70),
    ("TG-NLG", "mb-006", "Nalgonda sweet orange belt supplies juice and pulp processors per Package005", "High", "Medium", 68),
    ("TG-NLG", "mb-027", "Perishable horticulture output creates cold storage demand", "Medium", "Medium", 65),
    ("AP-KRI", "mb-006", "Krishna district mango belt (Nuzvid) supports pulp processing per Package005", "Very High", "High", 69),
    ("AP-EAS", "mb-003", "East Godavari coconut belt supports coconut oil extraction per Package005", "High", "High", 68),
    ("AP-WES", "mb-001", "West Godavari is among the highest-yield paddy districts", "Very High", "High", 70),
    ("TG-ADB", "mb-024", "Adilabad cotton belt supports downstream apparel activity per Package005", "High", "Low", 64),
    ("TG-WGL", "mb-024", "Warangal has an established textile and apparel cluster", "High", "Medium", 66),
    ("TG-HYD", "mb-014", "Hyderabad is the state's dominant IT services concentration", "Very High", "Very High", 74),
    ("TG-HYD", "mb-016", "T-Hub and the wider startup ecosystem support AI ventures", "Very High", "Very High", 71),
    ("TG-HYD", "mb-015", "Deepest access to incubation, talent and early-stage capital", "Very High", "Very High", 72),
    ("TG-HYD", "mb-036", "Established pharmaceutical and medical device ecosystem", "High", "Very High", 66),
    ("TG-HYD", "mb-032", "Urban e-waste generation volume supports recovery operations", "High", "Very High", 66),
    ("TG-RRD", "mb-008", "Rangareddy hosts substantial engineering and ancillary industry", "Very High", "High", 69),
    ("TG-RRD", "mb-030", "Manufacturing density creates derived packaging demand", "High", "High", 67),
    ("TG-SNG", "mb-009", "Sangareddy industrial corridor (Patancheru belt) supports fabrication", "High", "High", 67),
    ("TG-MDK", "mb-012", "Medak industrial area hosts electrical and engineering units", "High", "Medium", 65),
    ("AP-VIS", "mb-028", "Visakhapatnam port and industrial base support warehousing", "Very High", "Very High", 70),
    ("AP-VIS", "mb-031", "Urban and industrial plastic waste volume supports recycling", "High", "High", 66),
    ("AP-SRI", "mb-030", "Srikakulam cashew processing belt creates packaging demand per Package005", "Medium", "Low", 62),
    ("AP-CHI", "mb-006", "Chittoor is a major mango and tomato district per Package005", "Very High", "High", 69),
    ("AP-CHI", "mb-027", "High perishable output creates cold storage demand", "High", "Medium", 66),
    ("TG-MBN", "mb-005", "Mahbubnagar has significant millet and sorghum acreage per Package005", "High", "Low", 66),
    ("TG-KHM", "mb-004", "Khammam chilli acreage supports spice processing per Package005", "High", "Medium", 66),
    ("AP-PRA", "mb-002", "Prakasam has substantial pulse acreage per Package005", "High", "Medium", 66),
]

# ===========================================================================
# 15. export_opportunities.csv
# ===========================================================================
H_EXP = ["opportunity_id", "business_id", "business_name", "export_product",
         "destination_markets", "required_certifications", "applicable_standards",
         "export_readiness_barrier", "promotion_body", "data_source",
         "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

DGFT = "Directorate General of Foreign Trade"
DGFT_URL = "https://www.dgft.gov.in/"
APEDA = "APEDA (Agricultural and Processed Food Products Export Development Authority)"
APEDA_URL = "https://apeda.gov.in/"

EXPORTS = [
    ("mb-004", "Turmeric and chilli powder; spice blends", "UAE, United States, Bangladesh, Malaysia, United Kingdom", "FSSAI; IEC; Spices Board registration (RCMC); ISO 22000 or HACCP for most buyers", "Pesticide residue limits; aflatoxin limits; ASTA colour value", "Residue compliance and lab testing capability", "Spices Board of India", "Spices Board of India; APEDA", "https://www.indianspices.com/", 72, "India's largest spice export category; residue compliance is the binding constraint"),
    ("mb-003", "Cold-pressed groundnut and sesame oil", "United States, United Kingdom, UAE, Singapore", "FSSAI; IEC; APEDA registration; organic certification for the premium segment", "Aflatoxin limits; free fatty acid limits; labelling rules", "Aflatoxin control in groundnut sourcing", APEDA, APEDA, APEDA_URL, 68, "Premium health-oil positioning is what makes the export economics work"),
    ("mb-002", "Split pulses (toor, chana dal)", "United States, United Kingdom, UAE, Nepal, Sri Lanka", "FSSAI; IEC; APEDA registration; phytosanitary certificate", "Grain size and damage limits; moisture; fumigation requirements", "Consistent grade sorting at export volume", APEDA, APEDA, APEDA_URL, 67, "Export policy on pulses changes with domestic price conditions"),
    ("mb-001", "Milled rice (non-basmati and specialty)", "Bangladesh, UAE, Nepal, West Africa", "FSSAI; IEC; APEDA registration; phytosanitary certificate", "Broken percentage; moisture; fumigation", "Export policy volatility and quota conditions", APEDA, APEDA, APEDA_URL, 66, "Central export restrictions on non-basmati rice have been imposed and lifted repeatedly"),
    ("mb-006", "Aseptic mango and tomato pulp", "United States, European Union, UAE, Japan", "FSSAI; IEC; APEDA registration; HACCP; ISO 22000; buyer-specific audits", "Brix and acidity specification; microbiological limits; heavy metal limits", "Aseptic capability and audit-ready quality systems", APEDA, APEDA, APEDA_URL, 67, "EU market entry requires buyer-led social and quality audits beyond certification"),
    ("mb-024", "Ready-made garments", "United States, European Union, United Kingdom, UAE", "IEC; Apparel Export Promotion Council RCMC; buyer social compliance audit (e.g. SEDEX)", "Restricted substances lists; labelling and fibre content rules", "Social compliance audit readiness, not product quality", "Apparel Export Promotion Council", "Ministry of Textiles; AEPC", "https://texmin.nic.in/", 70, "Social compliance is the usual failure point for first-time garment exporters"),
    ("mb-025", "Handloom textiles and handicraft products", "United States, European Union, Japan, Australia", "IEC; Export Promotion Council for Handicrafts RCMC; GI certification where applicable", "Dye and restricted substance limits; country-of-origin marking", "Order-size consistency and lead-time reliability", "Export Promotion Council for Handicrafts", "Ministry of Textiles; EPCH", "https://texmin.nic.in/", 66, "GI tagging materially raises realisation in Western markets"),
    ("mb-026", "Technical textiles (medical, agro, geo)", "European Union, United States, Middle East", "IEC; buyer-specified product certification; ISO 9001; CE marking where applicable", "Product-specific performance standards; biocompatibility for medical grades", "Testing and certification infrastructure access", "Ministry of Textiles (National Technical Textiles Mission)", "Ministry of Textiles", "https://texmin.nic.in/", 62, "Certification cost is disproportionate for a micro unit; consortium approach is common"),
    ("mb-014", "Software development and IT services", "United States, United Kingdom, European Union, Australia, Singapore", "IEC not required for services; STPI or SEZ registration optional; ISO 27001 commonly required", "Data protection compliance (GDPR where EU clients); contractual SLAs", "Client acquisition and data-protection compliance, not physical certification", "Software Technology Parks of India; NASSCOM", "NASSCOM; Ministry of Electronics and IT", "https://nasscom.in/", 71, "Services export needs no physical certification; the barrier is trust and compliance"),
    ("mb-016", "AI products and services", "United States, United Kingdom, European Union, Singapore", "ISO 27001; SOC 2 for enterprise buyers; EU AI Act conformity for in-scope systems", "Data protection; emerging AI governance requirements", "Enterprise security certification and AI governance readiness", "NASSCOM", "NASSCOM", "https://nasscom.in/", 62, "EU AI Act introduces conformity obligations for high-risk systems from 2026 onward"),
    ("mb-010", "Tools, dies and moulds", "United States, European Union, Middle East, Southeast Asia", "IEC; ISO 9001; material test certificates; buyer-specific PPAP", "Dimensional tolerance specification; material traceability", "Metrology capability and documentation discipline", "Engineering Export Promotion Council", "EEPC India; Ministry of Commerce", "https://commerce.gov.in/", 64, "High value per kilogram makes air freight viable for this category"),
    ("mb-030", "Corrugated and flexible packaging", "Middle East, Africa, Sri Lanka, Nepal", "IEC; food-contact compliance where applicable; FSC certification for the premium segment", "Food-contact material rules; migration limits", "Freight cost relative to product value", "Ministry of Commerce and Industry", "Ministry of Commerce and Industry", "https://commerce.gov.in/", 60, "Low value-to-volume ratio limits viable export distance"),
]


# ------------------------------------------------------------------- builders
def rows_machinery():
    out = []
    for i, (bid, mname, role, p5, inv, autom, ess, conf) in enumerate(MACHINERY, start=1):
        if p5:
            mid, mnm = resolve(P005_MACH, "machinery_name", p5, "machinery_id", f"P005 machinery {p5}")
        else:
            mid, mnm = PV, PV
        note = ("Machine also exists in Package005 farm_machinery; referenced by id rather than "
                "restated" if p5 else
                "No Package005 counterpart: this machine is outside the agricultural machinery scope")
        out.append((f"mmap-{i:03d}", bid, BIZ_NAME[bid], mname, role, mid, mnm, inv,
                    autom, ess, DCMSME, MSME_URL, CD, str(conf), VST, note))
    return out


def rows_raw():
    out = []
    for i, (bid, mat, cls, crop, sup, avail, season, vol, conf) in enumerate(RAW, start=1):
        if crop:
            cid, cnm = resolve(P005_CROPS, "crop_name", crop, "crop_id", f"P005 crop {crop}")
            note = "Input is a Package005 crop; referenced by crop_id rather than restated"
        else:
            cid, cnm = PV, PV
            note = "Input is not an agricultural crop, so no Package005 reference applies"
        out.append((f"rmap-{i:03d}", bid, BIZ_NAME[bid], mat, cls, cid, cnm, sup,
                    avail, season, vol, DCMSME, MSME_URL, CD, str(conf), VST, note))
    return out


def rows_scheme():
    out = []
    for i, (bid, short, rel, stage, nature, conf) in enumerate(SCHEME_LINKS, start=1):
        sid, snm = resolve(P007_SCH, "short_name", short, "scheme_id", f"P007 scheme {short}")
        out.append((f"smap-{i:03d}", bid, BIZ_NAME[bid], sid, snm, rel, stage, nature,
                    "Package007_Government_Schemes reconciliation", "https://www.myscheme.gov.in/",
                    CD, str(conf), VST,
                    "Scheme detail (benefit, eligibility, process) lives in Package007 and is "
                    "reached by joining on package007_scheme_id; it is not duplicated here"))
    return out


def rows_skill():
    out = []
    for i, (bid, skill, role, crit, who, conf) in enumerate(SKILL_LINKS, start=1):
        if skill:
            sid, snm = resolve(P006_SKILLS, "skill_name", skill, "skill_id", f"P006 skill {skill}")
            note = ("Skill detail (NSQF level, duration, training route) lives in Package006 and "
                    "is reached by joining on package006_skill_id; it is not duplicated here")
        else:
            sid, snm = PV, PV
            note = ("No Package006 v1.0.0 skill record matches this requirement, so the reference "
                    "is left unasserted rather than pointed at an approximate skill")
        out.append((f"kmap-{i:03d}", bid, BIZ_NAME[bid], sid, snm, role, crit, who,
                    "Package006_Skills_and_Training reconciliation", "https://msde.gov.in/",
                    CD, str(conf), VST, note))
    return out


def rows_industry():
    out = []
    for i, (bid, dsname, needle, rel, conf, note) in enumerate(IND_LINKS, start=1):
        rows = P004[dsname]
        key = "adapted_indian_concept" if dsname == "china_inspired_adapted_opportunities" else "name"
        oid, onm = resolve(rows, key, needle, "id", f"P004 {dsname} {needle}")
        out.append((f"imap-{i:03d}", bid, BIZ_NAME[bid], dsname, oid, onm, rel,
                    "Package004_Industries reconciliation", "https://msme.gov.in/",
                    CD, str(conf), VST, note))
    return out


def rows_agri():
    out = []
    for i, (bid, crop, proc, stage, conf, note) in enumerate(AGB_LINKS, start=1):
        cid, cnm = (resolve(P005_CROPS, "crop_name", crop, "crop_id", f"P005 crop {crop}")
                    if crop else (PV, PV))
        pid, pnm = (resolve(P005_PROC, "opportunity_name", proc, "opportunity_id", f"P005 proc {proc}")
                    if proc else (PV, PV))
        out.append((f"amap-{i:03d}", bid, BIZ_NAME[bid], cid, cnm, pid, pnm, stage,
                    "Package005_Agriculture reconciliation", "https://agricoop.gov.in/",
                    CD, str(conf), VST, note))
    return out


def rows_edu():
    out = []
    for i, (etype, ename, p2, p6, cats, nature, conf, note) in enumerate(EDU_LINKS, start=1):
        uid, unm = (resolve(P002_UNIV, "name", p2, "id", f"P002 institution {p2}")
                    if p2 else (PV, PV))
        pid, pnm = (resolve(P006_PROV, "provider_name", p6, "provider_id", f"P006 provider {p6}")
                    if p6 else (PV, PV))
        out.append((f"emap-{i:03d}", etype, ename, uid, unm, pid, pnm, cats, nature,
                    "Package002_Education and Package006 reconciliation",
                    "https://www.education.gov.in/", CD, str(conf), VST, note))
    return out


def rows_district():
    by_ref = {d["dist_ref"]: d for d in P001_DIST}
    out = []
    for i, (ref, bid, basis, res, mkt, conf) in enumerate(DISTRICT_LINKS, start=1):
        if ref not in by_ref:
            sys.exit(f"FATAL: dist_ref {ref!r} not found in Package001 district.csv")
        d = by_ref[ref]
        state = "Telangana" if ref.startswith("TG") else "Andhra Pradesh"
        out.append((f"dmap-{i:03d}", d["dist_id"], ref, d["district_name"], state,
                    bid, BIZ_NAME[bid], basis, res, mkt,
                    "Package001_Geography district master; Package005 crop district attribution",
                    MSME_URL, CD, str(conf), VST,
                    "Suitability is asserted only where a documented district characteristic "
                    "drives it; no blanket district-business cross-product is generated"))
    return out


def rows_export():
    out = []
    for i, (bid, prod, dest, certs, stds, barrier, body, src, url, conf, note) in enumerate(EXPORTS, start=1):
        out.append((f"exp-{i:03d}", bid, BIZ_NAME[bid], prod, dest, certs, stds,
                    barrier, body, src, url, CD, str(conf), VST, note))
    return out


if __name__ == "__main__":
    print("Generating Package008_MSME mapping datasets:\n")
    write("machinery_mapping.csv", H_MACH, rows_machinery())
    write("raw_material_mapping.csv", H_RAW, rows_raw())
    write("scheme_mapping.csv", H_SCHM, rows_scheme())
    write("skill_mapping.csv", H_SKM, rows_skill())
    write("industry_mapping.csv", H_IND, rows_industry())
    write("agriculture_business_mapping.csv", H_AGB, rows_agri())
    write("education_support_mapping.csv", H_EDU, rows_edu())
    write("district_business_mapping.csv", H_DBM, rows_district())
    write("export_opportunities.csv", H_EXP, rows_export())
    print("\nMapping generation complete.")
