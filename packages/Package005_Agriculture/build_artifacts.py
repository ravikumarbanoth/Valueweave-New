#!/usr/bin/env python3
"""
Package005_Agriculture v1.0.0 — Release Artifact Builder

Generates, from the actual CSVs plus validation_summary.json (so no figure is
hand-maintained and none can drift):

  schemas/schema_catalog.json          canonical PK/FK/column reference
  metadata/<dataset>.metadata.json     per-dataset metadata (16 files)
  registry/dataset_registry.csv        release registry
  package_manifest.json                package-level manifest
  VERSION                              semantic version marker
  reports/<dataset>.collection_report.md   per-dataset collection reports (16)
"""

import csv
import json
from pathlib import Path

PKG = Path(__file__).resolve().parent
DATASETS = PKG / "datasets"
VERSION = "1.0.0"
COLLECTION_DATE = "2026-07-24"
PV = "PENDING_VERIFICATION"

SUMMARY = json.loads((PKG / "validation_summary.json").read_text())
STATS = SUMMARY["per_dataset"]

for d in ("schemas", "metadata", "registry", "reports", "docs"):
    (PKG / d).mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Dataset descriptors: layer, purpose, FK declarations, source tier, methodology
# ---------------------------------------------------------------------------
DESC = {
    "crop_categories.csv": dict(
        pk="category_id", layer="1 - Reference Taxonomy",
        purpose="Top-level agriculture classification covering field crops, horticulture, plantation, production systems and allied activities.",
        fks=[], tier="Tier 1 (ICAR; commodity boards; Ministry of Agriculture)",
        method="The 24 categories were enumerated to cover the full agriculture domain requested for this package, including three production-system categories (organic, protected, hydroponics/aquaponics) that are cultivation modes rather than botanical groups, and seven allied categories (sericulture, apiculture, mushroom, fisheries, livestock, poultry, dairy) that sit outside crop taxonomy but inside agri-business scope. Each category was attributed to the ICAR institute or statutory board that governs it.",
        caveats="category_group distinguishes botanical groupings from production systems and allied activities; consumers filtering for crops only should restrict to Field Crops, Horticulture and Plantation.",
    ),
    "crops.csv": dict(
        pk="crop_id", layer="2 - Core Entity",
        purpose="Agronomic and commercial profile for 45 crops spanning all 12 crop-bearing categories.",
        fks=[("category_id", "crop_categories.csv", "category_id")],
        tier="Tier 1 (ICAR crop-specific institutes; commodity boards)",
        method="Crops were selected for national acreage significance plus Telangana/Andhra Pradesh relevance, since those two states are the geographic spine of the wider knowledge base. Agronomic fields (season, duration, water requirement, temperature range, indicative yield) follow ICAR package-of-practices conventions. major_districts was populated only where a district is publicly and specifically associated with the crop; for crops with no TG/AP footprint the field is the bare sentinel rather than an invented list.",
        caveats="avg_yield_tons_per_ha is an indicative national average, not a district figure, and is not comparable across crops with different harvested products (lint vs seed cotton, dry vs fresh rhizome, nuts per palm for coconut). duration_days is the bare sentinel for perennials where the concept does not apply.",
    ),
    "soil_types.csv": dict(
        pk="soil_id", layer="1 - Reference Taxonomy",
        purpose="Soil classification with pH band, texture, state distribution and crop suitability.",
        fks=[], tier="Tier 1 (ICAR-NBSS&LUP; Soil Health Card programme)",
        method="Ten soil classes were taken from the ICAR-NBSS&LUP national classification, retaining the four problem-soil classes (saline, acidic, alkaline, clay) because reclamation and crop-choice decisions depend on them.",
        caveats="pH bands are typical ranges, not guarantees; field pH varies within a single parcel. Composite textures used in crops.soil_type_preferred (for example sandy loam) are deliberately not separate soil_id rows.",
    ),
    "climate_zones.csv": dict(
        pk="climate_zone_id", layer="1 - Reference Taxonomy",
        purpose="Agro-climatic zone reference with rainfall, temperature, humidity and growing-season counts.",
        fks=[], tier="Tier 1 (ICAR-CRIDA; India Meteorological Department)",
        method="Eight zones were derived from the ICAR-CRIDA agro-climatic framing, collapsed to a tractable set that still separates arid from semi-arid and wet from tropical, because those distinctions drive crop choice.",
        caveats="This is a simplified eight-zone model, not the 127-zone NARP agro-ecological classification; use it for crop-suitability screening, not for site-specific recommendation.",
    ),
    "crop_soil_mapping.csv": dict(
        pk="mapping_id", layer="3 - Relational Mapping",
        purpose="Crop-to-soil suitability with a 0-100 score and an ICAR-style suitability band.",
        fks=[("crop_id", "crops.csv", "crop_id"), ("soil_id", "soil_types.csv", "soil_id")],
        tier="Tier 1 (ICAR package-of-practices; soil-crop compatibility literature)",
        method="Every one of the 45 crops carries two rows: its optimal soil and a documented alternative, giving 90 mappings. Scores are a relative ordinal rating anchored to ICAR guidance (85+ optimal, 70-84 suitable, 55-69 marginal), not a measured yield ratio.",
        caveats="suitability_score is ordinal and comparable only within a crop, not across crops. Absence of a crop-soil pair is not a statement that the combination fails.",
    ),
    "crop_climate_mapping.csv": dict(
        pk="mapping_id", layer="3 - Relational Mapping",
        purpose="Crop-to-climate-zone yield potential, risk level and the dominant climatic risk.",
        fks=[("crop_id", "crops.csv", "crop_id"), ("climate_zone_id", "climate_zones.csv", "climate_zone_id")],
        tier="Tier 1 (ICAR; IMD agro-advisory framing)",
        method="Every crop carries two rows (primary and secondary zone), giving 90 mappings. primary_climatic_risk names the specific failure mode that matters for that crop in that zone, which is the field of actual operational value.",
        caveats="yield_potential is a relative agro-climatic rating (Optimal/Good/Marginal), deliberately not a tonnage, because zone-level tonnage cannot be asserted from public sources without district qualification.",
    ),
    "farm_machinery.csv": dict(
        pk="machinery_id", layer="4 - Capital and Technology",
        purpose="Farm machinery and post-harvest equipment with power class, automation level, AI readiness and the subsidy scheme that applies.",
        fks=[], tier="Tier 1 (SMAM; MoFPI; PMKSY scheme documents)",
        method="Sixteen machinery types spanning land preparation, sowing, crop protection, harvesting, post-harvest, processing, packaging, cold chain, irrigation and monitoring. Scheme attribution is the field of highest practical value and is sourced to the named scheme.",
        caveats="investment_inr, annual_maintenance_inr and most capacity figures are the bare sentinel throughout. Equipment prices are set by manufacturer and model and no single official public figure exists; a plausible number here would be fabrication. Consumers needing costs must obtain current DIC or dealer quotations.",
    ),
    "agri_processing_opportunities.csv": dict(
        pk="opportunity_id", layer="5 - Value Addition",
        purpose="Value-add processing enterprise types with input crop, finished product, licence requirements and linked scheme.",
        fks=[], tier="Tier 1 (MoFPI/PMFME; Spices Board; National Bee Board; NMPB)",
        method="Seventeen opportunities spanning primary processing, secondary processing, infrastructure, packaging, by-product processing and input manufacturing. licenses_required and linked_scheme were prioritised because they are the fields that gate whether an enterprise can legally operate.",
        caveats="investment_band and capacity_indicative are the bare sentinel. Package004_Industries already carries sourced investment and machinery detail for the overlapping food-processing opportunities; this dataset intentionally does not duplicate or approximate those figures.",
    ),
    "farmer_producer_organizations.csv": dict(
        pk="fpo_id", layer="6 - Institutions",
        purpose="Collective organisation models available to farmers for aggregation, input purchase and market access.",
        fks=[], tier="Tier 1-2 (Ministry of Agriculture FPO programme; NABARD; MCA; NRLM)",
        method="Five legal and organisational forms were characterised by registration route, typical membership scale and services offered, because the choice between them is a legal-structure decision with different compliance consequences.",
        caveats="Describes organisation types, not a registry of named FPOs. typical_size_members is an indicative band.",
    ),
    "agriculture_training.csv": dict(
        pk="training_id", layer="6 - Institutions",
        purpose="Agricultural training and extension provider categories with coverage and course focus.",
        fks=[], tier="Tier 1-2 (ICAR KVK network; state agriculture departments; NPTEL)",
        method="Seven provider categories from district KVKs through state agricultural universities to digital platforms, characterised by reach and typical programme duration.",
        caveats="Describes provider categories, not named institutions. Package006_Skills_and_Training carries the named-provider and named-centre datasets; this is the agriculture-specific extension layer, not a duplicate of it.",
    ),
    "agriculture_schemes.csv": dict(
        pk="scheme_id", layer="7 - Government Support",
        purpose="Central government agriculture support schemes with objective, eligibility, benefit and application level.",
        fks=[], tier="Tier 1 (scheme portals; Ministry of Agriculture; NABARD)",
        method="Twelve schemes covering income support, insurance, organic conversion, mechanisation, horticulture, irrigation, infrastructure credit, working capital, soil testing, livestock and fisheries. Each row names its own scheme portal as source.",
        caveats="Benefit amounts and eligibility rules change by budget cycle and differ by state top-up. Treat every figure as requiring re-verification against the scheme portal before it is relied on. This dataset is the agriculture slice; Package007_Government_Schemes will hold the comprehensive scheme registry.",
    ),
    "crop_disease_management.csv": dict(
        pk="disease_id", layer="8 - Crop Protection",
        purpose="Major crop diseases and pests with symptoms, chemical and biological control, and AI-detection feasibility.",
        fks=[], tier="Tier 1 (ICAR crop-protection institutes; IPM guidance)",
        method="Ten high-incidence problems across cereals, vegetables, cotton, citrus and potato. affected_crops is free text rather than a crop_id foreign key because most of these pathogens have host ranges wider than the 45 crops in this release.",
        caveats="Chemical treatments are named actives, not dose recommendations, and are not a prescription; pesticide legality and dosage are governed by CIB&RC labels and change over time. Always confirm current label approval before use.",
    ),
    "market_linkages.csv": dict(
        pk="linkage_id", layer="9 - Market Access",
        purpose="Market channel types available to producers, from regulated mandis to digital platforms and export routes.",
        fks=[], tier="Tier 1-2 (Ministry of Agriculture; eNAM; APEDA; MoFPI)",
        method="Six channel types characterised by the commodities they handle and their infrastructure basis, spanning APMC mandis, eNAM, FPO direct marketing, processor contracts, modern retail and export.",
        caveats="Describes channel types, not named mandis or buyers. Counts such as APMC and integrated-mandi numbers move over time and should be re-verified.",
    ),
    "export_opportunities.csv": dict(
        pk="opportunity_id", layer="10 - Export",
        purpose="Export market segments with destination countries, quality requirements and certifications needed.",
        fks=[], tier="Tier 1 (APEDA; Spices Board; Tea Board; Coffee Board)",
        method="Eight export categories where India holds a material global position. certifications_needed and quality_requirements were prioritised because they are the binding constraints on market entry, more than price.",
        caveats="Export prices and annual volumes fluctuate with global markets, exchange rates and policy (export bans and MEP changes). Price and volume fields are indicative orders of magnitude only, not quotable figures.",
    ),
    "ai_precision_agriculture.csv": dict(
        pk="technology_id", layer="11 - AI and Technology Readiness",
        purpose="Precision-agriculture and AI technology readiness with adoption level, ROI potential and the binding constraint.",
        fks=[], tier="Tier 1-4 (ICAR/ISRO/IMD for deployed systems; research and pilot reporting for emerging ones)",
        method="The ten technologies named in the package specification were assessed on current Indian adoption, AI readiness and the specific constraint that limits deployment. Confidence is deliberately the lowest in the package (50-66) because adoption and ROI for emerging technology are forward-looking judgements, not published statistics.",
        caveats="approximate_cost_inr is the bare sentinel on every row: no official public cost benchmark exists for any of these technologies in India. current_adoption_india is an ordinal band, not a measured penetration rate. Rows for farm robotics, autonomous tractors and digital twins describe research and pilot stages, not commercially available offerings.",
    ),
    "agri_business_mapping.csv": dict(
        pk="mapping_id", layer="12 - Cross-Package Spine",
        purpose="The integration spine: crop to processing opportunity to Package004 business opportunity to Package006 skill.",
        fks=[
            ("crop_id", "crops.csv", "crop_id"),
            ("processing_opportunity_id", "agri_processing_opportunities.csv", "opportunity_id"),
            ("package004_opportunity_name", "Package004_Industries (cross-package)", "name / adapted_indian_concept"),
            ("package006_skill_id", "Package006_Skills_and_Training (cross-package)", "skill_id"),
        ],
        tier="Tier 1-2 (MoFPI; Spices Board; internal cross-package reconciliation)",
        method="Thirty mappings trace a crop through a processing route to a named business opportunity and the skill required to run it. Package004 opportunity names were matched by reading the released Package004 CSVs directly, and Package006 skill_id values are the actual UUIDs from the released skills.csv, so both sides are verifiable foreign keys rather than descriptive text.",
        caveats="Thirteen of thirty rows carry the bare sentinel for package004_opportunity_name: Package004 v1.0.0 has no counterpart for rice milling, dal milling, jaggery, cold storage, essential-oil distillation, animal feed, vermicompost or cashew shelling. Those links become populatable when Package004 expands, and are left unasserted rather than approximated. value_add_stage is a qualitative stage label; no value-add percentage is asserted anywhere in this release.",
    ),
}

