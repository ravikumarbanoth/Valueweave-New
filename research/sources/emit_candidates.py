#!/usr/bin/env python3
"""
Turn the Electrician & Allied Trades document into review candidates.

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
Only the SEVEN roles with no Skill entity in the graph. The other thirteen
already exist, and re-proposing them would put thirteen rows in front of a
reviewer whose correct decision on every one of them is "we have this" — the
exact queue-fatigue failure the review design exists to prevent. Those thirteen
produce an enrichment report instead (see docs/TRADE_ENRICHMENT_REPORT.md).

Run:
    python3 -m research.sources.emit_candidates            # dry, prints
    python3 -m research.sources.emit_candidates --write    # merges into the queue
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from collection import review                                     # noqa: E402
from research.sources.electrician_trades_2026 import (            # noqa: E402
    SOURCE, new_roles)

#: The document is one file, read once. `item_key` is the role slug, so a
#: second run over a corrected document reopens the same candidate rather than
#: creating a duplicate — the same identity rule every feed uses.
SOURCE_ID = SOURCE["source_id"]


def candidates():
    """One candidate per role the graph does not already hold."""
    out = []
    for role in new_roles():
        aliases = ", ".join(role["aliases"][:4])
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
                f"a trade with no Skill entity in the graph; "
                f"also known as {aliases}"),
            is_entity=True,
            state=review.NEEDS_REVIEW,
            #: The raw record a reviewer reads before deciding. The whole role
            #: as extracted, so the decision is made against what the source
            #: said rather than against this script's summary of it.
            raw={
                "title": role["title"],
                "aliases": role["aliases"],
                "industries": role["industries"],
                "nature_of_work": role["nature"],
                "future_demand": role["future_demand"],
                "automation_risk": role["automation_risk"],
                "entrepreneurship": role["entrepreneurship"],
                "tools": role["tools"],
                "skills_beginner": role["skills_beginner"],
                "skills_intermediate": role["skills_intermediate"],
                "skills_advanced": role["skills_advanced"],
                "future_technologies": role["future_tech"],
                "career_ladder": role["ladder"],
                "related_careers": role["relates"],
                "licence": role["licence"] or "none stated",
                "confidence": role["confidence"],
                "_source": SOURCE["origin"],
                "_source_limits": SOURCE["self_declared_limits"],
                "_reviewer_note": (
                    "Salary, course fees and institute contacts from this "
                    "document are NOT included: it states its contacts are "
                    "XXXX placeholders and its salary figures are estimates. "
                    "Research those against a primary source before promoting."),
            },
        ))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="emit_candidates", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="merge into collection/state/review_queue.jsonl")
    args = ap.parse_args(argv)

    incoming = candidates()
    existing = review.load()
    merged, stats = review.merge(existing, incoming)

    print(f"  {SOURCE['title']}")
    print(f"  {len(incoming)} candidate(s) — the roles with no Skill entity\n")
    for c in incoming:
        print(f"    {c.candidate_id}")
        print(f"      {c.title:34} {c.classified_reason[:72]}")
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
