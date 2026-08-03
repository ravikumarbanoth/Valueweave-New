#!/usr/bin/env python3
"""
Other names the researched entities already answer to.

WHY THIS IS GENERATED AND NOT WRITTEN
-------------------------------------
The concept table in frontend/lib/search/vocabulary/concepts.js is curated,
because "what a person means by 'dairy'" is a judgement. This file is not a
judgement. Every string it emits is already sitting in a package dataset,
in a column whose whole purpose is to hold an alternative name:

    government_schemes.csv          short_name
        "Prime Minister's Employment Generation Programme"  ->  "PMEGP"
        40 schemes, every one of them with the abbreviation people actually
        type, already collected and already verified.

    china_inspired_adapted_opportunities.csv  original_china_concept
        "Telangana Homestays / Andhra Pradesh ... "  ->  "Courtyard Guesthouse"
        The nine opportunities Package004 adapted from Chinese models. The
        Chinese concept is why the row exists and appears nowhere in its name.

    category / sub_category / category_name
        The taxonomy the researchers filed each row under. Searching
        "Construction & Skilled Trades" should return the eleven trades in it,
        and before this it returned only the Industry entity of that name.

Hand-copying any of that would be a second copy to go stale. This reads the
packages and writes one module; `--check` fails if the module has drifted, so
a package release that adds a scheme cannot leave search behind.

    python3 scripts/build_search_aliases.py            # rebuild
    python3 scripts/build_search_aliases.py --check    # CI: exit 1 on drift

WHAT IT DOES NOT DO
-------------------
It does not invent, translate, or infer. If a column is empty the entity gets
no alias. The output is a strict subset of what the packages already say.
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
ENTITIES = ROOT / "knowledge_graph" / "entities" / "entities.csv"
OUT = ROOT / "frontend" / "lib" / "search" / "vocabulary" / "entity_aliases.js"

#: Columns that hold an alternative NAME for the row they sit on. Everything
#: else in a dataset is a fact about the row, not another way to say it, and
#: indexing facts as names is how a search box starts returning "Warangal" for
#: "12000" because that is the district's area.
ALIAS_COLUMNS = {
    "short_name": "short name",
    "original_china_concept": "China-inspired",
    "category": "category",
    "category_name": "category",
    "sub_category": "category",
}

#: The column each dataset keys on, matching knowledge_sync/config.py. A row
#: joins to an entity through `package_local_id`, so the wrong key column
#: silently produces zero aliases rather than wrong ones.
ID_COLUMNS = ("scheme_id", "skill_id", "business_id", "id", "dist_id",
              "crop_id", "category_id", "machinery_id", "provider_id")

MIN_ALIAS = 3
MAX_ALIAS = 60

#: A category shared by more than this share of a dataset's rows tells a reader
#: nothing and, as a search alias, actively misleads: it makes every row in the
#: dataset answer to a word that describes almost none of them.
#:
#: This is not a hypothetical. Package006's skills.csv files 42 of its 45 skills
#: — Python Programming, Full Stack Web Development, Electrician — under
#: "Soft Skills & Communication", all sharing one category_id. Importing that
#: would have made a search for "communication" return Python Programming, with
#: the platform's own badge on it.
#:
#: The threshold is a filter on THIS output, not a fix. The underlying rows are
#: research data; correcting them is the research team's call and is reported
#: rather than performed here. See docs/SEARCH_ARCHITECTURE.md.
CATEGORY_SHARE_LIMIT = 0.4


def entities_by_local_id():
    with open(ENTITIES, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    index = defaultdict(list)
    for row in rows:
        if row["package_local_id"]:
            index[row["package_local_id"]].append(row)
    return index


def normalise(text):
    return " ".join(str(text or "").split()).strip()


def uninformative(rows, column):
    """Values of `column` so dominant in `rows` that they distinguish nothing.

    A column with ONE value throughout is not a defect — it is a scoped
    dataset. construction_skilled_trade_services.csv is entirely construction,
    and "Construction & Skilled Trades" is a genuinely useful alias for all
    eleven trades in it. The defect shape is a column that HAS categories and
    does not apply them: skills.csv offers four and puts 42 of 45 rows in one.
    """
    counts = Counter(normalise(r.get(column)) for r in rows)
    counts.pop("", None)
    if len(counts) < 2:
        return set()
    total = sum(counts.values())
    return {value for value, n in counts.items() if n / total > CATEGORY_SHARE_LIMIT}


def collect():
    index = entities_by_local_id()
    # entity id -> {alias -> kind}, so the same string arriving from two
    # columns is one alias and keeps the first kind that named it.
    aliases = defaultdict(dict)
    hits = defaultdict(int)
    skipped = []

    for path in sorted(PACKAGES.glob("*/datasets/*.csv")):
        with open(path, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
            columns = list(rows[0].keys()) if rows else []
            key = next((c for c in ID_COLUMNS if c in columns), None)
            present = {c: ALIAS_COLUMNS[c] for c in columns if c in ALIAS_COLUMNS}
            if not key or not present:
                continue
            # Only categories are checked. A short_name shared by every row
            # would be a different and much louder kind of broken.
            blocked = set()
            for column, kind in present.items():
                if kind != "category":
                    continue
                for value in uninformative(rows, column):
                    blocked.add(value)
                    skipped.append(f"{path.name}:{column} = {value!r}")
            for row in rows:
                targets = index.get(normalise(row.get(key)), [])
                if not targets:
                    continue
                for column, kind in present.items():
                    value = normalise(row.get(column))
                    if not (MIN_ALIAS <= len(value) <= MAX_ALIAS) or value in blocked:
                        continue
                    for entity in targets:
                        # An alias identical to the name teaches the ranker
                        # nothing and costs it a comparison per query.
                        if value.lower() == entity["canonical_name"].lower():
                            continue
                        if value not in aliases[entity["global_entity_id"]]:
                            aliases[entity["global_entity_id"]][value] = kind
                            hits[f"{path.name}:{column}"] += 1
    return aliases, hits, sorted(set(skipped))


def render(aliases):
    payload = {eid: sorted(names) for eid, names in sorted(aliases.items()) if names}
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    return f"""// GENERATED — do not edit. `python3 scripts/build_search_aliases.py`
//
// Other names the researched entities already answer to, lifted verbatim from
// the columns in packages/*/datasets that exist to hold them: a scheme's
// short_name, the original_china_concept a business was adapted from, the
// category a row was filed under.
//
// Nothing here is invented or translated. Curated meaning lives next door in
// concepts.js; this file only repeats what the packages already say, so that
// a release which adds a scheme does not leave its abbreviation unsearchable.
//
// {len(payload)} entities carry at least one alias.

export default Object.freeze({body});
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed file differs from a fresh build")
    args = ap.parse_args(argv)

    aliases, hits, skipped = collect()
    rendered = render(aliases)

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != rendered:
            print("search aliases are stale — run scripts/build_search_aliases.py",
                  file=sys.stderr)
            return 1
        print(f"search aliases up to date: {len(aliases)} entities")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    total = sum(len(v) for v in aliases.values())
    print(f"wrote {OUT.relative_to(ROOT)}: {total} aliases over {len(aliases)} entities")
    for source, count in sorted(hits.items(), key=lambda kv: -kv[1]):
        print(f"  {count:5d}  {source}")
    for note in skipped:
        print(f"  SKIPPED (>{CATEGORY_SHARE_LIMIT:.0%} of a dataset that has other "
              f"categories — a data defect, reported not fixed): {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
