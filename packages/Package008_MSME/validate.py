#!/usr/bin/env python3
"""
Package008_MSME v1.0.0 — Validation Engine

Checks enforced before release:
  V1  Structural       every row has exactly the header's column count
  V2  Primary key      first column unique and non-empty in every dataset
  V3  Provenance       the 6 mandatory provenance columns present on every dataset
  V4  Confidence       integer, 0-100, and <= the 85 policy ceiling
  V5  Sentinel         PENDING_VERIFICATION appears only as a bare exact string
  V6  Verification     verification_status drawn from the allowed enum
  V7  Collection date  uniform ISO date across the package
  V8  Internal FK      business/category/model references resolve in-package
  V9  Cross-package FK Package001/002/004/005/006/007 references resolve upstream
  V10 Empty cells      no silently blank cells (a gap must be the sentinel)
  V11 Coverage         every business has >=1 scheme, skill and machinery mapping,
                       and exactly one investment_intelligence row
  V12 Enum integrity   closed domains on the classification columns
  V13 NORMALIZATION    Package008 must not restate upstream attributes. Any column
                       whose name collides with an upstream entity's own attribute
                       (scheme benefit, skill NSQF level, crop agronomy, district
                       demographics) is a violation. This check exists because the
                       package brief makes non-duplication a hard requirement, and a
                       rule that is only written down is a rule that erodes.

Exit code 0 = release-clean, 1 = violations found.
"""

import csv
import json
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
DATASETS = PKG / "datasets"
PACKAGES = PKG.parent

PV = "PENDING_VERIFICATION"
CEILING = 85
EXPECTED_DATE = "2026-07-25"
ALLOWED_VST = {"VST-NEEDS_REVIEW", "VST-VERIFIED"}
PROVENANCE = ["data_source", "source_url", "collection_date",
              "confidence_score", "verification_status", "notes"]

violations = []
stats = {}


def vio(check, dataset, detail):
    violations.append({"check": check, "dataset": dataset, "detail": detail})


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        return next(r), list(r)


def dicts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def upstream(rel):
    p = PACKAGES / rel
    return dicts(p) if p.exists() else None


# ---------------------------------------------------------------- per-dataset
files = sorted(DATASETS.glob("*.csv"))
if len(files) != 18:
    vio("MANIFEST", "package", f"expected 18 datasets, found {len(files)}")

for path in files:
    name = path.name
    header, rows = load(path)
    ncols, pk_col = len(header), header[0]
    seen, conf_values, pv_cells = set(), [], 0

    missing = [c for c in PROVENANCE if c not in header]
    if missing:
        vio("V3-PROVENANCE", name, f"missing provenance columns: {missing}")

    idx = {c: i for i, c in enumerate(header)}

    for rn, row in enumerate(rows, start=2):
        if len(row) != ncols:
            vio("V1-STRUCTURAL", name, f"line {rn}: {len(row)} cells, expected {ncols}")
            continue

        pk = row[0].strip()
        if not pk:
            vio("V2-PRIMARY_KEY", name, f"line {rn}: empty {pk_col}")
        elif pk in seen:
            vio("V2-PRIMARY_KEY", name, f"line {rn}: duplicate {pk_col}={pk}")
        else:
            seen.add(pk)

        for col, i in idx.items():
            cell = row[i]
            if cell.strip() == "":
                vio("V10-EMPTY_CELL", name, f"line {rn}: column '{col}' is blank")
            if PV in cell:
                if cell != PV:
                    vio("V5-SENTINEL", name,
                        f"line {rn}: column '{col}' contains but does not equal the sentinel: {cell!r}")
                else:
                    pv_cells += 1

        if "confidence_score" in idx:
            raw = row[idx["confidence_score"]]
            if raw == PV:
                vio("V4-CONFIDENCE", name, f"line {rn}: confidence_score must be numeric")
            elif not re.fullmatch(r"\d{1,3}", raw):
                vio("V4-CONFIDENCE", name, f"line {rn}: confidence_score not an integer: {raw!r}")
            else:
                c = int(raw)
                conf_values.append(c)
                if not 0 <= c <= 100:
                    vio("V4-CONFIDENCE", name, f"line {rn}: {c} outside 0-100")
                if c > CEILING:
                    vio("V4-CONFIDENCE", name, f"line {rn}: {c} exceeds the {CEILING} ceiling")

        if "verification_status" in idx and row[idx["verification_status"]] not in ALLOWED_VST:
            vio("V6-VERIFICATION", name,
                f"line {rn}: verification_status {row[idx['verification_status']]!r} not allowed")

        if "collection_date" in idx and row[idx["collection_date"]] != EXPECTED_DATE:
            vio("V7-COLLECTION_DATE", name,
                f"line {rn}: collection_date {row[idx['collection_date']]!r} != {EXPECTED_DATE}")

    total = len(rows) * ncols
    stats[name] = {
        "records": len(rows), "columns": ncols, "primary_key": pk_col,
        "pending_verification_cells": pv_cells, "total_cells": total,
        "pending_verification_rate_pct": round(100 * pv_cells / total, 2) if total else 0.0,
        "confidence_min": min(conf_values) if conf_values else None,
        "confidence_max": max(conf_values) if conf_values else None,
        "confidence_avg": round(sum(conf_values) / len(conf_values), 1) if conf_values else None,
    }

