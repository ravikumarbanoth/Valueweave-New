#!/usr/bin/env python3
"""
ValueWeave collection — command line.

    python3 -m collection.cli sources                    what we monitor, and its state
    python3 -m collection.cli run                        a dry run: report only
    python3 -m collection.cli run --write                write the queue and state
    python3 -m collection.cli run --only fix-rss-001 --force
    python3 -m collection.cli verify pib-msme-001        prove a candidate URL is reachable
    python3 -m collection.cli queue                      what is waiting for a person
    python3 -m collection.cli health                     dashboard-ready metrics
    python3 -m collection.cli backlog --events x.json    topics people wanted and we lack

`run` is a DRY RUN by default, like every other write path in this repository
(knowledge_sync, stewardship apply, the health check). Collecting is cheap and
reversible; writing a queue that a person will then read is not, and the default
should be the one that cannot surprise anybody.

Nothing here can publish. `verify` does not edit the registry — it prints the
edit to make, because activating a source is a decision that belongs in a pull
request where somebody can see it.
"""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collection import backlog as backlog_module              # noqa: E402
from collection import monitor, registry, review, runner      # noqa: E402

RUN_LOG = Path(__file__).resolve().parent / "state" / "last_run.json"


def _emit(payload, as_json):
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        return True
    return False


def cmd_sources(args):
    sources = registry.load()
    if args.category:
        sources = [s for s in sources if s.category.lower() == args.category.lower()]
    if _emit([s.to_dict() for s in sources], args.json):
        return 0

    print(f"{'source_id':<20} {'status':<22} {'type':<10} {'freq':<10} "
          f"{'rel':>3}  {'last ok':<21} name")
    print("-" * 118)
    for s in sources:
        print(f"{s.source_id:<20} {s.status:<22} {s.source_type:<10} {s.frequency:<10} "
              f"{s.reliability:>3}  {(s.fetch.last_ok or '—'):<21} {s.name[:40]}")
    active = sum(1 for s in sources if s.status == "ACTIVE")
    pending = sum(1 for s in sources if s.status == "PENDING_VERIFICATION")
    print(f"\n  {len(sources)} sources · {active} active · {pending} awaiting verification")
    if pending:
        print("  A PENDING_VERIFICATION source is never fetched on schedule. "
              "Run `verify <id>` from a network that can reach it.")
    return 0


def cmd_run(args):
    report = runner.run(only=args.only, force=args.force, write=args.write)
    payload = report.as_dict()

    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    if args.write:
        RUN_LOG.write_text(json.dumps(payload, indent=2, default=str) + "\n",
                           encoding="utf-8")

    if _emit(payload, args.json):
        return 2 if report.failed else 0

    if not report.sources:
        print("nothing was due. --force checks every active source regardless of schedule.")
        return 0

    print(f"{'source_id':<20} {'status':<14} {'recs':>5} {'new':>4} {'upd':>4} "
          f"{'dup':>4} {'queued':>7}  classified")
    print("-" * 100)
    for s in report.sources:
        changes = s.changes or {}
        classified = ", ".join(f"{k}×{v}" for k, v in list((s.classified or {}).items())[:3])
        print(f"{s.source_id:<20} {s.status:<14} {s.records:>5} "
              f"{changes.get('new', 0):>4} {changes.get('updated', 0):>4} "
              f"{(s.duplicates or {}).get('duplicates', 0):>4} {s.queued:>7}  "
              f"{classified or '—'}")
        if s.error:
            print(f"{'':<20} └─ {s.error[:90]}")

    merged = report.merged
    print(f"\n  queue: +{merged.get('added', 0)} new · "
          f"{merged.get('reopened', 0)} reopened · "
          f"{merged.get('kept_decided', 0)} already decided · "
          f"{merged.get('promoted_to_review', 0)} moved to NEEDS_REVIEW")
    print(f"  {report.queue.get('total', 0)} candidates total — "
          f"{report.queue.get('by_state', {})}")
    if report.dry_run:
        print("\n  DRY RUN — nothing was written. Pass --write to record the queue and state.")
    return 2 if report.failed else 0


def cmd_verify(args):
    """Fetch a source once, ignoring its schedule and its status.

    The only command that will touch a PENDING_VERIFICATION source, and it
    reports rather than edits: activating a feed is a change to a
    human-authored file and belongs in a diff somebody approves.
    """
    sources = {s.source_id: s for s in registry.load()}
    source = sources.get(args.source_id)
    if not source:
        print(f"no such source: {args.source_id}", file=sys.stderr)
        return 64

    print(f"  {source.name}\n  {source.url}\n")
    # A copy with status forced to ACTIVE, because `run_source` refuses to
    # fetch anything else — which is the whole point of PENDING_VERIFICATION,
    # and this command is the one sanctioned way past it.
    probe = replace(source, status="ACTIVE")
    run, candidates, _state = runner.run_source(probe, use_conditional=False)

    print(f"  status        {run.status}")
    print(f"  http          {run.http_status or '—'}")
    print(f"  took          {run.duration_ms} ms")
    print(f"  records       {run.records}")
    if run.error:
        print(f"  error         {run.error}")
    if candidates:
        print("\n  first records as the pipeline sees them:")
        for candidate in candidates[:3]:
            print(f"    · [{candidate.classified_as}] {candidate.title[:70]}")
            print(f"      {candidate.classified_reason}")

    if run.status == "ok" and run.records:
        print(f"\n  Reachable and parseable. To activate, edit "
              f"{registry.REGISTRY_PATH.relative_to(registry.ROOT)}:")
        print(f"      {args.source_id}: status PENDING_VERIFICATION -> ACTIVE")
        print("  and open a pull request. This command does not edit the registry.")
        return 0
    print("\n  Not activated. Fix the URL, the collector or the parser and try again.")
    return 1


