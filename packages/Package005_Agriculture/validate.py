#!/usr/bin/env python3
"""
Package005_Agriculture v1.0.0 — Validation Engine

Checks enforced before release:
  V1  Structural       every row has exactly the header's column count
  V2  Primary key      first column unique and non-empty in every dataset
  V3  Provenance       the 6 mandatory provenance columns present on every dataset
  V4  Confidence       integer, 0-100, and <= the 85 policy ceiling
  V5  Sentinel         PENDING_VERIFICATION appears only as a bare exact string
  V6  Verification     verification_status drawn from the allowed enum
  V7  Collection date  uniform ISO date across the package
  V8  Internal FK      crop/soil/climate/processing references resolve in-package
  V9  Cross-package FK Package006 skill_id and Package004 opportunity names resolve
  V10 Empty cells      no silently blank cells (a gap must be the sentinel)

Exit code 0 = release-clean, 1 = violations found.
"""

import csv
import json
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
DATASETS = PKG / "datasets"
PKG004 = PKG.parent / "Package004_Industries" / "datasets"
PKG006 = PKG.parent / "Package006_Skills_and_Training" / "datasets"

PV = "PENDING_VERIFICATION"
CONFIDENCE_CEILING = 85
EXPECTED_DATE = "2026-07-24"
ALLOWED_VST = {"VST-NEEDS_REVIEW", "VST-VERIFIED"}
PROVENANCE = ["data_source", "source_url", "collection_date",
              "confidence_score", "verification_status", "notes"]

violations = []
stats = {}


def vio(check, dataset, detail):
    violations.append({"check": check, "dataset": dataset, "detail": detail})


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    return header, rows


def load_dicts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- per-dataset
files = sorted(DATASETS.glob("*.csv"))
if len(files) != 16:
    vio("MANIFEST", "package", f"expected 16 datasets, found {len(files)}")

for path in files:
    name = path.name
    header, rows = load(path)
    ncols = len(header)
    pk_col = header[0]
    seen_pk = set()
    conf_values = []
    pv_cells = 0

    # V3 provenance columns present
    missing_prov = [c for c in PROVENANCE if c not in header]
    if missing_prov:
        vio("V3-PROVENANCE", name, f"missing provenance columns: {missing_prov}")

    idx = {c: i for i, c in enumerate(header)}

    for rn, row in enumerate(rows, start=2):
        # V1 structural
        if len(row) != ncols:
            vio("V1-STRUCTURAL", name, f"line {rn}: {len(row)} cells, expected {ncols}")
            continue

        # V2 primary key
        pk = row[0].strip()
        if not pk:
            vio("V2-PRIMARY_KEY", name, f"line {rn}: empty {pk_col}")
        elif pk in seen_pk:
            vio("V2-PRIMARY_KEY", name, f"line {rn}: duplicate {pk_col}={pk}")
        else:
            seen_pk.add(pk)

        for col, i in idx.items():
            cell = row[i]

            # V10 no blank cells
            if cell.strip() == "":
                vio("V10-EMPTY_CELL", name, f"line {rn}: column '{col}' is blank")

            # V5 sentinel must be bare
            if PV in cell:
                if cell != PV:
                    vio("V5-SENTINEL", name,
                        f"line {rn}: column '{col}' contains but does not equal the sentinel: {cell!r}")
                else:
                    pv_cells += 1

        # V4 confidence
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
                    vio("V4-CONFIDENCE", name, f"line {rn}: confidence_score {c} outside 0-100")
                if c > CONFIDENCE_CEILING:
                    vio("V4-CONFIDENCE", name,
                        f"line {rn}: confidence_score {c} exceeds the {CONFIDENCE_CEILING} policy ceiling")

        # V6 verification status
        if "verification_status" in idx:
            v = row[idx["verification_status"]]
            if v not in ALLOWED_VST:
                vio("V6-VERIFICATION", name, f"line {rn}: verification_status {v!r} not in {sorted(ALLOWED_VST)}")

        # V7 collection date
        if "collection_date" in idx:
            d = row[idx["collection_date"]]
            if d != EXPECTED_DATE:
                vio("V7-COLLECTION_DATE", name, f"line {rn}: collection_date {d!r} != {EXPECTED_DATE}")

    total_cells = len(rows) * ncols
    stats[name] = {
        "records": len(rows),
        "columns": ncols,
        "primary_key": pk_col,
        "pending_verification_cells": pv_cells,
        "total_cells": total_cells,
        "pending_verification_rate_pct": round(100 * pv_cells / total_cells, 2) if total_cells else 0.0,
        "confidence_min": min(conf_values) if conf_values else None,
        "confidence_max": max(conf_values) if conf_values else None,
        "confidence_avg": round(sum(conf_values) / len(conf_values), 1) if conf_values else None,
    }

