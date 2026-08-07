#!/usr/bin/env python3
"""
Turn a supplied research document into review candidates.

WHY CANDIDATES AND NOT PACKAGE ROWS
-----------------------------------
Everything this document says that is a claim about the world — that a Lift
Technician earns ₹15,000–22,000, that Don Bosco Tech runs a three-month course,
that Otis hires in Hyderabad — is an LLM's estimate. The document says so
itself. `packages/` is published knowledge, so none of it may go there until a
person has checked it.

The collection framework already has exactly this pipeline: a source produces
candidates, `collection.cli queue` shows them, a named person runs
`review`/`approve`, and only then does `promote` write a package row. This
script is the source. It writes nothing but the queue.

WHAT BECOMES A CANDIDATE AND WHAT DOES NOT
-------------------------------------------
Only roles with no Skill entity in the graph. A role that already exists is not
re-proposed: putting a dozen rows in front of a reviewer whose correct decision
on every one is "we have this" is the queue-fatigue failure the review design
exists to prevent. Those produce an enrichment report instead — see
docs/TRADE_ENRICHMENT_REPORT.md.

Run:
    python3 -m research.sources.emit_candidates                     # all, dry
    python3 -m research.sources.emit_candidates --doc construction  # one
    python3 -m research.sources.emit_candidates --write             # merge in
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from collection import review                                     # noqa: E402
from research.sources import (                                    # noqa: E402
    automobile_trades_2026, construction_trades_2026,
    electrician_trades_2026, electronics_trades_2026,
    manufacturing_trades_2026)

#: Each document is one file, read once. `item_key` is the role slug and the
#: candidate id is prefixed by the document, so a second run over a corrected
#: document reopens the same candidates rather than creating duplicates — the
#: same identity rule every feed uses.
DOCUMENTS = {
    "electrician": electrician_trades_2026,
    "construction": construction_trades_2026,
    "manufacturing": manufacturing_trades_2026,
    "automobile": automobile_trades_2026,
    "electronics": electronics_trades_2026,
}


def candidates(module):
    """One candidate per role the graph does not already hold."""
    SOURCE = module.SOURCE
    SOURCE_ID = SOURCE["source_id"]
    out = []
    pairings = (module.businesses_without_a_skill()
                if hasattr(module, "businesses_without_a_skill") else {})

    #: The reviewer note quotes THIS document's own declared limits rather
    #: than a stock sentence. An earlier version branched on whether the list
    #: was empty and then hard-coded the ELECTRICIAN document's caveat for
    #: every document that had one — so the manufacturing candidates claimed
    #: their contacts were `XXXX` placeholders, which is the one thing that
    #: document does not do. Reading the field is the only way the note can
    #: stay true as documents are added.
    limits = SOURCE["self_declared_limits"]
    note = ("Salary, course fees and institute contacts are NOT included. "
            + ("This document says of itself: " + "; ".join(limits) + "."
               if limits else
               "This document declares no limits on itself, but its salary "
               "tables are uncited all the same — absence of a caveat is not "
               "evidence of accuracy.")
            + " Research those against a primary source before promoting.")

    for role in module.new_roles():
        aliases = ", ".join(role["aliases"][:4])
        business = pairings.get(role["slug"])
        out.append(review.Candidate(
            candidate_id=f"{SOURCE_ID}:{role['slug']}",
            source_id=SOURCE_ID,
            source_name=SOURCE["title"],
            item_key=role["slug"],
            title=role["title"],
            #: No URL. The document is a supplied file, not a fetched page, and
            #: inventing a link would be the one thing this whole pipeline is
            #: built to prevent.
            url="",
            published_at=SOURCE["retrieved"],
            change="NEW",
            classified_as="Skill",
            classified_reason=(
                (f"the graph offers “{business}” as a business but cannot "
                 f"teach the trade; also known as {aliases}") if business else
                (f"a trade with no Skill entity in the graph; "
                 f"also known as {aliases}")),
            is_entity=True,
            state=review.NEEDS_REVIEW,
            #: The raw record a reviewer reads before deciding. The whole role
            #: as extracted, so the decision is made against what the source
            #: said rather than against this script's summary of it.
            #: `.get` throughout: the two documents cover different ground and
            #: neither is padded to match the other. The electrician dataset
            #: has three skill tiers and a career ladder; the construction one
            #: has a business pairing. A key absent from a raw record means the
            #: source did not say, which is exactly what a reviewer needs to
            #: know — and is different from the source saying "none".
            raw={k: v for k, v in {
                "title": role["title"],
                "aliases": role["aliases"],
                "industries": role.get("industries"),
                "nature_of_work": role.get("nature"),
                "future_demand": role.get("future_demand"),
                "automation_risk": role.get("automation_risk"),
                "entrepreneurship": role.get("entrepreneurship"),
                "tools": role.get("tools"),
                "skills_beginner": role.get("skills_beginner"),
                "skills_intermediate": role.get("skills_intermediate"),
                "skills_advanced": role.get("skills_advanced"),
                "future_technologies": role.get("future_tech"),
                "career_ladder": role.get("ladder"),
                "related_careers": role.get("relates"),
                "licence": role.get("licence") or None,
                "existing_business": business,
                "source_defect": role.get("notes") or None,
                "confidence": role["confidence"],
                "_source": SOURCE["origin"],
                "_source_limits": SOURCE["self_declared_limits"] or
                                  ["none declared by the document — see the "
                                   "source module for why that is not reassuring"],
                "_reviewer_note": note,
            }.items() if v not in (None, [], "")},
        ))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="emit_candidates", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", choices=sorted(DOCUMENTS),
                    help="one document; default is all of them")
    ap.add_argument("--write", action="store_true",
                    help="merge into collection/state/review_queue.jsonl")
    args = ap.parse_args(argv)

    chosen = [args.doc] if args.doc else sorted(DOCUMENTS)
    incoming = []
    for name in chosen:
        module = DOCUMENTS[name]
        rows = candidates(module)
        incoming.extend(rows)
        print(f"\n  {module.SOURCE['title'][:78]}")
        print(f"  {len(rows)} candidate(s) — roles with no Skill entity\n")
        for c in rows:
            print(f"    {c.title:36} {c.classified_reason[:74]}")

    existing = review.load()
    merged, stats = review.merge(existing, incoming)
    print(f"\n  queue: +{stats.get('added', 0)} new · "
          f"{stats.get('reopened', 0)} reopened · "
          f"{stats.get('kept_decided', 0)} already decided")

    if args.write:
        review.save(merged)
        print(f"\n  written. {len(merged)} candidates in the queue.")
        print("  Next:  python3 -m collection.cli queue")
        print("         python3 -m collection.cli review <candidate_id> "
              "--actor NAME --evidence URL")
    else:
        print("\n  DRY RUN — nothing written. Pass --write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
