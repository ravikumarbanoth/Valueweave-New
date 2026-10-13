#!/usr/bin/env python3
"""Import scheme/support awareness workbook into canonical package data.

The workbook is an editorial source, not an application schema. This script
keeps every populated row, preserves missing fields explicitly, and mirrors the
canonical CSV into a frontend JSON file used by the Schemes directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
PACKAGE_CSV = ROOT / "packages" / "Package007_Government_Schemes" / "datasets" / "scheme_support_resources.csv"
FRONTEND_JSON = ROOT / "frontend" / "data" / "scheme-support-resources.json"

CATEGORY_LABELS = {
    "BANK LOAN SCHEMES": "Bank Loan Schemes",
    "SKILL DEVELOPMENT CENTERS": "Skill Development Centres",
    "HAND HOLDING/EDP": "Handholding and Entrepreneurship Development",
    "SOCIAL SECURITY SCHEMES": "Social Security Schemes",
    "AWARENESS": "Awareness and Digital Literacy",
    "COMPLIANTS/AWARENESS": "Complaints and Grievance Redressal",
}

ENTITY_BY_CATEGORY = {
    "BANK LOAN SCHEMES": "GovernmentScheme",
    "SKILL DEVELOPMENT CENTERS": "TrainingProvider",
    "HAND HOLDING/EDP": "Institution",
    "SOCIAL SECURITY SCHEMES": "GovernmentScheme",
    "AWARENESS": "Institution",
    "COMPLIANTS/AWARENESS": "Institution",
}

PORTAL_NAMES = {
    "PSB LOAN IN 59MINUTES": ("Institution", "Loan portal"),
    "PSB LOAN IN 59MINUTES SCHEME": ("Institution", "Loan portal"),
    "VIDYALAKSHMI": ("Institution", "Education loan portal"),
    "CHAMPIONS (MSME)": ("Institution", "MSME support portal"),
    "DIGITAL BANKING": ("Institution", "Awareness resource"),
    "DISHA/NDLM": ("Institution", "Digital literacy programme"),
    "IGOD": ("Institution", "Government information portal"),
    "RBI OMBUDSMAN": ("Institution", "Grievance redressal"),
}

KIND_BY_CATEGORY = {
    "BANK LOAN SCHEMES": "Government scheme",
    "SKILL DEVELOPMENT CENTERS": "Training provider",
    "HAND HOLDING/EDP": "Entrepreneurship support",
    "SOCIAL SECURITY SCHEMES": "Government scheme",
    "AWARENESS": "Awareness resource",
    "COMPLIANTS/AWARENESS": "Grievance redressal",
}

GOVT_SCHEME_IDS = {
    "AIF": "sch-012",
    "CGTMSE": "sch-017",
    "PMMY": "sch-015",
    "PMEGP": "sch-014",
    "PMFME": "sch-019",
    "PMAY": "sch-037",
    "STAND UP INDIA": "sch-016",
    "DDU-GKY": "sch-023",
    "APY": "sch-004",
    "PMJDY": "sch-001",
    "PMJJBY": "sch-003",
    "PMSBY": "sch-002",
}

ORGANISATION_TYPE_LABELS = {
    "GOVT": "Government",
    "NGO": "NGO",
    "NON PROFIT ORGANISATION": "Non-profit organisation",
    "VOCATIONAL TRAINING PROVIDER (VTP)": "Vocational Training Provider (VTP)",
    "FOUNDATION": "Foundation",
    "TRUST": "Trust",
}

EXPLICIT_ACRONYMS = {
    "AIF": "AIF",
    "DIC": "DIC",
    "IDEA": "IDEA",
    "PRIDE": "PRIDE",
    "WE-HUB": "WE-HUB",
    "PM SVANIDHI (PM STREET VENDOR'S ATMANIRBHAR NIDHI)": "PM SVANidhi",
    "PRADHAN MANTRI AWAAS YOJANA (PMAY)": "PMAY",
    "NI MSME (NATIONAL INSTITUTE FOR MICRO, SMALL AND MEDIUM ENTERPRISES)": "NI-MSME",
    "T-HUB (TECHNOLOGY HUB)": "T-Hub",
    "TS IPASS (TELANGANA STATE INDUSTRIAL PROJECT APPROVAL AND SELF-CERTIFICATION SYSTEM)": "TS-iPASS",
    "CHAMPIONS (MSME)": "CHAMPIONS",
    "DISHA (DIGITAL SAKSHARTA ABHIYAN) OR NATIONAL DIGITAL LITERACY MISSION (NDLM)": "DISHA / NDLM",
}

PV = "PENDING_VERIFICATION"
COLLECTION_DATE = "2026-07-25"


def clean(value: str | None) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    replacements = {
        "\u00a0": " ",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def display_name(source_name: str) -> str:
    fixes = {
        "PRADHAN MANTRI JAN DAN YOJANA(PMJDY)": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "PRADHAN MANTRI JEEVAN JYOTHI YOJANA(PMJJBY)": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "PRADHAN MANTRI SURAKSHA BIMA YOJANA(PMSBY)": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "SUKANYA SAMRUDDHI YOJANA (SSY)": "Sukanya Samriddhi Yojana (SSY)",
        "PRADHAN MANTRI AWAAS YOJANA (PMAY)": "Pradhan Mantri Awaas Yojana (PMAY)",
        "PM SVANIDHI": "PM SVANidhi",
        "PSB LOAN IN 59MINUTES": "PSB Loan in 59 Minutes",
        "PSB LOAN IN 59MINUTES SCHEME": "PSB Loan in 59 Minutes",
        "STAND UP INDIA": "Stand Up India",
        "DIGITAL BANKING": "Digital Banking",
        "RBI OMBUDSMAN": "RBI Ombudsman",
        "YASHODA FOUNDATION)": "YASHODA FOUNDATION",
    }
    title = fixes.get(source_name.upper(), source_name)
    return title.replace("Employement", "Employment").replace("Formlisation", "Formalisation")


def display_description(description: str) -> str:
    fixes = {
        "Employement": "Employment",
        "enterprenuership": "entrepreneurship",
        "Formlisation": "Formalisation",
        "YOJANA": "Yojana",
    }
    result = description
    for old, new in fixes.items():
        result = result.replace(old, new)
    return result


def slugify(value: str) -> str:
    value = clean(value).lower()
    value = re.sub(r"&", " and ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "resource"


def acronym_for(name: str) -> str:
    upper_name = clean(name).upper()
    if upper_name in EXPLICIT_ACRONYMS:
        return EXPLICIT_ACRONYMS[upper_name]
    lead_paren = re.match(r"^([A-Z0-9/-]{2,})\s*\(", clean(name))
    if lead_paren:
        return lead_paren.group(1)
    tail_paren = re.search(r"\(([A-Z0-9/-]{2,})\)$", clean(name))
    if tail_paren:
        return tail_paren.group(1)
    return ""


def organisation_type_for(raw_org_type: str, entity_type: str) -> str:
    key = clean(raw_org_type).upper()
    if key in ORGANISATION_TYPE_LABELS:
        return ORGANISATION_TYPE_LABELS[key]
    if key:
        return clean(raw_org_type)
    return "Government" if entity_type == "GovernmentScheme" else "Support organisation or portal"


def read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        xml = zf.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(xml)
    strings = []
    for si in root.findall("x:si", ns):
        parts = [node.text or "" for node in si.findall(".//x:t", ns)]
        strings.append(clean("".join(parts)))
    return strings


def read_sheet_rows(workbook: Path) -> list[dict[str, str]]:
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(workbook) as zf:
        shared = read_shared_strings(zf)
        xml = zf.read("xl/worksheets/sheet1.xml")
    root = ET.fromstring(xml)
    rows = []
    for row in root.findall(".//x:sheetData/x:row", ns):
        row_number = int(row.attrib["r"])
        values: dict[str, str] = {}
        for cell in row.findall("x:c", ns):
            ref = cell.attrib.get("r", "")
            col = re.sub(r"\d+", "", ref)
            value_node = cell.find("x:v", ns)
            inline_node = cell.find("x:is/x:t", ns)
            value = ""
            if inline_node is not None:
                value = clean(inline_node.text)
            elif value_node is not None:
                raw = value_node.text or ""
                value = shared[int(raw)] if cell.attrib.get("t") == "s" and raw.isdigit() else clean(raw)
            values[col] = value
        if row_number > 1 and any(values.values()):
            rows.append({"excel_row": str(row_number), **values})
    return rows


def normalize_record(index: int, row: dict[str, str]) -> dict[str, str]:
    source_category = clean(row.get("B"))
    raw_org_type = clean(row.get("C"))
    source_name = clean(row.get("D"))
    source_key = source_name.upper()
    entity_type = ENTITY_BY_CATEGORY.get(source_category, "Institution")
    record_kind = KIND_BY_CATEGORY.get(source_category, "Support resource")
    if source_key in PORTAL_NAMES:
        entity_type, record_kind = PORTAL_NAMES[source_key]

    description = display_description(clean(row.get("F")))
    website = clean(row.get("G"))
    extra = clean(row.get("H"))
    if not website.startswith(("http://", "https://")) and extra.startswith(("http://", "https://")):
        website, extra = extra, website

    name = display_name(source_name)
    acronym = acronym_for(source_name)
    missing = []
    if not description:
        missing.append("description")
    if not website:
        missing.append("official_website")
    if not clean(row.get("E")):
        missing.append("logo")

    canonical_scheme_id = GOVT_SCHEME_IDS.get(acronym.upper(), "") or GOVT_SCHEME_IDS.get(source_key, "")
    resource_id = f"ssr-{index:03d}"
    slug = slugify(name)
    return {
        "resource_id": resource_id,
        "slug": slug,
        "source_excel_row": row["excel_row"],
        "source_category": source_category,
        "display_category": CATEGORY_LABELS.get(source_category, source_category.title()),
        "entity_type": entity_type,
        "record_kind": record_kind,
        "organisation_type": organisation_type_for(raw_org_type, entity_type),
        "name": name,
        "source_name": source_name,
        "acronym": acronym,
        "description": description,
        "official_website": website,
        "supplemental_notes": extra,
        "logo": clean(row.get("E")),
        "canonical_scheme_id": canonical_scheme_id,
        "data_source": "Schemes programs awareness.xlsx",
        "verification_status": "VST-NEEDS_REVIEW",
        "missing_fields": ";".join(missing),
    }


def to_csv_row(record: dict[str, str]) -> dict[str, str]:
    sentinel_fields = {"description", "official_website", "logo"}
    csv_row: dict[str, str] = {}
    for key, value in record.items():
        if value:
            csv_row[key] = value
        elif key in sentinel_fields:
            csv_row[key] = PV
        else:
            csv_row[key] = "None"
    csv_row["source_url"] = record["official_website"] or PV
    csv_row["collection_date"] = COLLECTION_DATE
    csv_row["confidence_score"] = "60"
    csv_row["verification_status"] = "VST-NEEDS_REVIEW"
    csv_row["notes"] = record["supplemental_notes"] or "Imported from Schemes programs awareness.xlsx"
    return csv_row


def write_outputs(records: list[dict[str, str]]) -> None:
    PACKAGE_CSV.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_JSON.parent.mkdir(parents=True, exist_ok=True)
    csv_rows = [to_csv_row(record) for record in records]
    headers = list(csv_rows[0].keys())
    with PACKAGE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    category_counts = Counter(record["display_category"] for record in records)
    payload = {
        "source": "Schemes programs awareness.xlsx",
        "canonicalPackageDataset": "packages/Package007_Government_Schemes/datasets/scheme_support_resources.csv",
        "recordCount": len(records),
        "categoryCounts": dict(sorted(category_counts.items())),
        "records": records,
    }
    FRONTEND_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    rows = read_sheet_rows(args.workbook)
    records = [normalize_record(i, row) for i, row in enumerate(rows, start=1)]
    slugs = [record["slug"] for record in records]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate slugs after import: {', '.join(duplicates)}")
    write_outputs(records)
    print(f"Imported {len(records)} records")
    for category, count in sorted(Counter(record["display_category"] for record in records).items()):
        print(f"- {category}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
