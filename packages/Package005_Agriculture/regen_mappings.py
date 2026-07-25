#!/usr/bin/env python3
"""
Package005_Agriculture v1.0.0 — Mapping Dataset Regeneration

Rebuilds the three relational mapping datasets after the crops.csv expansion
(35 -> 45 crops) renumbered crop_id values:

  - crop_soil_mapping.csv      crop_id -> soil_id      (suitability scored)
  - crop_climate_mapping.csv   crop_id -> climate_zone_id (yield potential)
  - agri_business_mapping.csv  crop_id -> processing -> Package004 opportunity -> Package006 skill

Cross-package foreign keys are REAL values read from the released packages:
  - Package004_Industries  opportunity names (datasets/*.csv `name` column)
  - Package006_Skills_and_Training  skill_id UUIDs (datasets/skills.csv)

Where no genuine counterpart exists in the referenced package, the bare sentinel
PENDING_VERIFICATION is written rather than an invented link.
"""

import csv
from pathlib import Path

COLLECTION_DATE = "2026-07-24"
VST = "VST-NEEDS_REVIEW"
PV = "PENDING_VERIFICATION"
DATASETS = Path("datasets")

ICAR = "ICAR; Ministry of Agriculture & Farmers Welfare"
ICAR_URL = "https://icar.org.in/"

# --- Canonical soil ids (soil_types.csv) --------------------------------------
BLACK, RED, ALLUV, LAT, SANDY, LOAM, CLAY, SALINE, ACID, ALKALI = (
    "st-001", "st-002", "st-003", "st-004", "st-005",
    "st-006", "st-007", "st-008", "st-009", "st-010",
)
SOIL_NAME = {
    BLACK: "Black Soil", RED: "Red Soil", ALLUV: "Alluvial", LAT: "Laterite",
    SANDY: "Sandy", LOAM: "Loamy", CLAY: "Clay", SALINE: "Saline",
    ACID: "Acidic", ALKALI: "Alkaline",
}

# --- Canonical climate zone ids (climate_zones.csv) ---------------------------
TROP, SUBTROP, TEMP, ARID, SEMIARID, DRY, WET, HIGH = (
    "cz-001", "cz-002", "cz-003", "cz-004",
    "cz-005", "cz-006", "cz-007", "cz-008",
)
ZONE_NAME = {
    TROP: "Tropical", SUBTROP: "Sub-tropical", TEMP: "Temperate", ARID: "Arid",
    SEMIARID: "Semi-arid", DRY: "Dry", WET: "Wet", HIGH: "Highland",
}

# --- Crop registry: must match crops.csv exactly ------------------------------
CROPS = {
    "crop-001": "Rice", "crop-002": "Wheat", "crop-003": "Maize", "crop-004": "Barley",
    "crop-005": "Pearl Millet", "crop-006": "Sorghum", "crop-007": "Finger Millet",
    "crop-008": "Foxtail Millet", "crop-009": "Chickpea", "crop-010": "Pigeon Pea",
    "crop-011": "Moong (Green Gram)", "crop-012": "Urad (Black Gram)", "crop-013": "Lentil",
    "crop-014": "Groundnut", "crop-015": "Soybean", "crop-016": "Sunflower",
    "crop-017": "Safflower", "crop-018": "Mustard", "crop-019": "Sugarcane",
    "crop-020": "Cotton", "crop-021": "Tobacco", "crop-022": "Jute",
    "crop-023": "Tomato", "crop-024": "Potato", "crop-025": "Onion", "crop-026": "Brinjal",
    "crop-027": "Okra (Lady Finger)", "crop-028": "Cabbage", "crop-029": "Mango",
    "crop-030": "Banana", "crop-031": "Citrus (Sweet Orange)", "crop-032": "Grapes",
    "crop-033": "Guava", "crop-034": "Pomegranate", "crop-035": "Turmeric",
    "crop-036": "Chilli", "crop-037": "Black Pepper", "crop-038": "Cardamom",
    "crop-039": "Coriander", "crop-040": "Cumin", "crop-041": "Ginger",
    "crop-042": "Ashwagandha", "crop-043": "Tulsi (Holy Basil)", "crop-044": "Coconut",
    "crop-045": "Cashew",
}


def band(score):
    """ICAR-style suitability band from a 0-100 suitability score."""
    if score >= 85:
        return "Optimal"
    if score >= 70:
        return "Suitable"
    if score >= 55:
        return "Marginal"
    return "Unsuitable"