# ------------------------------------------------------------ V8 internal FKs
biz = dicts(DATASETS / "msme_businesses.csv")
cats = dicts(DATASETS / "msme_categories.csv")
models = dicts(DATASETS / "business_models.csv")

biz_ids = {r["business_id"] for r in biz}
biz_names = {r["business_id"]: r["business_name"] for r in biz}
cat_ids = {r["category_id"] for r in cats}
cat_names = {r["category_id"]: r["category_name"] for r in cats}
model_ids = {r["business_model_id"] for r in models}
model_names = {r["business_model_id"]: r["business_model_name"] for r in models}

for r in biz:
    if r["category_id"] not in cat_ids:
        vio("V8-FK", "msme_businesses.csv", f"{r['business_id']}: category_id {r['category_id']} unknown")
    elif cat_names[r["category_id"]] != r["category_name"]:
        vio("V8-FK-DENORM", "msme_businesses.csv",
            f"{r['business_id']}: category_name {r['category_name']!r} != {cat_names[r['category_id']]!r}")
    if r["business_model_id"] not in model_ids:
        vio("V8-FK", "msme_businesses.csv",
            f"{r['business_id']}: business_model_id {r['business_model_id']} unknown")
    elif model_names[r["business_model_id"]] != r["business_model_name"]:
        vio("V8-FK-DENORM", "msme_businesses.csv",
            f"{r['business_id']}: business_model_name mismatch")

BIZ_CHILDREN = [
    ("machinery_mapping.csv", "mapping_id"),
    ("raw_material_mapping.csv", "mapping_id"),
    ("scheme_mapping.csv", "mapping_id"),
    ("skill_mapping.csv", "mapping_id"),
    ("industry_mapping.csv", "mapping_id"),
    ("agriculture_business_mapping.csv", "mapping_id"),
    ("district_business_mapping.csv", "mapping_id"),
    ("export_opportunities.csv", "opportunity_id"),
    ("investment_intelligence.csv", "intelligence_id"),
]
for fname, pk in BIZ_CHILDREN:
    for r in dicts(DATASETS / fname):
        b = r["business_id"]
        if b not in biz_ids:
            vio("V8-FK", fname, f"{r[pk]}: business_id {b} not in msme_businesses.csv")
        elif biz_names[b] != r["business_name"]:
            vio("V8-FK-DENORM", fname,
                f"{r[pk]}: business_name {r['business_name']!r} != {biz_names[b]!r}")

# -------------------------------------------------------- V9 cross-package FKs
cross = {}


def check_x(label, fname, col, rel, upcol, name_col=None, upname=None):
    up = upstream(rel)
    if up is None:
        vio("V9-XPKG-FK", fname, f"upstream missing: {rel}")
        return
    lookup = {r[upcol]: (r[upname] if upname else None) for r in up}
    res = sen = 0
    for r in dicts(DATASETS / fname):
        v = r[col]
        if v == PV:
            sen += 1
            continue
        if v not in lookup:
            vio("V9-XPKG-FK", fname, f"{col}={v} not found in {rel}")
            continue
        res += 1
        if name_col and upname and r[name_col] != PV and lookup[v] != r[name_col]:
            vio("V9-XPKG-DENORM", fname,
                f"{col}={v}: {name_col} {r[name_col]!r} != upstream {lookup[v]!r}")
    cross[label] = {"resolved": res, "sentinel": sen}


check_x("Package001 district", "district_business_mapping.csv", "package001_dist_id",
        "Package001_Geography/datasets/district.csv", "dist_id", "district_name", "district_name")
check_x("Package002 institution", "education_support_mapping.csv", "package002_institution_id",
        "Package002_Education/datasets/universities_telangana_andhra_pradesh.csv", "id",
        "package002_institution_name", "name")
check_x("Package005 crop (raw material)", "raw_material_mapping.csv", "package005_crop_id",
        "Package005_Agriculture/datasets/crops.csv", "crop_id", "package005_crop_name", "crop_name")
check_x("Package005 crop (agri business)", "agriculture_business_mapping.csv", "package005_crop_id",
        "Package005_Agriculture/datasets/crops.csv", "crop_id", "package005_crop_name", "crop_name")
