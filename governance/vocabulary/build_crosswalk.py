#!/usr/bin/env python3
"""
ValueWeave Platform v3.0 — Step 0: Vocabulary Crosswalk

THE PROBLEM THIS SOLVES
-----------------------
The application and the knowledge graph name the same things differently, and
until v3.0 nothing measured how badly. The answer, measured here rather than
estimated: 7 of the 57 skills the onboarding form suggests resolve to a graph
Skill. Every feature that connects a *user* to the graph — Recommended Skills,
Skill Gap Analysis, Business Match — runs through that join, so all of them would
have returned nothing for roughly nine users in ten, silently.

This script builds the mapping. It is the prerequisite for Steps 5, 6 and 7 of
docs/IMPLEMENTATION_ROADMAP.md.

MATCHING IS CONSERVATIVE, FOR THE SAME REASON AS ADR-003
--------------------------------------------------------
A wrong crosswalk row silently redirects a user from the skill they claimed to an
unrelated one, and nothing downstream can detect it. A missing row is visible.
So five matchers run in decreasing order of evidential strength:

  EXACT_NAME      normalised names are identical
  ALIAS           the term matches a registered graph alias
  PREFIX          exactly one entity name starts with the term
  FUZZY           similarity >= FUZZY_THRESHOLD, accepted only when exactly one
                  candidate clears it — two is ambiguity, not a hint
  CURATED         a human decision recorded in curated_overrides.json, with a
                  reason, because some mappings are knowledge no matcher has

Anything left is NO_COUNTERPART.

NO_COUNTERPART IS NOT A FAILURE
-------------------------------
It is a determinate statement: "this term is real and the knowledge base has no
researched data for it." `AC Repair`, `Beautician Services` and `CCTV
Installation` have no Package006 counterpart at all, and no similarity threshold
conjures a row that does not exist. Forcing those to the nearest Skill would be
fabrication.

The unresolved list is therefore two useful things at once: the honest empty state
for the UI, and the Package006 collection backlog ranked by how many users are
affected.

Outputs
  governance/vocabulary/skill_crosswalk.csv
  governance/vocabulary/sector_crosswalk.csv
  governance/vocabulary/district_crosswalk.csv
  governance/vocabulary/crosswalk_summary.json

    python3 governance/vocabulary/build_crosswalk.py            # build + report
    python3 governance/vocabulary/build_crosswalk.py --check     # CI: exit 1 on drift
"""

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
KG = ROOT / "knowledge_graph"

FUZZY_THRESHOLD = 0.88
NO_COUNTERPART = "NO_COUNTERPART"

#: term_kind -> the graph entity type it must resolve to
TARGET_TYPE = {"skill": "Skill", "sector": "Industry", "district": "District"}


# ------------------------------------------------------------------ normalise
def normalise(text):
    """Match search/index.py: ascii, lowercase, & -> and, punctuation collapsed."""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------- term sources
def onboarding_skills():
    """The 57 suggestions in the onboarding form — what users are nudged to claim."""
    src = (FRONTEND / "app" / "onboarding" / "page.js").read_text(encoding="utf-8")
    m = re.search(r"const SKILL_SUGGESTIONS = \[(.*?)\];", src, re.S)
    if not m:
        raise SystemExit("onboarding SKILL_SUGGESTIONS not found — the form changed shape")
    return re.findall(r'"([^"]+)"', m.group(1))


def idea_library():
    base = FRONTEND / "lib" / "idea-library"
    ideas = json.loads((base / "ideas.json").read_text(encoding="utf-8"))
    sectors = json.loads((base / "sectors.json").read_text(encoding="utf-8"))
    groups = json.loads((base / "skills.json").read_text(encoding="utf-8"))
    return ideas, sectors, groups


def static_districts():
    src = (FRONTEND / "lib" / "districts-data.js").read_text(encoding="utf-8")
    return re.findall(r'\n    slug: "[a-z-]+",\n    name: "([^"]+)"', src)


def collect_terms():
    """(term_kind, source_vocab, term) for every term the app can produce."""
    ideas, sectors, groups = idea_library()
    sector_label = {s["id"]: s["label"] for s in sectors}
    terms = []

    for t in onboarding_skills():
        terms.append(("skill", "onboarding", t))
    for i in ideas:
        for t in i.get("skills_needed") or []:
            terms.append(("skill", "idea_library", t))
    for g in groups:
        for t in g["skills"]:
            terms.append(("skill", "idea_library_groups", t))

    for i in ideas:
        sid = i.get("sector")
        if sid:
            terms.append(("sector", "idea_library", sector_label.get(sid, sid)))
    for s in sectors:
        terms.append(("sector", "idea_library", s["label"]))

    for n in static_districts():
        terms.append(("district", "static_districts", n))
    for i in ideas:
        for d in i.get("district_fit") or []:
            terms.append(("district", "idea_library", d))

    # Distinct on (kind, vocab, normalised) — the same term from two ideas is one term.
    seen, out = set(), []
    for kind, vocab, term in terms:
        key = (kind, vocab, normalise(term))
        if key in seen or not normalise(term):
            continue
        seen.add(key)
        out.append((kind, vocab, term))
    return out


