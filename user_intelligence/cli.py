#!/usr/bin/env python3
"""
User Intelligence Engine — command line.

    python3 -m user_intelligence capabilities
    python3 -m user_intelligence run --fixture resolving
    python3 -m user_intelligence run --fixture resolving --explain
    python3 -m user_intelligence run --fixture unresolvable --table user_skill_profile
    python3 -m user_intelligence run --profile-json path/to/profile.json
    python3 -m user_intelligence rules

No Supabase credentials are needed for any of this: the engine reads the Git
knowledge artifacts, and profiles are supplied as fixtures or as JSON.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from user_intelligence import RULES_VERSION, __version__            # noqa: E402
from user_intelligence import fixtures                              # noqa: E402
from user_intelligence.config import (RECOMMENDATION_CATEGORIES,    # noqa: E402
                                      SCORES)
from user_intelligence.context import UserContext, from_supabase_rows  # noqa: E402
from user_intelligence.engine import IntelligenceEngine             # noqa: E402


def cmd_capabilities(args):
    caps = IntelligenceEngine().capabilities()
    if args.json:
        print(json.dumps(caps, indent=2))
        return 0
    print(f"User Intelligence Engine {caps['engine_version']} "
          f"(rules {caps['rules_version']})\n")
    k = caps["knowledge"]
    print(f"  knowledge: {k['entities']} entities, {k['edges']} edges, "
          f"snapshot {k['snapshot_hash']}")
    print(f"  crosswalk resolved: {k['crosswalk_resolved']}")
    print(f"  crosswalk no-counterpart: {k['crosswalk_no_counterpart']}")

    print(f"\n  scores ({len(caps['scores'])}):")
    for s in caps["scores"]:
        flag = f"  BLOCKED by {', '.join(s['blocked_by'])}" if s["blocked_by"] else ""
        print(f"    {s['key']:<22} {len(s['rules'])} rule(s){flag}")

    print(f"\n  recommendation categories ({len(caps['categories'])}):")
    for c in caps["categories"]:
        if not c["has_data"]:
            print(f"    {c['key']:<22} NO DATA — {c['no_data_reason'][:64]}...")
        elif c["sparse_note"]:
            print(f"    {c['key']:<22} sparse — {c['sparse_note'][:64]}...")
        else:
            print(f"    {c['key']:<22} ok")

    if caps["unavailable_inputs"]:
        print(f"\n  inputs the brief names that do not exist:")
        for name, detail in caps["unavailable_inputs"].items():
            print(f"    {name:<22} {detail[:70]}")
    return 0


def cmd_rules(args):
    print(f"rules version {RULES_VERSION}\n")
    print("SCORES")
    for s in SCORES:
        print(f"\n  {s.key}  —  {s.label}")
        print(f"    {s.description}")
        print(f"    requires: {', '.join(s.requires)}")
        for r in s.rules:
            print(f"      {r}")
    print("\n\nRECOMMENDATION CATEGORIES")
    for c in RECOMMENDATION_CATEGORIES:
        print(f"\n  {c.key}  —  {c.label}")
        if c.no_data_reason:
            print(f"    NO DATA SOURCE: {c.no_data_reason}")
            continue
        print(f"    sources: {', '.join(c.sources) or '(caller-supplied)'}")
        for r in c.rules:
            print(f"      {r}")
        if c.sparse_note:
            print(f"    sparse: {c.sparse_note}")
    return 0


def _load_context(args):
    if args.profile_json:
        data = json.loads(Path(args.profile_json).read_text(encoding="utf-8"))
        if "profile" in data:
            return from_supabase_rows(
                data["profile"], collaborator=data.get("collaborator_profile"),
                connections=data.get("connections", ()),
                peers=data.get("peers", ()),
                opportunities=data.get("opportunities", ()))
        return from_supabase_rows(data)
    return fixtures.ALL[args.fixture]()


def cmd_run(args):
    ctx = _load_context(args)
    engine = IntelligenceEngine()
    result = engine.run(
        ctx,
        articles=fixtures.research_articles() if args.fixture else (),
        candidates=fixtures.candidate_profiles() if args.fixture else ())

    if args.explain:
        print(result.explain(args.score))
        return 0

    tables = result.tables()
    if args.table:
        print(json.dumps(tables[args.table], indent=2, default=str))
        return 0
    if args.json:
        print(json.dumps(tables, indent=2, default=str))
        return 0

    summary = tables["user_activity_summary"]
    print(f"user {ctx.user_id}  ·  result {summary['result_hash']}  ·  "
          f"snapshot {summary['knowledge_snapshot_hash']}\n")
    print("  scores")
    for key, s in summary["scores"].items():
        value = "   n/a" if s["score"] is None else f"{s['score']:6.1f}"
        print(f"    {value}  conf {s['confidence']:>3}  {key:<22} [{s['status']}]")
    print(f"\n  recommendations ({summary['total_recommendations']} total)")
    for key, c in summary["recommendations_by_category"].items():
        note = f"  — {c['note'][:58]}" if c["note"] else ""
        print(f"    {c['count']:>3}  {key:<22} [{c['status']}]{note}")
    if summary["scores_unavailable"]:
        print(f"\n  scores unavailable: {', '.join(summary['scores_unavailable'])}")
    if summary["categories_without_data"]:
        print(f"  categories without data: "
              f"{', '.join(summary['categories_without_data'])}")
    if summary["inputs_unavailable"]:
        print(f"  inputs unavailable: {', '.join(summary['inputs_unavailable'])}")
    return 0


def cmd_write(args):
    """
    Compute intelligence and write it to the `user_intelligence` schema.

    The step deployment preparation named blocker B3: the engine had always
    produced correct rows and nothing put them in a database. `--target memory`
    is the default so that a mistyped command computes and reports rather than
    writing somewhere unintended.
    """
    from user_intelligence.writer import (IntelligenceWriter, WriterError,  # noqa: PLC0415
                                          make_target)
    try:
        target = make_target(args.target)
    except WriterError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    engine = IntelligenceEngine()
    writer = IntelligenceWriter(engine, target, force=args.force)

    if args.users_json:
        payload = json.loads(Path(args.users_json).read_text(encoding="utf-8"))
        users = payload if isinstance(payload, list) else payload.get("users", [])
        contexts = [_context_from_payload(u) for u in users]
    else:
        contexts = [_load_context(args)]

    run = writer.write_many(contexts, stop_after_failures=args.stop_after_failures)

    if args.json:
        print(json.dumps(run.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"\n  target: {type(target).__name__}  rules {RULES_VERSION}")
        print(f"  {run.summary()}\n")
        for failure in run.as_dict()["failures"]:
            print(f"  FAILED {failure['user_id']}: {failure['error']}",
                  file=sys.stderr)
    return 0 if run.ok else 1


def _context_from_payload(entry):
    """One entry of --users-json. Same shape --profile-json accepts, per user."""
    if "profile" in entry:
        return from_supabase_rows(
            entry["profile"], collaborator=entry.get("collaborator_profile"),
            connections=entry.get("connections", ()),
            peers=entry.get("peers", ()),
            opportunities=entry.get("opportunities", ()))
    return from_supabase_rows(entry)


def build_parser():
    ap = argparse.ArgumentParser(prog="user_intelligence",
                                 description="Rule-based user intelligence engine")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("capabilities",
                   help="what the engine can and cannot do, computed from config"
                   ).set_defaults(fn=cmd_capabilities)
    sub.add_parser("rules", help="every rule, by score and category").set_defaults(
        fn=cmd_rules)

    r = sub.add_parser("run", help="compute intelligence for one user")
    r.add_argument("--fixture", choices=sorted(fixtures.ALL), default="resolving")
    r.add_argument("--profile-json", help="a JSON file of Supabase rows")
    r.add_argument("--table", choices=("user_skill_profile", "user_business_profile",
                                       "user_learning_profile",
                                       "user_recommendations",
                                       "user_activity_summary"))
    r.add_argument("--explain", action="store_true", help="rule-by-rule trace")
    r.add_argument("--score", help="limit --explain to one score key")
    r.set_defaults(fn=cmd_run)

    w = sub.add_parser("write",
                       help="compute and WRITE to the user_intelligence schema")
    w.add_argument("--target", choices=("memory", "supabase"), default="memory",
                   help="memory needs no credentials (default)")
    w.add_argument("--fixture", choices=sorted(fixtures.ALL), default="resolving")
    w.add_argument("--profile-json", help="a JSON file of Supabase rows, one user")
    w.add_argument("--users-json",
                   help="a JSON array (or {\"users\": [...]}) for a batch")
    w.add_argument("--force", action="store_true",
                   help="write even when the result hash is unchanged")
    w.add_argument("--stop-after-failures", type=int, default=None,
                   help="abort the batch once this many users have failed")
    w.set_defaults(fn=cmd_write)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
