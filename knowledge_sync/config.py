#!/usr/bin/env python3
"""
Table specifications — what syncs, from where, into what.

THE TARGET SCHEMA IS `knowledge`, NOT `public`
----------------------------------------------
Three of the eight table names the brief asks for — `kg_skills`, `kg_schemes`
and `kg_relationships` — already exist in `public` as admin-authored CMS tables
with different columns, different RLS and a different purpose. The brief also
says, in the same document, not to touch existing application tables.

Both instructions are satisfiable at once by putting the projection in its own
Postgres schema. The tables get exactly the names the brief specifies,
`public.kg_skills` and its siblings are never opened, and `drop schema knowledge
cascade` becomes a complete, safe rollback that cannot reach application data.

See docs/SYNC_ARCHITECTURE.md §2 for the full argument.

WHAT A TableSpec DECLARES
-------------------------
Everything the pipeline needs, in one place, so that adding a ninth table is a
data change rather than a code change. The modules read this; none of them
hard-codes a table name.
"""

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
KG = ROOT / "knowledge_graph"

#: Dedicated Postgres schema. Nothing in `public` is read or written.
TARGET_SCHEMA = "knowledge"

#: The six provenance columns every package row carries.
PROVENANCE = ("data_source", "source_url", "collection_date",
              "confidence_score", "verification_status", "notes")

#: Every bare sentinel used across the eight packages. An explicit set, not a
#: `PENDING_*` pattern: a pattern would also swallow legitimate uppercase values
#: such as PMEGP, NABARD, CGTMSE and DEPRECATED_REFERENCE.
SENTINELS = frozenset({
    "PENDING_VERIFICATION",      # 2,456 cells — a fact could not be sourced
    "PENDING_GEOCODING",         #   272 cells — Package001 coordinates not yet resolved
})

PENDING_VERIFICATION = "PENDING_VERIFICATION"


@dataclass(frozen=True)
class Source:
    """One CSV that feeds a target table."""

    path: Path
    #: Column holding the row's natural key within its dataset.
    key_column: str
    #: Recorded on every row so a synced row can name the file it came from.
    package: str
    dataset: str
    #: Optional constant columns merged into every row from this source. Used
    #: where one target table unions several differently-shaped datasets.
    constants: dict = field(default_factory=dict)


@dataclass(frozen=True)
class TableSpec:
    name: str
    description: str
    sources: tuple
    #: Columns copied through as-is when present. Anything else is dropped, so a
    #: new column upstream cannot silently widen the projection.
    columns: tuple
    #: Must be present and non-empty on every row, or validation fails.
    required: tuple = ()
    #: (column, target_table, target_column) — checked after all tables extract.
    foreign_keys: tuple = ()
    #: Package that owns this entity type, per the ownership registry.
    owner_package: str = ""
    #: Columns carrying provenance in THIS source's vocabulary. The graph
    #: artifacts name them differently from the packages, so this is per-table
    #: rather than a global constant.
    provenance_columns: tuple = PROVENANCE
    #: Confidence column name, or "" when the source carries none.
    confidence_column: str = "confidence_score"
    verification_column: str = "verification_status"


def pkg(package, dataset, key_column, **constants):
    return Source(path=PACKAGES / package / "datasets" / dataset,
                  key_column=key_column, package=package, dataset=dataset,
                  constants=constants)


def graph(rel_path, key_column, dataset):
    return Source(path=KG / rel_path, key_column=key_column,
                  package="knowledge_graph", dataset=dataset)


