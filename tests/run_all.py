#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — full test runner (Work Package 6)

Runs every suite in the repository, including the Knowledge Engine's own 117 tests,
and prints one summary. This is the command CI would run and the command the Git
report quotes.

    python3 tests/run_all.py
    python3 tests/run_all.py --suite api search
    python3 tests/run_all.py --quiet

Exit code 0 = everything passed.

`unittest` rather than pytest, deliberately: the Knowledge Engine was written to
depend on the standard library alone so it can be run and reviewed on a bare Python
install, and a test runner that needs a pip install would undo that.

The runner still needs none. The suite itself now needs exactly one package —
PyYAML, so a test can read the CI workflow — declared in requirements-dev.txt:

    python3 -m pip install -r requirements-dev.txt

Everything under test remains standard-library only, and two tests hold that
line: no runtime module may import PyYAML or the Supabase SDK.
"""

import argparse
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SUITES = {
    "knowledge_engine_unit": ("knowledge_engine.tests",
                              "Knowledge Engine unit tests (recovered with the engine)"),
    "knowledge_engine": ("tests.test_knowledge_engine",
                         "Knowledge Engine recovery and Platform v2 compatibility"),
    "ownership": ("tests.test_ownership", "Ownership rules and the ADR-003 crosswalk"),
    "api": ("tests.test_api", "REST API: envelope, routing, errors, HTTP transport"),
    "search": ("tests.test_search", "Search: index, four match modes, filters"),
    "search_experience": ("tests.test_search_experience",
                          "PX Phase 1: semantic search quality on the live graph"),
    "search_routing": ("tests.test_search_routing",
                       "The /knowledge route actually calls the search engine"),
    "multilingual": ("tests.test_multilingual_search",
                     "English, Telugu and Tanglish resolve to the same knowledge"),
    "universal": ("tests.test_universal_search",
                  "One box over knowledge and research, grouped, never a dead end"),
    "connected_knowledge": ("tests.test_connected_knowledge",
                            "PX Phase 5: intent sections, ranking and the second hop"),
    "landing": ("tests.test_landing",
                "PX Phase 6: hero search, audience routes and their destinations"),
    "plain_language": ("tests.test_plain_language",
                       "PX Phase 7: entry-page headings a student can act on"),
    "persona_review": ("tests.test_persona_review",
                       "PX Phase 8: the five defects found walking seven personas"),
    "journey": ("tests.test_journey",
                "PX Phase 9: the remembered audience and what it may reweight"),
    "stewardship": ("tests.test_stewardship", "Lifecycle, ledger and review queue"),
    "collection": ("tests.test_collection",
                   "Automated collection: registry, conditional fetch, review queue"),
    "operations": ("tests.test_operations",
                   "Knowledge ops: feed priority, quality score, integrity, dashboard"),
    "deployment": ("tests.test_deployment",
                   "Deployment: writer, scripts, migration 011"),
    "graph": ("tests.test_graph_integrity", "Graph integrity and the 11 G-checks"),
    "graph_compiler": ("tests.test_graph_compiler",
                       "Builder dataset coverage: every dataset registered"),
    "regression": ("tests.test_regression", "One test per bug previously fixed"),
    "vocabulary": ("tests.test_vocabulary",
                   "v3.0 Step 0: vocabulary crosswalk integrity and coverage"),
    "knowledge_sync": ("tests.test_knowledge_sync",
                       "v3.0 Step 1: Git -> Supabase synchronisation framework"),
    "user_intelligence": ("tests.test_user_intelligence",
                          "v3.0 Step 1.5: rule-based user intelligence engine"),
    "frontend_integration": ("tests.test_frontend_integration",
                             "v3.0 Step 2: JS <-> Python contract and page wiring"),
    "frontend_activation": ("tests.test_frontend_activation",
                            "v3.0 Step 4: placeholders removed, every type routed"),
    "production_ux": ("tests.test_production_ux",
                      "v1.0 UX polish: no internal vocabulary reaches a user"),
    "knowledge_pipeline": ("tests.test_knowledge_pipeline",
                           "v1.0 audit: the import exists, is invoked, and can read"),
}


def load(name):
    module, _ = SUITES[name]
    loader = unittest.TestLoader()
    if module.endswith(".tests"):
        return loader.discover(start_dir=str(ROOT / module.replace(".", "/")),
                               top_level_dir=str(ROOT))
    return loader.loadTestsFromName(module)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", nargs="*", choices=sorted(SUITES), default=sorted(SUITES))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    print("ValueWeave Platform v2.2 — test suite\n")
    rows, failed_total = [], 0
    started = time.time()

    for name in args.suite:
        _module, description = SUITES[name]
        suite = load(name)
        stream = open("/dev/null", "w") if args.quiet else sys.stderr
        runner = unittest.TextTestRunner(stream=stream, verbosity=0)
        t0 = time.time()
        result = runner.run(suite)
        if args.quiet:
            stream.close()
        bad = len(result.failures) + len(result.errors)
        failed_total += bad
        rows.append({
            "suite": name, "description": description,
            "tests": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "skipped": len(result.skipped),
            "seconds": round(time.time() - t0, 2),
            "status": "PASS" if bad == 0 else "FAIL",
        })
        for case, trace in result.failures + result.errors:
            print(f"\n  {name} :: {case}\n{trace}", file=sys.stderr)

    total = sum(r["tests"] for r in rows)
    print(f"\n{'suite':<24} {'tests':>6} {'fail':>5} {'err':>4} {'skip':>5} "
          f"{'secs':>6}  status")
    print("-" * 72)
    for r in rows:
        print(f"{r['suite']:<24} {r['tests']:>6} {r['failures']:>5} {r['errors']:>4} "
              f"{r['skipped']:>5} {r['seconds']:>6}  {r['status']}")
    print("-" * 72)
    print(f"{'TOTAL':<24} {total:>6} "
          f"{sum(r['failures'] for r in rows):>5} "
          f"{sum(r['errors'] for r in rows):>4} "
          f"{sum(r['skipped'] for r in rows):>5} "
          f"{round(time.time() - started, 2):>6}  "
          f"{'PASS' if failed_total == 0 else 'FAIL'}")
    return 0 if failed_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
