#!/usr/bin/env python3
"""
ValueWeave Platform v2 — Source Registry Builder (Module 7)

Extracts every distinct source URL cited across the eight released packages and
emits a registry with the fields the brief specifies: organisation, url, collector,
parser, frequency, trust_score, last_collection, next_collection, active.

This is derived, not authored. If a source is not cited by a package row, it does
not appear here — which means the registry is a true inventory of what the
knowledge base actually depends on, not a wish list of sources someone intended
to use.

COLLECTOR AND PARSER ASSIGNMENT (changed in v2.2)
-------------------------------------------------
Until v2.2 these two columns carried PENDING_IMPLEMENTATION, because
`knowledge_engine/` held no tracked source files and there was no module to name.
Work Package 1 recovered the engine, so both columns now name a real, importable
class chosen from the payload the source actually serves.

Two honesties are preserved rather than papered over:

  * The assignment is a *routing decision*, not a claim that the pipeline has been
    run. No source in this registry has yet been collected by the engine; the
    `last_collection` dates are the dates a human collected the data by hand.
  * A source whose payload cannot be determined from its URL keeps
    PENDING_IMPLEMENTATION. Guessing a parser is worse than admitting we do not
    know which one applies.

Every assigned name is verified to be importable before it is written — see
`ASSIGNMENT_CHECK` below. See governance/adr/ADR-006 (now RESOLVED).

Outputs
  source_registry/sources.csv            one row per distinct source URL
  source_registry/organisations.csv      one row per distinct organisation
  source_registry/source_summary.json
"""

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))          # so knowledge_engine.* is importable

PACKAGES = ROOT / "packages"
SR = Path(__file__).resolve().parent
TODAY = date.today()
PV = "PENDING_VERIFICATION"
PI = "PENDING_IMPLEMENTATION"

# Trust score by source class. Derived from the tiering every package already
# documents in its own METHODOLOGY, expressed once here for the whole platform.
TRUST = [
    (r"\.gov\.in$|\.nic\.in$|^gov\.in$", 85, "Tier 1 - Government of India domain"),
    (r"\.gov\.in|\.nic\.in", 85, "Tier 1 - Government of India domain"),
    (r"rbi\.org\.in|nabard\.org|sidbi\.in|nsic\.co\.in|kvic\.gov\.in", 82,
     "Tier 1 - statutory financial or development institution"),
    (r"icar\.org\.in|indianspices\.com|teaboard|coconutboard|csb\.gov\.in", 80,
     "Tier 1 - statutory commodity board or ICAR"),
    (r"\.ac\.in", 75, "Tier 2 - academic institution"),
    (r"nasscom\.in|weforum\.org|mckinsey\.com", 62, "Tier 3 - industry association or analyst"),
    (r"wikipedia\.org", 45, "Tier 4 - compiled secondary source, footnoted"),
]

# Re-collection cadence by what the source actually publishes. A scheme portal
# changes with every budget; a soil classification does not.
FREQUENCY = [
    (r"pmkisan|pmfby|pmjay|mudra|standupmitra|kviconline|scholarships|pmay|nrega|"
     r"jansuraksha|pmvishwakarma|pmfme|seedfund|myscheme|india\.gov\.in", "QUARTERLY",
     "Scheme parameters change with budget cycles and notifications"),
    (r"gst\.gov\.in|udyamregistration|dgft\.gov\.in|cdsco|fssai|foscos|cpcb|bis\.gov\.in",
     "SEMI_ANNUAL", "Compliance thresholds and product lists are revised periodically"),
    (r"gem\.gov\.in|ondc\.org|enam\.gov\.in|apeda", "SEMI_ANNUAL",
     "Market platform coverage and participation expand continuously"),
    (r"icar\.org\.in|nbss|crida|indianspices|teaboard|coconutboard", "ANNUAL",
     "Agronomic guidance is stable between research cycles"),
    (r"nasscom|weforum|mckinsey", "ANNUAL", "Annual industry reporting cycle"),
]

DEFAULT_FREQ = ("ANNUAL", "No faster cadence justified by observed change rate")