# ------------------------------------------------------------ V8 internal FKs
crops = load_dicts(DATASETS / "crops.csv")
cats = load_dicts(DATASETS / "crop_categories.csv")
soils = load_dicts(DATASETS / "soil_types.csv")
zones = load_dicts(DATASETS / "climate_zones.csv")
procs = load_dicts(DATASETS / "agri_processing_opportunities.csv")

crop_ids = {r["crop_id"] for r in crops}
crop_name_by_id = {r["crop_id"]: r["crop_name"] for r in crops}
cat_ids = {r["category_id"] for r in cats}
cat_name_by_id = {r["category_id"]: r["category_name"] for r in cats}
soil_ids = {r["soil_id"] for r in soils}
soil_name_by_id = {r["soil_id"]: r["soil_name"] for r in soils}
zone_ids = {r["climate_zone_id"] for r in zones}
zone_name_by_id = {r["climate_zone_id"]: r["zone_name"] for r in zones}
proc_ids = {r["opportunity_id"] for r in procs}
proc_name_by_id = {r["opportunity_id"]: r["opportunity_name"] for r in procs}

# crops.csv -> crop_categories.csv
for r in crops:
    if r["category_id"] not in cat_ids:
        vio("V8-FK", "crops.csv", f"{r['crop_id']}: category_id {r['category_id']} not in crop_categories.csv")
    elif cat_name_by_id[r["category_id"]] != r["category_name"]:
        vio("V8-FK-DENORM", "crops.csv",
            f"{r['crop_id']}: category_name {r['category_name']!r} != {cat_name_by_id[r['category_id']]!r}")

# crop_soil_mapping.csv
for r in load_dicts(DATASETS / "crop_soil_mapping.csv"):
    if r["crop_id"] not in crop_ids:
        vio("V8-FK", "crop_soil_mapping.csv", f"{r['mapping_id']}: crop_id {r['crop_id']} not in crops.csv")
    elif crop_name_by_id[r["crop_id"]] != r["crop_name"]:
        vio("V8-FK-DENORM", "crop_soil_mapping.csv",
            f"{r['mapping_id']}: crop_name mismatch for {r['crop_id']}")
    if r["soil_id"] not in soil_ids:
        vio("V8-FK", "crop_soil_mapping.csv", f"{r['mapping_id']}: soil_id {r['soil_id']} not in soil_types.csv")
    elif soil_name_by_id[r["soil_id"]] != r["soil_name"]:
        vio("V8-FK-DENORM", "crop_soil_mapping.csv",
            f"{r['mapping_id']}: soil_name mismatch for {r['soil_id']}")

# crop_climate_mapping.csv
for r in load_dicts(DATASETS / "crop_climate_mapping.csv"):
    if r["crop_id"] not in crop_ids:
        vio("V8-FK", "crop_climate_mapping.csv", f"{r['mapping_id']}: crop_id {r['crop_id']} not in crops.csv")
    elif crop_name_by_id[r["crop_id"]] != r["crop_name"]:
        vio("V8-FK-DENORM", "crop_climate_mapping.csv",
            f"{r['mapping_id']}: crop_name mismatch for {r['crop_id']}")
    if r["climate_zone_id"] not in zone_ids:
        vio("V8-FK", "crop_climate_mapping.csv",
            f"{r['mapping_id']}: climate_zone_id {r['climate_zone_id']} not in climate_zones.csv")
    elif zone_name_by_id[r["climate_zone_id"]] != r["climate_zone_name"]:
        vio("V8-FK-DENORM", "crop_climate_mapping.csv",
            f"{r['mapping_id']}: climate_zone_name mismatch for {r['climate_zone_id']}")

# agri_business_mapping.csv internal FKs
abm = load_dicts(DATASETS / "agri_business_mapping.csv")
for r in abm:
    if r["crop_id"] not in crop_ids:
        vio("V8-FK", "agri_business_mapping.csv", f"{r['mapping_id']}: crop_id {r['crop_id']} not in crops.csv")
    elif crop_name_by_id[r["crop_id"]] != r["crop_name"]:
        vio("V8-FK-DENORM", "agri_business_mapping.csv",
            f"{r['mapping_id']}: crop_name mismatch for {r['crop_id']}")
    if r["processing_opportunity_id"] not in proc_ids:
        vio("V8-FK", "agri_business_mapping.csv",
            f"{r['mapping_id']}: processing_opportunity_id {r['processing_opportunity_id']} not in agri_processing_opportunities.csv")
    elif proc_name_by_id[r["processing_opportunity_id"]] != r["processing_opportunity_name"]:
        vio("V8-FK-DENORM", "agri_business_mapping.csv",
            f"{r['mapping_id']}: processing_opportunity_name mismatch")

