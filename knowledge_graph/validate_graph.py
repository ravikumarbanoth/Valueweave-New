#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Knowledge Graph Validator

Checks enforced before the graph is considered releasable:

  G1  Entity identity     global_entity_id unique, well-formed, matches type+name slug
  G2  Entity completeness all 11 registry fields present and non-empty on every entity
  G3  Type registration   every entity_type is one of the 18 registered types
  G4  Provenance          every entity names a real source package, and a local id
                          that resolves in that package where one is claimed
  G5  Edge integrity      both endpoints of every edge exist in the entity registry
  G6  Edge typing         every relationship_type is registered, and endpoints match
                          the declared expected types
  G7  OWNERSHIP           no package publishes a column owning an attribute that the
                          ownership registry assigns to a different package. This
                          generalises Package008's V13 to all eight packages.
  G8  Lifecycle           lifecycle_state is a registered state
  G9  Confidence          integer 0-100 on every entity and edge
  G10 Orphans             report entities with no edges (a warning, not a failure)
  G11 Scheme ownership    ADR-003: one owner per type; every domain scheme row
                          declares its relationship to the Package007 canonical row

Exit code 0 = clean, 1 = violations found.

Run from the repository root:
  python3 knowledge_graph/validate_graph.py
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "knowledge_graph"
PACKAGES = ROOT / "packages"

LIFECYCLE_STATES = ["DRAFT", "COLLECTED", "VALIDATED", "REVIEWED",
                    "APPROVED", "PUBLISHED", "ARCHIVED"]

PV = "PENDING_VERIFICATION"

violations = []
warnings_ = []


def vio(check, detail):
    violations.append({"check": check, "detail": detail})


def warn(check, detail):
    warnings_.append({"check": check, "detail": detail})


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


entities = read(KG / "entities" / "entities.csv")
edges = read(KG / "relationships" / "relationships.csv")
etypes = read(KG / "entities" / "entity_types.csv")
rtypes = read(KG / "relationships" / "relationship_types.csv")
ownership = read(KG / "ownership" / "ownership_registry.csv")
attr_own = read(KG / "ownership" / "attribute_ownership.csv")
overlaps = read(KG / "ownership" / "known_overlaps.csv")

# (owner_package, other_package) pairs whose duplication is DECLARED and governed.
DECLARED_OVERLAP = set()
for o in overlaps:
    for other in o["also_held_by"].split(";"):
        DECLARED_OVERLAP.add((o["canonical_owner"], other.strip(), o["adr"]))
DECLARED_PAIRS = {(a, b): adr for a, b, adr in DECLARED_OVERLAP}

REGISTERED_TYPES = {r["entity_type"] for r in etypes}
TYPE_SLUG = {r["entity_type"]: r["entity_type_slug"] for r in etypes}
REGISTERED_RELS = {r["relationship_type"]: r for r in rtypes}
by_gid = {e["global_entity_id"]: e for e in entities}

ENTITY_FIELDS = ["global_entity_id", "entity_type", "canonical_name", "source_package",
                 "package_local_id", "status", "lifecycle_state", "created_at",
                 "updated_at", "confidence_score", "verification_status"]

print("ValueWeave Knowledge Graph validation\n")

# ------------------------------------------------------------------ G1, G2, G3
seen = set()
for e in entities:
    gid = e["global_entity_id"]
    if gid in seen:
        vio("G1-IDENTITY", f"duplicate global_entity_id {gid}")
    seen.add(gid)

    if not re.fullmatch(r"vw:[a-z0-9-]+:[a-z0-9-]+", gid):
        vio("G1-IDENTITY", f"malformed global_entity_id {gid!r}")

    et = e["entity_type"]
    if et not in REGISTERED_TYPES:
        vio("G3-TYPE", f"{gid}: unregistered entity_type {et!r}")
    elif not gid.startswith(f"vw:{TYPE_SLUG[et]}:"):
        vio("G1-IDENTITY", f"{gid}: id prefix does not match entity_type {et!r}")

    for field in ENTITY_FIELDS:
        if not e.get(field, "").strip():
            vio("G2-COMPLETENESS", f"{gid}: empty required field {field!r}")