# =============================================================================
# 1. crop_soil_mapping.csv — every crop gets its optimal soil, plus alternates
# =============================================================================
H_CSM = [
    "mapping_id", "crop_id", "crop_name", "soil_id", "soil_name",
    "suitability_score", "suitability_level", "data_source", "source_url",
    "collection_date", "confidence_score", "verification_status", "notes",
]

# (crop_id, soil_id, score, confidence, note)
SOIL_PAIRS = [
    ("crop-001", ALLUV, 95, 78, "Puddled alluvial lowland is the classic rice situation"),
    ("crop-001", CLAY, 82, 75, "High water retention suits transplanted rice"),
    ("crop-002", ALLUV, 93, 78, "Indo-Gangetic alluvium is the principal wheat base"),
    ("crop-002", LOAM, 85, 76, "Well-drained loam performs comparably under irrigation"),
    ("crop-003", LOAM, 90, 77, "Free-draining loam avoids waterlogging sensitivity"),
    ("crop-003", RED, 74, 74, "Workable with organic matter and fertiliser correction"),
    ("crop-004", LOAM, 86, 73, "Tolerates lighter soils than wheat"),
    ("crop-004", ALKALI, 66, 70, "Comparatively tolerant of mild alkalinity"),
    ("crop-005", SANDY, 88, 76, "Sandy light soils suit the crop's drought strategy"),
    ("crop-005", RED, 76, 74, "Common on shallow red soils in rainfed tracts"),
    ("crop-006", BLACK, 88, 76, "Deep black soils supply the stored moisture the crop needs"),
    ("crop-006", RED, 74, 74, "Rainfed red-soil tracts of the Deccan"),
    ("crop-007", RED, 86, 74, "Traditional red-soil crop of the southern plateau"),
    ("crop-007", LAT, 70, 71, "Grown on lateritic uplands with amendment"),
    ("crop-008", RED, 85, 70, "Shallow red soils of the rainfed south"),
    ("crop-008", SANDY, 74, 69, "Tolerates light textures on low fertility"),
    ("crop-009", BLACK, 92, 77, "Residual-moisture rabi crop on deep black soils"),
    ("crop-009", LOAM, 78, 75, "Requires assured drainage to avoid wilt"),
    ("crop-010", BLACK, 90, 76, "Deep soils accommodate the long taproot"),
    ("crop-010", RED, 74, 74, "Widely intercropped on red soils"),
    ("crop-011", LOAM, 85, 75, "Short duration; needs free drainage"),
    ("crop-011", SANDY, 74, 73, "Suits light soils in summer catch-crop slots"),
    ("crop-012", LOAM, 85, 75, "Standard kharif situation"),
    ("crop-012", CLAY, 68, 72, "Tolerates heavier soils better than moong"),
    ("crop-013", LOAM, 88, 75, "Cool-season crop on well-drained loam"),
    ("crop-013", ALLUV, 84, 74, "Grown widely on Indo-Gangetic alluvium"),
    ("crop-014", SANDY, 90, 77, "Light soils allow pod development and easy harvest"),
    ("crop-014", RED, 78, 75, "Anantapur red sandy loam tract"),
    ("crop-015", BLACK, 90, 76, "Malwa plateau black soils dominate acreage"),
    ("crop-015", LOAM, 78, 74, "Performs on loam with assured drainage"),
    ("crop-016", LOAM, 87, 75, "Well-drained loam under rabi irrigation"),
    ("crop-016", BLACK, 76, 74, "Grown on black soils in the Deccan rabi season"),
    ("crop-017", BLACK, 90, 71, "Residual-moisture crop; needs deep black soil"),
    ("crop-017", RED, 62, 68, "Shallow red soils give materially lower yield"),
    ("crop-018", LOAM, 88, 75, "Standard rabi oilseed situation"),
    ("crop-018", ALLUV, 84, 74, "Northern alluvial belt"),
    ("crop-019", ALLUV, 94, 77, "Deep alluvium with assured irrigation"),
    ("crop-019", BLACK, 82, 75, "Grown on black soils with adequate irrigation"),
    ("crop-020", BLACK, 93, 77, "Black cotton soil is the definitive situation"),
    ("crop-020", RED, 72, 74, "Rainfed red-soil cotton with lower yield"),
    ("crop-021", LOAM, 86, 72, "Light loam supports leaf quality"),
    ("crop-021", RED, 74, 70, "Southern light-soil tobacco tracts"),
    ("crop-022", ALLUV, 92, 70, "Lower Ganga alluvial floodplain"),
    ("crop-022", CLAY, 72, 68, "Tolerates heavy soils under high rainfall"),
    ("crop-023", LOAM, 90, 76, "Free drainage is critical for root health"),
    ("crop-023", RED, 76, 74, "Widely grown on red soils in the south"),
    ("crop-024", SANDY, 90, 77, "Loose light soils permit tuber expansion"),
    ("crop-024", LOAM, 84, 76, "Sandy loam is the preferred texture"),
    ("crop-025", LOAM, 88, 76, "Well-drained loam for bulb development"),
    ("crop-025", RED, 76, 74, "Kurnool and Chittoor red-soil onion tracts"),
    ("crop-026", LOAM, 86, 73, "Long-duration vegetable on fertile loam"),
    ("crop-026", ALLUV, 82, 72, "Alluvial vegetable belts"),
    ("crop-027", LOAM, 86, 73, "Standard kharif vegetable situation"),
    ("crop-027", ALLUV, 80, 72, "Alluvial peri-urban belts"),
    ("crop-028", LOAM, 87, 73, "Cool-season crop on fertile loam"),
    ("crop-028", ALLUV, 80, 72, "Alluvial vegetable belts"),
    ("crop-029", ALLUV, 88, 77, "Deep well-drained alluvium for orchard establishment"),
    ("crop-029", RED, 80, 75, "Krishna and Chittoor red-soil mango belts"),
    ("crop-030", ALLUV, 92, 76, "Deep fertile alluvium with high water availability"),
    ("crop-030", LOAM, 82, 74, "Requires assured irrigation and drainage"),
    ("crop-031", LOAM, 88, 75, "Deep well-drained soil; citrus is drainage-sensitive"),
    ("crop-031", RED, 78, 74, "Nalgonda sweet orange tract"),
    ("crop-032", BLACK, 86, 75, "Deccan black-soil vineyards"),
    ("crop-032", LOAM, 82, 74, "Well-drained loam with trellis systems"),
    ("crop-033", LOAM, 86, 73, "Hardy; tolerates a wide texture range"),
    ("crop-033", RED, 80, 72, "Common on red soils across the south"),
    ("crop-034", LOAM, 86, 73, "Free drainage reduces bacterial blight pressure"),
    ("crop-034", SANDY, 78, 72, "Light soils in the arid and semi-arid belt"),
    ("crop-035", RED, 90, 77, "Nizamabad and Duggirala red-soil turmeric tracts"),
    ("crop-035", LOAM, 84, 76, "Rich well-drained loam for rhizome development"),
    ("crop-036", BLACK, 90, 77, "Guntur black-soil chilli belt"),
    ("crop-036", RED, 78, 75, "Rainfed red-soil chilli in Telangana"),
    ("crop-037", LAT, 90, 74, "Lateritic Western Ghats plantation soils"),
    ("crop-037", RED, 76, 72, "Grown on red soils in transitional tracts"),
    ("crop-038", LAT, 88, 72, "Shade-grown on lateritic hill soils"),
    ("crop-038", ACID, 76, 70, "Tolerates the acidity typical of its habitat"),
    ("crop-039", BLACK, 86, 73, "Rabi seed-spice crop on black soils"),
    ("crop-039", LOAM, 82, 72, "Loam suits leafy coriander production"),
    ("crop-040", SANDY, 88, 73, "Light sandy loam of the arid rabi belt"),
    ("crop-040", LOAM, 76, 71, "Requires very good drainage"),
    ("crop-041", LOAM, 88, 73, "Rich friable loam for rhizome expansion"),
    ("crop-041", LAT, 76, 71, "Lateritic tracts of Kerala and the Northeast"),
    ("crop-042", SANDY, 88, 70, "Light dry soils suit root development"),
    ("crop-042", RED, 74, 68, "Grown on red soils under rainfed conditions"),
    ("crop-043", LOAM, 86, 66, "General-purpose loam; widely adaptable"),
    ("crop-043", RED, 76, 65, "Adaptable to red soils"),
    ("crop-044", SANDY, 90, 74, "Coastal sandy soils are the classic situation"),
    ("crop-044", ALLUV, 82, 73, "Coastal deltaic alluvium of the Godavari belt"),
    ("crop-045", LAT, 88, 73, "Lateritic coastal uplands"),
    ("crop-045", RED, 78, 72, "Srikakulam and Vizianagaram red-soil tracts"),
]


