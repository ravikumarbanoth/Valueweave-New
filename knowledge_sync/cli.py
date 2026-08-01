#!/usr/bin/env python3
"""
ValueWeave knowledge sync — command line.

    python3 -m knowledge_sync plan                      # dry run, writes nothing
    python3 -m knowledge_sync sync                      # incremental
    python3 -m knowledge_sync sync --full               # treat every row as new
    python3 -m knowledge_sync sync --table kg_schemes
    python3 -m knowledge_sync rollback <run_id>
    python3 -m knowledge_sync rollback <run_id> --dry-run
    python3 -m knowledge_sync status
    python3 -m knowledge_sync history --limit 5
    python3 -m knowledge_sync snapshots

`plan` and `--target memory` need no credentials. `sync` against Supabase needs
SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY, and refuses to start without them
rather than failing halfway through.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from knowledge_sync import __version__                                   # noqa: E402
from knowledge_sync.adapters import InMemoryTarget, SupabaseTarget       # noqa: E402
from knowledge_sync.config import TABLE_SPECS                            # noqa: E402
from knowledge_sync.changes import Manifest                              # noqa: E402
from knowledge_sync.engine import SyncAborted, SyncEngine, SyncMode      # noqa: E402
from knowledge_sync.logs import read_log                                 # noqa: E402
from knowledge_sync.rollback import list_snapshots                       # noqa: E402


def build_target(name):
    if name == "memory":
        return InMemoryTarget()
    return SupabaseTarget()


def cmd_plan(args):
    engine = SyncEngine(target=build_target(args.target), quiet=args.json)
    try:
        result = engine.run(SyncMode.DRY_RUN, tables=args.table)
    except SyncAborted as exc:
        print(f"\nABORTED: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    return 0


def cmd_sync(args):
    if args.target == "supabase":
        try:
            target = SupabaseTarget()
        except Exception as exc:                                       # noqa: BLE001
            print(f"cannot reach Supabase: {exc}", file=sys.stderr)
            return 2
    else:
        target = InMemoryTarget()
        print("NOTE: --target memory writes to an in-process store that is discarded "
              "when this command exits. Useful for rehearsal; it syncs nothing.\n")

    mode = SyncMode.FULL if args.full else SyncMode.INCREMENTAL
    engine = SyncEngine(target=target, quiet=args.json)
    try:
        result = engine.run(mode, tables=args.table)
    except SyncAborted as exc:
        print(f"\nABORTED: {exc}", file=sys.stderr)
        if getattr(exc, "report", None):
            for f in exc.report.errors[:20]:
                print(f"  {f}", file=sys.stderr)
        for e in (exc.errors or [])[:20]:
            print(f"  {e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\n  run {result.run_id}  ·  snapshot {Path(result.snapshot).name}")
        print(f"  roll back with: python3 -m knowledge_sync rollback {result.run_id}")
    return 0


def cmd_rollback(args):
    engine = SyncEngine(target=build_target(args.target), quiet=True)
    try:
        report = engine.rollback(args.run_id, dry_run=args.dry_run)
    except Exception as exc:                                           # noqa: BLE001
        print(f"rollback failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    print(f"rollback of {args.run_id}"
          f"{' (dry run — nothing changed)' if args.dry_run else ''}\n")
    for table, plan in report["tables"].items():
        if any(plan.values()):
            print(f"  {table:<20} " + "  ".join(f"{k}={v}" for k, v in plan.items()))
    if args.target == "memory":
        print("\n  NOTE: --target memory means this ran against an empty in-process "
              "store. Use --target supabase to roll back a real sync.")
    return 0


def cmd_status(args):
    manifest = Manifest()
    print(f"knowledge_sync {__version__}\n")
    print(f"  tables owned ........ {len(TABLE_SPECS)}")
    print(f"  manifest ............ {manifest.path}")
    if manifest.data.get("version"):
        print(f"  last sync version ... {manifest.data['version']}")
        print(f"  last sync at ........ {manifest.data.get('synced_at')}")
        print(f"  rows tracked ........ {manifest.row_count()}")
        for name, hashes in sorted(manifest.tables.items()):
            print(f"    {name:<20} {len(hashes)}")
    else:
        print("  last sync ........... never — the next run is a full insert")
    print("\n  target tables:")
    for s in TABLE_SPECS:
        srcs = ", ".join(f"{x.package}/{x.dataset}" for x in s.sources)
        print(f"    {s.name:<20} <- {srcs[:78]}")
    return 0


def cmd_history(args):
    runs = read_log(limit=args.limit)
    if not runs:
        print("no sync has been recorded")
        return 0
    if args.json:
        print(json.dumps(runs, indent=2))
        return 0
    print(f"{'run':<28} {'mode':<12} {'outcome':<20} {'secs':>6}  rows")
    print("-" * 84)
    for r in runs:
        m = r.get("metrics") or {}
        rows = m.get("rows_synchronised", "-")
        print(f"{r['run_id']:<28} {r['mode']:<12} {r['outcome']:<20} "
              f"{r.get('duration_seconds', 0):>6}  {rows}")
    return 0


def cmd_snapshots(args):
    snaps = list_snapshots()
    if not snaps:
        print("no snapshots")
        return 0
    for s in snaps[:args.limit]:
        counts = {k: sum(v.values()) for k, v in s["tables"].items() if sum(v.values())}
        print(f"{s['run_id']:<28} {s['created_at']}  "
              + (", ".join(f"{k}:{v}" for k, v in counts.items()) or "no changes"))
    return 0


def build_parser():
    ap = argparse.ArgumentParser(prog="knowledge_sync",
                                 description="Git -> Supabase knowledge synchronisation")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--target", choices=("memory", "supabase"), default="memory",
                    help="memory needs no credentials (default)")
    sub = ap.add_subparsers(dest="command", required=True)

    # `--target` and `--json` are declared above, on the top-level parser, which
    # means argparse only accepts them BEFORE the subcommand:
    #
    #     knowledge_sync --target supabase sync      works
    #     knowledge_sync sync --target supabase      "unrecognized arguments"
    #
    # The second form is the one everybody writes, and it is the one
    # scripts/run_sync.sh wrote. It failed in CI at the apply step, after the
    # tests and the plan had both passed — the latest possible moment, against a
    # real database, having already reported success twice.
    #
    # Accepting both positions rather than only correcting the callers: the
    # trailing form is the natural one, the error argparse gives for it is
    # obscure, and this trap has now cost one production run. The same hazard is
    # documented for `--json` in the deployment guide, which is a sign the design
    # was surprising people before it broke anything.
    #
    # Separate dests, resolved in main(). A subparser sharing `dest="target"`
    # would overwrite the top-level value with its own default on every run where
    # the flag came first — turning `--target supabase sync` into a silent
    # in-memory no-op, which is far worse than the loud error this replaces.
    def shared(parser):
        parser.add_argument("--target", dest="target_after", default=None,
                            choices=("memory", "supabase"),
                            help="same as the top-level --target; accepted here too")
        parser.add_argument("--json", dest="json_after", action="store_true",
                            default=False, help=argparse.SUPPRESS)
        return parser

    p = shared(sub.add_parser("plan",
               help="dry run: report what would change, write nothing"))
    p.add_argument("--table", action="append")
    p.set_defaults(fn=cmd_plan)

    p = shared(sub.add_parser("sync", help="apply changes"))
    p.add_argument("--full", action="store_true", help="treat every row as new")
    p.add_argument("--table", action="append")
    p.set_defaults(fn=cmd_sync)

    p = sub.add_parser("rollback", help="undo a run using its snapshot")
    p.add_argument("run_id")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_rollback)

    sub.add_parser("status", help="manifest and table configuration").set_defaults(
        fn=cmd_status)

    p = sub.add_parser("history", help="recent runs")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(fn=cmd_history)

    p = sub.add_parser("snapshots", help="available rollback points")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(fn=cmd_snapshots)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    # A flag given after the subcommand wins, because it is the more specific
    # position. Absent there, the top-level value (or its default) stands.
    if getattr(args, "target_after", None) is not None:
        args.target = args.target_after
    if getattr(args, "json_after", False):
        args.json = True
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
