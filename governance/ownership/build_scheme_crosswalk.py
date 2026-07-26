#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — Work Package 2: Government Scheme Crosswalk

ADR-003 is decided in favour of Option 1: Package007_Government_Schemes is the
authoritative owner of GovernmentScheme entities and attributes.

This script implements the mechanical half of that decision. It matches every
scheme row held by the five domain packages against Package007's canonical
registry and writes the crosswalk that the ownership registry, the graph and the
API all read.

MATCHING IS CONSERVATIVE BY DESIGN
----------------------------------
A wrong crosswalk row is worse than a missing one: it would silently redirect a
consumer from a domain scheme to an unrelated canonical scheme. Four matchers run
in decreasing order of evidential strength, and each records how it fired:

  EXACT_NAME      normalised canonical names are identical
  ACRONYM         a parenthetical acronym in the domain name equals a Package007
                  short_name, e.g. "... (PM-KISAN)" -> PM-KISAN
  PORTAL          both rows cite the same official portal host
  FUZZY           token-and-sequence similarity above FUZZY_THRESHOLD, accepted
                  only when exactly one Package007 scheme clears it

Anything unmatched is left unmatched. It is recorded as DOMAIN_CANONICAL, which is
a determinate statement — this package remains the owner of that scheme until a
steward promotes it into Package007 — not an admission of ignorance.

BACKWARD COMPATIBILITY
----------------------
No existing column is renamed, reordered or removed. No row is deleted. Two
columns are appended to each domain scheme dataset:

  package007_scheme_id   the canonical id, or PENDING_VERIFICATION when unmatched
  scheme_ownership       DEPRECATED_REFERENCE | DOMAIN_CANONICAL

A consumer that ignores both columns reads exactly what it read before.

Outputs
  governance/ownership/scheme_crosswalk.csv    one row per domain scheme row
  governance/ownership/crosswalk_summary.json
  and, with --apply, the two new columns in the five domain datasets
