#!/usr/bin/env python3
"""
Package007_Government_Schemes v1.0.0 — Validation Engine

Checks enforced before release:
  V1  Structural       every row has exactly the header's column count
  V2  Primary key      first column unique and non-empty in every dataset
  V3  Provenance       the 6 mandatory provenance columns present on every dataset
  V4  Confidence       integer, 0-100, and <= the 85 policy ceiling
  V5  Sentinel         PENDING_VERIFICATION appears only as a bare exact string
  V6  Verification     verification_status drawn from the allowed enum
  V7  Collection date  uniform ISO date across the package
  V8  Internal FK      scheme/category/agency references resolve in-package
  V9  Cross-package FK Package001/002/004/005/006 references resolve upstream
  V10 Empty cells      no silently blank cells (a gap must be the sentinel)
  V11 Coverage         every scheme has >=1 eligibility criterion and >=1 benefit
  V12 Enum integrity   government_level, status, is_mandatory use closed domains

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
if len(files) != 15:
    vio("MANIFEST", "package", f"expected 15 datasets, found {len(files)}")

for path in files:
    name = path.name
    header, rows = load(path)
    ncols = len(header)
    pk_col = header[0]
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
                vio("V4-CONFIDENCE", name, f"line {rn}: confidence_score must be numeric, not a sentinel")
            elif not re.fullmatch(r"\d{1,3}", raw):
                vio("V4-CONFIDENCE", name, f"line {rn}: confidence_score not an integer: {raw!r}")
            else:
                c = int(raw)
                conf_values.append(c)
                if not 0 <= c <= 100:
                    vio("V4-CONFIDENCE", name, f"line {rn}: {c} outside 0-100")
                if c > CEILING:
                    vio("V4-CONFIDENCE", name, f"line {rn}: {c} exceeds the {CEILING} policy ceiling")

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
schemes = dicts(DATASETS / "government_schemes.csv")
cats = dicts(DATASETS / "scheme_categories.csv")
docs = dicts(DATASETS / "required_documents.csv")

scheme_ids = {r["scheme_id"] for r in schemes}
scheme_short = {r["scheme_id"]: r["short_name"] for r in schemes}
cat_ids = {r["category_id"] for r in cats}
cat_names = {r["category_id"]: r["category_name"] for r in cats}
doc_names = {r["document_name"] for r in docs}

for r in schemes:
    if r["category_id"] not in cat_ids:
        vio("V8-FK", "government_schemes.csv",
            f"{r['scheme_id']}: category_id {r['category_id']} not in scheme_categories.csv")
    elif cat_names[r["category_id"]] != r["category_name"]:
        vio("V8-FK-DENORM", "government_schemes.csv",
            f"{r['scheme_id']}: category_name {r['category_name']!r} != {cat_names[r['category_id']]!r}")

SCHEME_CHILDREN = [
    ("eligibility_criteria.csv", "criterion_id"),
    ("scheme_benefits.csv", "benefit_id"),
    ("application_process.csv", "step_id"),
    ("education_scheme_mapping.csv", "mapping_id"),
    ("agriculture_scheme_mapping.csv", "mapping_id"),
    ("skill_scheme_mapping.csv", "mapping_id"),
    ("industry_scheme_mapping.csv", "mapping_id"),
    ("district_scheme_mapping.csv", "mapping_id"),
    ("scheme_ai_recommendations.csv", "recommendation_id"),
]
for fname, pk in SCHEME_CHILDREN:
    for r in dicts(DATASETS / fname):
        sid = r["scheme_id"]
        if sid not in scheme_ids:
            vio("V8-FK", fname, f"{r[pk]}: scheme_id {sid} not in government_schemes.csv")
        elif scheme_short[sid] != r["scheme_short_name"]:
            vio("V8-FK-DENORM", fname,
                f"{r[pk]}: scheme_short_name {r['scheme_short_name']!r} != {scheme_short[sid]!r}")

# eligibility document hints must name a real document (or be sentinel)
for r in dicts(DATASETS / "eligibility_criteria.csv"):
    hint = r["verification_document_hint"]
    if hint != PV and not any(hint.lower() in d.lower() for d in doc_names):
        vio("V8-FK", "eligibility_criteria.csv",
            f"{r['criterion_id']}: verification_document_hint {hint!r} matches no required_documents.csv row")

# AI recommendation self-references must resolve
for r in dicts(DATASETS / "scheme_ai_recommendations.csv"):
    nxt = r["suggested_next_scheme_id"]
    if nxt != PV and nxt not in scheme_ids:
        vio("V8-FK", "scheme_ai_recommendations.csv",
            f"{r['recommendation_id']}: suggested_next_scheme_id {nxt} not in government_schemes.csv")
    rel = r["related_scheme_ids"]
    if rel != PV:
        for part in rel.split(";"):
            if part.strip() and part.strip() not in scheme_ids:
                vio("V8-FK", "scheme_ai_recommendations.csv",
                    f"{r['recommendation_id']}: related_scheme_ids member {part!r} not in government_schemes.csv")

# ------------------------------------------------------- V9 cross-package FKs
cross = {}


def check_xpkg(label, fname, col, upstream_rel, upstream_col, name_col=None, up_name_col=None):
    up = upstream(upstream_rel)
    if up is None:
        vio("V9-XPKG-FK", fname, f"upstream missing: {upstream_rel}")
        return
    lookup = {r[upstream_col]: (r[up_name_col] if up_name_col else None) for r in up}
    resolved = sentinel = 0
    for r in dicts(DATASETS / fname):
        v = r[col]
        if v == PV:
            sentinel += 1
            continue
        if v not in lookup:
            vio("V9-XPKG-FK", fname, f"{col}={v} not found in {upstream_rel}")
            continue
        resolved += 1
        if name_col and up_name_col and r[name_col] != PV and lookup[v] != r[name_col]:
            vio("V9-XPKG-DENORM", fname,
                f"{col}={v}: {name_col} {r[name_col]!r} != upstream {lookup[v]!r}")
    cross[label] = {"resolved": resolved, "sentinel": sentinel}


check_xpkg("Package001 district", "district_scheme_mapping.csv", "package001_dist_id",
           "Package001_Geography/datasets/district.csv", "dist_id",
           "district_name", "district_name")
check_xpkg("Package002 scholarship", "education_scheme_mapping.csv", "package002_record_id",
           "Package002_Education/datasets/scholarships.csv", "id",
           "package002_record_name", "scheme_name")
check_xpkg("Package005 scheme", "agriculture_scheme_mapping.csv", "package005_scheme_id",
           "Package005_Agriculture/datasets/agriculture_schemes.csv", "scheme_id",
           "package005_scheme_name", "scheme_name")
check_xpkg("Package005 crop", "agriculture_scheme_mapping.csv", "package005_crop_id",
           "Package005_Agriculture/datasets/crops.csv", "crop_id",
           "package005_crop_name", "crop_name")
check_xpkg("Package006 scheme", "skill_scheme_mapping.csv", "package006_scheme_id",
           "Package006_Skills_and_Training/datasets/government_skill_schemes.csv", "scheme_id",
           "package006_scheme_name", "scheme_name")
check_xpkg("Package006 skill", "skill_scheme_mapping.csv", "package006_skill_id",
           "Package006_Skills_and_Training/datasets/skills.csv", "skill_id",
           "package006_skill_name", "skill_name")
check_xpkg("Package006 certification", "skill_scheme_mapping.csv", "package006_certification_id",
           "Package006_Skills_and_Training/datasets/certifications.csv", "certification_id",
           "package006_certification_name", "certification_name")
check_xpkg("Package006 provider", "skill_scheme_mapping.csv", "package006_provider_id",
           "Package006_Skills_and_Training/datasets/training_providers.csv", "provider_id",
           "package006_provider_name", "provider_name")

# Package004 opportunity names (matched by name, not id)
p4_names = set()
p4_dir = PACKAGES / "Package004_Industries" / "datasets"
if p4_dir.exists():
    for f in p4_dir.glob("*.csv"):
        for r in dicts(f):
            for k in ("name", "scheme_name", "adapted_indian_concept"):
                if r.get(k):
                    p4_names.add(r[k].strip())
    res = sen = 0
    for r in dicts(DATASETS / "industry_scheme_mapping.csv"):
        v = r["package004_opportunity_name"]
        if v == PV:
            sen += 1
        elif v not in p4_names:
            vio("V9-XPKG-FK", "industry_scheme_mapping.csv",
                f"package004_opportunity_name {v!r} not found in Package004 datasets")
        else:
            res += 1
    cross["Package004 opportunity"] = {"resolved": res, "sentinel": sen}
else:
    vio("V9-XPKG-FK", "industry_scheme_mapping.csv", "Package004 datasets not found")

# --------------------------------------------------------------- V11 coverage
elig_by_scheme = {}
for r in dicts(DATASETS / "eligibility_criteria.csv"):
    elig_by_scheme.setdefault(r["scheme_id"], 0)
    elig_by_scheme[r["scheme_id"]] += 1
ben_by_scheme = {}
for r in dicts(DATASETS / "scheme_benefits.csv"):
    ben_by_scheme.setdefault(r["scheme_id"], 0)
    ben_by_scheme[r["scheme_id"]] += 1

for sid in sorted(scheme_ids):
    if sid not in elig_by_scheme:
        vio("V11-COVERAGE", "eligibility_criteria.csv",
            f"scheme {sid} ({scheme_short[sid]}) has no eligibility criterion row")
    if sid not in ben_by_scheme:
        vio("V11-COVERAGE", "scheme_benefits.csv",
            f"scheme {sid} ({scheme_short[sid]}) has no benefit row")

# ----------------------------------------------------------- V12 enum domains
ENUMS = {
    ("government_schemes.csv", "government_level"): {"Central", "State", "Central-State", "Local"},
    ("government_schemes.csv", "status"): {"Active", "Closed", "Subsumed", "Revised"},
    ("eligibility_criteria.csv", "is_mandatory"): {"Yes", "No"},
    ("scheme_application_status.csv", "is_terminal"): {"Yes", "No"},
    ("financial_institutions.csv", "priority_sector_lending"): {"Yes", "No", "Not applicable"},
}
for (fname, col), allowed in ENUMS.items():
    for r in dicts(DATASETS / fname):
        if r[col] not in allowed and r[col] != PV:
            vio("V12-ENUM", fname, f"{col}={r[col]!r} not in {sorted(allowed)}")

# ------------------------------------------------------------------ reporting
total_records = sum(s["records"] for s in stats.values())
total_cells = sum(s["total_cells"] for s in stats.values())
total_pv = sum(s["pending_verification_cells"] for s in stats.values())
confs = [s for s in stats.values() if s["confidence_min"] is not None]

summary = {
    "package": "Package007_Government_Schemes",
    "version": "1.0.0",
    "collection_date": EXPECTED_DATE,
    "datasets": len(stats),
    "total_records": total_records,
    "total_cells": total_cells,
    "pending_verification_cells": total_pv,
    "pending_verification_rate_pct": round(100 * total_pv / total_cells, 2) if total_cells else 0.0,
    "confidence_min": min(s["confidence_min"] for s in confs) if confs else None,
    "confidence_max": max(s["confidence_max"] for s in confs) if confs else None,
    "confidence_ceiling_policy": CEILING,
    "schemes_registered": len(scheme_ids),
    "cross_package_fk": cross,
    "violations": len(violations),
    "result": "PASS" if not violations else "FAIL",
    "per_dataset": stats,
}
(PKG / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

print("Package007_Government_Schemes v1.0.0 validation")
print(f"  datasets ............. {len(stats)}")
print(f"  total records ........ {total_records}")
print(f"  total cells .......... {total_cells}")
print(f"  schemes registered ... {len(scheme_ids)}")
print(f"  PENDING_VERIFICATION . {total_pv} ({summary['pending_verification_rate_pct']}%)")
print(f"  confidence range ..... {summary['confidence_min']}-{summary['confidence_max']} (ceiling {CEILING})")
print("  cross-package FKs:")
for k, v in cross.items():
    print(f"    {k:32s} {v['resolved']:4d} resolved, {v['sentinel']:3d} sentinel")
print()

if violations:
    print(f"FAIL — {len(violations)} violation(s):\n")
    for v in violations[:60]:
        print(f"  [{v['check']}] {v['dataset']}: {v['detail']}")
    if len(violations) > 60:
        print(f"  ... and {len(violations) - 60} more")
    sys.exit(1)

print("PASS — all checks clean. Release-ready.")