# -------------------------------------------------------- V9 cross-package FKs
cross = {"package006_skill_id": {"resolved": 0, "sentinel": 0},
         "package004_opportunity_name": {"resolved": 0, "sentinel": 0}}

if (PKG006 / "skills.csv").exists():
    p6 = load_dicts(PKG006 / "skills.csv")
    p6_ids = {r["skill_id"]: r["skill_name"] for r in p6}
    for r in abm:
        sid = r["package006_skill_id"]
        if sid == PV:
            cross["package006_skill_id"]["sentinel"] += 1
        elif sid not in p6_ids:
            vio("V9-XPKG-FK", "agri_business_mapping.csv",
                f"{r['mapping_id']}: package006_skill_id {sid} not in Package006 skills.csv")
        else:
            cross["package006_skill_id"]["resolved"] += 1
            if p6_ids[sid] != r["package006_skill_name"]:
                vio("V9-XPKG-DENORM", "agri_business_mapping.csv",
                    f"{r['mapping_id']}: skill_name {r['package006_skill_name']!r} != Package006 {p6_ids[sid]!r}")
else:
    vio("V9-XPKG-FK", "agri_business_mapping.csv", "Package006 skills.csv not found; cannot validate skill FKs")

if PKG004.exists():
    p4_names = set()
    for f in PKG004.glob("*.csv"):
        for r in load_dicts(f):
            for key in ("name", "adapted_indian_concept", "scheme_name"):
                if r.get(key):
                    p4_names.add(r[key].strip())
    for r in abm:
        oname = r["package004_opportunity_name"]
        if oname == PV:
            cross["package004_opportunity_name"]["sentinel"] += 1
        elif oname not in p4_names:
            vio("V9-XPKG-FK", "agri_business_mapping.csv",
                f"{r['mapping_id']}: package004_opportunity_name {oname!r} not found in Package004 datasets")
        else:
            cross["package004_opportunity_name"]["resolved"] += 1
else:
    vio("V9-XPKG-FK", "agri_business_mapping.csv", "Package004 datasets not found; cannot validate opportunity FKs")

# ------------------------------------------------------------------ reporting
total_records = sum(s["records"] for s in stats.values())
total_cells = sum(s["total_cells"] for s in stats.values())
total_pv = sum(s["pending_verification_cells"] for s in stats.values())
all_conf = [s for s in stats.values() if s["confidence_min"] is not None]

summary = {
    "package": "Package005_Agriculture",
    "version": "1.0.0",
    "validated_at_collection_date": EXPECTED_DATE,
    "datasets": len(stats),
    "total_records": total_records,
    "total_cells": total_cells,
    "pending_verification_cells": total_pv,
    "pending_verification_rate_pct": round(100 * total_pv / total_cells, 2) if total_cells else 0.0,
    "confidence_min": min(s["confidence_min"] for s in all_conf) if all_conf else None,
    "confidence_max": max(s["confidence_max"] for s in all_conf) if all_conf else None,
    "confidence_ceiling_policy": CONFIDENCE_CEILING,
    "cross_package_fk": cross,
    "violations": len(violations),
    "result": "PASS" if not violations else "FAIL",
    "per_dataset": stats,
}

(PKG / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

print(f"Package005_Agriculture v1.0.0 validation")
print(f"  datasets ............. {len(stats)}")
print(f"  total records ........ {total_records}")
print(f"  total cells .......... {total_cells}")
print(f"  PENDING_VERIFICATION . {total_pv} ({summary['pending_verification_rate_pct']}%)")
print(f"  confidence range ..... {summary['confidence_min']}-{summary['confidence_max']} (ceiling {CONFIDENCE_CEILING})")
print(f"  x-pkg skill FKs ...... {cross['package006_skill_id']['resolved']} resolved, "
      f"{cross['package006_skill_id']['sentinel']} sentinel")
print(f"  x-pkg P004 FKs ....... {cross['package004_opportunity_name']['resolved']} resolved, "
      f"{cross['package004_opportunity_name']['sentinel']} sentinel")
print()

if violations:
    print(f"FAIL — {len(violations)} violation(s):\n")
    for v in violations[:60]:
        print(f"  [{v['check']}] {v['dataset']}: {v['detail']}")
    if len(violations) > 60:
        print(f"  ... and {len(violations) - 60} more")
    sys.exit(1)

print("PASS — all checks clean. Release-ready.")