"""

import argparse
import csv
import difflib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES = ROOT / "packages"
OUT = Path(__file__).resolve().parent

PV = "PENDING_VERIFICATION"
DEPRECATED = "DEPRECATED_REFERENCE"
DOMAIN_CANONICAL = "DOMAIN_CANONICAL"
FUZZY_THRESHOLD = 0.88

CANONICAL_PACKAGE = "Package007_Government_Schemes"
CANONICAL_DATASET = "government_schemes.csv"

# The five domain packages that held scheme rows before Package007 existed.
# (package, dataset, id column, name column)
DOMAIN_SCHEME_DATASETS = [
    ("Package002_Education", "scholarships.csv", "id", "scheme_name"),
    ("Package003_Healthcare", "government_health_insurance_schemes.csv", "id", "scheme_name"),
    ("Package004_Industries", "msme_entrepreneurship_support_schemes.csv", "id", "name"),
    ("Package005_Agriculture", "agriculture_schemes.csv", "scheme_id", "scheme_name"),
    ("Package006_Skills_and_Training", "government_skill_schemes.csv", "scheme_id", "scheme_name"),
]

# Tokens that carry no discriminating meaning when comparing scheme names.
STOPWORDS = {
    "the", "of", "and", "for", "in", "a", "an", "scheme", "yojana", "india",
    "indian", "national", "central", "government", "pradhan", "mantri",
    "programme", "program", "mission",
}


def normalise(text):
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def tokens(text):
    return {t for t in normalise(text).split() if t and t not in STOPWORDS}


def similarity(a, b):
    ta, tb = tokens(a), tokens(b)
    jaccard = len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0
    seq = difflib.SequenceMatcher(None, normalise(a), normalise(b)).ratio()
    return round(0.6 * jaccard + 0.4 * seq, 4)


def acronyms(text):
    """Parenthetical acronyms: 'X (PM-KISAN; formerly Y)' -> {'PM-KISAN', 'Y'}."""
    out = set()
    for group in re.findall(r"\(([^)]*)\)", str(text)):
        for part in re.split(r"[;,/]", group):
            part = part.strip()
            part = re.sub(r"^(formerly|also|aka|erstwhile)\s+", "", part, flags=re.I).strip()
            # An acronym is short and mostly capitals or digits.
            if 2 <= len(part) <= 24 and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .\-]*", part):
                caps = sum(1 for c in part if c.isupper())
                if caps >= 2:
                    out.add(part.upper().replace(" ", ""))
    return out


def host(url):
    try:
        h = urlparse(str(url)).netloc.lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_canonical():
    rows = read_csv(PACKAGES / CANONICAL_PACKAGE / "datasets" / CANONICAL_DATASET)
    index = {
        "rows": rows,
        "by_norm": defaultdict(list),
        "by_acronym": defaultdict(list),
        "by_host": defaultdict(list),
    }
    for r in rows:
        index["by_norm"][normalise(r["scheme_name"])].append(r)
        for a in acronyms(r["scheme_name"]) | {str(r.get("short_name", "")).upper().replace(" ", "")}:
            if a and a != PV:
                index["by_acronym"][a].append(r)
        h = host(r.get("official_portal", ""))
        if h:
            index["by_host"][h].append(r)
    return index


def match(domain_row, name_col, index, portal_cols):
    """Return (canonical_row, method, score) or (None, 'NO_MATCH', 0.0)."""
    name = domain_row[name_col]

    hits = index["by_norm"].get(normalise(name), [])
    if len(hits) == 1:
        return hits[0], "EXACT_NAME", 1.0

    for a in acronyms(name):
        hits = index["by_acronym"].get(a, [])
        if len(hits) == 1:
            return hits[0], "ACRONYM", 1.0

    for col in portal_cols:
        h = host(domain_row.get(col, ""))
        if not h:
            continue
        hits = index["by_host"].get(h, [])
        if len(hits) == 1:
            return hits[0], "PORTAL", 1.0

    scored = [(similarity(name, r["scheme_name"]), r) for r in index["rows"]]
    above = [(s, r) for s, r in scored if s >= FUZZY_THRESHOLD]
    if len(above) == 1:
        return above[0][1], "FUZZY", above[0][0]
    # Two candidates above threshold is ambiguity, not a hint. Refuse.
    best = max(scored, key=lambda sr: sr[0])[0] if scored else 0.0
    return None, ("AMBIGUOUS" if len(above) > 1 else "NO_MATCH"), best


def build():
    index = load_canonical()
    crosswalk = []

    for pkg, dataset, id_col, name_col in DOMAIN_SCHEME_DATASETS:
        path = PACKAGES / pkg / "datasets" / dataset
        rows = read_csv(path)
        portal_cols = [c for c in rows[0]
                       if c in ("official_website", "application_portal", "official_portal")]
        for r in rows:
            canonical, method, score = match(r, name_col, index, portal_cols)
            crosswalk.append({
                "domain_package": pkg,
                "domain_dataset": dataset,
                "domain_row_id": r[id_col],
                "domain_scheme_name": r[name_col],
                "package007_scheme_id": canonical["scheme_id"] if canonical else PV,
                "package007_scheme_name": canonical["scheme_name"] if canonical else PV,
                "scheme_ownership": DEPRECATED if canonical else DOMAIN_CANONICAL,
                "match_method": method,
                "match_score": score,
            })
    return index, crosswalk


def apply_to_packages(crosswalk):
    """Append the two governance columns to each domain scheme dataset."""
    by_row = {(c["domain_package"], c["domain_dataset"], c["domain_row_id"]): c
              for c in crosswalk}
    changed = []
    for pkg, dataset, id_col, _name_col in DOMAIN_SCHEME_DATASETS:
        path = PACKAGES / pkg / "datasets" / dataset
        rows = read_csv(path)
        header = list(rows[0].keys())
        for col in ("package007_scheme_id", "scheme_ownership"):
            if col not in header:
                header.append(col)
        for r in rows:
            c = by_row[(pkg, dataset, r[id_col])]
            r["package007_scheme_id"] = c["package007_scheme_id"]
            r["scheme_ownership"] = c["scheme_ownership"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            w.writerows(rows)
        changed.append(f"{pkg}/{dataset}")
    return changed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the two governance columns into the domain datasets")
    args = ap.parse_args()

    index, crosswalk = build()

    with open(OUT / "scheme_crosswalk.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(crosswalk[0].keys()))
        w.writeheader()
        w.writerows(crosswalk)

    by_method = defaultdict(int)
    by_package = defaultdict(lambda: {"rows": 0, "matched": 0})
    for c in crosswalk:
        by_method[c["match_method"]] += 1
        by_package[c["domain_package"]]["rows"] += 1
        if c["scheme_ownership"] == DEPRECATED:
            by_package[c["domain_package"]]["matched"] += 1

    matched = sum(1 for c in crosswalk if c["scheme_ownership"] == DEPRECATED)
    distinct_canonical = len({c["package007_scheme_id"] for c in crosswalk
                              if c["package007_scheme_id"] != PV})
    summary = {
        "canonical_package": CANONICAL_PACKAGE,
        "canonical_scheme_count": len(index["rows"]),
        "domain_scheme_rows": len(crosswalk),
        "matched_to_canonical": matched,
        "domain_canonical_unmatched": len(crosswalk) - matched,
        "distinct_canonical_schemes_referenced": distinct_canonical,
        "by_match_method": dict(sorted(by_method.items(), key=lambda kv: -kv[1])),
        "by_package": {k: v for k, v in sorted(by_package.items())},
        "fuzzy_threshold": FUZZY_THRESHOLD,
        "total_scheme_rows_platform_wide": len(crosswalk) + len(index["rows"]),
    }
    (OUT / "crosswalk_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"Package007 canonical registry: {len(index['rows'])} schemes")
    print(f"Domain scheme rows:            {len(crosswalk)}")
    print(f"  matched -> {DEPRECATED}: {matched}")
    print(f"  unmatched -> {DOMAIN_CANONICAL}: {len(crosswalk) - matched}")
    print("  by method: " + ", ".join(f"{k} {v}" for k, v in summary["by_match_method"].items()))
    print()
    for pkg, v in summary["by_package"].items():
        print(f"  {pkg:<34} {v['matched']:>2}/{v['rows']:<3} matched")

    if args.apply:
        changed = apply_to_packages(crosswalk)
        print(f"\napplied 2 governance columns to {len(changed)} datasets:")
        for c in changed:
            print(f"  {c}")
    else:
        print("\n(dry run — pass --apply to write the columns into the datasets)")