check_x("Package005 machinery", "machinery_mapping.csv", "package005_machinery_id",
        "Package005_Agriculture/datasets/farm_machinery.csv", "machinery_id",
        "package005_machinery_name", "machinery_name")
check_x("Package005 processing", "agriculture_business_mapping.csv",
        "package005_processing_opportunity_id",
        "Package005_Agriculture/datasets/agri_processing_opportunities.csv", "opportunity_id",
        "package005_processing_opportunity_name", "opportunity_name")
check_x("Package006 skill", "skill_mapping.csv", "package006_skill_id",
        "Package006_Skills_and_Training/datasets/skills.csv", "skill_id",
        "package006_skill_name", "skill_name")
check_x("Package006 provider", "education_support_mapping.csv", "package006_provider_id",
        "Package006_Skills_and_Training/datasets/training_providers.csv", "provider_id",
        "package006_provider_name", "provider_name")
check_x("Package007 scheme", "scheme_mapping.csv", "package007_scheme_id",
        "Package007_Government_Schemes/datasets/government_schemes.csv", "scheme_id",
        "package007_scheme_short_name", "short_name")

# Package004: opportunity id lives across four datasets, all keyed 'id'
p4_dir = PACKAGES / "Package004_Industries" / "datasets"
if p4_dir.exists():
    p4 = {}
    for f in p4_dir.glob("*.csv"):
        for r in dicts(f):
            key = r.get("id")
            if key:
                p4[key] = r.get("name") or r.get("adapted_indian_concept") or r.get("scheme_name")
    res = sen = 0
    for r in dicts(DATASETS / "industry_mapping.csv"):
        v = r["package004_opportunity_id"]
        if v == PV:
            sen += 1
        elif v not in p4:
            vio("V9-XPKG-FK", "industry_mapping.csv", f"package004_opportunity_id {v} not found")
        else:
            res += 1
            if p4[v] != r["package004_opportunity_name"]:
                vio("V9-XPKG-DENORM", "industry_mapping.csv",
                    f"{v}: name {r['package004_opportunity_name']!r} != upstream {p4[v]!r}")
    cross["Package004 opportunity"] = {"resolved": res, "sentinel": sen}
else:
    vio("V9-XPKG-FK", "industry_mapping.csv", "Package004 datasets not found")

# --------------------------------------------------------------- V11 coverage
def by_business(fname):
    out = {}
    for r in dicts(DATASETS / fname):
        out.setdefault(r["business_id"], 0)
        out[r["business_id"]] += 1
    return out


sch_cov = by_business("scheme_mapping.csv")
skl_cov = by_business("skill_mapping.csv")
mch_cov = by_business("machinery_mapping.csv")
inv_cov = by_business("investment_intelligence.csv")

for bid in sorted(biz_ids):
    if bid not in sch_cov:
        vio("V11-COVERAGE", "scheme_mapping.csv", f"{bid} ({biz_names[bid]}) has no scheme mapping")
    if bid not in skl_cov:
        vio("V11-COVERAGE", "skill_mapping.csv", f"{bid} ({biz_names[bid]}) has no skill mapping")
    if bid not in mch_cov:
        vio("V11-COVERAGE", "machinery_mapping.csv",
            f"{bid} ({biz_names[bid]}) has no machinery mapping")
    if inv_cov.get(bid, 0) != 1:
        vio("V11-COVERAGE", "investment_intelligence.csv",
            f"{bid} ({biz_names[bid]}) has {inv_cov.get(bid, 0)} investment rows, expected exactly 1")

# ----------------------------------------------------------- V12 enum domains
LEVELS = {"Very Low", "Low", "Medium", "High", "Very High"}
ENUMS = {
    ("msme_businesses.csv", "udyam_classification"): {"Micro", "Small", "Medium"},
    ("msme_businesses.csv", "difficulty"): {"Easy", "Moderate", "Hard", "Very Hard"},
    ("msme_businesses.csv", "risk_level"): LEVELS,
    ("msme_businesses.csv", "market_demand"): LEVELS,
    ("msme_businesses.csv", "export_potential"): LEVELS,
    ("msme_businesses.csv", "district_suitability"): {"Rural", "Urban", "Both", "Variable"},
    ("machinery_mapping.csv", "is_essential"): {"Yes", "No"},
    ("investment_intelligence.csv", "investment_band"): {"Micro", "Small", "Medium"},
    ("license_compliance.csv", "is_mandatory_when_applicable"): {"Yes", "No"},
    ("skill_mapping.csv", "criticality"): {"Essential", "Useful", "Optional"},
    ("scheme_mapping.csv", "relevance"): {"Primary", "Secondary"},
}
for (fname, col), allowed in ENUMS.items():
    for r in dicts(DATASETS / fname):
        if r[col] not in allowed and r[col] != PV:
            vio("V12-ENUM", fname, f"{col}={r[col]!r} not in {sorted(allowed)}")