# ------------------------------------------------------------------- matching
class Matcher:
    def __init__(self):
        from knowledge_graph.resolution.resolver import Resolver   # noqa: E402
        self.resolver = Resolver()

        self.entities = read_csv(KG / "entities" / "entities.csv")
        self.by_gid = {e["global_entity_id"]: e for e in self.entities}
        self.by_type_norm = defaultdict(dict)
        for e in self.entities:
            self.by_type_norm[e["entity_type"]].setdefault(
                normalise(e["canonical_name"]), e)

        self.alias_by_type_norm = defaultdict(dict)
        for a in read_csv(KG / "entities" / "aliases.csv"):
            ent = self.by_gid.get(a["global_entity_id"])
            if ent:
                self.alias_by_type_norm[ent["entity_type"]].setdefault(
                    normalise(a["alias"]), ent)

        path = OUT / "curated_overrides.json"
        raw = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        self.curated = {k: v for k, v in raw.items() if not k.startswith("_")}
        # Terms that are real but span more than one entity. They stay unresolved —
        # the crosswalk is 1:1 by construction and a partial mapping silently drops
        # half the meaning — but the candidates are recorded for the UI and the steward.
        self.multi = raw.get("_multi_candidate", {})

    def match(self, kind, term):
        """Return (entity | None, method, score, note)."""
        etype = TARGET_TYPE[kind]
        n = normalise(term)

        hit = self.by_type_norm[etype].get(n)
        if hit:
            return hit, "EXACT_NAME", 1.0, ""

        hit = self.alias_by_type_norm[etype].get(n)
        if hit:
            return hit, "ALIAS", 1.0, f"matched alias of {hit['canonical_name']}"

        pref = [e for norm, e in self.by_type_norm[etype].items()
                if norm.startswith(n + " ")]
        if len(pref) == 1:
            return pref[0], "PREFIX", 0.9, ""

        # Reuse the graph resolver's blended similarity so the crosswalk and the
        # graph agree on what "similar" means.
        scored = [(self.resolver.similarity(term, e["canonical_name"]), e)
                  for e in self.by_type_norm[etype].values()]
        above = [(s, e) for s, e in scored if s >= FUZZY_THRESHOLD]
        if len(above) == 1:
            return above[0][1], "FUZZY", round(above[0][0], 4), ""

        override = self.curated.get(kind, {}).get(term)
        if override:
            gid = override["global_entity_id"]
            ent = self.by_gid.get(gid)
            if ent is None:
                raise SystemExit(
                    f"curated override for {term!r} points at {gid!r}, which is not "
                    f"in the entity registry. Refusing to write a broken crosswalk.")
            if ent["entity_type"] != etype:
                raise SystemExit(
                    f"curated override for {term!r} points at a {ent['entity_type']}, "
                    f"expected {etype}.")
            return ent, "CURATED", 1.0, override.get("reason", "")

        best = max(scored, key=lambda se: se[0])[0] if scored else 0.0

        multi = self.multi.get(kind, {}).get(term)
        if multi:
            for gid in multi.get("candidates", []):
                if gid not in self.by_gid:
                    raise SystemExit(
                        f"_multi_candidate for {term!r} lists {gid!r}, which is not in "
                        f"the entity registry.")
            names = "; ".join(self.by_gid[g]["canonical_name"]
                              for g in multi.get("candidates", []))
            note = f"MULTI: {multi['reason']}" + (f" Candidates: {names}." if names else "")
            return None, NO_COUNTERPART, round(best, 4), note

        note = (f"{len(above)} candidates above threshold — ambiguous, refused"
                if len(above) > 1 else
                f"no counterpart in the knowledge base (closest {best:.2f})")
        return None, NO_COUNTERPART, round(best, 4), note


# ---------------------------------------------------------------------- build
def build():
    matcher = Matcher()
    rows = defaultdict(list)
    for kind, vocab, term in collect_terms():
        ent, method, score, note = matcher.match(kind, term)
        rows[kind].append({
            "term_kind": kind,
            "source_vocab": vocab,
            "source_term": term,
            "normalised_term": normalise(term),
            "global_entity_id": ent["global_entity_id"] if ent else "",
            "entity_type": ent["entity_type"] if ent else "",
            "canonical_name": ent["canonical_name"] if ent else "",
            "match_method": method,
            "match_score": score,
            "notes": note,
        })
    for kind in rows:
        rows[kind].sort(key=lambda r: (r["match_method"] == NO_COUNTERPART,
                                       r["source_vocab"], r["normalised_term"]))
    return rows


HEADER = ["term_kind", "source_vocab", "source_term", "normalised_term",
          "global_entity_id", "entity_type", "canonical_name",
          "match_method", "match_score", "notes"]


def write(rows):
    written = []
    for kind, items in sorted(rows.items()):
        path = OUT / f"{kind}_crosswalk.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            w.writerows(items)
        written.append(path)
    return written


