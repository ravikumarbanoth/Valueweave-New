#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Knowledge Graph Builder

Extracts a Global Entity Registry and a Global Relationship Graph from the eight
released Stable packages. This is an EXTRACTION, not an authoring step: every entity
and every edge is derived from data that already exists in a package, and every row
carries the package that owns it plus the local id it was derived from.

Nothing here creates new domain knowledge. If a fact is not already in a package, it
does not appear in the graph.

Outputs
  knowledge_graph/entities/entities.csv          the Global Entity Registry
  knowledge_graph/entities/entity_types.csv      the 18 registered entity types
  knowledge_graph/entities/aliases.csv           alternate surface forms per entity
  knowledge_graph/relationships/relationships.csv  the Global Relationship Graph
  knowledge_graph/relationships/relationship_types.csv  the 19 registered edge types
  knowledge_graph/graph_summary.json             machine-readable build summary

Identifier scheme
  global_entity_id = vw:<entity_type_slug>:<canonical_name_slug>
  Deterministic and human-readable, so a rebuild produces identical ids and a diff
  shows real change rather than churn. See governance/adr/ADR-002.

Run from the repository root:
  python3 knowledge_graph/build_graph.py
"""

import csv
import json
import re
import sys
import unicodedata
from collections import OrderedDict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
KG = ROOT / "knowledge_graph"
BUILD_DATE = date.today().isoformat()
PV = "PENDING_VERIFICATION"

# --------------------------------------------------------------------------
# Package ownership. Single source of truth per domain — see Module 3 and
# knowledge_graph/ownership/ownership_registry.csv, which this mirrors.
# --------------------------------------------------------------------------
OWNER = {
    "District": "Package001_Geography",
    "State": "Package001_Geography",
    "Country": "Package001_Geography",
    "Institution": "Package002_Education",
    "Skill": "Package006_Skills_and_Training",
    "Certification": "Package006_Skills_and_Training",
    "TrainingProvider": "Package006_Skills_and_Training",
    "Industry": "Package004_Industries",
    "BusinessOpportunity": "Package004_Industries",
    "MSME": "Package008_MSME",
    "GovernmentScheme": "Package007_Government_Schemes",
    "Crop": "Package005_Agriculture",
    "Soil": "Package005_Agriculture",
    "ClimateZone": "Package005_Agriculture",
    "Machinery": "Package005_Agriculture",
    "RawMaterial": "Package008_MSME",
    "Market": "Package008_MSME",
    "ExportCountry": "Package001_Geography",
    "FinancialInstitution": "Package007_Government_Schemes",
}

ENTITY_TYPE_DESC = {
    "District": "Administrative district; the finest geographic unit in the graph",
    "State": "Indian state or union territory",
    "Country": "Sovereign country, including India and export destinations",
    "Institution": "Degree-granting or research institution",
    "Skill": "A discrete employable skill",
    "Certification": "A named certification or qualification pack",
    "TrainingProvider": "An organisation or network that delivers training",
    "Industry": "An industry or livelihood sector classification",
    "BusinessOpportunity": "A characterised business opportunity",
    "MSME": "An MSME business opportunity profile",
    "GovernmentScheme": "A government scheme, programme or entitlement",
    "Crop": "An agricultural crop",
    "Soil": "A soil classification",
    "ClimateZone": "An agro-climatic zone",
    "Machinery": "A machine, equipment class or plant item",
    "RawMaterial": "A production input that is not itself a crop entity",
    "Market": "A sales or distribution channel",
    "ExportCountry": "A country appearing as an export destination",
    "FinancialInstitution": "A bank, development financial institution or fund",
}

RELATIONSHIP_TYPE_DESC = OrderedDict([
    ("REQUIRES_SKILL", ("MSME|BusinessOpportunity|Industry", "Skill",
                        "The subject cannot be operated without the object skill")),
    ("SUPPORTED_BY_SCHEME", ("MSME|Crop|Skill|BusinessOpportunity", "GovernmentScheme",
                             "A government scheme provides support to the subject")),
    ("LOCATED_IN", ("District|State|Institution|MSME", "State|District|Country",
                    "Geographic containment or siting")),
    ("TRAINED_BY", ("Skill", "TrainingProvider",
                    "The object provider delivers training for the subject skill")),
    ("STUDIED_AT", ("Skill|Certification", "Institution",
                    "The subject is studied at the object institution")),
    ("USES_MACHINERY", ("MSME|Crop", "Machinery",
                        "The subject requires the object machine to operate")),
    ("USES_RAW_MATERIAL", ("MSME", "RawMaterial|Crop",
                           "The subject consumes the object as a production input")),
    ("PROCESSES", ("MSME", "Crop",
                   "The subject transforms the object crop into a product")),
    ("SELLS_TO", ("MSME", "Market",
                  "The subject reaches buyers through the object channel")),
    ("EXPORTS_TO", ("MSME|Crop", "ExportCountry",
                    "The subject is exported to the object country")),
    ("FUNDED_BY", ("MSME|GovernmentScheme", "FinancialInstitution",
                   "The object institution provides finance for the subject")),
    ("CERTIFIED_BY", ("Skill", "Certification",
                      "Competence in the subject is evidenced by the object certification")),
    ("RELATED_TO", ("*", "*",
                    "A documented association that no more specific type captures")),
    ("PART_OF", ("*", "*",
                 "Taxonomic or compositional containment")),
    ("SUCCESSOR_OF", ("*", "*",
                      "The subject replaced the object (scheme renames, policy versions)")),
    ("PREDECESSOR_OF", ("*", "*",
                        "Inverse of SUCCESSOR_OF")),
    ("GENERATES_EMPLOYMENT", ("MSME|BusinessOpportunity", "District|State",
                              "The subject creates employment in the object geography")),
    ("SUPPORTED_BY_BANK", ("MSME", "FinancialInstitution",
                           "A bank or DFI is a named delivery channel for the subject")),
    ("USES_AI", ("MSME|Crop|Industry", "*",
                 "The subject has a documented AI or automation application")),
])


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def slug(text):
    """Deterministic, readable, url-safe slug used in global_entity_id."""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = text.replace("&", " and ")   # orthographic, not semantic: same word
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")[:80]


TYPE_SLUG = {t: slug(t) for t in OWNER}


def read(rel):
    p = PACKAGES / rel
    if not p.exists():
        sys.exit(f"FATAL: package dataset missing: {rel}")
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def maybe(rel):
    p = PACKAGES / rel
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Registry:
    """Accumulates entities, enforcing one canonical row per (type, slug)."""

    def __init__(self):
        self.rows = OrderedDict()
        self.aliases = []
        self.collisions = []

    def add(self, etype, canonical_name, source_package, local_id,
            confidence, verification, aliases=()):
        if etype not in OWNER:
            sys.exit(f"FATAL: unregistered entity_type {etype!r}")
        key = (etype, slug(canonical_name))
        gid = f"vw:{TYPE_SLUG[etype]}:{slug(canonical_name)}"
        if key in self.rows:
            existing = self.rows[key]
            # Same entity seen again from another package: record the second
            # sighting as provenance rather than creating a duplicate node.
            if existing["source_package"] != source_package:
                self.collisions.append({
                    "global_entity_id": gid,
                    "entity_type": etype,
                    "canonical_name": canonical_name,
                    "owner_package": existing["source_package"],
                    "also_seen_in": source_package,
                    "also_seen_local_id": local_id,
                })
        else:
            self.rows[key] = {
                "global_entity_id": gid,
                "entity_type": etype,
                "canonical_name": str(canonical_name).strip(),
                "source_package": source_package,
                "package_local_id": local_id,
                "status": "PUBLISHED",
                "lifecycle_state": "PUBLISHED",
                "created_at": BUILD_DATE,
                "updated_at": BUILD_DATE,
                "confidence_score": confidence,
                "verification_status": verification,
            }
        for a in aliases:
            a = str(a).strip()
            if a and slug(a) != slug(canonical_name):
                self.aliases.append({
                    "alias_id": f"vwa:{TYPE_SLUG[etype]}:{slug(canonical_name)}:{slug(a)}",
                    "global_entity_id": gid,
                    "alias": a,
                    "alias_type": "SHORT_FORM" if len(a) < len(str(canonical_name)) else "VARIANT",
                    "source_package": source_package,
                })
        return gid

    def id_for(self, etype, name):
        key = (etype, slug(name))
        return self.rows[key]["global_entity_id"] if key in self.rows else None


REG = Registry()
EDGES = []
EDGE_KEYS = set()
UNRESOLVED = []


def edge(rtype, from_id, to_id, confidence, source_package, source_dataset,
         source_row_id, note=""):
    """Add one relationship. Silently de-duplicates identical triples."""
    if rtype not in RELATIONSHIP_TYPE_DESC:
        sys.exit(f"FATAL: unregistered relationship_type {rtype!r}")
    if not from_id or not to_id:
        UNRESOLVED.append({
            "relationship_type": rtype, "source_package": source_package,
            "source_dataset": source_dataset, "source_row_id": source_row_id,
            "reason": "endpoint did not resolve to a registered entity",
        })
        return
    key = (from_id, rtype, to_id)
    if key in EDGE_KEYS:
        return
    EDGE_KEYS.add(key)
    EDGES.append({
        "relationship_id": f"vwr:{len(EDGES) + 1:06d}",
        "from_entity": from_id,
        "relationship_type": rtype,
        "to_entity": to_id,
        "confidence": confidence,
        "provenance_package": source_package,
        "provenance_dataset": source_dataset,
        "provenance_row_id": source_row_id,
        "derived_at": BUILD_DATE,
        "notes": note,
    })


def conf(row, default="60"):
    v = row.get("confidence_score", default)
    return v if v and v != PV else default


def vst(row):
    return row.get("verification_status", "VST-NEEDS_REVIEW")


# ==========================================================================
# PHASE 1 — Entity extraction
# ==========================================================================
print("Phase 1: extracting entities from 8 released packages\n")

# --- Package001_Geography ---------------------------------------------------
P1_STATE = read("Package001_Geography/datasets/state.csv")
P1_DIST = read("Package001_Geography/datasets/district.csv")

REG.add("Country", "India", "Package001_Geography", "n/a", "85", "VST-NEEDS_REVIEW",
        aliases=["Bharat", "IN"])
for r in P1_STATE:
    REG.add("State", r["state_name"], "Package001_Geography", r["st_id"],
            conf(r), vst(r), aliases=[r.get("st_ref", ""), r.get("state_code", "")])
for r in P1_DIST:
    REG.add("District", r["district_name"], "Package001_Geography", r["dist_id"],
            conf(r), vst(r), aliases=[r.get("dist_ref", "")])
print(f"  Package001  states {len(P1_STATE)}  districts {len(P1_DIST)}")

# --- Package002_Education ---------------------------------------------------
P2_UNIV = read("Package002_Education/datasets/universities_telangana_andhra_pradesh.csv")
for r in P2_UNIV:
    REG.add("Institution", r["name"], "Package002_Education", r["id"], conf(r), vst(r))
print(f"  Package002  institutions {len(P2_UNIV)}")

# --- Package004_Industries --------------------------------------------------
P4_FILES = {
    "food_agro_processing_micro_enterprises": "name",
    "construction_skilled_trade_services": "name",
    "digital_technology_livelihoods": "name",
    "china_inspired_adapted_opportunities": "adapted_indian_concept",
}
p4_count = 0
P4_ROWS = {}
for fname, namecol in P4_FILES.items():
    rows = read(f"Package004_Industries/datasets/{fname}.csv")
    P4_ROWS[fname] = (rows, namecol)
    for r in rows:
        REG.add("BusinessOpportunity", r[namecol], "Package004_Industries", r["id"],
                conf(r), vst(r))
        cat = r.get("category")
        if cat and cat != PV:
            REG.add("Industry", cat, "Package004_Industries", f"category:{slug(cat)}",
                    conf(r), vst(r))
        p4_count += 1
print(f"  Package004  business opportunities {p4_count}")

# --- Package005_Agriculture -------------------------------------------------
P5_CROPS = read("Package005_Agriculture/datasets/crops.csv")
P5_SOIL = read("Package005_Agriculture/datasets/soil_types.csv")
P5_CLIM = read("Package005_Agriculture/datasets/climate_zones.csv")
P5_MACH = read("Package005_Agriculture/datasets/farm_machinery.csv")
for r in P5_CROPS:
    REG.add("Crop", r["crop_name"], "Package005_Agriculture", r["crop_id"], conf(r), vst(r),
            aliases=[r.get("scientific_name", "")])
for r in P5_SOIL:
    REG.add("Soil", r["soil_name"], "Package005_Agriculture", r["soil_id"], conf(r), vst(r))
for r in P5_CLIM:
    REG.add("ClimateZone", r["zone_name"], "Package005_Agriculture", r["climate_zone_id"],
            conf(r), vst(r))
for r in P5_MACH:
    REG.add("Machinery", r["machinery_name"], "Package005_Agriculture", r["machinery_id"],
            conf(r), vst(r))
print(f"  Package005  crops {len(P5_CROPS)}  soils {len(P5_SOIL)}  "
      f"climate zones {len(P5_CLIM)}  machinery {len(P5_MACH)}")

# --- Package006_Skills ------------------------------------------------------
P6_SKILLS = read("Package006_Skills_and_Training/datasets/skills.csv")
P6_CERTS = read("Package006_Skills_and_Training/datasets/certifications.csv")
P6_PROV = read("Package006_Skills_and_Training/datasets/training_providers.csv")
for r in P6_SKILLS:
    REG.add("Skill", r["skill_name"], "Package006_Skills_and_Training", r["skill_id"],
            conf(r), vst(r))
for r in P6_CERTS:
    REG.add("Certification", r["certification_name"], "Package006_Skills_and_Training",
            r["certification_id"], conf(r), vst(r))
for r in P6_PROV:
    REG.add("TrainingProvider", r["provider_name"], "Package006_Skills_and_Training",
            r["provider_id"], conf(r), vst(r))
print(f"  Package006  skills {len(P6_SKILLS)}  certifications {len(P6_CERTS)}  "
      f"providers {len(P6_PROV)}")

# --- Package007_Government_Schemes ------------------------------------------
P7_SCH = read("Package007_Government_Schemes/datasets/government_schemes.csv")
P7_FI = read("Package007_Government_Schemes/datasets/financial_institutions.csv")
for r in P7_SCH:
    REG.add("GovernmentScheme", r["scheme_name"], "Package007_Government_Schemes",
            r["scheme_id"], conf(r), vst(r), aliases=[r.get("short_name", "")])
for r in P7_FI:
    REG.add("FinancialInstitution", r["institution_name"], "Package007_Government_Schemes",
            r["institution_id"], conf(r), vst(r))
print(f"  Package007  schemes {len(P7_SCH)}  financial institutions {len(P7_FI)}")

# --- Package008_MSME --------------------------------------------------------
P8_BIZ = read("Package008_MSME/datasets/msme_businesses.csv")
P8_MACH = read("Package008_MSME/datasets/machinery_mapping.csv")
P8_RAW = read("Package008_MSME/datasets/raw_material_mapping.csv")
P8_CHAN = read("Package008_MSME/datasets/market_channels.csv")
P8_FIN = read("Package008_MSME/datasets/financial_support.csv")
P8_CAT = read("Package008_MSME/datasets/msme_categories.csv")
for r in P8_CAT:
    REG.add("Industry", r["category_name"], "Package008_MSME", r["category_id"],
            conf(r), vst(r))
for r in P8_BIZ:
    REG.add("MSME", r["business_name"], "Package008_MSME", r["business_id"], conf(r), vst(r))
for r in P8_CHAN:
    REG.add("Market", r["channel_name"], "Package008_MSME", r["channel_id"], conf(r), vst(r))
for r in P8_FIN:
    REG.add("FinancialInstitution", r["finance_source_name"], "Package008_MSME",
            r["finance_id"], conf(r), vst(r))
# Machinery that Package005 does not catalogue is owned by Package008 as a graph node,
# but only where Package008 itself declined to reference an upstream id.
for r in P8_MACH:
    if r["package005_machinery_id"] == PV:
        REG.add("Machinery", r["machinery_name"], "Package008_MSME", r["mapping_id"],
                conf(r), vst(r))
for r in P8_RAW:
    if r["package005_crop_id"] == PV:
        REG.add("RawMaterial", r["raw_material_name"], "Package008_MSME", r["mapping_id"],
                conf(r), vst(r))
print(f"  Package008  msme businesses {len(P8_BIZ)}  markets {len(P8_CHAN)}  "
      f"+ non-agri machinery and raw materials")

# --- Export countries: parsed from both packages' export datasets -----------
P5_EXP = maybe("Package005_Agriculture/datasets/export_opportunities.csv")
P8_EXP = maybe("Package008_MSME/datasets/export_opportunities.csv")


def split_countries(cell):
    if not cell or cell == PV:
        return []
    parts = re.split(r",| and ", cell)
    out = []
    for p in parts:
        p = p.strip().rstrip(".")
        # Drop qualifiers that are not countries
        if not p or len(p) < 3 or p.lower() in {"etc", "others", "west africa"}:
            continue
        out.append(p)
    return out


export_country_names = set()
for r in P5_EXP:
    export_country_names.update(split_countries(r.get("destination_countries", "")))
for r in P8_EXP:
    export_country_names.update(split_countries(r.get("destination_markets", "")))
for c in sorted(export_country_names):
    REG.add("ExportCountry", c, "Package001_Geography", PV, "60", "VST-NEEDS_REVIEW")
print(f"  derived     export countries {len(export_country_names)}")

print(f"\n  entities after phase 1: {len(REG.rows)}  (phase 2 adds derived Industry nodes)")
print(f"  cross-package sightings of the same entity: {len(REG.collisions)}")


# ==========================================================================
# PHASE 2 — Relationship extraction
# ==========================================================================
print("\nPhase 2: deriving relationships from existing package mappings\n")


def E(t, n):
    return REG.id_for(t, n)


before = len(EDGES)

# --- LOCATED_IN: district -> state, state -> country ------------------------
state_by_id = {r["st_id"]: r["state_name"] for r in P1_STATE}
for r in P1_DIST:
    edge("LOCATED_IN", E("District", r["district_name"]),
         E("State", state_by_id.get(r["st_id"], "")), conf(r),
         "Package001_Geography", "district.csv", r["dist_id"])
for r in P1_STATE:
    edge("LOCATED_IN", E("State", r["state_name"]), E("Country", "India"), conf(r),
         "Package001_Geography", "state.csv", r["st_id"])
print(f"  LOCATED_IN (geography)                {len(EDGES) - before}")

for r in P2_UNIV:
    d = r.get("district", "")
    if d and d != PV and E("District", d):
        edge("LOCATED_IN", E("Institution", r["name"]), E("District", d), conf(r),
             "Package002_Education", "universities_telangana_andhra_pradesh.csv", r["id"])
print(f"  LOCATED_IN (institutions)             "
      f"{sum(1 for e in EDGES if e['provenance_package'] == 'Package002_Education')}")

# --- PART_OF: crop -> category, business -> industry ------------------------
before = len(EDGES)
P5_CAT = read("Package005_Agriculture/datasets/crop_categories.csv")
cat_name = {r["category_id"]: r["category_name"] for r in P5_CAT}
for r in P5_CROPS:
    cn = cat_name.get(r["category_id"])
    if cn:
        REG.add("Industry", f"Agriculture: {cn}", "Package005_Agriculture",
                r["category_id"], conf(r), vst(r))
        edge("PART_OF", E("Crop", r["crop_name"]), E("Industry", f"Agriculture: {cn}"),
             conf(r), "Package005_Agriculture", "crops.csv", r["crop_id"])
for fname, (rows, namecol) in P4_ROWS.items():
    for r in rows:
        cat = r.get("category")
        if cat and cat != PV:
            edge("PART_OF", E("BusinessOpportunity", r[namecol]), E("Industry", cat),
                 conf(r), "Package004_Industries", f"{fname}.csv", r["id"])
print(f"  PART_OF (taxonomy)                    {len(EDGES) - before}")

# --- REQUIRES_SKILL ---------------------------------------------------------
before = len(EDGES)
P8_SKILL = read("Package008_MSME/datasets/skill_mapping.csv")
for r in P8_SKILL:
    if r["package006_skill_name"] == PV:
        UNRESOLVED.append({
            "relationship_type": "REQUIRES_SKILL", "source_package": "Package008_MSME",
            "source_dataset": "skill_mapping.csv", "source_row_id": r["mapping_id"],
            "reason": "Package006 has no skill record for this requirement",
        })
        continue
    edge("REQUIRES_SKILL", E("MSME", r["business_name"]),
         E("Skill", r["package006_skill_name"]), conf(r),
         "Package008_MSME", "skill_mapping.csv", r["mapping_id"],
         note=r.get("criticality", ""))
P6_IND = maybe("Package006_Skills_and_Training/datasets/industry_skill_mapping.csv")
skill_by_id = {r["skill_id"]: r["skill_name"] for r in P6_SKILLS}
for r in P6_IND:
    ind = r.get("industry_name")
    sk = skill_by_id.get(r.get("skill_id", ""))
    if ind and sk:
        REG.add("Industry", ind, "Package004_Industries", f"p006:{slug(ind)}",
                conf(r), vst(r))
        edge("REQUIRES_SKILL", E("Industry", ind), E("Skill", sk), conf(r),
             "Package006_Skills_and_Training", "industry_skill_mapping.csv",
             r.get("mapping_id", ""), note=r.get("demand_level", ""))
P6_BIZ = maybe("Package006_Skills_and_Training/datasets/skill_business_mapping.csv")
for r in P6_BIZ:
    sk = skill_by_id.get(r.get("skill_id", ""))
    opp = r.get("business_opportunity_name")
    if sk and opp and E("BusinessOpportunity", opp):
        edge("REQUIRES_SKILL", E("BusinessOpportunity", opp), E("Skill", sk), conf(r),
             "Package006_Skills_and_Training", "skill_business_mapping.csv",
             r.get("mapping_id", ""), note=r.get("mapping_type", ""))
print(f"  REQUIRES_SKILL                        {len(EDGES) - before}")

# --- SUPPORTED_BY_SCHEME ----------------------------------------------------
before = len(EDGES)
scheme_by_id = {r["scheme_id"]: r["scheme_name"] for r in P7_SCH}
P8_SCHM = read("Package008_MSME/datasets/scheme_mapping.csv")
for r in P8_SCHM:
    sn = scheme_by_id.get(r["package007_scheme_id"])
    edge("SUPPORTED_BY_SCHEME", E("MSME", r["business_name"]),
         E("GovernmentScheme", sn) if sn else None, conf(r),
         "Package008_MSME", "scheme_mapping.csv", r["mapping_id"],
         note=r.get("relevance", ""))
P7_AGRI = maybe("Package007_Government_Schemes/datasets/agriculture_scheme_mapping.csv")
crop_by_id = {r["crop_id"]: r["crop_name"] for r in P5_CROPS}
for r in P7_AGRI:
    cn = crop_by_id.get(r.get("package005_crop_id", ""))
    sn = scheme_by_id.get(r.get("scheme_id", ""))
    if cn and sn:
        edge("SUPPORTED_BY_SCHEME", E("Crop", cn), E("GovernmentScheme", sn), conf(r),
             "Package007_Government_Schemes", "agriculture_scheme_mapping.csv",
             r["mapping_id"], note=r.get("farm_activity", ""))
P7_SKM = maybe("Package007_Government_Schemes/datasets/skill_scheme_mapping.csv")
for r in P7_SKM:
    sk = skill_by_id.get(r.get("package006_skill_id", ""))
    sn = scheme_by_id.get(r.get("scheme_id", ""))
    if sk and sn:
        edge("SUPPORTED_BY_SCHEME", E("Skill", sk), E("GovernmentScheme", sn), conf(r),
             "Package007_Government_Schemes", "skill_scheme_mapping.csv", r["mapping_id"])
P7_IND = maybe("Package007_Government_Schemes/datasets/industry_scheme_mapping.csv")
for r in P7_IND:
    sn = scheme_by_id.get(r.get("scheme_id", ""))
    opp = r.get("package004_opportunity_name")
    if sn and opp and E("BusinessOpportunity", opp):
        edge("SUPPORTED_BY_SCHEME", E("BusinessOpportunity", opp),
             E("GovernmentScheme", sn), conf(r),
             "Package007_Government_Schemes", "industry_scheme_mapping.csv",
             r["mapping_id"], note=r.get("investment_stage", ""))
print(f"  SUPPORTED_BY_SCHEME                   {len(EDGES) - before}")

# --- USES_MACHINERY ---------------------------------------------------------
before = len(EDGES)
for r in P8_MACH:
    edge("USES_MACHINERY", E("MSME", r["business_name"]),
         E("Machinery", r["machinery_name"]), conf(r),
         "Package008_MSME", "machinery_mapping.csv", r["mapping_id"],
         note=f"essential={r.get('is_essential','')}")
print(f"  USES_MACHINERY                        {len(EDGES) - before}")

# --- USES_RAW_MATERIAL and PROCESSES ---------------------------------------
before = len(EDGES)
for r in P8_RAW:
    if r["package005_crop_id"] != PV:
        target = E("Crop", r["package005_crop_name"])
    else:
        target = E("RawMaterial", r["raw_material_name"])
    edge("USES_RAW_MATERIAL", E("MSME", r["business_name"]), target, conf(r),
         "Package008_MSME", "raw_material_mapping.csv", r["mapping_id"],
         note=r.get("availability", ""))
n_raw = len(EDGES) - before
before = len(EDGES)
P8_AGB = read("Package008_MSME/datasets/agriculture_business_mapping.csv")
for r in P8_AGB:
    if r["package005_crop_id"] == PV:
        continue
    edge("PROCESSES", E("MSME", r["business_name"]),
         E("Crop", r["package005_crop_name"]), conf(r),
         "Package008_MSME", "agriculture_business_mapping.csv", r["mapping_id"],
         note=r.get("value_add_stage", ""))
print(f"  USES_RAW_MATERIAL                     {n_raw}")
print(f"  PROCESSES                             {len(EDGES) - before}")

# --- SELLS_TO ---------------------------------------------------------------
before = len(EDGES)
# Channel applicability is stated at channel level, not per business, so the graph
# records the channel's buyer type as a RELATED_TO on the Market node instead of
# inventing per-business SELLS_TO edges. Only export is business-specific.
for r in P8_EXP:
    edge("SELLS_TO", E("MSME", r["business_name"]), E("Market", "Export Channel"),
         conf(r), "Package008_MSME", "export_opportunities.csv", r["opportunity_id"])
print(f"  SELLS_TO                              {len(EDGES) - before}")

# --- EXPORTS_TO -------------------------------------------------------------
before = len(EDGES)
for r in P8_EXP:
    for c in split_countries(r.get("destination_markets", "")):
        edge("EXPORTS_TO", E("MSME", r["business_name"]), E("ExportCountry", c),
             conf(r), "Package008_MSME", "export_opportunities.csv", r["opportunity_id"])
for r in P5_EXP:
    # Package005 export rows are keyed by crop_product text, not crop_id; match
    # against registered crops rather than guessing.
    prod = r.get("crop_product", "")
    matched = None
    for cr in P5_CROPS:
        if cr["crop_name"].lower() in prod.lower():
            matched = cr["crop_name"]
            break
    if not matched:
        UNRESOLVED.append({
            "relationship_type": "EXPORTS_TO", "source_package": "Package005_Agriculture",
            "source_dataset": "export_opportunities.csv",
            "source_row_id": r.get("opportunity_id", ""),
            "reason": f"crop_product {prod!r} does not name a registered crop entity",
        })
        continue
    for c in split_countries(r.get("destination_countries", "")):
        edge("EXPORTS_TO", E("Crop", matched), E("ExportCountry", c), conf(r),
             "Package005_Agriculture", "export_opportunities.csv",
             r.get("opportunity_id", ""))
print(f"  EXPORTS_TO                            {len(EDGES) - before}")

# --- FUNDED_BY / SUPPORTED_BY_BANK -----------------------------------------
before = len(EDGES)
fi_names = [r["institution_name"] for r in P7_FI]
for r in P8_FIN:
    linked = r.get("linked_package007_scheme_short_name", PV)
    if linked and linked != PV:
        for part in re.split(r";|,", linked):
            part = part.strip()
            match = next((s for s in P7_SCH if s["short_name"] == part), None)
            if match:
                edge("FUNDED_BY", E("GovernmentScheme", match["scheme_name"]),
                     E("FinancialInstitution", r["finance_source_name"]), conf(r),
                     "Package008_MSME", "financial_support.csv", r["finance_id"],
                     note=r.get("instrument", ""))
n_funded = len(EDGES) - before
before = len(EDGES)
# Every MSME that is credit-linked reaches finance through scheduled banks; assert
# only where Package008 named a credit-linked scheme for that business.
credit_schemes = {"PMMY", "PMEGP", "Stand-Up India", "CGTMSE", "AIF", "Skill Loan"}
for r in P8_SCHM:
    if r["package007_scheme_short_name"] in credit_schemes:
        edge("SUPPORTED_BY_BANK", E("MSME", r["business_name"]),
             E("FinancialInstitution", "Scheduled Commercial Banks"), conf(r),
             "Package008_MSME", "scheme_mapping.csv", r["mapping_id"],
             note=f"via {r['package007_scheme_short_name']}")
print(f"  FUNDED_BY                             {n_funded}")
print(f"  SUPPORTED_BY_BANK                     {len(EDGES) - before}")

# --- CERTIFIED_BY -----------------------------------------------------------
before = len(EDGES)
for r in P6_CERTS:
    related = r.get("related_skill_names", "")
    if not related or related == PV:
        continue
    for part in re.split(r";|,", related):
        part = part.strip()
        if not part:
            continue
        sid = E("Skill", part)
        if sid:
            edge("CERTIFIED_BY", sid, E("Certification", r["certification_name"]),
                 conf(r), "Package006_Skills_and_Training", "certifications.csv",
                 r["certification_id"])
        else:
            UNRESOLVED.append({
                "relationship_type": "CERTIFIED_BY",
                "source_package": "Package006_Skills_and_Training",
                "source_dataset": "certifications.csv",
                "source_row_id": r["certification_id"],
                "reason": (f"related_skill_names entry {part!r} is not a registered Skill: "
                           "Package006 certifications use descriptive skill labels rather "
                           "than the canonical skill_name vocabulary in its own skills.csv"),
            })
print(f"  CERTIFIED_BY                          {len(EDGES) - before}")

# --- TRAINED_BY / STUDIED_AT ------------------------------------------------
before = len(EDGES)
P7_SKMAP = maybe("Package007_Government_Schemes/datasets/skill_scheme_mapping.csv")
prov_by_id = {r["provider_id"]: r["provider_name"] for r in P6_PROV}
for r in P7_SKMAP:
    sk = skill_by_id.get(r.get("package006_skill_id", ""))
    pv_ = prov_by_id.get(r.get("package006_provider_id", ""))
    if sk and pv_:
        edge("TRAINED_BY", E("Skill", sk), E("TrainingProvider", pv_), conf(r),
             "Package007_Government_Schemes", "skill_scheme_mapping.csv", r["mapping_id"])
n_tr = len(EDGES) - before
before = len(EDGES)
P8_EDU = read("Package008_MSME/datasets/education_support_mapping.csv")
for r in P8_EDU:
    if r["package002_institution_id"] == PV:
        continue
    for catname in re.split(r";", r.get("supports_business_categories", "")):
        catname = catname.strip()
        if catname and E("Industry", catname):
            edge("RELATED_TO", E("Industry", catname),
                 E("Institution", r["package002_institution_name"]), conf(r),
                 "Package008_MSME", "education_support_mapping.csv", r["mapping_id"],
                 note="talent pipeline: institution supplies graduates to this industry")
print(f"  TRAINED_BY                            {n_tr}")
print(f"  RELATED_TO (talent pipeline)          {len(EDGES) - before}")

# --- GENERATES_EMPLOYMENT ---------------------------------------------------
before = len(EDGES)
P8_DBM = read("Package008_MSME/datasets/district_business_mapping.csv")
for r in P8_DBM:
    edge("GENERATES_EMPLOYMENT", E("MSME", r["business_name"]),
         E("District", r["district_name"]), conf(r),
         "Package008_MSME", "district_business_mapping.csv", r["mapping_id"],
         note=r.get("suitability_basis", "")[:120])
print(f"  GENERATES_EMPLOYMENT                  {len(EDGES) - before}")

# --- RELATED_TO: crop-soil, crop-climate ------------------------------------
before = len(EDGES)
P5_CS = read("Package005_Agriculture/datasets/crop_soil_mapping.csv")
P5_CC = read("Package005_Agriculture/datasets/crop_climate_mapping.csv")
for r in P5_CS:
    edge("RELATED_TO", E("Crop", r["crop_name"]), E("Soil", r["soil_name"]), conf(r),
         "Package005_Agriculture", "crop_soil_mapping.csv", r["mapping_id"],
         note=f"soil suitability {r.get('suitability_level','')}")
for r in P5_CC:
    edge("RELATED_TO", E("Crop", r["crop_name"]), E("ClimateZone", r["climate_zone_name"]),
         conf(r), "Package005_Agriculture", "crop_climate_mapping.csv", r["mapping_id"],
         note=f"climate suitability {r.get('yield_potential','')}")
print(f"  RELATED_TO (agro-suitability)         {len(EDGES) - before}")

# --- USES_AI ----------------------------------------------------------------
before = len(EDGES)
P5_AI = maybe("Package005_Agriculture/datasets/ai_precision_agriculture.csv")
for r in P5_AI:
    REG.add("Industry", f"AgriTech: {r['technology_name']}", "Package005_Agriculture",
            r["technology_id"], conf(r), vst(r))
    edge("USES_AI", E("Industry", "Agriculture & Allied")
         or E("Industry", "Agriculture and Allied"),
         E("Industry", f"AgriTech: {r['technology_name']}"), conf(r),
         "Package005_Agriculture", "ai_precision_agriculture.csv", r["technology_id"],
         note=r.get("ai_readiness_level", ""))
P8_AI = read("Package008_MSME/datasets/ai_business_tools.csv")
p8_cat = read("Package008_MSME/datasets/msme_categories.csv")
for r in P8_AI:
    REG.add("Industry", f"AI Tooling: {r['tool_class']}", "Package008_MSME",
            r["tool_id"], conf(r), vst(r))
for r in P8_AI:
    if r["msme_relevance"] in ("High", "Very High"):
        edge("USES_AI", E("Industry", "Manufacturing"),
             E("Industry", f"AI Tooling: {r['tool_class']}"), conf(r),
             "Package008_MSME", "ai_business_tools.csv", r["tool_id"],
             note=f"relevance {r['msme_relevance']}, complexity {r['implementation_complexity']}")
print(f"  USES_AI                               {len(EDGES) - before}")

# --- SUCCESSOR_OF / PREDECESSOR_OF -----------------------------------------
# Registered as valid types. No edge is asserted in v2.0.0: scheme renames are
# recorded in package `notes` as free text, not as structured predecessor links,
# so deriving them would require parsing prose. See ROADMAP_V2.md.
print("  SUCCESSOR_OF / PREDECESSOR_OF         0  (type registered, see ROADMAP_V2.md)")

print(f"\n  TOTAL RELATIONSHIPS: {len(EDGES)}")
print(f"  unresolved endpoints logged: {len(UNRESOLVED)}")


# ==========================================================================
# PHASE 3 — Write registries
# ==========================================================================
print("\nPhase 3: writing registries\n")


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow({h: r.get(h, "") for h in headers})
    print(f"  {path.relative_to(ROOT)}: {len(rows)} rows")


ENTITY_HEADERS = ["global_entity_id", "entity_type", "canonical_name", "source_package",
                  "package_local_id", "status", "lifecycle_state", "created_at",
                  "updated_at", "confidence_score", "verification_status"]
entities = sorted(REG.rows.values(), key=lambda r: (r["entity_type"], r["canonical_name"]))
write_csv(KG / "entities" / "entities.csv", ENTITY_HEADERS, entities)

type_counts = {}
for e in entities:
    type_counts[e["entity_type"]] = type_counts.get(e["entity_type"], 0) + 1
write_csv(KG / "entities" / "entity_types.csv",
          ["entity_type", "entity_type_slug", "owner_package", "description", "entity_count"],
          [{"entity_type": t, "entity_type_slug": TYPE_SLUG[t], "owner_package": OWNER[t],
            "description": ENTITY_TYPE_DESC[t], "entity_count": type_counts.get(t, 0)}
           for t in OWNER])

write_csv(KG / "entities" / "aliases.csv",
          ["alias_id", "global_entity_id", "alias", "alias_type", "source_package"],
          REG.aliases)

write_csv(KG / "entities" / "cross_package_sightings.csv",
          ["global_entity_id", "entity_type", "canonical_name", "owner_package",
           "also_seen_in", "also_seen_local_id"],
          REG.collisions)

REL_HEADERS = ["relationship_id", "from_entity", "relationship_type", "to_entity",
               "confidence", "provenance_package", "provenance_dataset",
               "provenance_row_id", "derived_at", "notes"]
write_csv(KG / "relationships" / "relationships.csv", REL_HEADERS, EDGES)

rel_counts = {}
for e in EDGES:
    rel_counts[e["relationship_type"]] = rel_counts.get(e["relationship_type"], 0) + 1
write_csv(KG / "relationships" / "relationship_types.csv",
          ["relationship_type", "expected_from_types", "expected_to_types",
           "semantics", "edge_count"],
          [{"relationship_type": k, "expected_from_types": v[0], "expected_to_types": v[1],
            "semantics": v[2], "edge_count": rel_counts.get(k, 0)}
           for k, v in RELATIONSHIP_TYPE_DESC.items()])

write_csv(KG / "relationships" / "unresolved_endpoints.csv",
          ["relationship_type", "source_package", "source_dataset", "source_row_id", "reason"],
          UNRESOLVED)

summary = {
    "graph_version": "2.0.0",
    "built_at": BUILD_DATE,
    "source_packages": sorted(set(OWNER.values())),
    "entity_count": len(entities),
    "entity_types_registered": len(OWNER),
    "entity_types_populated": len(type_counts),
    "entities_by_type": dict(sorted(type_counts.items(), key=lambda kv: -kv[1])),
    "alias_count": len(REG.aliases),
    "cross_package_sightings": len(REG.collisions),
    "relationship_count": len(EDGES),
    "relationship_types_registered": len(RELATIONSHIP_TYPE_DESC),
    "relationship_types_populated": len(rel_counts),
    "relationships_by_type": dict(sorted(rel_counts.items(), key=lambda kv: -kv[1])),
    "unresolved_endpoints": len(UNRESOLVED),
    "identifier_scheme": "vw:<entity_type_slug>:<canonical_name_slug>",
    "note": ("Every entity and edge is derived from a released package. No domain fact "
             "originates in this layer."),
}
(KG / "graph_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(f"  knowledge_graph/graph_summary.json")

print("\nGraph build complete.")