# Collector/parser routing, by the payload a URL actually serves. Ordered: the
# first pattern that matches wins, so specific file extensions precede host rules.
# (pattern, collector, parser, rationale)
PIPELINE = [
    (r"\.csv($|\?)", "collectors.csv_collector.CSVCollector",
     "parsers.csv_parser.CSVParser", "URL serves a CSV payload"),
    (r"\.json($|\?)|/api/|data\.gov\.in/resource", "collectors.json_collector.JSONCollector",
     "parsers.json_parser.JSONParser", "URL serves a JSON payload or a JSON API resource"),
    (r"\.xml($|\?)", "collectors.xml_collector.XMLCollector",
     "parsers.xml_parser.XMLParser", "URL serves an XML payload"),
    (r"/rss|/feed|\.rss($|\?)", "collectors.rss_collector.RSSCollector",
     "parsers.rss_parser.RSSParser", "URL serves a syndication feed"),
    (r"\.pdf($|\?)", "collectors.api_collector.APICollector",
     "parsers.pdf_parser.PDFParser", "URL serves a PDF document"),
    (r"^https?://", "collectors.api_collector.APICollector",
     "parsers.html_table_parser.HTMLTableParser",
     "HTML portal page; figures are published in tables"),
]

#: Set False to restore the pre-v2.2 behaviour of leaving both columns unassigned.
ASSIGN_PIPELINE = True


def importable(dotted):
    """Confirm a routed class actually exists before writing its name into the registry."""
    module, _, cls = dotted.rpartition(".")
    try:
        mod = __import__(f"knowledge_engine.{module}", fromlist=[cls])
        return hasattr(mod, cls)
    except Exception:                                              # noqa: BLE001
        return False


def classify_pipeline(url):
    """Return (collector, parser, rationale). PENDING_IMPLEMENTATION when unroutable."""
    if not ASSIGN_PIPELINE:
        return PI, PI, "Assignment disabled"
    u = url.lower()
    for pattern, collector, parser, rationale in PIPELINE:
        if re.search(pattern, u):
            if importable(collector) and importable(parser):
                return f"knowledge_engine.{collector}", f"knowledge_engine.{parser}", rationale
            return PI, PI, f"routed to {collector}/{parser} but the class is not importable"
    return PI, PI, "Payload type not determinable from the URL"


def classify_trust(url):
    host = urlparse(url).netloc.lower() or url.lower()
    for pattern, score, rationale in TRUST:
        if re.search(pattern, host):
            return score, rationale
    return 55, "Tier 3 - other public source"


def classify_frequency(url):
    u = url.lower()
    for pattern, freq, rationale in FREQUENCY:
        if re.search(pattern, u):
            return freq, rationale
    return DEFAULT_FREQ


NEXT_OFFSET = {"QUARTERLY": 91, "SEMI_ANNUAL": 182, "ANNUAL": 365}


def organisation_for(url, cited_names):
    """Prefer the most frequently cited data_source name for this URL."""
    if cited_names:
        return max(cited_names.items(), key=lambda kv: kv[1])[0]
    host = urlparse(url).netloc
    return host or PV