# ------------------------------------------------------------------------- G4
package_dirs = {p.name for p in PACKAGES.iterdir() if p.is_dir()}
local_id_cache = {}


def package_has_local_id(pkg, local_id):
    """Confirm a claimed package_local_id actually appears in that package."""
    if pkg not in local_id_cache:
        ids = set()
        d = PACKAGES / pkg / "datasets"
        if d.exists():
            for f in d.glob("*.csv"):
                try:
                    with open(f, newline="", encoding="utf-8") as fh:
                        rdr = csv.reader(fh)
                        next(rdr)
                        for row in rdr:
                            if row:
                                ids.add(row[0].strip())
                except Exception:
                    pass
        local_id_cache[pkg] = ids
    return local_id in local_id_cache[pkg]


for e in entities:
    pkg = e["source_package"]
    if pkg not in package_dirs:
        vio("G4-PROVENANCE", f"{e['global_entity_id']}: source_package {pkg!r} does not exist")
        continue
    lid = e["package_local_id"]
    # Derived and composite ids are legitimately not package row keys.
    if lid in ("PENDING_VERIFICATION", "n/a") or ":" in lid:
        continue
    if not package_has_local_id(pkg, lid):
        vio("G4-PROVENANCE",
            f"{e['global_entity_id']}: package_local_id {lid!r} not found in {pkg}")

# --------------------------------------------------------------------- G5, G6
for r in edges:
    rid = r["relationship_id"]
    rt = r["relationship_type"]

    if rt not in REGISTERED_RELS:
        vio("G6-EDGE_TYPE", f"{rid}: unregistered relationship_type {rt!r}")
        continue

    fe, te = by_gid.get(r["from_entity"]), by_gid.get(r["to_entity"])
    if fe is None:
        vio("G5-EDGE_INTEGRITY", f"{rid}: from_entity {r['from_entity']} not in registry")
    if te is None:
        vio("G5-EDGE_INTEGRITY", f"{rid}: to_entity {r['to_entity']} not in registry")
    if fe is None or te is None:
        continue

    spec = REGISTERED_RELS[rt]
    exp_from = spec["expected_from_types"]
    exp_to = spec["expected_to_types"]
    if exp_from != "*" and fe["entity_type"] not in exp_from.split("|"):
        vio("G6-EDGE_TYPE",
            f"{rid}: {rt} from {fe['entity_type']}, expected one of {exp_from}")
    if exp_to != "*" and te["entity_type"] not in exp_to.split("|"):
        vio("G6-EDGE_TYPE",
            f"{rid}: {rt} to {te['entity_type']}, expected one of {exp_to}")

    if r["from_entity"] == r["to_entity"]:
        vio("G5-EDGE_INTEGRITY", f"{rid}: self-loop on {r['from_entity']}")

# ------------------------------------------------------------------------- G7
# The ownership check. A package may hold a foreign key to another package's
# entity; it may not publish a column that IS that entity's owned attribute.
OWNED = {}
for a in attr_own:
    OWNED.setdefault(a["owned_attribute"], set()).add(a["owner_package"])

# Columns that are legitimately denormalised alongside a foreign key for
# readability, and relationship qualifiers that share a name with an attribute.
DENORM_ALLOWED = {
    "district_name", "state_name", "crop_name", "skill_name", "scheme_name",
    "machinery_name", "channel_name", "business_name", "provider_name",
    "certification_name", "institution_name", "soil_name", "zone_name",
    "category_name", "raw_material_name", "country_name", "name",
}