def summarise(rows):
    per_kind, methods = {}, defaultdict(int)
    for kind, items in sorted(rows.items()):
        resolved = [r for r in items if r["match_method"] != NO_COUNTERPART]
        by_method = defaultdict(int)
        for r in items:
            by_method[r["match_method"]] += 1
            methods[r["match_method"]] += 1
        per_kind[kind] = {
            "terms": len(items),
            "resolved": len(resolved),
            "no_counterpart": len(items) - len(resolved),
            "resolve_pct": round(100 * len(resolved) / len(items), 1) if items else 0.0,
            "target_entity_type": TARGET_TYPE[kind],
            "distinct_entities_referenced": len({r["global_entity_id"] for r in resolved}),
            "by_match_method": dict(sorted(by_method.items(), key=lambda kv: -kv[1])),
        }
    total = sum(len(v) for v in rows.values())
    resolved = sum(p["resolved"] for p in per_kind.values())

    # The onboarding rate is the number that matters: it is what a real user's
    # profile can actually join on.
    onboarding = [r for r in rows["skill"] if r["source_vocab"] == "onboarding"]
    on_resolved = [r for r in onboarding if r["match_method"] != NO_COUNTERPART]

    backlog, multi = defaultdict(list), defaultdict(list)
    for kind, items in rows.items():
        for r in items:
            if r["match_method"] != NO_COUNTERPART:
                continue
            (multi if r["notes"].startswith("MULTI:") else backlog)[kind].append(
                r["source_term"])
    return {
        "built_at": date.today().isoformat(),
        "fuzzy_threshold": FUZZY_THRESHOLD,
        "terms_total": total,
        "resolved_total": resolved,
        "no_counterpart_total": total - resolved,
        "resolve_pct_total": round(100 * resolved / total, 1) if total else 0.0,
        "onboarding_skill_terms": len(onboarding),
        "onboarding_skill_resolved": len(on_resolved),
        "onboarding_skill_resolve_pct": (
            round(100 * len(on_resolved) / len(onboarding), 1) if onboarding else 0.0),
        "by_kind": per_kind,
        "by_match_method": dict(sorted(methods.items(), key=lambda kv: -kv[1])),
        "collection_backlog": {k: sorted(set(v)) for k, v in sorted(backlog.items())},
        "multi_target_terms": {k: sorted(set(v)) for k, v in sorted(multi.items())},
    }


def report(summary):
    print("ValueWeave vocabulary crosswalk\n")
    print(f"  {'kind':<10} {'terms':>6} {'resolved':>9} {'gap':>5} {'rate':>7}   methods")
    print("  " + "-" * 74)
    for kind, p in summary["by_kind"].items():
        methods = ", ".join(f"{k} {v}" for k, v in p["by_match_method"].items()
                            if k != NO_COUNTERPART) or "—"
        print(f"  {kind:<10} {p['terms']:>6} {p['resolved']:>9} "
              f"{p['no_counterpart']:>5} {p['resolve_pct']:>6}%   {methods}")
    print("  " + "-" * 74)
    print(f"  {'TOTAL':<10} {summary['terms_total']:>6} {summary['resolved_total']:>9} "
          f"{summary['no_counterpart_total']:>5} {summary['resolve_pct_total']:>6}%")
    print(f"\n  onboarding skills specifically: "
          f"{summary['onboarding_skill_resolved']}/{summary['onboarding_skill_terms']} "
          f"({summary['onboarding_skill_resolve_pct']}%) — this is the rate a real "
          f"user's profile joins at")
    print(f"\n  unresolved, split by reason:")
    for kind in sorted(set(summary["collection_backlog"]) | set(summary["multi_target_terms"])):
        gap = len(summary["collection_backlog"].get(kind, []))
        mt = len(summary["multi_target_terms"].get(kind, []))
        print(f"    {kind:<10} {gap:>3} no researched counterpart   {mt:>3} span multiple entities")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="CI mode: rebuild and exit 1 if the committed files differ")
    args = ap.parse_args()

    rows = build()
    summary = summarise(rows)

    if args.check:
        drift = []
        for kind, items in sorted(rows.items()):
            path = OUT / f"{kind}_crosswalk.csv"
            if not path.exists():
                drift.append(f"{path.name} is missing")
                continue
            if read_csv(path) != [{k: str(v) for k, v in r.items()} for r in items]:
                drift.append(f"{path.name} differs from a fresh build")
        report(summary)
        if drift:
            print("\nDRIFT:")
            for d in drift:
                print(f"  {d}")
            print("\nRun without --check to regenerate.")
            sys.exit(1)
        print("\n  --check: committed crosswalks match a fresh build.")
        sys.exit(0)

    written = write(rows)
    (OUT / "crosswalk_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    report(summary)
    print()
    for p in written:
        print(f"  wrote {p.relative_to(ROOT)}")
    print(f"  wrote {(OUT / 'crosswalk_summary.json').relative_to(ROOT)}")
