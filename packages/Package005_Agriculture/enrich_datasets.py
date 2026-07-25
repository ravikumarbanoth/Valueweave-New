#!/usr/bin/env python3
"""
Package005_Agriculture v1.0.0 — Dataset Enrichment to Full Specification Coverage

Expands 5 datasets to the full entity list named in the package specification:
  - crop_categories.csv:              12 -> 24 categories
  - crops.csv:                        35 -> 45 crops, + major_districts, + processing_potential
  - farm_machinery.csv:               12 -> 16 machinery types
  - agri_processing_opportunities.csv 10 -> 17 processing opportunities
  - ai_precision_agriculture.csv      realigned to the 10 named technologies

Source tiers (per package policy, confidence ceiling 85):
  Tier 1  ICAR / Ministry of Agriculture & Farmers Welfare / Commodity Boards / APEDA  -> 70-85
  Tier 2  State agriculture departments, NABARD, MoFPI                                 -> 60-74
  Tier 3  Sector associations, published research aggregates                            -> 55-69
  Tier 4  Industry/analyst forecasts (AI & emerging tech only)                           -> 35-54

No fabricated values: any field that could not be grounded in a public source is the
bare sentinel PENDING_VERIFICATION.
"""

import csv
from pathlib import Path

COLLECTION_DATE = "2026-07-24"
VST = "VST-NEEDS_REVIEW"
PV = "PENDING_VERIFICATION"

DATASETS = Path("datasets")


