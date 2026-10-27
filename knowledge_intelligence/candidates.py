#!/usr/bin/env python3
"""
Knowledge gaps as research candidates, through the existing review queue.

NO PARALLEL APPROVAL SYSTEM
----------------------------
These are `collection.review.Candidate` rows, written by `review.merge`/`save`,
shown by `collection.cli queue`, decided by `collection.cli
review/approve/reject` with a named actor. Same identity rule, same states,
same ledger. This module is a SOURCE, exactly like the six research documents;
it just derives its rows from our own graph instead of a PDF.

WHY ONLY A SLICE, AND NOT ALL 45
---------------------------------
Every one of the 45 Skill entities is missing something — certification on all
45, district on all 45, training on 42. Queueing 45 rows would be the
queue-fatigue failure `emit_candidates` already names: a reviewer whose correct
decision on most rows is "yes, we know" stops reading the ones that matter.

So the filter is the sharpest form of the problem, and it is a rule rather
than a hand-picked list. A skill qualifies when all three hold:

  1. a BusinessOpportunity or MSME in the graph REQUIRES it — the platform is
     already telling somebody they could run this business;
  2. it has no training and no certification edge — so it cannot say where to
     learn it or what credential proves it;
  3. the concept table points at it — so people reach it by trade words, in
     English or Telugu, and arrive at that hole on purpose.

That is the platform recommending a livelihood it cannot teach, to a reader who
searched for it in their own language. It is worth somebody's afternoon. "We
have no district edge on Python Programming" is not.

WHAT A GAP CANDIDATE IS NOT
----------------------------
Not knowledge, and not a proposed entity. `classified_as` is `KnowledgeGap`,
deliberately NOT one of the four types `collection/decide.py` can promote — so
even a human who approves one cannot accidentally turn it into a package row.
Approving it means "yes, research this", and the research comes back through
the normal document route and is reviewed again there.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collection import review                                     # noqa: E402
from knowledge_intelligence import RESEARCH_REQUIRED              # noqa: E402
from knowledge_intelligence import profiles as P                  # noqa: E402

SOURCE_ID = "kg-gap-skills"
SOURCE_NAME = "ValueWeave knowledge-gap detection (derived from the live graph)"

#: Intentionally absent from collection/decide.py's TARGETS. A gap must not be
#: promotable into a package row under any circumstances.
GAP_TYPE = "KnowledgeGap"

#: Gaps worth a research task. `district` and `machinery` are excluded on
#: purpose — see the module docstring.
REPORTED = ("training", "certification")


def actionable(profiles=None):
    """Skills the platform recommends as a livelihood and cannot teach."""
    profiles = P.build(("Skill",)) if profiles is None else profiles
    aliases = P.load_aliases()
    out = []
    for profile in profiles:
        if not profile["dimensions"].get("business"):
            continue
        if profile["dimensions"].get("training") or \
           profile["dimensions"].get("certification"):
            continue
        if not aliases.get(profile["entity"].lower()):
            continue                      # not reachable by trade vocabulary
        out.append(profile)
    return out


def candidates(profiles=None):
    rows = []
    for profile in actionable(profiles):
        businesses = [d["entity"] for d in profile["dimensions"]["business"]]
        missing = [d for d in REPORTED if d in profile["missing"]]
        slug = profile["entity_id"].split(":")[-1]
        rows.append(review.Candidate(
            candidate_id=f"{SOURCE_ID}:{slug}",
            source_id=SOURCE_ID,
            source_name=SOURCE_NAME,
            item_key=slug,
            title=f"Knowledge gap: {profile['entity']}",
            url="",
            published_at="",
            change="NEW",
            classified_as=GAP_TYPE,
            classified_reason=(
                f"the graph recommends “{businesses[0]}” which requires this "
                f"skill, and holds no {' or '.join(missing)} for it"),
            #: Not an entity. `is_entity` is what tells the promoter whether a
            #: row could ever become one, and this never can.
            is_entity=False,
            state=review.NEEDS_REVIEW,
            raw={
                "entity": profile["entity"],
                "entity_id": profile["entity_id"],
                "missing": missing,
                "have": [d for d in P.GAP_DIMENSIONS if d not in profile["missing"]],
                "recommended_businesses": businesses,
                "reachable_by_vocabulary": True,
                "status": RESEARCH_REQUIRED,
                "_source": "derived from knowledge_graph/ — no external claim",
                "_reviewer_note": (
                    "This is a RESEARCH TASK, not a proposed entity. Approving "
                    "it means 'yes, go and find the training and certification "
                    "for this trade'; the findings come back through the normal "
                    "document route and are reviewed again there. It carries no "
                    "salary, fee, contact, provider or demand claim and must "
                    "never acquire one here."),
            },
        ))
    return rows


def main(argv=None):
    import argparse                                               # noqa: PLC0415
    ap = argparse.ArgumentParser(prog="knowledge_intelligence.candidates",
                                 description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="merge into collection/state/review_queue.jsonl")
    args = ap.parse_args(argv)

    rows = candidates()
    print(f"\n  {SOURCE_NAME}")
    print(f"  {len(rows)} knowledge gap(s) worth a research task\n")
    for c in rows:
        print(f"    {c.title[:46]:48} {c.classified_reason[:70]}")

    merged, stats = review.merge(review.load(), rows)
    print(f"\n  queue: +{stats.get('added', 0)} new · "
          f"{stats.get('reopened', 0)} reopened · "
          f"{stats.get('kept_decided', 0)} already decided")
    if args.write:
        review.save(merged)
        print(f"\n  written. {len(merged)} candidates in the queue.")
    else:
        print("\n  DRY RUN — nothing written. Pass --write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