def build_soil_mapping():
    rows = []
    for i, (crop_id, soil_id, score, conf, note) in enumerate(SOIL_PAIRS, start=1):
        rows.append((
            f"csm-{i:03d}", crop_id, CROPS[crop_id], soil_id, SOIL_NAME[soil_id],
            str(score), band(score), ICAR, ICAR_URL, COLLECTION_DATE,
            str(conf), VST, note,
        ))
    return rows


# =============================================================================
# 2. crop_climate_mapping.csv — every crop against its agro-climatic zones
# =============================================================================
H_CCM = [
    "mapping_id", "crop_id", "crop_name", "climate_zone_id", "climate_zone_name",
    "season", "yield_potential", "risk_level", "primary_climatic_risk",
    "data_source", "source_url", "collection_date", "confidence_score",
    "verification_status", "notes",
]

# (crop_id, zone_id, season, potential, risk, climatic_risk, confidence)
CLIMATE_PAIRS = [
    ("crop-001", TROP, "Kharif", "Optimal", "Low", "Late-monsoon deficit at panicle initiation", 77),
    ("crop-001", WET, "Kharif", "Good", "Medium", "Submergence and flood damage", 75),
    ("crop-002", TEMP, "Rabi", "Optimal", "Low", "Terminal heat stress at grain filling", 78),
    ("crop-002", SUBTROP, "Rabi", "Good", "Medium", "Early onset of summer temperatures", 76),
    ("crop-003", SUBTROP, "Kharif", "Optimal", "Low", "Dry spell at tasselling", 76),
    ("crop-003", SEMIARID, "Kharif", "Good", "Medium", "Erratic rainfall distribution", 74),
    ("crop-004", TEMP, "Rabi", "Optimal", "Low", "Unseasonal warm spells", 73),
    ("crop-004", ARID, "Rabi", "Marginal", "High", "Moisture deficit through grain fill", 70),
    ("crop-005", ARID, "Kharif", "Good", "Medium", "Extended intra-season dry spells", 75),
    ("crop-005", SEMIARID, "Kharif", "Optimal", "Low", "Delayed monsoon onset", 76),
    ("crop-006", SEMIARID, "Kharif", "Optimal", "Low", "Mid-season drought", 76),
    ("crop-006", DRY, "Rabi", "Good", "Medium", "Residual-moisture exhaustion", 74),
    ("crop-007", SEMIARID, "Kharif", "Optimal", "Low", "Erratic rainfall at grain fill", 74),
    ("crop-007", HIGH, "Kharif", "Good", "Medium", "Cold at maturity in higher elevations", 70),
    ("crop-008", SEMIARID, "Kharif", "Optimal", "Low", "Short dry spells (crop escapes via early maturity)", 70),
    ("crop-008", ARID, "Kharif", "Good", "Medium", "Severe moisture deficit", 68),
    ("crop-009", DRY, "Rabi", "Optimal", "Low", "Terminal drought and heat", 77),
    ("crop-009", SEMIARID, "Rabi", "Good", "Medium", "Insufficient residual moisture", 74),
    ("crop-010", SEMIARID, "Kharif", "Optimal", "Medium", "Excess rain at flowering causes pod drop", 76),
    ("crop-010", DRY, "Kharif", "Good", "Medium", "Long-duration exposure to late drought", 74),
    ("crop-011", SEMIARID, "Kharif", "Good", "Medium", "Rain at maturity causes pod shattering", 75),
    ("crop-011", DRY, "Summer", "Good", "Medium", "Heat stress at flowering", 73),
    ("crop-012", SUBTROP, "Kharif", "Good", "Medium", "Rain during pod maturity", 75),
    ("crop-012", TROP, "Rabi", "Good", "Low", "Limited cool-season window", 73),
    ("crop-013", TEMP, "Rabi", "Optimal", "Low", "Terminal heat", 75),
    ("crop-013", SUBTROP, "Rabi", "Good", "Medium", "Early summer onset", 73),
    ("crop-014", SEMIARID, "Kharif", "Optimal", "Medium", "Dry spell at pod formation", 77),
    ("crop-014", DRY, "Rabi", "Good", "Low", "Requires irrigation in rabi", 75),
    ("crop-015", SUBTROP, "Kharif", "Optimal", "Medium", "Excess rain causes root rot", 76),
    ("crop-015", SEMIARID, "Kharif", "Good", "High", "Moisture deficit at pod fill", 74),
    ("crop-016", DRY, "Rabi", "Optimal", "Low", "Heat at seed fill", 75),
    ("crop-016", SEMIARID, "Kharif", "Good", "Medium", "Rain at flowering disrupts pollination", 73),
    ("crop-017", DRY, "Rabi", "Optimal", "Medium", "Residual-moisture exhaustion", 71),
    ("crop-017", SEMIARID, "Rabi", "Marginal", "High", "Inadequate stored moisture", 68),
    ("crop-018", TEMP, "Rabi", "Optimal", "Low", "Warm spells during siliqua fill", 75),
    ("crop-018", SUBTROP, "Rabi", "Good", "Medium", "Aphid pressure in warm winters", 73),
    ("crop-019", TROP, "Annual", "Optimal", "Low", "Water deficit in the summer months", 77),
    ("crop-019", SUBTROP, "Annual", "Good", "Medium", "Frost risk in northern belts", 75),
    ("crop-020", SEMIARID, "Kharif", "Optimal", "Medium", "Rain at boll opening degrades lint", 77),
    ("crop-020", DRY, "Kharif", "Good", "High", "Terminal drought on rainfed cotton", 75),
    ("crop-021", SUBTROP, "Rabi", "Good", "Medium", "Unseasonal rain damages cured leaf", 72),
    ("crop-021", TROP, "Rabi", "Good", "Medium", "High humidity raises disease pressure", 70),
    ("crop-022", WET, "Kharif", "Optimal", "Medium", "Flooding during retting stage", 70),
    ("crop-022", TROP, "Kharif", "Good", "Medium", "Insufficient rainfall for fibre quality", 68),
    ("crop-023", SUBTROP, "Rabi", "Optimal", "Medium", "Frost and low night temperature", 76),
    ("crop-023", TROP, "Kharif", "Good", "High", "Heavy rain and high disease pressure", 74),
    ("crop-024", TEMP, "Rabi", "Optimal", "Medium", "Frost damage to haulm", 77),
    ("crop-024", SUBTROP, "Rabi", "Good", "Medium", "Warm spells trigger late blight", 75),
    ("crop-025", DRY, "Rabi", "Optimal", "Low", "Unseasonal rain at bulb maturity", 76),
    ("crop-025", SEMIARID, "Kharif", "Good", "High", "Waterlogging causes bulb rot", 74),
    ("crop-026", TROP, "Year Round", "Optimal", "Low", "Extreme heat reduces fruit set", 73),
    ("crop-026", SUBTROP, "Kharif", "Good", "Medium", "Cold checks growth in winter", 72),
    ("crop-027", TROP, "Kharif", "Optimal", "Low", "High temperature causes fruit fibrousness", 73),
    ("crop-027", SUBTROP, "Summer", "Good", "Medium", "Cold limits the winter window", 72),
    ("crop-028", TEMP, "Rabi", "Optimal", "Low", "Heat causes bolting and loose heads", 73),
    ("crop-028", SUBTROP, "Rabi", "Good", "Medium", "Warm winters reduce head compactness", 72),
    ("crop-029", TROP, "Perennial", "Optimal", "Medium", "Unseasonal rain at flowering causes fruit drop", 77),
    ("crop-029", SUBTROP, "Perennial", "Good", "Medium", "Frost injury to young flush", 75),
    ("crop-030", TROP, "Perennial", "Optimal", "Medium", "Cyclonic wind causes plant toppling", 76),
    ("crop-030", SUBTROP, "Perennial", "Good", "High", "Cold checks bunch development", 74),
    ("crop-031", SUBTROP, "Perennial", "Optimal", "Medium", "Moisture stress causes fruit drop", 75),
    ("crop-031", DRY, "Perennial", "Good", "Medium", "Requires assured irrigation", 74),
    ("crop-032", DRY, "Perennial", "Optimal", "Medium", "Rain at berry ripening causes cracking and rot", 75),
    ("crop-032", SEMIARID, "Perennial", "Good", "High", "Unseasonal rain during harvest", 73),
    ("crop-033", TROP, "Perennial", "Optimal", "Low", "Fruit fly pressure in humid periods", 73),
    ("crop-033", SUBTROP, "Perennial", "Good", "Low", "Cold checks off-season cropping", 72),
    ("crop-034", SEMIARID, "Perennial", "Optimal", "Medium", "Humidity drives bacterial blight", 73),
    ("crop-034", ARID, "Perennial", "Good", "Medium", "Water scarcity limits fruit size", 71),
    ("crop-035", TROP, "Kharif", "Optimal", "Low", "Deficient rainfall in the rhizome bulking phase", 77),
    ("crop-035", SUBTROP, "Kharif", "Good", "Medium", "Requires supplementary irrigation", 74),
    ("crop-036", SEMIARID, "Kharif", "Optimal", "Medium", "Rain during drying degrades colour value", 77),
    ("crop-036", DRY, "Kharif", "Good", "Medium", "Thrips and mite pressure in dry spells", 75),
    ("crop-037", WET, "Perennial", "Optimal", "Medium", "Quick wilt (foot rot) in waterlogged conditions", 74),
    ("crop-037", TROP, "Perennial", "Good", "Medium", "Insufficient rainfall for spike development", 72),
    ("crop-038", HIGH, "Perennial", "Optimal", "Medium", "Drought in the hill capsule-fill period", 72),
    ("crop-038", WET, "Perennial", "Good", "Medium", "Excess rain causes capsule rot", 70),
    ("crop-039", DRY, "Rabi", "Optimal", "Low", "Powdery mildew in humid winters", 73),
    ("crop-039", SEMIARID, "Rabi", "Good", "Medium", "Moisture deficit at seed fill", 71),
    ("crop-040", ARID, "Rabi", "Optimal", "Medium", "Blight and wilt in cloudy humid weather", 73),
    ("crop-040", SEMIARID, "Rabi", "Good", "Medium", "Unseasonal rain at maturity", 71),
    ("crop-041", TROP, "Kharif", "Optimal", "Medium", "Rhizome rot under waterlogging", 73),
    ("crop-041", WET, "Kharif", "Good", "High", "Excess rainfall drives soft rot", 71),
    ("crop-042", SEMIARID, "Rabi", "Optimal", "Low", "Excess moisture causes root rot", 70),
    ("crop-042", ARID, "Rabi", "Good", "Medium", "Severe moisture deficit reduces root yield", 68),
    ("crop-043", TROP, "Kharif", "Optimal", "Low", "Waterlogging causes wilting", 66),
    ("crop-043", SUBTROP, "Kharif", "Good", "Low", "Frost injury in northern winters", 65),
    ("crop-044", TROP, "Perennial", "Optimal", "Medium", "Cyclonic wind damage in coastal belts", 74),
    ("crop-044", WET, "Perennial", "Good", "Medium", "Bud rot pressure in prolonged wet weather", 72),
    ("crop-045", TROP, "Perennial", "Optimal", "Medium", "Rain at flowering causes flower and nut drop", 73),
    ("crop-045", WET, "Perennial", "Good", "Medium", "Tea mosquito bug pressure in humid conditions", 71),
]