def cmd_queue(args):
    candidates = review.load()
    if args.state:
        candidates = [c for c in candidates if c.state == args.state.upper()]
    if args.limit:
        candidates = candidates[:args.limit]
    if _emit([vars(c) for c in candidates], args.json):
        return 0

    if not candidates:
        print("the queue is empty.")
        return 0
    print(f"{'state':<14} {'type':<20} {'source':<18} title")
    print("-" * 110)
    for c in candidates:
        print(f"{c.state:<14} {c.classified_as:<20} {c.source_id:<18} {c.title[:50]}")
        if c.duplicate_of:
            print(f"{'':<14} └─ duplicate of {c.duplicate_of} ({c.duplicate_reason})")
        if c.supersedes:
            print(f"{'':<14} └─ appears to supersede {c.supersedes}")
    print(f"\n  {json.dumps(review.summary(review.load()), ensure_ascii=False)}")
    print("\n  Approval happens in stewardship, not here:")
    print("      python3 -m stewardship.cli review <entity_id> --actor NAME --evidence URL")
    return 0


def cmd_health(args):
    last_run = json.loads(RUN_LOG.read_text(encoding="utf-8")) if RUN_LOG.exists() else None
    health = monitor.check(registry.load(), last_run=last_run)
    if _emit(health.as_dict(), args.json):
        return 2 if health.status == "critical" else 0

    print(f"  collection health: {health.status.upper()}")
    print(f"  {json.dumps(health.totals)}\n")
    for finding in health.findings:
        mark = {"CRITICAL": "✗", "WARN": "!", "OK": "✓", "UNKNOWN": "?"}[finding.severity]
        print(f"    {mark} {finding.check}: {finding.source_id} — {finding.detail}")
    if not health.findings:
        print("    ✓ every monitored source is fresh and reachable")
    return 2 if health.status == "critical" else 0


def cmd_backlog(args):
    events = json.loads(Path(args.events).read_text(encoding="utf-8")) if args.events else []
    requests = json.loads(Path(args.requests).read_text(encoding="utf-8")) if args.requests else []
    incoming = backlog_module.build(search_events=events, user_requests=requests)
    merged = backlog_module.merge(backlog_module.load(), incoming)
    if args.write:
        backlog_module.save(merged)

    if _emit([s.to_dict() for s in merged], args.json):
        return 0
    if not merged:
        print("no gaps recorded yet.\n"
              "  Search tracking feeds this — see collection/backlog.py for where it comes from.")
        return 0
    print(f"{'score':>7}  {'searches':>8} {'requests':>8}  {'status':<8} term")
    print("-" * 80)
    for s in merged:
        print(f"{s.score:>7.1f}  {s.searches:>8} {s.requests:>8}  {s.status:<8} {s.term}")
    print("\n  These are GAPS, not knowledge. Nothing here may become an entity "
          "without research against a public source.")
    if not args.write:
        print("  (not written — pass --write)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="collection", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable output")

    # `--json` on every subcommand as well as before it. Anyone reaching for
    # machine output types `health --json`, not `--json health`, and an
    # "unrecognized arguments" error for the natural word order is a papercut
    # that costs a minute every single time.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="machine-readable output")

    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("sources", help="what we monitor", parents=[common])
    p.add_argument("--category")
    p.set_defaults(func=cmd_sources)

    p = sub.add_parser("run", help="collect from every due source", parents=[common])
    p.add_argument("--only", nargs="*", help="source ids")
    p.add_argument("--force", action="store_true", help="ignore the schedule")
    p.add_argument("--write", action="store_true", help="record the queue and state")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("verify", help="prove a candidate source is reachable", parents=[common])
    p.add_argument("source_id")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("queue", help="candidates awaiting a person", parents=[common])
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(func=cmd_queue)

    p = sub.add_parser("health", help="feed health metrics", parents=[common])
    p.set_defaults(func=cmd_health)

    p = sub.add_parser("backlog", help="topics people searched for and we lack", parents=[common])
    p.add_argument("--events", help="JSON export of search_events")
    p.add_argument("--requests", help="JSON export of user_requests")
    p.add_argument("--write", action="store_true")
    p.set_defaults(func=cmd_backlog)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