# ------------------------------------------------------- V13 NORMALIZATION RULE
# The brief forbids Package008 from duplicating upstream domain content. These
# column-name fragments are attributes owned by an upstream package. If any appear
# in a Package008 dataset, the data has been restated instead of referenced.
FORBIDDEN = {
    "scheme (Package007)": ["scheme_benefit", "benefit_amount", "eligibility_criteri",
                            "application_mode", "ministry", "scheme_objective",
                            "subsidy_component"],
    "skill (Package006)": ["nsqf", "skill_duration", "learning_duration",
                           "training_duration", "skill_description"],
    "crop (Package005)": ["crop_season", "crop_yield", "water_requirement",
                          "soil_type", "rainfall", "scientific_name"],
    "district (Package001)": ["population", "area_sq_km", "literacy", "sex_ratio",
                              "latitude", "longitude", "mandal_count"],
    "institution (Package002)": ["established_year", "affiliation", "university_type"],
}
ALLOWED_EXCEPTIONS = {
    # financial_support legitimately names which Package007 scheme a source is linked
    # to, by short_name, as a navigational pointer -- it states no scheme attribute.
    ("financial_support.csv", "linked_package007_scheme_short_name"),
}
# official_portal is Package008-owned on licences and sales channels, but WOULD be
# duplication on any dataset that references a Package007 scheme. Scope it that way
# rather than banning or allowing the column name globally.
for path in files:
    header, _ = load(path)
    references_p007 = any(c.startswith("package007_") for c in header)
    for col in header:
        if (path.name, col) in ALLOWED_EXCEPTIONS:
            continue
        low = col.lower()
        if low == "official_portal" and references_p007:
            vio("V13-NORMALIZATION", path.name,
                "column 'official_portal' restates the scheme portal owned by Package007 "
                "on a dataset that already references package007_scheme_id")
            continue
        for owner, frags in FORBIDDEN.items():
            for frag in frags:
                if frag in low:
                    vio("V13-NORMALIZATION", path.name,
                        f"column '{col}' restates an attribute owned by {owner}; "
                        f"reference the upstream id instead")

# ------------------------------------------------------------------ reporting
total_records = sum(s["records"] for s in stats.values())
total_cells = sum(s["total_cells"] for s in stats.values())
total_pv = sum(s["pending_verification_cells"] for s in stats.values())
confs = [s for s in stats.values() if s["confidence_min"] is not None]

summary = {
    "package": "Package008_MSME",
    "version": "1.0.0",
    "collection_date": EXPECTED_DATE,
    "datasets": len(stats),
    "total_records": total_records,
    "total_cells": total_cells,
    "businesses_catalogued": len(biz_ids),
    "pending_verification_cells": total_pv,
    "pending_verification_rate_pct": round(100 * total_pv / total_cells, 2) if total_cells else 0.0,
    "confidence_min": min(s["confidence_min"] for s in confs) if confs else None,
    "confidence_max": max(s["confidence_max"] for s in confs) if confs else None,
    "confidence_ceiling_policy": CEILING,
    "cross_package_fk": cross,
    "normalization_check": "V13 PASS" if not [v for v in violations if v["check"] == "V13-NORMALIZATION"] else "V13 FAIL",
    "violations": len(violations),
    "result": "PASS" if not violations else "FAIL",
    "per_dataset": stats,
}
(PKG / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

print("Package008_MSME v1.0.0 validation")
print(f"  datasets ............. {len(stats)}")
print(f"  total records ........ {total_records}")
print(f"  total cells .......... {total_cells}")
print(f"  businesses ........... {len(biz_ids)}")
print(f"  PENDING_VERIFICATION . {total_pv} ({summary['pending_verification_rate_pct']}%)")
print(f"  confidence range ..... {summary['confidence_min']}-{summary['confidence_max']} (ceiling {CEILING})")
print(f"  normalization (V13) .. {summary['normalization_check']}")
print("  cross-package FKs:")
for k, v in cross.items():
    print(f"    {k:34s} {v['resolved']:4d} resolved, {v['sentinel']:3d} sentinel")
print()

if violations:
    print(f"FAIL — {len(violations)} violation(s):\n")
    for v in violations[:60]:
        print(f"  [{v['check']}] {v['dataset']}: {v['detail']}")
    if len(violations) > 60:
        print(f"  ... and {len(violations) - 60} more")
    sys.exit(1)

print("PASS — all checks clean. Release-ready.")