def build_climate_mapping():
    rows = []
    for i, (crop_id, zone_id, season, pot, risk, crisk, conf) in enumerate(CLIMATE_PAIRS, start=1):
        rows.append((
            f"ccm-{i:03d}", crop_id, CROPS[crop_id], zone_id, ZONE_NAME[zone_id],
            season, pot, risk, crisk, ICAR, ICAR_URL, COLLECTION_DATE,
            str(conf), VST,
            "Yield potential is a relative agro-climatic rating, not an absolute tonnage",
        ))
    return rows


# =============================================================================
# 3. agri_business_mapping.csv — the cross-package spine of the package
# =============================================================================
H_ABM = [
    "mapping_id", "crop_id", "crop_name", "processing_opportunity_id",
    "processing_opportunity_name", "package004_opportunity_name",
    "package006_skill_id", "package006_skill_name", "value_add_stage",
    "data_source", "source_url", "collection_date", "confidence_score",
    "verification_status", "notes",
]

# Real Package006_Skills_and_Training skill_id values (datasets/skills.csv)
SK_FOOD = "e9a9d72b-0c80-4932-b907-ffc466d58717"   # Food Processing & Preservation
SK_ORG = "28856a79-9005-4630-92b2-17ace673fe72"    # Organic Farming
SK_PREC = "6b7f03f2-6f23-4fbb-9daf-b13d8b85d4b8"   # Precision Agriculture & IoT
SK_MODERN = "6e1063d5-3c2e-4c49-a8c9-59aa381554a7"  # Modern Farming Techniques
SKILL_NAME = {
    SK_FOOD: "Food Processing & Preservation",
    SK_ORG: "Organic Farming",
    SK_PREC: "Precision Agriculture & IoT",
    SK_MODERN: "Modern Farming Techniques",
}