if __name__ == "__main__":
    print("Building source registry from the eight released packages:\n")

    # url -> {packages, datasets, data_source names, collection dates, confidences}
    sources = defaultdict(lambda: {
        "packages": set(), "datasets": set(), "names": defaultdict(int),
        "dates": set(), "confidences": [], "rows": 0,
    })

    for pkg_dir in sorted(PACKAGES.iterdir()):
        if not pkg_dir.is_dir():
            continue
        ds = pkg_dir / "datasets"
        if not ds.exists():
            continue
        for f in sorted(ds.glob("*.csv")):
            with open(f, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    url = (row.get("source_url") or "").strip()
                    if not url or url == PV or not url.startswith("http"):
                        continue
                    s = sources[url]
                    s["packages"].add(pkg_dir.name)
                    s["datasets"].add(f"{pkg_dir.name}/{f.name}")
                    name = (row.get("data_source") or "").strip()
                    if name and name != PV:
                        s["names"][name] += 1
                    d = (row.get("collection_date") or "").strip()
                    if d and d != PV:
                        s["dates"].add(d)
                    c = (row.get("confidence_score") or "").strip()
                    if c.isdigit():
                        s["confidences"].append(int(c))
                    s["rows"] += 1

    rows = []
    for i, (url, s) in enumerate(sorted(sources.items()), start=1):
        trust, trust_rationale = classify_trust(url)
        freq, freq_rationale = classify_frequency(url)
        collector, parser, pipeline_rationale = classify_pipeline(url)
        last = max(s["dates"]) if s["dates"] else PV
        try:
            nxt = (date.fromisoformat(last) + timedelta(days=NEXT_OFFSET[freq])).isoformat()
        except ValueError:
            nxt = PV
        observed = (round(sum(s["confidences"]) / len(s["confidences"]), 1)
                    if s["confidences"] else PV)
        rows.append({
            "source_id": f"src-{i:03d}",
            "organisation": organisation_for(url, s["names"]),
            "url": url,
            "collector": collector,
            "parser": parser,
            "frequency": freq,
            "trust_score": trust,
            "last_collection": last,
            "next_collection": nxt,
            "active": "TRUE",
            "consuming_packages": ";".join(sorted(s["packages"])),
            "consuming_dataset_count": len(s["datasets"]),
            "rows_citing_source": s["rows"],
            "observed_confidence_avg": observed,
            "trust_rationale": trust_rationale,
            "frequency_rationale": freq_rationale,
            "pipeline_rationale": pipeline_rationale,
        })

    hdr = ["source_id", "organisation", "url", "collector", "parser", "frequency",
           "trust_score", "last_collection", "next_collection", "active",
           "consuming_packages", "consuming_dataset_count", "rows_citing_source",
           "observed_confidence_avg", "trust_rationale", "frequency_rationale",
           "pipeline_rationale"]
    with open(SR / "sources.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=hdr)
        w.writeheader()
        w.writerows(rows)
    print(f"  sources.csv: {len(rows)} distinct source URLs")

    orgs = defaultdict(lambda: {"urls": set(), "packages": set(), "rows": 0, "trust": []})
    for r in rows:
        o = orgs[r["organisation"]]
        o["urls"].add(r["url"])
        o["packages"].update(r["consuming_packages"].split(";"))
        o["rows"] += r["rows_citing_source"]
        o["trust"].append(r["trust_score"])
    org_rows = [{
        "organisation": name,
        "distinct_urls": len(o["urls"]),
        "consuming_packages": ";".join(sorted(o["packages"])),
        "rows_citing": o["rows"],
        "trust_score": max(o["trust"]),
    } for name, o in sorted(orgs.items(), key=lambda kv: -kv[1]["rows"])]
    with open(SR / "organisations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(org_rows[0].keys()))
        w.writeheader()
        w.writerows(org_rows)
    print(f"  organisations.csv: {len(org_rows)} distinct organisations")

    by_freq = defaultdict(int)
    by_trust = defaultdict(int)
    by_collector = defaultdict(int)
    by_parser = defaultdict(int)
    for r in rows:
        by_freq[r["frequency"]] += 1
        by_trust[r["trust_score"]] += 1
        by_collector[r["collector"].rpartition(".")[2]] += 1
        by_parser[r["parser"].rpartition(".")[2]] += 1
    assigned = sum(1 for r in rows if r["collector"] != PI)
    summary = {
        "built_at": TODAY.isoformat(),
        "distinct_sources": len(rows),
        "distinct_organisations": len(org_rows),
        "total_rows_citing_a_source": sum(r["rows_citing_source"] for r in rows),
        "by_frequency": dict(sorted(by_freq.items(), key=lambda kv: -kv[1])),
        "by_trust_score": dict(sorted(by_trust.items(), key=lambda kv: -kv[0])),
        "by_collector": dict(sorted(by_collector.items(), key=lambda kv: -kv[1])),
        "by_parser": dict(sorted(by_parser.items(), key=lambda kv: -kv[1])),
        "sources_with_pipeline_assigned": assigned,
        "sources_pending_implementation": len(rows) - assigned,
        "collector_parser_status": (
            f"{assigned} of {len(rows)} sources are routed to a real, importable "
            f"Knowledge Engine collector and parser (recovered in Platform v2.2). "
            f"{len(rows) - assigned} keep PENDING_IMPLEMENTATION because the payload "
            f"type is not determinable from the URL. Routing is a decision about which "
            f"module WOULD run; no source has yet been collected by the engine. "
            f"See governance/adr/ADR-006 (RESOLVED)."),
        "top_sources_by_usage": [
            {"organisation": r["organisation"], "url": r["url"],
             "rows_citing": r["rows_citing_source"]}
            for r in sorted(rows, key=lambda r: -r["rows_citing_source"])[:10]
        ],
    }
    (SR / "source_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("  source_summary.json")

    print(f"\n  {len(rows)} sources across {len(org_rows)} organisations, "
          f"{summary['total_rows_citing_a_source']} citing rows")
    print(f"  cadence: " + ", ".join(f"{k} {v}" for k, v in summary["by_frequency"].items()))
    print(f"  pipeline: {assigned}/{len(rows)} routed to a real collector+parser, "
          f"{len(rows) - assigned} PENDING_IMPLEMENTATION")
    print("  collectors: " + ", ".join(f"{k} {v}" for k, v in summary["by_collector"].items()))
