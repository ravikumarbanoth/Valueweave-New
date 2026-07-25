#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Ownership Registry Builder (Module 3)

Emits the Single Source of Truth registry: which package owns which entity type and
which attributes, and what every other package may and may not hold about it.

The registry is not decorative. `validate_graph.py` check G7 reads
owned_attributes and fails the build if a non-owner package publishes a column
matching an owned attribute. Package008's V13 already enforces this for one package;
this generalises it to all eight.

Outputs
  knowledge_graph/ownership/ownership_registry.csv    entity type -> owner + rules
  knowledge_graph/ownership/attribute_ownership.csv   owned attribute -> owner
  knowledge_graph/ownership/known_overlaps.csv        declared, accepted duplication
"""

import csv
from pathlib import Path

OWN = Path(__file__).resolve().parent

# (entity_type, owner_package, owned_attributes, others_may_hold, rationale)
OWNERSHIP = [
    ("District", "Package001_Geography",
     "district_name;population;area_sq_km;literacy_rate_pct;sex_ratio;latitude;longitude;mandal_count;district_headquarters",
     "dist_id as a foreign key; district_name denormalised alongside it for readability",
     "Geography is referenced by five other packages and changes only on administrative reorganisation."),
    ("State", "Package001_Geography",
     "state_name;state_code;capital_city;state_gdp_inr_cr;industrial_policy_name",
     "st_id as a foreign key",
     "Same reasoning as District."),
    ("Country", "Package001_Geography",
     "country_name;iso_code",
     "country name as free text in export destination lists",
     "Only India is modelled as a first-class Country in v2.0.0; export destinations are ExportCountry."),
    ("Institution", "Package002_Education",
     "name;university_type;affiliation;established_year;accreditation",
     "institution id as a foreign key",
     "Institutional facts are stable and verifiable; duplicating them invites divergence on accreditation."),
    ("Skill", "Package006_Skills_and_Training",
     "skill_name;nsqf_level;learning_duration;difficulty_level;automation_risk;salary_range",
     "skill_id as a foreign key; relationship attributes such as criticality and role",
     "Package008 V13 already enforces this. The distinction that matters: 'this business needs Welding' is a relationship Package008 owns; 'Welding is NSQF level 4' is an attribute Package006 owns."),
    ("Certification", "Package006_Skills_and_Training",
     "certification_name;issuing_body;nsqf_level;validity_period;recognition_level",
     "certification_id as a foreign key",
     "Certification validity changes with regulator decisions."),
    ("TrainingProvider", "Package006_Skills_and_Training",
     "provider_name;provider_type;jurisdiction",
     "provider_id as a foreign key",
     "Provider networks are restructured periodically."),
    ("Industry", "Package004_Industries",
     "industry classification names and sector descriptions",
     "category name as a label alongside a reference",
     "PARTIALLY CONTESTED: Package005, Package006 and Package008 each maintain their own sector taxonomy. See known_overlaps.csv."),
    ("BusinessOpportunity", "Package004_Industries",
     "name;investment_range_summary;machinery_equipment_summary;raw_materials_summary;licenses_required_summary;training_providers_summary",
     "opportunity id as a foreign key; relationship type qualifiers",
     "Package004 carries sourced investment and machinery detail. Package008 deliberately does not restate it."),
    ("MSME", "Package008_MSME",
     "business_name;udyam_classification;difficulty;risk_level;technology_level;automation_level;ai_readiness;profitability_outlook",
     "business_id as a foreign key",
     "Package008 is the Business Intelligence Layer; no other package models MSME opportunities."),
    ("GovernmentScheme", "Package007_Government_Schemes",
     "scheme_name;ministry;objective;benefit_summary;financial_assistance;eligibility;application_mode;official_portal;launch_year",
     "scheme_id as a foreign key; relationship qualifiers such as relevance and applicable_stage",
     "CONTESTED: five packages carry domain scheme slices predating Package007. See known_overlaps.csv and ADR-003."),
    ("Crop", "Package005_Agriculture",
     "crop_name;scientific_name;season;duration_days;water_requirement_mm;soil_type_preferred;rainfall_mm;avg_yield_tons_per_ha;major_states;major_districts",
     "crop_id as a foreign key",
     "Package008 V13 enforces this already."),
    ("Soil", "Package005_Agriculture",
     "soil_name;pH_range_min;pH_range_max;texture;soil_color;crop_suitability",
     "soil_id as a foreign key", "Single-package domain, uncontested."),
    ("ClimateZone", "Package005_Agriculture",
     "zone_name;rainfall_mm_min;rainfall_mm_max;temperature_min_c;temperature_max_c;humidity_percent;growing_seasons",
     "climate_zone_id as a foreign key", "Single-package domain, uncontested."),
    ("Machinery", "Package005_Agriculture",
     "machinery_name;power_hp;automation_level;ai_readiness;subsidy_scheme;capacity",
     "machinery_id as a foreign key; machinery_name as free text where Package005 has no record",
     "SCOPE-LIMITED: Package005 catalogues agricultural machinery only. 54 of 64 Package008 machinery references correctly have no upstream id. See known_overlaps.csv."),
    ("RawMaterial", "Package008_MSME",
     "raw_material_name;material_class;supplier_type;availability;seasonality;price_volatility",
     "crop_id where the input is a crop, in which case Package005 owns it",
     "Non-crop production inputs have no other home in the knowledge base."),
    ("Market", "Package008_MSME",
     "channel_name;channel_type;buyer_type;entry_barrier;digital_intensity",
     "channel_id as a foreign key", "Single-package domain, uncontested."),
    ("ExportCountry", "Package001_Geography",
     "country_name",
     "country name as free text in destination lists",
     "NOMINAL: Package001 v1.0.0 holds no country dataset. Ownership is assigned for future consolidation; the 29 ExportCountry entities are derived from Package005 and Package008 destination text. See known_overlaps.csv."),
    ("FinancialInstitution", "Package007_Government_Schemes",
     "institution_name;institution_type;ownership;priority_sector_lending;scheme_roles",
     "institution reference by name; instrument and typical_use as relationship attributes",
     "CONTESTED: Package008 financial_support overlaps Package007 financial_institutions. See known_overlaps.csv."),
]

# Declared, accepted duplication. Recording it is what makes it governable.
OVERLAPS = [
    ("GovernmentScheme", "Package007_Government_Schemes",
     "Package002_Education;Package003_Healthcare;Package004_Industries;Package005_Agriculture;Package006_Skills_and_Training",
     "79 scheme rows exist across five domain packages, predating Package007. Package007 "
     "government_schemes.also_in_package declares every overlap.",
     "UNRESOLVED", "ADR-003",
     "Highest-priority governance decision in the platform. Three options are set out in ADR-003."),
    ("Industry", "Package004_Industries",
     "Package005_Agriculture;Package006_Skills_and_Training;Package008_MSME",
     "Four packages maintain independent sector taxonomies with overlapping labels "
     "(Manufacturing, Technology, Healthcare, Textiles appear in more than one).",
     "PARTIALLY_RESOLVED", "ADR-005",
     "The graph normalises these into one Industry type; 4 near-duplicate pairs are "
     "flagged in resolution/merge_proposals.csv for steward decision."),
    ("FinancialInstitution", "Package007_Government_Schemes", "Package008_MSME",
     "Package007 financial_institutions (12 rows) and Package008 financial_support "
     "(12 rows) describe overlapping institutions with different framing.",
     "ACCEPTED", "ADR-005",
     "Accepted: Package007 frames institutions as scheme delivery channels, Package008 "
     "frames them as enterprise finance sources. Different attributes, same real bodies."),
    ("Machinery", "Package005_Agriculture", "Package008_MSME",
     "Package005 catalogues agricultural machinery; Package008 names 54 non-agricultural "
     "machines that have no upstream record.",
     "ACCEPTED", "ADR-005",
     "Not duplication: it is a scope boundary. A general industrial machinery reference "
     "would resolve it and is a v2.1 candidate."),
    ("ExportCountry", "Package001_Geography", "Package005_Agriculture;Package008_MSME",
     "Country names appear only as free text inside export destination lists; no package "
     "holds a country dataset.",
     "UNRESOLVED", "ADR-005",
     "The graph derives 29 ExportCountry entities by parsing that text. A proper country "
     "reference dataset in Package001 would make this a real foreign key."),
]


def write(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows")


if __name__ == "__main__":
    print("Building ownership registry:\n")

    write(OWN / "ownership_registry.csv",
          ["entity_type", "owner_package", "owned_attributes",
           "other_packages_may_hold", "rationale"],
          OWNERSHIP)

    # Generic column names that many entity types legitimately carry. Treating
    # these as domain-owned produced 22 false positives on the first validation
    # run -- a university, a hospital and a bank all have an "ownership" column
    # and none is restating another package's attribute. Only DISTINCTIVE
    # attributes are enforceable. Same lesson as Package008's V13.
    GENERIC = {
        "jurisdiction", "ownership", "established_year", "affiliation", "capacity",
        "season", "name", "description", "status", "category", "type", "level",
        "duration", "location", "address", "contact", "website",
        # Context-dependent: same column name, different meaning per domain.
        "risk_level", "provider_type", "institution_type", "official_portal",
        "objective", "capacity",
    }
    attr_rows = []
    for etype, owner, owned, _, _ in OWNERSHIP:
        for a in owned.split(";"):
            a = a.strip()
            if a and " " not in a and a not in GENERIC:
                attr_rows.append([a, etype, owner])
    write(OWN / "attribute_ownership.csv",
          ["owned_attribute", "entity_type", "owner_package"],
          sorted(set(map(tuple, attr_rows))))

    write(OWN / "known_overlaps.csv",
          ["entity_type", "canonical_owner", "also_held_by", "description",
           "status", "adr", "resolution_note"],
          OVERLAPS)

    print(f"\n  {len(OWNERSHIP)} entity types, "
          f"{len(set(t[0] for t in attr_rows))} enforceable owned attributes, "
          f"{len(OVERLAPS)} declared overlaps")
    print("  Ownership build complete.")
