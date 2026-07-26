#!/usr/bin/env python3
"""
ValueWeave Search — command line interface (Work Package 4)

    python3 -m search.cli "turmeric"
    python3 -m search.cli "PM-KISAN" --scope entity --scope alias
    python3 -m search.cli "python" --mode EXACT --mode PREFIX
    python3 -m search.cli "manufactring" --fuzzy-threshold 0.5
    python3 -m search.cli "millet" --type Crop --json
    python3 -m search.cli --stats
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from search.engine import SearchEngine          # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(prog="search", description="Search the ValueWeave knowledge graph")
    ap.add_argument("query", nargs="?", help="what to search for")
    ap.add_argument("--scope", action="append", dest="scopes",
                    help="entity | alias | relationship | package | dataset (repeatable)")
    ap.add_argument("--mode", action="append", dest="modes",
                    help="EXACT | PREFIX | ALIAS | FUZZY (repeatable)")
    ap.add_argument("--type", dest="entity_type", help="restrict to one entity or relationship type")
    ap.add_argument("--package", dest="source_package", help="restrict to one source package")
    ap.add_argument("--min-confidence", type=int, default=0)
    ap.add_argument("--fuzzy-threshold", type=float, default=None)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--suggest", action="store_true", help="type-ahead: no fuzzy matching")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--stats", action="store_true", help="print index statistics and exit")
    args = ap.parse_args(argv)

    engine = SearchEngine()

    if args.stats:
        print(json.dumps(engine.stats(), indent=2))
        return 0

    if not args.query:
        ap.error("a query is required unless --stats is given")

    try:
        if args.suggest:
            results = engine.suggest(args.query, scopes=args.scopes or "entity",
                                     limit=args.limit)
        else:
            results = engine.search(
                args.query, scopes=args.scopes, modes=args.modes,
                entity_type=args.entity_type, source_package=args.source_package,
                min_confidence=args.min_confidence, limit=args.limit,
                fuzzy_threshold=args.fuzzy_threshold)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return 0

    if not results:
        print(f"no results for {args.query!r}")
        return 1

    print(f"{len(results)} result(s) for {args.query!r}\n")
    for r in results:
        d = r.document
        conf = f"{d.confidence:>2}" if d.confidence else " -"
        print(f"  [{r.match_mode.value:<6} {r.score:.2f}] [{conf}] {d.scope:<12} {d.title[:58]}")
        detail = d.entity_id or d.doc_id
        print(f"                            {detail}  ({r.matched_on})")
    # Every row in this knowledge base is VST-NEEDS_REVIEW. Saying so on every
    # search is the point, not decoration.
    unverified = sum(1 for r in results if r.document.verification_status == "VST-NEEDS_REVIEW")
    if unverified:
        print(f"\n  {unverified}/{len(results)} results are VST-NEEDS_REVIEW "
              f"(no human data-steward review)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