# ---------------------------------------------------------------------------
# The eight tables. Order matters: kg_entities must extract before
# kg_relationships, because the relationship foreign keys resolve against it.
# ---------------------------------------------------------------------------
TABLE_SPECS = (
    TableSpec(
        name="kg_entities",
        description="Global entity registry — every node in the knowledge graph.",
        sources=(graph("entities/entities.csv", "global_entity_id", "entities.csv"),),
        columns=("global_entity_id", "entity_type", "canonical_name", "source_package",
                 "package_local_id", "status", "lifecycle_state", "created_at",
                 "updated_at", "confidence_score", "verification_status"),
        required=("global_entity_id", "entity_type", "canonical_name", "source_package"),
        owner_package="knowledge_graph",
        # The graph registry carries confidence and verification but not the
        # collection-time columns; those live on the package rows it derives from.
        provenance_columns=("confidence_score", "verification_status"),
    ),
    TableSpec(
        name="kg_relationships",
        description="Typed, provenance-carrying edges between entities.",
        sources=(graph("relationships/relationships.csv", "relationship_id",
                       "relationships.csv"),),
        columns=("relationship_id", "from_entity", "relationship_type", "to_entity",
                 "confidence", "provenance_package", "provenance_dataset",
                 "provenance_row_id", "derived_at", "notes"),
        required=("relationship_id", "from_entity", "relationship_type", "to_entity",
                  "provenance_package", "provenance_dataset", "provenance_row_id"),
        foreign_keys=(("from_entity", "kg_entities", "global_entity_id"),
                      ("to_entity", "kg_entities", "global_entity_id")),
        owner_package="knowledge_graph",
        provenance_columns=("provenance_package", "provenance_dataset",
                            "provenance_row_id"),
        confidence_column="confidence",
        verification_column="",
    ),
    TableSpec(
        name="kg_districts",
        description="Districts of Telangana and Andhra Pradesh.",
        sources=(pkg("Package001_Geography", "district.csv", "dist_id"),),
        columns=("dist_id", "district_name", "st_id", "district_headquarters",
                 "area_sq_km", "population", "mandal_count", "density_per_sq_km",
                 "urban_pct", "literacy_rate_pct", "sex_ratio", "latitude", "longitude",
                 "govt_district_code", "lgd_district_code") + PROVENANCE,
        required=("dist_id", "district_name", "st_id"),
        owner_package="Package001_Geography",
    ),
    TableSpec(
        name="kg_skills",
        description="Skills with NSQF level, demand and automation risk.",
        sources=(pkg("Package006_Skills_and_Training", "skills.csv", "skill_id"),),
        columns=("skill_id", "skill_name", "category_id", "category_name", "description",
                 "difficulty_level", "nsqf_level", "learning_duration", "demand_level",
                 "automation_risk", "ai_augmentation_level", "future_demand",
                 "self_employment_score", "startup_opportunity") + PROVENANCE,
        required=("skill_id", "skill_name"),
        owner_package="Package006_Skills_and_Training",
    ),
    TableSpec(
        name="kg_schemes",
        description="Government schemes — Package007 is the authoritative owner (ADR-003).",
        sources=(pkg("Package007_Government_Schemes", "government_schemes.csv",
                     "scheme_id"),),
        columns=("scheme_id", "scheme_name", "short_name", "category_id", "category_name",
                 "ministry", "department", "government_level", "launch_year", "objective",
                 "benefit_summary", "financial_assistance", "subsidy_component",
                 "loan_support", "coverage", "application_mode", "official_portal",
                 "status", "also_in_package") + PROVENANCE,
        required=("scheme_id", "scheme_name"),
        owner_package="Package007_Government_Schemes",
    ),
    TableSpec(
        name="kg_businesses",
        description=("MSME businesses and business opportunities. Unions Package008's "
                     "researched MSMEs with Package004's four opportunity datasets."),
        sources=(
            pkg("Package008_MSME", "msme_businesses.csv", "business_id",
                business_kind="MSME"),
            pkg("Package004_Industries", "food_agro_processing_micro_enterprises.csv",
                "id", business_kind="BusinessOpportunity"),
            pkg("Package004_Industries", "construction_skilled_trade_services.csv", "id",
                business_kind="BusinessOpportunity"),
            pkg("Package004_Industries", "digital_technology_livelihoods.csv", "id",
                business_kind="BusinessOpportunity"),
            pkg("Package004_Industries", "china_inspired_adapted_opportunities.csv", "id",
                business_kind="BusinessOpportunity"),
        ),
        columns=("business_id", "id", "business_kind", "business_name", "name",
                 "category_id", "category_name", "description", "udyam_classification",
                 "investment_range", "minimum_investment", "working_capital_need",
                 "employment_generation", "difficulty", "risk_level", "technology_level",
                 "automation_level", "ai_readiness", "profitability_outlook",
                 "ideal_target_audience") + PROVENANCE,
        required=("business_kind",),
        owner_package="Package008_MSME",
    ),
    TableSpec(
        name="kg_industries",
        description=("MSME sector taxonomy. Package004 has no standalone industry "
                     "dataset — its industries are embedded in opportunity rows — so "
                     "the graph's 78 Industry nodes stay in kg_entities and this table "
                     "is the browsable sector list."),
        sources=(pkg("Package008_MSME", "msme_categories.csv", "category_id"),),
        columns=("category_id", "category_name", "category_group", "description",
                 "nic_section_hint", "capital_intensity", "skill_intensity",
                 "typical_udyam_class") + PROVENANCE,
        required=("category_id", "category_name"),
        owner_package="Package008_MSME",
    ),
    TableSpec(
        name="kg_agriculture",
        description="Crops with agronomic attributes (Package005).",
        sources=(pkg("Package005_Agriculture", "crops.csv", "crop_id"),),
        columns=("crop_id", "crop_name", "scientific_name", "category_id",
                 "category_name", "season", "duration_days", "water_requirement_mm",
                 "soil_type_preferred", "rainfall_mm", "temperature_min_c",
                 "temperature_max_c", "avg_yield_tons_per_ha", "major_states",
                 "major_districts") + PROVENANCE,
        required=("crop_id", "crop_name"),
        owner_package="Package005_Agriculture",
    ),
)

BY_NAME = {s.name: s for s in TABLE_SPECS}

#: Columns the framework adds to every projected row. Named with a leading
#: underscore-free `sync_` prefix so they cannot collide with a package column.
SYNC_COLUMNS = ("sync_row_key", "sync_source_package", "sync_source_dataset",
                "sync_source_row_id", "sync_content_hash", "sync_deleted_at",
                "sync_synced_at", "sync_version")


def spec(name):
    if name not in BY_NAME:
        raise KeyError(f"unknown table {name!r}; known: {sorted(BY_NAME)}")
    return BY_NAME[name]