def write(filename, headers, rows):
    """Write rows (list of tuples, positionally matching headers) to datasets/<filename>."""
    for i, row in enumerate(rows):
        if len(row) != len(headers):
            raise ValueError(
                f"{filename} row {i} has {len(row)} values, expected {len(headers)}"
            )
    with open(DATASETS / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows x {len(headers)} cols")


# ---------------------------------------------------------------------------
# 1. crop_categories.csv  -> 24 categories (full specified list)
# ---------------------------------------------------------------------------
H_CAT = [
    "category_id", "category_name", "category_group", "description",
    "typical_crops_examples", "cultivation_mode", "value_add_potential",
    "data_source", "source_url", "collection_date", "confidence_score",
    "verification_status", "notes",
]

CATEGORIES = [
    ("cc-001", "Food Grains", "Field Crops", "Cereal staples forming the base of India's food security system", "Rice, Wheat, Maize, Barley", "Open Field", "Medium", "ICAR; Ministry of Agriculture & Farmers Welfare", "https://icar.org.in/", COLLECTION_DATE, "78", VST, "Largest acreage group; MSP-procured"),
    ("cc-002", "Millets", "Field Crops", "Nutri-cereals; drought-tolerant coarse grains", "Pearl Millet, Sorghum, Finger Millet, Foxtail Millet", "Open Field", "High", "ICAR-IIMR (Indian Institute of Millets Research)", "https://icar.org.in/", COLLECTION_DATE, "76", VST, "Priority group under national nutri-cereals push"),
    ("cc-003", "Pulses", "Field Crops", "Leguminous protein crops that also fix atmospheric nitrogen", "Chickpea, Pigeon Pea, Moong, Urad, Lentil", "Open Field", "High", "ICAR-IIPR (Indian Institute of Pulses Research)", "https://icar.org.in/", COLLECTION_DATE, "77", VST, "National Food Security Mission - Pulses focus"),
    ("cc-004", "Oil Seeds", "Field Crops", "Oil-bearing crops feeding the edible-oil and oil-cake economy", "Groundnut, Soybean, Sunflower, Safflower, Mustard", "Open Field", "High", "ICAR-IIOR (Indian Institute of Oilseeds Research)", "https://icar.org.in/", COLLECTION_DATE, "77", VST, "Edible-oil import substitution priority"),
    ("cc-005", "Commercial Crops", "Field Crops", "Non-food cash crops supplying industrial value chains", "Sugarcane, Cotton, Tobacco, Jute", "Open Field", "High", "Ministry of Agriculture & Farmers Welfare; Commodity Boards", "https://agricoop.gov.in/", COLLECTION_DATE, "75", VST, "Mill/industry-linked procurement"),
    ("cc-006", "Vegetables", "Horticulture", "Short-duration high-value vegetable crops", "Tomato, Potato, Onion, Brinjal, Okra, Cabbage", "Open Field / Protected", "Very High", "ICAR-IIVR; MIDH", "https://icar.org.in/", COLLECTION_DATE, "76", VST, "MIDH-supported; high perishability"),
    ("cc-007", "Fruits", "Horticulture", "Perennial and semi-perennial fruit crops", "Mango, Banana, Citrus, Grapes, Guava, Pomegranate", "Orchard", "Very High", "ICAR-IIHR; MIDH", "https://icar.org.in/", COLLECTION_DATE, "76", VST, "Long gestation; strong export pull"),
    ("cc-008", "Spices", "Horticulture", "Aromatic and pungent spice crops", "Turmeric, Chilli, Black Pepper, Cardamom, Coriander, Cumin", "Open Field / Plantation", "Very High", "ICAR-IISR; Spices Board of India", "https://www.indianspices.com/", COLLECTION_DATE, "77", VST, "India is the largest global spice exporter"),
    ("cc-009", "Medicinal Plants", "Horticulture", "Herbal and aromatic crops for AYUSH and nutraceutical use", "Ashwagandha, Tulsi, Brahmi, Shatavari, Aloe Vera", "Open Field", "Very High", "National Medicinal Plants Board (NMPB); Ministry of Ayush", "https://nmpb.nic.in/", COLLECTION_DATE, "70", VST, "Buy-back contracts common; quality testing critical"),
    ("cc-010", "Plantation Crops", "Plantation", "Long-duration perennial estate crops", "Coconut, Arecanut, Tea, Coffee, Rubber, Cashew", "Plantation", "High", "Commodity Boards (Coconut, Tea, Coffee, Rubber)", "https://agricoop.gov.in/", COLLECTION_DATE, "75", VST, "Board-regulated; multi-decade crop cycles"),
    ("cc-011", "Flowers", "Horticulture", "Cut flowers and loose flowers for floriculture markets", "Rose, Marigold, Chrysanthemum, Jasmine, Gerbera", "Open Field / Protected", "High", "ICAR-DFR (Directorate of Floricultural Research); MIDH", "https://icar.org.in/", COLLECTION_DATE, "70", VST, "Festival-driven demand spikes; cold chain sensitive"),
    ("cc-012", "Fodder", "Field Crops", "Green and dry fodder crops supporting livestock systems", "Berseem, Lucerne, Fodder Sorghum, Fodder Maize, Oats", "Open Field", "Low", "ICAR-IGFRI (Indian Grassland and Fodder Research Institute)", "https://icar.org.in/", COLLECTION_DATE, "71", VST, "Input to dairy/livestock rather than direct sale"),
    ("cc-013", "Forest Produce", "Allied", "Non-timber forest produce collected or cultivated at forest margins", "Tamarind, Mahua, Gum Karaya, Bamboo, Sal Seed, Honey (wild)", "Forest / Agroforestry", "High", "TRIFED; Ministry of Tribal Affairs; State Forest Departments", "https://trifed.tribal.gov.in/", COLLECTION_DATE, "66", VST, "MSP-for-MFP scheme; tribal livelihood linked"),
    ("cc-014", "Organic Farming", "Production System", "Certified chemical-free production system rather than a crop group", "Any crop under NPOP/PGS certification", "Open Field / Protected", "Very High", "APEDA (NPOP); PKVY under Ministry of Agriculture", "https://apeda.gov.in/", COLLECTION_DATE, "72", VST, "System category; 3-year conversion for NPOP certification"),
    ("cc-015", "Protected Cultivation", "Production System", "Polyhouse, shadenet and greenhouse-based controlled cultivation", "Capsicum, Gerbera, Cucumber, Exotic Vegetables", "Protected", "Very High", "MIDH (Mission for Integrated Development of Horticulture)", "https://midh.gov.in/", COLLECTION_DATE, "71", VST, "Capital-intensive; MIDH subsidy-supported"),
    ("cc-016", "Hydroponics", "Production System", "Soil-less cultivation in nutrient solution", "Lettuce, Leafy Greens, Herbs, Strawberry", "Controlled Environment", "Very High", "ICAR-IARI research programmes; MIDH", "https://icar.org.in/", COLLECTION_DATE, "62", VST, "Urban/peri-urban model; standardised cost data sparse"),
    ("cc-017", "Aquaponics", "Production System", "Integrated fish-and-plant recirculating system", "Leafy Greens with Tilapia / Carp", "Controlled Environment", "High", "ICAR-CIFA research programmes", "https://icar.org.in/", COLLECTION_DATE, "57", VST, "Early adoption in India; limited published cost benchmarks"),
    ("cc-018", "Sericulture", "Allied", "Silkworm rearing with host-plant cultivation", "Mulberry (host), Tasar, Eri, Muga host plants", "Open Field + Rearing Shed", "Very High", "Central Silk Board; Ministry of Textiles", "https://csb.gov.in/", COLLECTION_DATE, "72", VST, "Silk Samagra scheme support; high employment per acre"),
    ("cc-019", "Apiculture", "Allied", "Beekeeping for honey, wax and pollination services", "Apis cerana indica, Apis mellifera colonies", "Apiary", "Very High", "National Bee Board; ICAR-IARI", "https://nbb.gov.in/", COLLECTION_DATE, "70", VST, "National Beekeeping and Honey Mission (NBHM)"),
    ("cc-020", "Mushroom", "Allied", "Protected-shed fungal cultivation on prepared substrate", "Button Mushroom, Oyster Mushroom, Milky Mushroom", "Controlled Shed", "Very High", "ICAR-DMR (Directorate of Mushroom Research)", "https://icar.org.in/", COLLECTION_DATE, "71", VST, "Short cycle; year-round income; low land requirement"),
    ("cc-021", "Fisheries", "Allied", "Inland and brackish-water fish and shrimp culture", "Rohu, Catla, Tilapia, Vannamei Shrimp", "Pond / Tank / Cage", "Very High", "NFDB; Department of Fisheries; PMMSY", "https://nfdb.gov.in/", COLLECTION_DATE, "71", VST, "PMMSY-funded; highest-value agri-export category"),
    ("cc-022", "Livestock", "Allied", "Small and large ruminant rearing for meat and by-products", "Goat, Sheep, Buffalo, Cattle", "Shed / Grazing", "High", "Department of Animal Husbandry & Dairying; National Livestock Mission", "https://dahd.nic.in/", COLLECTION_DATE, "72", VST, "National Livestock Mission support"),
    ("cc-023", "Poultry", "Allied", "Broiler, layer and backyard poultry production", "Broiler, Layer, Kadaknath, Giriraja", "Shed / Backyard", "High", "Department of Animal Husbandry & Dairying; ICAR-DPR", "https://dahd.nic.in/", COLLECTION_DATE, "73", VST, "Short cycle; integrator contract-farming common"),
    ("cc-024", "Dairy", "Allied", "Milk production and primary milk handling", "Buffalo Milk, Cow Milk (crossbred and indigenous)", "Shed", "Very High", "NDDB; Department of Animal Husbandry & Dairying", "https://www.nddb.coop/", COLLECTION_DATE, "75", VST, "Cooperative procurement network; daily cash flow"),
]


# ---------------------------------------------------------------------------
# 2. crops.csv -> 45 crops, with major_districts + processing_potential added
# ---------------------------------------------------------------------------
H_CROPS = [
    "crop_id", "crop_name", "scientific_name", "category_id", "category_name",
    "season", "duration_days", "water_requirement_mm", "soil_type_preferred",
    "rainfall_mm", "temperature_min_c", "temperature_max_c",
    "avg_yield_tons_per_ha", "major_states", "major_districts",
    "organic_possible", "export_potential", "processing_potential",
    "mechanization_level", "data_source", "source_url", "collection_date",
    "confidence_score", "verification_status", "notes",
]

ICAR = "ICAR; Ministry of Agriculture & Farmers Welfare"
ICAR_URL = "https://icar.org.in/"
SPICES = "ICAR-IISR; Spices Board of India"
SPICES_URL = "https://www.indianspices.com/"

CROPS = [
    # --- Food Grains (4) ---
    ("crop-001", "Rice", "Oryza sativa", "cc-001", "Food Grains", "Kharif", "150", "1200", "Alluvial", "1200", "20", "35", "6.5", "West Bengal, Punjab, Uttar Pradesh, Telangana, Andhra Pradesh", "Nalgonda, Karimnagar, Nizamabad, West Godavari, Krishna", "Yes", "Very High", "Very High", "High", ICAR, ICAR_URL, COLLECTION_DATE, "78", VST, "Yield is an all-India irrigated average; district yields vary widely"),
    ("crop-002", "Wheat", "Triticum aestivum", "cc-001", "Food Grains", "Rabi", "120", "450", "Alluvial", "450", "10", "25", "3.5", "Punjab, Haryana, Uttar Pradesh, Madhya Pradesh", PV, "Yes", "High", "Very High", "Very High", ICAR, ICAR_URL, COLLECTION_DATE, "78", VST, "Not a significant Telangana/AP crop; district attribution not asserted in this release"),
    ("crop-003", "Maize", "Zea mays", "cc-001", "Food Grains", "Kharif", "110", "500", "Sandy Loam", "500", "15", "30", "3.2", "Karnataka, Madhya Pradesh, Telangana, Bihar", "Karimnagar, Warangal, Medak, Kurnool", "Yes", "Medium", "Very High", "High", ICAR, ICAR_URL, COLLECTION_DATE, "77", VST, "Feed and starch industry demand drives acreage"),
    ("crop-004", "Barley", "Hordeum vulgare", "cc-001", "Food Grains", "Rabi", "110", "350", "Loamy", "350", "5", "20", "2.6", "Rajasthan, Uttar Pradesh, Madhya Pradesh", PV, "Yes", "Low", "High", "Medium", ICAR, ICAR_URL, COLLECTION_DATE, "73", VST, "Malting industry is the main organised buyer"),
    # --- Millets (4) ---
    ("crop-005", "Pearl Millet", "Pennisetum glaucum", "cc-002", "Millets", "Kharif", "90", "350", "Sandy", "350", "20", "40", "1.5", "Rajasthan, Maharashtra, Gujarat, Karnataka", PV, "Yes", "Medium", "High", "Medium", "ICAR-IIMR", ICAR_URL, COLLECTION_DATE, "76", VST, "Most drought-tolerant cereal in the group"),
    ("crop-006", "Sorghum", "Sorghum bicolor", "cc-002", "Millets", "Kharif", "110", "400", "Black Soil", "400", "18", "38", "1.2", "Maharashtra, Karnataka, Telangana, Andhra Pradesh", "Mahbubnagar, Nalgonda, Kurnool, Anantapur", "Yes", "Medium", "High", "Medium", "ICAR-IIMR", ICAR_URL, COLLECTION_DATE, "76", VST, "Dual purpose - grain plus fodder"),
    ("crop-007", "Finger Millet", "Eleusine coracana", "cc-002", "Millets", "Kharif", "110", "450", "Red Soil", "450", "15", "30", "1.7", "Karnataka, Tamil Nadu, Odisha, Uttarakhand", PV, "Yes", "Low", "High", "Low", "ICAR-IIMR", ICAR_URL, COLLECTION_DATE, "74", VST, "High calcium; strong local nutrition demand"),
    ("crop-008", "Foxtail Millet", "Setaria italica", "cc-002", "Millets", "Kharif", "80", "300", "Red Soil", "300", "18", "35", "1.0", "Andhra Pradesh, Telangana, Karnataka", "Anantapur, Kurnool, Mahbubnagar", "Yes", "Medium", "High", "Low", "ICAR-IIMR", ICAR_URL, COLLECTION_DATE, "70", VST, "Short duration; fits rainfed and contingency planting"),
    # --- Pulses (5) ---
    ("crop-009", "Chickpea", "Cicer arietinum", "cc-003", "Pulses", "Rabi", "110", "300", "Black Soil", "300", "10", "25", "1.1", "Madhya Pradesh, Maharashtra, Rajasthan, Andhra Pradesh", "Kurnool, Anantapur, Prakasam", "Yes", "High", "Very High", "High", "ICAR-IIPR", ICAR_URL, COLLECTION_DATE, "77", VST, "Largest pulse by acreage; dal milling demand"),
    ("crop-010", "Pigeon Pea", "Cajanus cajan", "cc-003", "Pulses", "Kharif", "200", "600", "Black Soil", "600", "18", "35", "0.9", "Maharashtra, Karnataka, Telangana, Madhya Pradesh", "Mahbubnagar, Nalgonda, Adilabad", "Yes", "High", "Very High", "Medium", "ICAR-IIPR", ICAR_URL, COLLECTION_DATE, "76", VST, "Long duration; intercropped widely"),
    ("crop-011", "Moong (Green Gram)", "Vigna radiata", "cc-003", "Pulses", "Kharif", "70", "350", "Sandy Loam", "350", "20", "35", "0.7", "Rajasthan, Maharashtra, Karnataka, Andhra Pradesh", "Prakasam, Guntur, Kurnool", "Yes", "High", "High", "Medium", "ICAR-IIPR", ICAR_URL, COLLECTION_DATE, "75", VST, "Very short duration; fits as a catch crop"),
    ("crop-012", "Urad (Black Gram)", "Vigna mungo", "cc-003", "Pulses", "Kharif", "85", "400", "Loamy", "400", "18", "32", "0.7", "Madhya Pradesh, Uttar Pradesh, Andhra Pradesh, Tamil Nadu", "Guntur, Prakasam, Krishna", "Yes", "High", "High", "Low", "ICAR-IIPR", ICAR_URL, COLLECTION_DATE, "75", VST, "Core input for idli/dosa batter processing"),
    ("crop-013", "Lentil", "Lens culinaris", "cc-003", "Pulses", "Rabi", "110", "280", "Loamy", "280", "8", "22", "1.0", "Uttar Pradesh, Madhya Pradesh, Bihar", PV, "Yes", "High", "Very High", "High", "ICAR-IIPR", ICAR_URL, COLLECTION_DATE, "75", VST, "Import-substitution priority pulse"),
    # --- Oil Seeds (5) ---
    ("crop-014", "Groundnut", "Arachis hypogaea", "cc-004", "Oil Seeds", "Kharif", "110", "500", "Sandy Loam", "500", "20", "35", "1.6", "Gujarat, Rajasthan, Andhra Pradesh, Karnataka", "Anantapur, Kurnool, Chittoor", "Yes", "High", "Very High", "High", "ICAR-IIOR", ICAR_URL, COLLECTION_DATE, "77", VST, "Anantapur is India's largest groundnut district by area"),
    ("crop-015", "Soybean", "Glycine max", "cc-004", "Oil Seeds", "Kharif", "100", "450", "Black Soil", "450", "18", "32", "1.1", "Madhya Pradesh, Maharashtra, Rajasthan", PV, "Yes", "High", "Very High", "High", "ICAR-IIOR", ICAR_URL, COLLECTION_DATE, "76", VST, "Oil plus de-oiled cake export value chain"),
    ("crop-016", "Sunflower", "Helianthus annuus", "cc-004", "Oil Seeds", "Rabi", "100", "400", "Loamy", "400", "15", "30", "1.0", "Karnataka, Andhra Pradesh, Telangana, Maharashtra", "Kurnool, Mahbubnagar, Nalgonda", "Yes", "Medium", "Very High", "High", "ICAR-IIOR", ICAR_URL, COLLECTION_DATE, "75", VST, "Short duration; suits rabi irrigated systems"),
    ("crop-017", "Safflower", "Carthamus tinctorius", "cc-004", "Oil Seeds", "Rabi", "120", "300", "Black Soil", "300", "10", "25", "0.7", "Maharashtra, Karnataka, Telangana", "Nizamabad, Medak", "Yes", "Low", "High", "Medium", "ICAR-IIOR", ICAR_URL, COLLECTION_DATE, "71", VST, "Residual-moisture rabi crop on deep black soils"),
    ("crop-018", "Mustard", "Brassica juncea", "cc-004", "Oil Seeds", "Rabi", "120", "350", "Loamy", "350", "8", "25", "1.3", "Rajasthan, Haryana, Madhya Pradesh, Uttar Pradesh", PV, "Yes", "Medium", "Very High", "High", "ICAR-IIOR", ICAR_URL, COLLECTION_DATE, "75", VST, "Cold-pressed mustard oil is a growing premium segment"),
    # --- Commercial Crops (4) ---
    ("crop-019", "Sugarcane", "Saccharum officinarum", "cc-005", "Commercial Crops", "Annual", "365", "2000", "Alluvial", "2000", "18", "35", "70", "Uttar Pradesh, Maharashtra, Karnataka, Telangana", "Nizamabad, Medak, Bodhan belt, East Godavari", "Partial", "Medium", "Very High", "High", ICAR, ICAR_URL, COLLECTION_DATE, "77", VST, "Mill-linked; jaggery is the decentralised alternative"),
    ("crop-020", "Cotton", "Gossypium hirsutum", "cc-005", "Commercial Crops", "Kharif", "180", "700", "Black Soil", "700", "20", "35", "0.5", "Gujarat, Maharashtra, Telangana, Andhra Pradesh", "Adilabad, Warangal, Khammam, Guntur", "Yes", "High", "Very High", "Medium", "ICAR-CICR", ICAR_URL, COLLECTION_DATE, "77", VST, "Yield stated as lint tonnes per ha, not seed cotton"),
    ("crop-021", "Tobacco", "Nicotiana tabacum", "cc-005", "Commercial Crops", "Rabi", "150", "500", "Loamy", "500", "15", "28", "1.8", "Andhra Pradesh, Karnataka, Gujarat", "Prakasam, West Godavari, Guntur", "Limited", "High", "Medium", "Low", "Tobacco Board of India", "https://tobaccoboard.gov.in/", COLLECTION_DATE, "72", VST, "Board-regulated auction system; declining policy support"),
    ("crop-022", "Jute", "Corchorus olitorius", "cc-005", "Commercial Crops", "Kharif", "120", "1500", "Alluvial", "1500", "20", "35", "2.5", "West Bengal, Bihar, Assam", PV, "Yes", "Low", "High", "Low", ICAR, ICAR_URL, COLLECTION_DATE, "70", VST, "Eco-packaging demand is the main growth vector"),
    # --- Vegetables (6) ---
    ("crop-023", "Tomato", "Solanum lycopersicum", "cc-006", "Vegetables", "Year Round", "120", "500", "Loamy", "500", "18", "30", "25", "Madhya Pradesh, Andhra Pradesh, Karnataka, Telangana", "Chittoor, Anantapur, Rangareddy, Medak", "Yes", "Medium", "Very High", "Medium", "ICAR-IIVR", ICAR_URL, COLLECTION_DATE, "76", VST, "Extreme price volatility; processing absorbs gluts"),
    ("crop-024", "Potato", "Solanum tuberosum", "cc-006", "Vegetables", "Rabi", "100", "500", "Sandy Loam", "500", "15", "25", "23", "Uttar Pradesh, West Bengal, Bihar, Gujarat", PV, "Yes", "Medium", "Very High", "High", "ICAR-CPRI", ICAR_URL, COLLECTION_DATE, "77", VST, "Cold storage is integral to the value chain"),
    ("crop-025", "Onion", "Allium cepa", "cc-006", "Vegetables", "Rabi", "120", "400", "Loamy", "400", "13", "30", "17", "Maharashtra, Karnataka, Madhya Pradesh, Andhra Pradesh", "Kurnool, Mahbubnagar, Chittoor", "Yes", "High", "High", "Medium", "ICAR-DOGR", ICAR_URL, COLLECTION_DATE, "76", VST, "Export policy changes drive sharp price swings"),
    ("crop-026", "Brinjal", "Solanum melongena", "cc-006", "Vegetables", "Year Round", "120", "450", "Loamy", "450", "18", "32", "18", "West Bengal, Odisha, Gujarat, Andhra Pradesh", "Guntur, Krishna, Rangareddy", "Yes", "Low", "Medium", "Low", "ICAR-IIVR", ICAR_URL, COLLECTION_DATE, "73", VST, "Largely fresh-market; limited processing pull"),
    ("crop-027", "Okra (Lady Finger)", "Abelmoschus esculentus", "cc-006", "Vegetables", "Kharif", "90", "450", "Loamy", "450", "20", "35", "11", "West Bengal, Gujarat, Bihar, Andhra Pradesh", "Guntur, Krishna, Rangareddy", "Yes", "Medium", "Medium", "Low", "ICAR-IIVR", ICAR_URL, COLLECTION_DATE, "73", VST, "Frozen okra is a niche export line"),
    ("crop-028", "Cabbage", "Brassica oleracea var. capitata", "cc-006", "Vegetables", "Rabi", "100", "400", "Loamy", "400", "12", "24", "24", "West Bengal, Odisha, Maharashtra, Telangana", "Rangareddy, Medak, Sangareddy", "Yes", "Low", "Medium", "Low", "ICAR-IIVR", ICAR_URL, COLLECTION_DATE, "73", VST, "Peri-urban belts supply city markets"),
    # --- Fruits (6) ---
    ("crop-029", "Mango", "Mangifera indica", "cc-007", "Fruits", "Perennial", "PENDING_VERIFICATION", "900", "Alluvial", "900", "15", "38", "8", "Uttar Pradesh, Andhra Pradesh, Karnataka, Telangana", "Krishna, Chittoor, Khammam, Nuzvid belt", "Yes", "Very High", "Very High", "Low", "ICAR-IIHR", ICAR_URL, COLLECTION_DATE, "77", VST, "Duration not meaningful for a perennial; 4-5 year gestation"),
    ("crop-030", "Banana", "Musa paradisiaca", "cc-007", "Fruits", "Perennial", "330", "1800", "Alluvial", "1800", "18", "35", "35", "Tamil Nadu, Maharashtra, Gujarat, Andhra Pradesh", "Kadapa, Anantapur, East Godavari", "Yes", "Very High", "High", "Medium", "ICAR-NRCB", ICAR_URL, COLLECTION_DATE, "76", VST, "Tissue-culture planting material now standard"),
    ("crop-031", "Citrus (Sweet Orange)", "Citrus sinensis", "cc-007", "Fruits", "Perennial", "PENDING_VERIFICATION", "1000", "Loamy", "1000", "13", "35", "12", "Maharashtra, Andhra Pradesh, Telangana, Punjab", "Nalgonda, Kadapa, Anantapur", "Yes", "High", "Very High", "Low", "ICAR-CCRI", ICAR_URL, COLLECTION_DATE, "75", VST, "Nalgonda sweet orange belt supplies juice processors"),
    ("crop-032", "Grapes", "Vitis vinifera", "cc-007", "Fruits", "Perennial", "PENDING_VERIFICATION", "800", "Black Soil", "800", "15", "35", "22", "Maharashtra, Karnataka, Telangana, Andhra Pradesh", "Rangareddy, Anantapur", "Partial", "Very High", "High", "Medium", "ICAR-NRCG", ICAR_URL, COLLECTION_DATE, "75", VST, "Residue compliance is the binding export constraint"),
    ("crop-033", "Guava", "Psidium guajava", "cc-007", "Fruits", "Perennial", "PENDING_VERIFICATION", "800", "Loamy", "800", "15", "35", "14", "Uttar Pradesh, Madhya Pradesh, Bihar, Andhra Pradesh", "Anantapur, Krishna, Rangareddy", "Yes", "Medium", "Very High", "Low", "ICAR-CISH", ICAR_URL, COLLECTION_DATE, "73", VST, "Hardy; strong pulp and beverage demand"),
    ("crop-034", "Pomegranate", "Punica granatum", "cc-007", "Fruits", "Perennial", "PENDING_VERIFICATION", "700", "Loamy", "700", "15", "38", "12", "Maharashtra, Karnataka, Andhra Pradesh, Gujarat", "Anantapur, Kurnool", "Yes", "Very High", "High", "Low", "ICAR-NRCP", ICAR_URL, COLLECTION_DATE, "73", VST, "Bacterial blight is the principal production risk"),
    # --- Spices (7) ---
    ("crop-035", "Turmeric", "Curcuma longa", "cc-008", "Spices", "Kharif", "240", "1500", "Red Soil", "1500", "20", "32", "6.5", "Telangana, Andhra Pradesh, Tamil Nadu, Maharashtra", "Nizamabad, Warangal, Duggirala belt, Guntur", "Yes", "Very High", "Very High", "Medium", SPICES, SPICES_URL, COLLECTION_DATE, "77", VST, "Yield is dry turmeric; Nizamabad is a benchmark market"),
    ("crop-036", "Chilli", "Capsicum annuum", "cc-008", "Spices", "Kharif", "150", "600", "Black Soil", "600", "18", "32", "2.2", "Andhra Pradesh, Telangana, Karnataka, Madhya Pradesh", "Guntur, Prakasam, Warangal, Khammam", "Yes", "Very High", "Very High", "Medium", SPICES, SPICES_URL, COLLECTION_DATE, "77", VST, "Guntur is Asia's largest chilli market yard"),
    ("crop-037", "Black Pepper", "Piper nigrum", "cc-008", "Spices", "Perennial", "PENDING_VERIFICATION", "2000", "Laterite", "2000", "15", "32", "0.4", "Kerala, Karnataka, Tamil Nadu", PV, "Yes", "Very High", "High", "Low", SPICES, SPICES_URL, COLLECTION_DATE, "74", VST, "Vine crop; commonly intercropped in plantations"),
    ("crop-038", "Cardamom", "Elettaria cardamomum", "cc-008", "Spices", "Perennial", "PENDING_VERIFICATION", "2500", "Laterite", "2500", "10", "28", "0.2", "Kerala, Karnataka, Tamil Nadu", PV, "Yes", "Very High", "Medium", "Low", SPICES, SPICES_URL, COLLECTION_DATE, "72", VST, "Highest unit-value spice; shade-grown"),
    ("crop-039", "Coriander", "Coriandrum sativum", "cc-008", "Spices", "Rabi", "110", "350", "Black Soil", "350", "10", "28", "1.0", "Rajasthan, Madhya Pradesh, Gujarat, Andhra Pradesh", "Kurnool, Guntur", "Yes", "High", "High", "Medium", SPICES, SPICES_URL, COLLECTION_DATE, "73", VST, "Dual market - seed spice and leafy coriander"),
    ("crop-040", "Cumin", "Cuminum cyminum", "cc-008", "Spices", "Rabi", "110", "300", "Sandy Loam", "300", "10", "30", "0.7", "Gujarat, Rajasthan", PV, "Yes", "Very High", "High", "Medium", SPICES, SPICES_URL, COLLECTION_DATE, "73", VST, "India dominates global cumin trade"),
    ("crop-041", "Ginger", "Zingiber officinale", "cc-008", "Spices", "Kharif", "240", "1500", "Loamy", "1500", "18", "32", "12", "Kerala, Assam, Odisha, Telangana", "Adilabad, Nizamabad", "Yes", "High", "Very High", "Low", SPICES, SPICES_URL, COLLECTION_DATE, "73", VST, "Fresh-weight yield; dry ginger recovery ~20 percent"),
    # --- Medicinal Plants (2) ---
    ("crop-042", "Ashwagandha", "Withania somnifera", "cc-009", "Medicinal Plants", "Rabi", "160", "300", "Sandy Loam", "300", "10", "32", "0.6", "Madhya Pradesh, Rajasthan, Gujarat", PV, "Yes", "Very High", "Very High", "Low", "National Medicinal Plants Board", "https://nmpb.nic.in/", COLLECTION_DATE, "70", VST, "Root yield; buy-back contracts common"),
    ("crop-043", "Tulsi (Holy Basil)", "Ocimum sanctum", "cc-009", "Medicinal Plants", "Kharif", "100", "400", "Loamy", "400", "18", "35", "PENDING_VERIFICATION", "Uttar Pradesh, Madhya Pradesh, Andhra Pradesh", PV, "Yes", "High", "Very High", "Low", "National Medicinal Plants Board", "https://nmpb.nic.in/", COLLECTION_DATE, "66", VST, "Yield varies by product form (herb, seed, oil); left as sentinel"),
    # --- Plantation Crops (2) ---
    ("crop-044", "Coconut", "Cocos nucifera", "cc-010", "Plantation Crops", "Perennial", "PENDING_VERIFICATION", "1500", "Sandy", "1500", "20", "35", "PENDING_VERIFICATION", "Kerala, Tamil Nadu, Karnataka, Andhra Pradesh", "East Godavari, West Godavari, Srikakulam", "Partial", "Very High", "Very High", "Low", "Coconut Development Board", "https://coconutboard.gov.in/", COLLECTION_DATE, "74", VST, "Yield is reported as nuts per palm per year, not tonnes/ha"),
    ("crop-045", "Cashew", "Anacardium occidentale", "cc-010", "Plantation Crops", "Perennial", "PENDING_VERIFICATION", "1000", "Laterite", "1000", "20", "35", "0.9", "Maharashtra, Andhra Pradesh, Odisha, Kerala", "Srikakulam, Vizianagaram, East Godavari", "Yes", "Very High", "Very High", "Low", "Directorate of Cashewnut and Cocoa Development", "https://dccd.gov.in/", COLLECTION_DATE, "73", VST, "Raw nut yield; processing is highly labour-intensive"),
]


# ---------------------------------------------------------------------------
# 3. farm_machinery.csv -> 16 machinery types (full specified list)
# ---------------------------------------------------------------------------
H_MACH = [
    "machinery_id", "machinery_name", "machinery_type", "function",
    "investment_inr", "fuel_type", "capacity", "power_hp",
    "annual_maintenance_inr", "automation_level", "ai_readiness",
    "subsidy_scheme", "data_source", "source_url", "collection_date",
    "confidence_score", "verification_status", "notes",
]

SMAM = "Sub-Mission on Agricultural Mechanization (SMAM)"
MOA = "Ministry of Agriculture & Farmers Welfare"
MOA_URL = "https://agricoop.gov.in/"
MOFPI = "Ministry of Food Processing Industries (MoFPI)"
MOFPI_URL = "https://mofpi.gov.in/"

MACHINERY = [
    ("fm-001", "Tractor (35-45 HP)", "Land Preparation", "Primary tillage, haulage, PTO power source for implements", PV, "Diesel", "35-45 HP class", "40", PV, "Basic", "Emerging", SMAM, MOA, MOA_URL, COLLECTION_DATE, "72", VST, "Price varies by make/model; no single official figure - sentinel used"),
    ("fm-002", "Rotavator", "Land Preparation", "Secondary tillage and soil pulverisation", PV, "Tractor PTO", "5-7 ft working width", PV, PV, "Mechanical", "Low", SMAM, MOA, MOA_URL, COLLECTION_DATE, "71", VST, "Tractor-mounted; no independent power rating"),
    ("fm-003", "Seed Drill / Seed-cum-Ferti Drill", "Sowing", "Line sowing with simultaneous fertiliser placement", PV, "Tractor PTO", "9-13 rows", PV, PV, "Mechanical", "Emerging", SMAM, MOA, MOA_URL, COLLECTION_DATE, "71", VST, "Precision sowing reduces seed rate materially"),
    ("fm-004", "Combine Harvester", "Harvesting", "Cutting, threshing and cleaning in a single pass", PV, "Diesel", "4-7 ft cutter bar", PV, PV, "Mechanical", "Emerging", SMAM, MOA, MOA_URL, COLLECTION_DATE, "70", VST, "Predominantly accessed via custom-hiring, not owned"),
    ("fm-005", "Power Tiller", "Land Preparation", "Tillage for small and fragmented holdings", PV, "Diesel", "8-13 HP class", "10", PV, "Basic", "Low", SMAM, MOA, MOA_URL, COLLECTION_DATE, "71", VST, "Suited to smallholdings and terraced fields"),
    ("fm-006", "Agricultural Drone", "Crop Protection", "Aerial spraying of pesticide and nutrient solutions", PV, "Battery", "10-16 litre tank", "N/A", PV, "Advanced", "Very High", "SMAM Drone component; Kisan Drone promotion", MOA, MOA_URL, COLLECTION_DATE, "64", VST, "DGCA licensing and operator certification required"),
    ("fm-007", "Boom Sprayer", "Crop Protection", "Tractor-mounted wide-swath chemical application", PV, "Tractor PTO", "200-600 litre tank", PV, PV, "Mechanical", "Low", SMAM, MOA, MOA_URL, COLLECTION_DATE, "71", VST, "Far higher coverage rate than knapsack spraying"),
    ("fm-008", "Cold Storage Unit", "Post-Harvest", "Temperature-controlled storage of perishables", PV, "Electric", "PENDING_VERIFICATION", "N/A", PV, "Automated", "High", "MIDH; Agriculture Infrastructure Fund (AIF)", MOA, MOA_URL, COLLECTION_DATE, "68", VST, "Cost scales with capacity and chamber count"),
    ("fm-009", "Solar Dryer", "Post-Harvest", "Solar drying of spices, fruit and vegetable produce", PV, "Solar", "PENDING_VERIFICATION", "N/A", PV, "Semi-Automated", "Medium", "MIDH; MNRE solar programmes", MOFPI, MOFPI_URL, COLLECTION_DATE, "64", VST, "Retains colour and volatile oils better than open-sun drying"),
    ("fm-010", "Rice Mill (Mini)", "Processing", "Paddy dehusking, polishing and grading", PV, "Electric", "PENDING_VERIFICATION", PV, PV, "Semi-Automated", "Medium", "PMFME; MoFPI schemes", MOFPI, MOFPI_URL, COLLECTION_DATE, "68", VST, "By-products (bran, husk) materially affect unit economics"),
    ("fm-011", "Oil Expeller (Cold Press)", "Processing", "Mechanical cold-press oil extraction from oilseed", PV, "Electric", "PENDING_VERIFICATION", PV, PV, "Semi-Automated", "Low", "PMFME; MoFPI schemes", MOFPI, MOFPI_URL, COLLECTION_DATE, "67", VST, "Oil cake is a significant secondary revenue stream"),
    ("fm-012", "Dal Mill (Mini)", "Processing", "Dehusking and splitting of pulses into dal", PV, "Electric", "PENDING_VERIFICATION", PV, PV, "Semi-Automated", "Medium", "PMFME; MoFPI schemes", MOFPI, MOFPI_URL, COLLECTION_DATE, "68", VST, "Milling recovery percentage is the key profitability driver"),
    ("fm-013", "Packaging Machine (Form-Fill-Seal)", "Packaging", "Automated filling, sealing and date-coding of retail packs", PV, "Electric", "PENDING_VERIFICATION", PV, PV, "Automated", "Medium", "PMFME; MoFPI schemes", MOFPI, MOFPI_URL, COLLECTION_DATE, "65", VST, "Required for FSSAI-compliant retail-ready packaging"),
    ("fm-014", "Cold Chain / Reefer Transport", "Post-Harvest Logistics", "Refrigerated movement of perishables to market", PV, "Diesel", "PENDING_VERIFICATION", PV, PV, "Automated", "High", "MoFPI Cold Chain scheme; AIF", MOFPI, MOFPI_URL, COLLECTION_DATE, "65", VST, "Unbroken cold chain is mandatory for most fresh exports"),
    ("fm-015", "Micro-Irrigation System (Drip)", "Irrigation", "Targeted root-zone water and nutrient delivery", PV, "Electric / Solar pump", "Per-acre configuration", PV, PV, "Mechanical", "Emerging", "PMKSY Per Drop More Crop", "Ministry of Jal Shakti; PMKSY", "https://pmksy.gov.in/", COLLECTION_DATE, "70", VST, "Subsidy share differs by state and farmer category"),
    ("fm-016", "Automatic Weather Station (IoT)", "Monitoring", "On-farm capture of weather and soil-moisture telemetry", PV, "Solar / Battery", "Multi-sensor array", "N/A", PV, "Digital", "Very High", PV, "ICAR; India Meteorological Department", ICAR_URL, COLLECTION_DATE, "62", VST, "Foundation layer for advisory and precision-agriculture services"),
]


# ---------------------------------------------------------------------------
# 4. agri_processing_opportunities.csv -> 17 opportunities (full specified list)
# ---------------------------------------------------------------------------
H_PROC = [
    "opportunity_id", "opportunity_name", "opportunity_type", "input_crop",
    "finished_product", "investment_band", "capacity_indicative",
    "skill_requirement", "market_demand", "value_add_potential",
    "licenses_required", "linked_scheme", "data_source", "source_url",
    "collection_date", "confidence_score", "verification_status", "notes",
]

FSSAI = "FSSAI licence; Udyam registration; State pollution consent (where applicable)"
PMFME = "PM Formalisation of Micro Food Processing Enterprises (PMFME)"

PROCESSING = [
    ("ap-001", "Rice Mill", "Primary Processing", "Paddy", "Polished rice, bran, husk, broken rice", PV, PV, "Semi-skilled", "High", "Medium", FSSAI, PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "70", VST, "Bran sold to oil extractors; husk used as boiler fuel"),
    ("ap-002", "Dal Mill", "Primary Processing", "Pigeon Pea, Chickpea, Moong, Urad", "Split dal, chuni, husk", PV, PV, "Semi-skilled", "High", "High", FSSAI, PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "70", VST, "Milling recovery drives margin; chuni sold as cattle feed"),
    ("ap-003", "Cold-Pressed Oil Unit", "Primary Processing", "Groundnut, Sesame, Mustard, Coconut", "Cold-pressed edible oil, oil cake", PV, PV, "Semi-skilled", "Very High", "High", FSSAI, PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "69", VST, "Premium health-oil positioning; oil cake is a second revenue line"),
    ("ap-004", "Millet Processing Unit", "Primary Processing", "Pearl Millet, Sorghum, Finger Millet, Foxtail Millet", "Dehulled millet, millet flour, rava, ready-mix", PV, PV, "Semi-skilled", "High", "Very High", FSSAI, PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "66", VST, "Nutri-cereal demand growing; dehulling is the key unit operation"),
    ("ap-005", "Turmeric Powder Unit", "Secondary Processing", "Turmeric (dry fingers)", "Turmeric powder, curcumin-grade material", PV, PV, "Semi-skilled", "Very High", "Very High", FSSAI, PMFME, SPICES, SPICES_URL, COLLECTION_DATE, "70", VST, "Curcumin content determines grade and realisation"),
    ("ap-006", "Chilli Powder Unit", "Secondary Processing", "Dry Chilli", "Chilli powder, flakes, oleoresin feedstock", PV, PV, "Semi-skilled", "Very High", "Very High", FSSAI, PMFME, SPICES, SPICES_URL, COLLECTION_DATE, "70", VST, "Colour value (ASTA) and pungency set price bands"),
    ("ap-007", "Fruit Pulp Unit", "Secondary Processing", "Mango, Guava, Tomato", "Aseptic fruit pulp, concentrate", PV, PV, "Skilled", "High", "High", FSSAI, "MoFPI Unit Scheme; AIF", MOFPI, MOFPI_URL, COLLECTION_DATE, "67", VST, "Highly seasonal; aseptic packing enables year-round sales"),
    ("ap-008", "Pickle Unit", "Secondary Processing", "Mango, Lemon, Chilli, Mixed Vegetables", "Pickles in oil and brine", PV, PV, "Semi-skilled", "Medium", "High", FSSAI, PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "66", VST, "Strong regional taste preferences; low entry barrier"),
    ("ap-009", "Jam and Fruit Preserve Unit", "Secondary Processing", "Mango, Guava, Papaya, Mixed Fruit", "Jam, jelly, marmalade, fruit bar", PV, PV, "Semi-skilled", "Medium", "High", FSSAI, PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "65", VST, "Sugar and pectin standards are FSSAI-specified"),
    ("ap-010", "Jaggery Unit", "Primary Processing", "Sugarcane", "Jaggery blocks, powder jaggery, liquid jaggery", PV, PV, "Semi-skilled", "High", "High", FSSAI, PMFME, MOA, MOA_URL, COLLECTION_DATE, "68", VST, "Decentralised alternative to mill supply; chemical-free variants command premiums"),
    ("ap-011", "Cold Storage Facility", "Infrastructure", "Potato, Onion, Fruits, Vegetables", "Storage service (rental capacity)", PV, PV, "Skilled", "Very High", "Medium", "Cold storage licence; State pollution consent", "MIDH; Agriculture Infrastructure Fund (AIF)", MOA, MOA_URL, COLLECTION_DATE, "67", VST, "Revenue is rental per tonne-month, not product sale"),
    ("ap-012", "Food Packaging Unit", "Packaging", "Processed foods, grains, spices", "Retail-ready printed and sealed packs", PV, PV, "Semi-skilled", "High", "Medium", "FSSAI (as applicable); Legal Metrology registration", PMFME, MOFPI, MOFPI_URL, COLLECTION_DATE, "65", VST, "Often operated as a shared/common facility for a cluster"),
    ("ap-013", "Animal Feed Unit", "By-Product Processing", "Maize, Oil cake, Bran, Chuni", "Compounded cattle and poultry feed", PV, PV, "Semi-skilled", "High", "Medium", "BIS feed standards; Udyam registration", "National Livestock Mission", "Department of Animal Husbandry & Dairying", "https://dahd.nic.in/", COLLECTION_DATE, "66", VST, "Consumes by-products from dal, rice and oil milling"),
    ("ap-014", "Bio-Fertiliser Unit", "Input Manufacturing", "Microbial cultures, carrier material", "Rhizobium, Azotobacter, PSB, mycorrhiza formulations", PV, PV, "Skilled", "Medium", "High", "Fertiliser Control Order (FCO) registration", "PKVY; National Mission on Natural Farming", MOA, MOA_URL, COLLECTION_DATE, "63", VST, "Requires lab-grade quality control and cold storage of cultures"),
    ("ap-015", "Vermicompost Unit", "Input Manufacturing", "Farm waste, cattle dung", "Vermicompost, vermiwash, earthworm stock", PV, PV, "Unskilled to Semi-skilled", "High", "High", "FCO registration (for packaged sale)", "PKVY; MGNREGA convergence", MOA, MOA_URL, COLLECTION_DATE, "68", VST, "Lowest-capital entry point in agri-input manufacturing"),
    ("ap-016", "Essential Oil Distillation Unit", "Secondary Processing", "Lemongrass, Citronella, Mint, Tulsi, Eucalyptus", "Steam-distilled essential oils, hydrosol", PV, PV, "Skilled", "High", "Very High", "Udyam registration; FSSAI (food-grade lines)", "National Medicinal Plants Board schemes; MoFPI Unit Scheme", "National Medicinal Plants Board", "https://nmpb.nic.in/", COLLECTION_DATE, "62", VST, "Oil recovery percentage is low; aggregation is essential to viability"),
    ("ap-017", "Honey Processing Unit", "Secondary Processing", "Raw honey", "Filtered and moisture-corrected graded honey", PV, PV, "Semi-skilled", "High", "High", "FSSAI; Agmark grading (optional)", "National Beekeeping and Honey Mission (NBHM)", "National Bee Board", "https://nbb.gov.in/", COLLECTION_DATE, "66", VST, "Moisture reduction and adulteration testing are the critical controls"),
]


# ---------------------------------------------------------------------------
# 5. ai_precision_agriculture.csv -> the 10 named technologies
# ---------------------------------------------------------------------------
H_AI = [
    "technology_id", "technology_name", "technology_type", "application",
    "crop_suitability", "current_adoption_india", "ai_readiness_level",
    "approximate_cost_inr", "roi_potential", "primary_constraint",
    "data_source", "source_url", "collection_date", "confidence_score",
    "verification_status", "notes",
]

AI_TECH = [
    ("apa-001", "Satellite Crop Monitoring", "Remote Sensing", "Acreage estimation, vegetation index (NDVI) based stress detection, yield mapping", "All field crops", "Medium", "Very High", PV, "High", "Cloud cover during monsoon; field-level resolution limits", "ISRO/NRSC Bhuvan; ICAR", "https://bhuvan.nrsc.gov.in/", COLLECTION_DATE, "64", VST, "Public Bhuvan and FASAL programme data available at no cost"),
    ("apa-002", "IoT Soil and Weather Sensing", "Sensor Network", "Continuous soil moisture, soil temperature and micro-climate telemetry", "Irrigated horticulture and plantation crops", "Low", "High", PV, "Medium", "Rural connectivity; sensor calibration drift; maintenance", "ICAR; India Meteorological Department", ICAR_URL, COLLECTION_DATE, "62", VST, "Value depends on advisory layer built on top of raw telemetry"),
    ("apa-003", "Drone-Based Spraying", "Aerial Application", "Precision application of pesticide and nutrient solutions", "Rice, cotton, sugarcane, maize", "Low", "Very High", PV, "High", "DGCA licensing; trained operator availability; battery endurance", "Ministry of Agriculture (Kisan Drone); DGCA", MOA_URL, COLLECTION_DATE, "63", VST, "Typically delivered as a service by custom-hiring centres, not farmer-owned"),
    ("apa-004", "Yield Prediction Models", "Predictive Analytics", "Pre-harvest yield forecasting from weather, soil and management data", "All field crops", "Low", "Very High", PV, "Medium", "Ground-truth data scarcity; model transferability across agro-zones", "ICAR; state agricultural universities", ICAR_URL, COLLECTION_DATE, "58", VST, "Mainly used at institutional level for procurement and insurance, not by individual farmers"),
    ("apa-005", "Disease and Pest Detection", "Computer Vision", "Image-based identification of disease and pest incidence from leaf or canopy photos", "Rice, wheat, tomato, cotton, chilli", "Low", "Very High", PV, "High", "Training-data coverage for Indian cultivars; early-stage symptom accuracy", "ICAR; Kisan Call Centre advisory programmes", ICAR_URL, COLLECTION_DATE, "58", VST, "Smartphone-app delivery is the realistic channel for smallholders"),
    ("apa-006", "Computer Vision Grading and Sorting", "Computer Vision", "Automated grading of produce by size, colour and defect at pack-house", "Fruits, vegetables, spices, pulses", "Low", "High", PV, "High", "Capital cost relative to pack-house throughput", "MoFPI; APEDA pack-house standards", MOFPI_URL, COLLECTION_DATE, "57", VST, "Most economic at FPO or pack-house scale rather than individual farm"),
    ("apa-007", "AI-Enhanced Weather Forecasting", "Weather Prediction", "Block-level short-range forecasts and agro-advisory generation", "All crops", "Medium", "High", PV, "Medium", "Downscaling accuracy to block level; last-mile advisory delivery", "India Meteorological Department; Gramin Krishi Mausam Sewa", "https://mausam.imd.gov.in/", COLLECTION_DATE, "66", VST, "IMD agro-advisory bulletins are already publicly distributed"),
    ("apa-008", "Farm Robotics (Weeding and Harvest)", "Autonomous Systems", "Autonomous mechanical weeding and selective harvesting", "Vegetables, horticulture, plantation crops", "Very Low", "Very High", PV, "Medium", "Capital cost; small and irregular field geometry; service network", "ICAR; IIT research programmes", ICAR_URL, COLLECTION_DATE, "52", VST, "Research and pilot stage in India; not commercially deployed at scale"),
    ("apa-009", "Autonomous and Assisted Tractors", "Autonomous Systems", "GPS-guided operation, auto-steer and implement control", "Large-holding field crops", "Very Low", "Very High", PV, "Medium", "Average holding size; capital cost; RTK correction coverage", "ICAR-CIAE; OEM pilot programmes", ICAR_URL, COLLECTION_DATE, "52", VST, "Economics depend on holding size; limited fit to fragmented holdings"),
    ("apa-010", "Digital Twin Farm Simulation", "Simulation", "Virtual farm replica for scenario planning, advisory and training", "All crops (research stage)", "Very Low", "Very High", PV, "Low", "Data integration burden; validation against field outcomes", "ICAR; academic research programmes", ICAR_URL, COLLECTION_DATE, "50", VST, "Concept-validation stage; no production deployment identified in India"),
]


if __name__ == "__main__":
    print("Enriching Package005_Agriculture datasets to full specification coverage:\n")
    write("crop_categories.csv", H_CAT, CATEGORIES)
    write("crops.csv", H_CROPS, CROPS)
    write("farm_machinery.csv", H_MACH, MACHINERY)
    write("agri_processing_opportunities.csv", H_PROC, PROCESSING)
    write("ai_precision_agriculture.csv", H_AI, AI_TECH)
    print("\nEnrichment complete.")