MOFPI = "Ministry of Food Processing Industries (MoFPI)"
MOFPI_URL = "https://mofpi.gov.in/"
SPICES = "ICAR-IISR; Spices Board of India"
SPICES_URL = "https://www.indianspices.com/"

# (crop_id, ap_id, ap_name, pkg004_name, skill_id, stage, source, url, conf, note)
BUSINESS_PAIRS = [
    ("crop-001", "ap-001", "Rice Mill", PV, SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 70,
     "No rice-milling opportunity exists in Package004 v1.0.0; link left as sentinel"),
    ("crop-002", "ap-012", "Food Packaging Unit", "Small-Scale Flour/Atta Milling Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 72,
     "Package004 atta milling unit is the direct wheat-milling counterpart"),
    ("crop-005", "ap-004", "Millet Processing Unit", "Small-Scale Millet Processing Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 72,
     "Pearl millet is a principal feedstock for the Package004 millet unit"),
    ("crop-006", "ap-004", "Millet Processing Unit", "Small-Scale Millet Processing Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 71,
     "Sorghum feeds the same dehulling and flour line"),
    ("crop-007", "ap-004", "Millet Processing Unit", "FPO-Level Primary Millet Processing Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 71,
     "Finger millet aggregation suits the FPO-scale unit"),
    ("crop-008", "ap-004", "Millet Processing Unit", "FPO-Level Primary Millet Processing Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 69,
     "Foxtail millet is a nutri-cereal line in the same unit"),
    ("crop-009", "ap-002", "Dal Mill", PV, SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 70,
     "No dal-milling opportunity exists in Package004 v1.0.0; link left as sentinel"),
    ("crop-010", "ap-002", "Dal Mill", PV, SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 70,
     "Pigeon pea is the primary toor dal feedstock; no Package004 counterpart yet"),
    ("crop-014", "ap-003", "Cold-Pressed Oil Unit", "Cold-Pressed Groundnut/Sesame Oil (Kachi Ghani) Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 74,
     "Direct one-to-one match with the Package004 kachi ghani unit"),
    ("crop-018", "ap-003", "Cold-Pressed Oil Unit", "Cold-Pressed Groundnut/Sesame Oil (Kachi Ghani) Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 71,
     "Mustard runs on the same cold-press line as groundnut and sesame"),
    ("crop-019", "ap-010", "Jaggery Unit", PV, SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 69,
     "No jaggery opportunity exists in Package004 v1.0.0; link left as sentinel"),
    ("crop-023", "ap-007", "Fruit Pulp Unit", "Small-Scale Multi-Product Food Processing Unit", SK_FOOD, "Secondary Processing", MOFPI, MOFPI_URL, 68,
     "Tomato paste and puree fall within the Package004 multi-product unit scope"),
    ("crop-024", "ap-011", "Cold Storage Facility", PV, SK_FOOD, "Post-Harvest Infrastructure", "Ministry of Agriculture & Farmers Welfare", "https://agricoop.gov.in/", 67,
     "Cold storage is infrastructure, not an enterprise line in Package004 v1.0.0"),
    ("crop-025", "ap-011", "Cold Storage Facility", PV, SK_FOOD, "Post-Harvest Infrastructure", "Ministry of Agriculture & Farmers Welfare", "https://agricoop.gov.in/", 67,
     "Onion storage reduces distress selling; no Package004 counterpart"),
    ("crop-029", "ap-008", "Pickle Unit", "Andhra-Style Pickle (Avakaya/Mixed) Making Unit", SK_FOOD, "Secondary Processing", MOFPI, MOFPI_URL, 73,
     "Raw mango is the defining input for the Package004 avakaya unit"),
    ("crop-029", "ap-007", "Fruit Pulp Unit", "Small-Scale Multi-Product Food Processing Unit", SK_FOOD, "Secondary Processing", MOFPI, MOFPI_URL, 69,
     "Ripe mango pulp is the second value path from the same crop"),
    ("crop-033", "ap-009", "Jam and Fruit Preserve Unit", "Small-Scale Multi-Product Food Processing Unit", SK_FOOD, "Secondary Processing", MOFPI, MOFPI_URL, 67,
     "Guava jam and jelly sit within the multi-product unit scope"),
    ("crop-035", "ap-005", "Turmeric Powder Unit", "Turmeric Processing & Powder-Making Unit", SK_FOOD, "Secondary Processing", SPICES, SPICES_URL, 74,
     "Direct one-to-one match with the Package004 turmeric unit"),
    ("crop-036", "ap-006", "Chilli Powder Unit", "Chilli Processing, Grading & Powder-Making Unit", SK_FOOD, "Secondary Processing", SPICES, SPICES_URL, 74,
     "Direct one-to-one match with the Package004 chilli unit"),
    ("crop-039", "ap-012", "Food Packaging Unit", "Masala Powder Manufacturing Unit (Small Scale)", SK_FOOD, "Secondary Processing", SPICES, SPICES_URL, 71,
     "Coriander is a bulk ingredient in blended masala manufacture"),
    ("crop-040", "ap-012", "Food Packaging Unit", "Masala Powder Manufacturing Unit (Small Scale)", SK_FOOD, "Secondary Processing", SPICES, SPICES_URL, 70,
     "Cumin is a core blend ingredient in the same unit"),
    ("crop-041", "ap-016", "Essential Oil Distillation Unit", PV, SK_FOOD, "Secondary Processing", "National Medicinal Plants Board", "https://nmpb.nic.in/", 63,
     "Ginger oil and oleoresin; no Package004 distillation counterpart"),
    ("crop-042", "ap-016", "Essential Oil Distillation Unit", PV, SK_ORG, "Secondary Processing", "National Medicinal Plants Board", "https://nmpb.nic.in/", 62,
     "Ashwagandha is processed to root powder and extract, not distilled oil; unit is indicative"),
    ("crop-043", "ap-016", "Essential Oil Distillation Unit", PV, SK_ORG, "Secondary Processing", "National Medicinal Plants Board", "https://nmpb.nic.in/", 62,
     "Tulsi oil distillation; no Package004 counterpart"),
    ("crop-044", "ap-003", "Cold-Pressed Oil Unit", "Cold-Pressed Coconut Oil Unit", SK_FOOD, "Primary Processing", MOFPI, MOFPI_URL, 74,
     "Direct one-to-one match with the Package004 coconut oil unit"),
    ("crop-020", "ap-013", "Animal Feed Unit", PV, SK_MODERN, "By-Product Processing", "Department of Animal Husbandry & Dairying", "https://dahd.nic.in/", 64,
     "Cottonseed cake is a feed input; no Package004 feed counterpart"),
    ("crop-003", "ap-013", "Animal Feed Unit", PV, SK_MODERN, "By-Product Processing", "Department of Animal Husbandry & Dairying", "https://dahd.nic.in/", 66,
     "Maize is the principal energy ingredient in compounded feed"),
    ("crop-001", "ap-015", "Vermicompost Unit", PV, SK_ORG, "Input Manufacturing", "Ministry of Agriculture & Farmers Welfare", "https://agricoop.gov.in/", 66,
     "Paddy straw is a major vermicompost feedstock; no Package004 counterpart"),
    ("crop-016", "ap-001", "Rice Mill", "Agricultural Seed Cleaning, Grading & Processing Unit", SK_PREC, "Seed Processing", MOFPI, MOFPI_URL, 68,
     "Sunflower seed grading maps to the Package004 seed processing unit"),
    ("crop-045", "ap-012", "Food Packaging Unit", PV, SK_FOOD, "Secondary Processing", "Directorate of Cashewnut and Cocoa Development", "https://dccd.gov.in/", 66,
     "Cashew shelling and grading; no Package004 counterpart in v1.0.0"),
]


def build_business_mapping():
    rows = []
    for i, (crop_id, ap_id, ap_name, p4, sk, stage, src, url, conf, note) in enumerate(BUSINESS_PAIRS, start=1):
        rows.append((
            f"abm-{i:03d}", crop_id, CROPS[crop_id], ap_id, ap_name, p4,
            sk, SKILL_NAME[sk], stage, src, url, COLLECTION_DATE,
            str(conf), VST, note,
        ))
    return rows


def write(filename, headers, rows):
    for i, row in enumerate(rows):
        if len(row) != len(headers):
            raise ValueError(f"{filename} row {i}: {len(row)} values, expected {len(headers)}")
    with open(DATASETS / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows x {len(headers)} cols")


if __name__ == "__main__":
    print("Regenerating Package005_Agriculture mapping datasets:\n")
    write("crop_soil_mapping.csv", H_CSM, build_soil_mapping())
    write("crop_climate_mapping.csv", H_CCM, build_climate_mapping())
    write("agri_business_mapping.csv", H_ABM, build_business_mapping())
    print("\nMapping regeneration complete.")