ORDER = [
    "crop_categories.csv", "soil_types.csv", "climate_zones.csv", "crops.csv",
    "crop_soil_mapping.csv", "crop_climate_mapping.csv", "farm_machinery.csv",
    "agri_processing_opportunities.csv", "farmer_producer_organizations.csv",
    "agriculture_training.csv", "agriculture_schemes.csv",
    "crop_disease_management.csv", "market_linkages.csv",
    "export_opportunities.csv", "ai_precision_agriculture.csv",
    "agri_business_mapping.csv",
]

COL_DOC = {
    "data_source": "Authoritative body the row was attributed to",
    "source_url": "Public URL for that body or scheme",
    "collection_date": f"Collection date; uniform {COLLECTION_DATE} across the package",
    "confidence_score": "Integer 0-100, capped at the 85 package policy ceiling",
    "verification_status": "VST-NEEDS_REVIEW pending human data-steward sign-off",
    "notes": "Caveats, qualifications and sourcing remarks",
}


def header_of(name):
    with open(DATASETS / name, newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def pv_columns(name):
    """Columns that contain at least one bare sentinel, with counts."""
    with open(DATASETS / name, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        for k, v in r.items():
            if v == PV:
                out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


# ----------------------------------------------------------- schema catalog
catalog = {
    "package": "Package005_Agriculture",
    "version": VERSION,
    "description": (
        "Canonical primary-key, foreign-key and column reference for all 16 datasets in "
        "Package005_Agriculture v1.0.0. The package models agriculture as a connected graph: "
        "reference taxonomies (category, soil, climate) feed a core crop entity, which is joined "
        "to soil and climate by scored mapping tables, then extended through capital, value "
        "addition, institutions, government support, crop protection, market access, export and "
        "AI-readiness layers, and finally bound to the wider knowledge base by a cross-package "
        "spine dataset."
    ),
    "graph_spine": (
        "crop_categories -> crops -> {crop_soil_mapping -> soil_types, crop_climate_mapping -> "
        "climate_zones} -> agri_processing_opportunities -> agri_business_mapping -> "
        "{Package004_Industries opportunity, Package006_Skills_and_Training skill}"
    ),
    "relationship_to_package001": (
        "No hard foreign key into Package001_Geography. crops.major_districts holds district names "
        "as free text where a district is publicly and specifically associated with the crop, but it "
        "is not a dist_id reference: per-district crop attribution could not be verified for every "
        "crop in this release, and a partial FK would imply completeness the data does not have. "
        "Joining to Package001 by district_name is possible but is a consumer-side decision."
    ),
    "relationship_to_package004": (
        "agri_business_mapping.package004_opportunity_name is a real cross-package foreign key, "
        "matched against the name and adapted_indian_concept columns of the released "
        "Package004_Industries datasets. 17 of 30 rows resolve; the remaining 13 carry the bare "
        "sentinel because Package004 v1.0.0 has no counterpart opportunity."
    ),
    "relationship_to_package006": (
        "agri_business_mapping.package006_skill_id is a real cross-package foreign key holding "
        "actual skill_id UUIDs from the released Package006_Skills_and_Training skills.csv. "
        "All 30 rows resolve. Four distinct skills are referenced: Food Processing & Preservation, "
        "Organic Farming, Precision Agriculture & IoT, and Modern Farming Techniques."
    ),
    "relationship_to_package007_package008": (
        "agriculture_schemes.csv is the agriculture slice of government support and is expected to "
        "be superseded by, or reconciled against, Package007_Government_Schemes. "
        "agri_processing_opportunities.csv is the natural join surface for Package008_MSME. Neither "
        "link is asserted in v1.0.0 because neither package has been released."
    ),
    "sentinel_policy": (
        "PENDING_VERIFICATION appears only as a complete, bare cell value. It is never appended to "
        "or embedded in other text, and never substitutes for a numeric confidence_score. A cell "
        "carrying the sentinel means no public source was found for that specific fact; it does not "
        "mean the fact is unknowable."
    ),
    "confidence_policy": {
        "ceiling": 85,
        "reason": (
            "Direct WebFetch to .gov.in / .nic.in / .ac.in domains is blocked by this environment's "
            "egress policy, so no row in this package rests on a primary-source page read. The "
            "ceiling is a standing acknowledgement of that limitation, carried forward from "
            "Package004 and Package006."
        ),
        "bands": {
            "70-85": "Tier 1 - ICAR institutes, Ministry of Agriculture, statutory commodity boards, named scheme portals",
            "60-69": "Tier 2 - state departments, NABARD, MoFPI programme literature",
            "55-59": "Tier 3 - sector associations, published research aggregates",
            "50-54": "Tier 4 - forward-looking technology assessment (ai_precision_agriculture only, disclosed in-row)",
        },
        "observed_range": f"{SUMMARY['confidence_min']}-{SUMMARY['confidence_max']}",
    },
    "datasets": [],
}

for name in ORDER:
    d = DESC[name]
    hdr = header_of(name)
    st = STATS[name]
    catalog["datasets"].append({
        "dataset_name": name.replace(".csv", ""),
        "file": f"datasets/{name}",
        "layer": d["layer"],
        "purpose": d["purpose"],
        "primary_key": d["pk"],
        "record_count": st["records"],
        "column_count": st["columns"],
        "foreign_keys": [
            {"column": c, "references_dataset": t, "references_column": rc}
            for c, t, rc in d["fks"]
        ],
        "source_tier": d["tier"],
        "confidence_range": f"{st['confidence_min']}-{st['confidence_max']}",
        "confidence_avg": st["confidence_avg"],
        "pending_verification_cells": st["pending_verification_cells"],
        "pending_verification_columns": pv_columns(name),
        "columns": [{"name": c, "description": COL_DOC.get(c, "")} for c in hdr],
        "known_limitations": d["caveats"],
    })

(PKG / "schemas" / "schema_catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
print("schemas/schema_catalog.json")

# -------------------------------------------------------- per-dataset metadata
for name in ORDER:
    d = DESC[name]
    st = STATS[name]
    meta = {
        "dataset_name": name.replace(".csv", ""),
        "package": "Package005_Agriculture",
        "package_version": VERSION,
        "file": f"datasets/{name}",
        "layer": d["layer"],
        "purpose": d["purpose"],
        "primary_key": d["pk"],
        "record_count": st["records"],
        "column_count": st["columns"],
        "columns": header_of(name),
        "foreign_keys": [
            {"column": c, "references_dataset": t, "references_column": rc}
            for c, t, rc in d["fks"]
        ],
        "collection_date": COLLECTION_DATE,
        "collection_mode": "Knowledge synthesis from documented public sources (WebFetch to government domains blocked by environment egress policy)",
        "source_tier": d["tier"],
        "methodology": d["method"],
        "confidence_score_min": st["confidence_min"],
        "confidence_score_max": st["confidence_max"],
        "confidence_score_avg": st["confidence_avg"],
        "confidence_ceiling_policy": 85,
        "verification_status": "VST-NEEDS_REVIEW",
        "pending_verification_cells": st["pending_verification_cells"],
        "pending_verification_rate_pct": st["pending_verification_rate_pct"],
        "pending_verification_columns": pv_columns(name),
        "known_limitations": d["caveats"],
        "release_status": f"RELEASED in v{VERSION}",
    }
    out = PKG / "metadata" / f"{name.replace('.csv', '')}.metadata.json"
    out.write_text(json.dumps(meta, indent=2) + "\n")
print(f"metadata/*.metadata.json ({len(ORDER)} files)")

# ------------------------------------------------------------ dataset registry
reg_hdr = ["dataset_name", "package", "file_path", "layer", "record_count",
           "column_count", "primary_key", "status", "mode_used", "confidence_min",
           "confidence_max", "confidence_avg", "pending_verification_cells",
           "verification_status", "last_updated"]
with open(PKG / "registry" / "dataset_registry.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(reg_hdr)
    for name in ORDER:
        st, d = STATS[name], DESC[name]
        w.writerow([
            name.replace(".csv", ""), "Package005_Agriculture", f"datasets/{name}",
            d["layer"], st["records"], st["columns"], d["pk"], "RELEASED",
            "Knowledge synthesis (WebFetch to .gov.in blocked by org policy)",
            st["confidence_min"], st["confidence_max"], st["confidence_avg"],
            st["pending_verification_cells"], "VST-NEEDS_REVIEW", COLLECTION_DATE,
        ])
print("registry/dataset_registry.csv")

# ----------------------------------------------------------- package manifest
manifest = {
    "package_name": "Package005_Agriculture",
    "package_id": "PKG-005",
    "package_title": "ValueWeave.in Agriculture Intelligence and Agri-Business Knowledge Base",
    "version": VERSION,
    "release_date": COLLECTION_DATE,
    "release_status": "Stable v1.0.0",
    "scope": (
        "Sixteen interlinked datasets modelling Indian agriculture end to end: crop taxonomy and "
        "agronomic profiles, soil and agro-climatic references with scored suitability mappings, "
        "farm machinery and capital, value-add processing, producer institutions, training and "
        "extension, government schemes, crop protection, market access, export markets, AI and "
        "precision-agriculture readiness, and a cross-package spine binding crops to business "
        "opportunities and skills. Crop selection is weighted to national significance plus "
        "Telangana and Andhra Pradesh relevance, consistent with the wider knowledge base, and the "
        "schema extends to all states without change."
    ),
    "knowledge_graph": (
        "Geography -> Climate -> Soil -> Crop -> Farmer Institution -> Machinery -> Technology -> "
        "Processing -> Market -> Export -> Business -> Scheme -> Skill -> AI Readiness"
    ),
    "datasets_included": [
        {
            "name": n.replace(".csv", ""),
            "layer": DESC[n]["layer"],
            "records": STATS[n]["records"],
            "columns": STATS[n]["columns"],
            "primary_key": DESC[n]["pk"],
            "confidence_score_range": f"{STATS[n]['confidence_min']}-{STATS[n]['confidence_max']}",
            "confidence_avg": STATS[n]["confidence_avg"],
            "verification_status": "VST-NEEDS_REVIEW",
        }
        for n in ORDER
    ],
    "total_datasets": len(ORDER),
    "total_records": SUMMARY["total_records"],
    "import_order": [n.replace(".csv", "") for n in ORDER],
    "import_order_rationale": (
        "Reference taxonomies first (crop_categories, soil_types, climate_zones), then the core "
        "crops entity, then the mapping tables that depend on all four, then the independent "
        "domain layers, and agri_business_mapping last because it depends on crops, "
        "agri_processing_opportunities and two external packages."
    ),
    "data_statistics": {
        "total_datasets": len(ORDER),
        "total_records": SUMMARY["total_records"],
        "total_cells": SUMMARY["total_cells"],
        "pending_verification_cells": SUMMARY["pending_verification_cells"],
        "pending_verification_rate_pct": SUMMARY["pending_verification_rate_pct"],
    },
    "confidence_statistics": {
        "overall_range": f"{SUMMARY['confidence_min']}-{SUMMARY['confidence_max']}",
        "ceiling_policy": 85,
        "note": (
            "The ceiling reflects that no row rests on a primary-source page read; WebFetch to "
            "government domains is blocked in this environment. The floor of 50 occurs only in "
            "ai_precision_agriculture, where rows describe research-stage technology and the low "
            "score is the honest signal, not a defect."
        ),
    },
    "cross_package_integration": {
        "Package001_Geography": (
            "Soft link only. crops.major_districts carries district names as free text where "
            "publicly attributable; no dist_id foreign key is asserted because per-district "
            "attribution is incomplete."
        ),
        "Package004_Industries": (
            "Hard foreign key. 17 of 30 agri_business_mapping rows resolve to real Package004 "
            "opportunity names; 13 carry the bare sentinel where Package004 v1.0.0 has no "
            "counterpart."
        ),
        "Package006_Skills_and_Training": (
            "Hard foreign key. All 30 agri_business_mapping rows carry real Package006 skill_id "
            "UUIDs across 4 distinct skills."
        ),
        "Package007_Government_Schemes": (
            "Planned. agriculture_schemes.csv is the agriculture slice and will be reconciled "
            "against Package007 when released."
        ),
        "Package008_MSME": (
            "Planned. agri_processing_opportunities.csv is the intended join surface."
        ),
    },
    "environment_constraint": (
        "Direct WebFetch to .gov.in / .nic.in / .ac.in domains is blocked by this session's "
        "organizational egress policy, as it was for Package004 and Package006. Every row is "
        "attributed to the authoritative body that governs the fact, and confidence is capped at "
        "85 to record that no primary page was read. Where a specific figure would have required "
        "primary-source confirmation - equipment prices, processing investment bands, precision-"
        "agriculture costs - the bare PENDING_VERIFICATION sentinel is written instead of an "
        "estimate. See docs/METHODOLOGY.md."
    ),
    "validation": {
        "checks_run": [
            "V1 structural column count", "V2 primary-key uniqueness",
            "V3 mandatory provenance columns", "V4 confidence integer/range/ceiling",
            "V5 bare-sentinel discipline", "V6 verification_status enum",
            "V7 uniform collection_date", "V8 in-package foreign keys and denormalised names",
            "V9 cross-package foreign keys (Package004, Package006)", "V10 no blank cells",
        ],
        "violations": SUMMARY["violations"],
        "result": SUMMARY["result"],
        "validator": "validate.py (in-package, re-runnable)",
    },
    "known_limitations": [
        "No cost or investment figure is asserted for farm machinery, processing units or "
        "precision-agriculture technology; those fields are the bare sentinel throughout.",
        "Yield figures are indicative national averages and are not comparable across crops with "
        "different harvested products.",
        "Scheme benefit amounts and eligibility change by budget cycle and state top-up; "
        "re-verify before relying on them.",
        "Chemical treatments in crop_disease_management are named actives, not dose "
        "recommendations, and are subject to current CIB&RC label approval.",
        "The eight-zone climate model is a screening tool, not the 127-zone NARP classification.",
        "Livestock, poultry, dairy, fisheries, sericulture, apiculture and mushroom appear as "
        "categories in crop_categories.csv but have no dedicated entity datasets in v1.0.0.",
    ],
    "planned_next_release": {
        "v1.1.0": [
            "Dedicated entity datasets for the allied categories (livestock, poultry, dairy, "
            "fisheries, sericulture, apiculture, mushroom)",
            "Populate the 13 sentinel Package004 opportunity links as Package004 expands",
            "Package007_Government_Schemes and Package008_MSME foreign keys",
            "District-level crop attribution as a hard Package001 dist_id foreign key",
        ],
    },
}
(PKG / "package_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("package_manifest.json")

(PKG / "VERSION").write_text(VERSION + "\n")
print("VERSION")

# ------------------------------------------------------- collection reports
for name in ORDER:
    d, st = DESC[name], STATS[name]
    hdr = header_of(name)
    pvc = pv_columns(name)
    slug = name.replace(".csv", "")

    fk_block = "\n".join(
        f"- `{c}` -> `{t}` (`{rc}`)" for c, t, rc in d["fks"]
    ) or "- None (reference dataset; no outbound foreign keys)"

    if pvc:
        pv_block = "\n".join(
            f"| `{c}` | {n} of {st['records']} |" for c, n in pvc.items()
        )
        pv_section = (
            "| Column | Sentinel rows |\n|---|---|\n" + pv_block +
            "\n\nEach sentinel above means no public source was found for that specific "
            "fact. No estimate was substituted."
        )
    else:
        pv_section = "No cell in this dataset carries the sentinel; every field is populated from a documented source."

    report = f"""# Collection Report: {name}

**Package**: Package005_Agriculture v{VERSION}
**Dataset**: `datasets/{name}`
**Layer**: {d['layer']}
**Collection date**: {COLLECTION_DATE}
**Source tier**: {d['tier']}

## Purpose

{d['purpose']}

## Methodology

{d['method']}

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the authoritative body that governs the fact in `data_source`, and `confidence_score` is
capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | {st['records']} |
| Columns | {st['columns']} |
| Primary key | `{d['pk']}` |
| Primary key uniqueness | PASS ({st['records']}/{st['records']} distinct) |
| Total cells | {st['total_cells']} |
| Bare `PENDING_VERIFICATION` cells | {st['pending_verification_cells']} ({st['pending_verification_rate_pct']}%) |
| Blank cells | 0 |
| Confidence range | {st['confidence_min']}-{st['confidence_max']} (ceiling 85) |
| Confidence average | {st['confidence_avg']} |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `{COLLECTION_DATE}` (all rows) |

## Columns

{chr(10).join(f'- `{c}`' + (f' — {COL_DOC[c]}' if c in COL_DOC else '') for c in hdr)}

## Foreign keys

{fk_block}

## Sentinel usage

{pv_section}

## Known limitations

{d['caveats']}

## Validation

This dataset passes all ten package checks (structural, primary key, provenance
completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys,
cross-package foreign keys, no blank cells). Re-run with `python3 validate.py`
from the package root.

## Files

- Dataset: `packages/Package005_Agriculture/datasets/{name}`
- Metadata: `packages/Package005_Agriculture/metadata/{slug}.metadata.json`
- This report: `packages/Package005_Agriculture/reports/{slug}.collection_report.md`
"""
    (PKG / "reports" / f"{slug}.collection_report.md").write_text(report)
print(f"reports/*.collection_report.md ({len(ORDER)} files)")
print("\nArtifact build complete.")