g7_checked = 0
for pkg in sorted(package_dirs):
    d = PACKAGES / pkg / "datasets"
    if not d.exists():
        continue
    for f in sorted(d.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            header = next(csv.reader(fh))
        g7_checked += 1
        for col in header:
            owners = OWNED.get(col)
            if not owners:
                continue
            if pkg in owners:
                continue                      # the owner may hold its own attribute
            if col in DENORM_ALLOWED:
                continue                      # denormalised for readability
            # A prefixed reference column (package005_crop_name) is a reference.
            if col.startswith("package00"):
                continue
            declared = next((DECLARED_PAIRS[(o, pkg)] for o in owners
                             if (o, pkg) in DECLARED_PAIRS), None)
            if declared:
                # Governed duplication: declared in known_overlaps.csv with an ADR.
                warn("G7-OWNERSHIP-DECLARED",
                     f"{pkg}/{f.name}: column {col!r} duplicates {sorted(owners)} - "
                     f"declared overlap, tracked under {declared}")
            else:
                vio("G7-OWNERSHIP",
                    f"{pkg}/{f.name}: column {col!r} is owned by {sorted(owners)} and the "
                    f"overlap is NOT declared in known_overlaps.csv; either reference the "
                    f"owner's id or declare the overlap with an ADR")

# ------------------------------------------------------------------- G8, G9
for e in entities:
    if e["lifecycle_state"] not in LIFECYCLE_STATES:
        vio("G8-LIFECYCLE",
            f"{e['global_entity_id']}: lifecycle_state {e['lifecycle_state']!r} not registered")
    c = e["confidence_score"]
    if not re.fullmatch(r"\d{1,3}", c) or not 0 <= int(c) <= 100:
        vio("G9-CONFIDENCE", f"{e['global_entity_id']}: confidence_score {c!r} invalid")

for r in edges:
    c = r["confidence"]
    if not re.fullmatch(r"\d{1,3}", c) or not 0 <= int(c) <= 100:
        vio("G9-CONFIDENCE", f"{r['relationship_id']}: confidence {c!r} invalid")

# ------------------------------------------------------------------------ G10
degree = defaultdict(int)
for r in edges:
    degree[r["from_entity"]] += 1
    degree[r["to_entity"]] += 1
orphans = [e for e in entities if degree[e["global_entity_id"]] == 0]
orphans_by_type = defaultdict(int)
for e in orphans:
    orphans_by_type[e["entity_type"]] += 1
if orphans:
    warn("G10-ORPHANS",
         f"{len(orphans)} entities have no relationships: "
         + ", ".join(f"{k} {v}" for k, v in sorted(orphans_by_type.items(),
                                                   key=lambda kv: -kv[1])))

# ------------------------------------------------------------------------ G11
# ADR-003 is decided: Package007 is the authoritative owner of GovernmentScheme.
# A decision written only in a document decays. This check makes it mechanical.
#
# Three things must hold, and each fails the build:
#   a) every entity type has exactly one owner in the registry
#   b) every domain scheme row carries both governance columns
#   c) every non-sentinel package007_scheme_id resolves to a real Package007 scheme
SCHEME_OWNER = "Package007_Government_Schemes"
SCHEME_GOVERNANCE_COLUMNS = ("package007_scheme_id", "scheme_ownership")
SCHEME_OWNERSHIP_VALUES = {"DEPRECATED_REFERENCE", "DOMAIN_CANONICAL"}
DOMAIN_SCHEME_DATASETS = {
    "Package002_Education": "scholarships.csv",
    "Package003_Healthcare": "government_health_insurance_schemes.csv",
    "Package004_Industries": "msme_entrepreneurship_support_schemes.csv",
    "Package005_Agriculture": "agriculture_schemes.csv",
    "Package006_Skills_and_Training": "government_skill_schemes.csv",
}

owners_per_type = defaultdict(set)
for row in read(KG / "ownership" / "ownership_registry.csv"):
    owners_per_type[row["entity_type"]].add(row["owner_package"])
for etype, owners in sorted(owners_per_type.items()):
    if len(owners) > 1:
        vio("G11-SCHEME_OWNERSHIP",
            f"{etype} has {len(owners)} owners in the registry: {', '.join(sorted(owners))}")

canonical_scheme_ids = {r["scheme_id"] for r in
                        read(PACKAGES / SCHEME_OWNER / "datasets" / "government_schemes.csv")}
g11_rows = g11_deprecated = 0
for pkg, dataset in sorted(DOMAIN_SCHEME_DATASETS.items()):
    path = PACKAGES / pkg / "datasets" / dataset
    if not path.exists():
        vio("G11-SCHEME_OWNERSHIP", f"{pkg}/{dataset} is missing")
        continue
    rows = read(path)
    missing = [c for c in SCHEME_GOVERNANCE_COLUMNS if rows and c not in rows[0]]
    if missing:
        vio("G11-SCHEME_OWNERSHIP",
            f"{pkg}/{dataset} lacks ADR-003 governance column(s): {', '.join(missing)}")
        continue
    for i, r in enumerate(rows, start=2):
        g11_rows += 1
        own, ref = r["scheme_ownership"], r["package007_scheme_id"]
        if own not in SCHEME_OWNERSHIP_VALUES:
            vio("G11-SCHEME_OWNERSHIP",
                f"{pkg}/{dataset}:{i} scheme_ownership {own!r} is not one of "
                f"{sorted(SCHEME_OWNERSHIP_VALUES)}")
        elif own == "DEPRECATED_REFERENCE":
            g11_deprecated += 1
            if ref not in canonical_scheme_ids:
                vio("G11-SCHEME_OWNERSHIP",
                    f"{pkg}/{dataset}:{i} is DEPRECATED_REFERENCE but package007_scheme_id "
                    f"{ref!r} is not a Package007 scheme")
        elif ref != PV:
            vio("G11-SCHEME_OWNERSHIP",
                f"{pkg}/{dataset}:{i} is DOMAIN_CANONICAL but carries "
                f"package007_scheme_id {ref!r}; expected the bare sentinel")

# ------------------------------------------------------------------ reporting
by_type = defaultdict(int)
for e in entities:
    by_type[e["entity_type"]] += 1
by_rel = defaultdict(int)
for r in edges:
    by_rel[r["relationship_type"]] += 1

connected = len(entities) - len(orphans)
summary = {
    "graph_version": "2.0.0",
    "entities": len(entities),
    "relationships": len(edges),
    "entity_types_registered": len(REGISTERED_TYPES),
    "entity_types_populated": len(by_type),
    "relationship_types_registered": len(REGISTERED_RELS),
    "relationship_types_populated": len(by_rel),
    "connected_entities": connected,
    "orphan_entities": len(orphans),
    "connectivity_pct": round(100 * connected / len(entities), 2) if entities else 0.0,
    "package_csvs_checked_for_ownership": g7_checked,
    "enforceable_owned_attributes": len(OWNED),
    "domain_scheme_rows_governed": g11_rows,
    "domain_scheme_rows_deprecated_reference": g11_deprecated,
    "checks_run": ["G1-IDENTITY", "G2-COMPLETENESS", "G3-TYPE", "G4-PROVENANCE",
                   "G5-EDGE_INTEGRITY", "G6-EDGE_TYPE", "G7-OWNERSHIP",
                   "G8-LIFECYCLE", "G9-CONFIDENCE", "G10-ORPHANS",
                   "G11-SCHEME_OWNERSHIP"],
    "violations": len(violations),
    "warnings": len(warnings_),
    "result": "PASS" if not violations else "FAIL",
}
(KG / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

print(f"  entities ................. {len(entities)}")
print(f"  relationships ............ {len(edges)}")
print(f"  entity types ............. {len(by_type)} populated / {len(REGISTERED_TYPES)} registered")
print(f"  relationship types ....... {len(by_rel)} populated / {len(REGISTERED_RELS)} registered")
print(f"  connectivity ............. {connected}/{len(entities)} ({summary['connectivity_pct']}%)")
print(f"  package CSVs ownership-checked  {g7_checked}")
print(f"  domain scheme rows governed  {g11_rows} ({g11_deprecated} DEPRECATED_REFERENCE, {g11_rows - g11_deprecated} DOMAIN_CANONICAL)")
print()

if warnings_:
    print(f"WARNINGS ({len(warnings_)}):")
    for w in warnings_:
        print(f"  [{w['check']}] {w['detail']}")
    print()

if violations:
    grouped = defaultdict(list)
    for v in violations:
        grouped[v["check"]].append(v["detail"])
    print(f"FAIL — {len(violations)} violation(s):\n")
    for check in sorted(grouped):
        print(f"  {check}  ({len(grouped[check])})")
        for d in grouped[check][:12]:
            print(f"    {d}")
        if len(grouped[check]) > 12:
            print(f"    ... and {len(grouped[check]) - 12} more")
    sys.exit(1)

print("PASS — graph is structurally sound, provenance-complete and ownership-clean.")
