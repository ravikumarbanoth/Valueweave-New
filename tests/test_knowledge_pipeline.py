#!/usr/bin/env python3
"""
Knowledge → Database pipeline: the audit's findings, held in place.

WHAT THE AUDIT FOUND
--------------------
The pipeline from Packages 001-008 to Supabase is complete, correct and covered
by 114 tests. It had never been executed. The only evidence of any run in the
whole repository was two lines in `knowledge_sync/state/sync_log.jsonl`, both
`"mode": "dry-run"`, both `"applied": false` — and there was no CI at all, so
nothing was ever going to invoke it.

That is why production shows "This information is being prepared" everywhere:
the code is right and the tables are empty.

WHAT THESE TESTS ARE FOR
------------------------
Three things, none of which any existing test covered:

1.  Every source file the sync reads must exist. A package dataset renamed or
    moved breaks the import at run time, in CI, after a merge — the slowest
    possible place to find out.

2.  The invocation must exist and must stay honest. A workflow that plans but
    never applies, or that verifies with the service-role key, would look like
    a working pipeline and deliver an empty database.

3.  The coverage the audit measured must not silently get worse.

    python3 tests/run_all.py --suite knowledge_pipeline
"""

import csv
import json
import re
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from knowledge_sync.config import TABLE_SPECS  # noqa: E402

WORKFLOW = ROOT / ".github" / "workflows" / "knowledge-sync.yml"
ENTITIES = ROOT / "knowledge_graph" / "entities" / "entities.csv"
RELATIONSHIPS = ROOT / "knowledge_graph" / "relationships" / "relationships.csv"


def rows(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ═══════════════════════════════════════════ 1. the pipeline can actually read
class PipelineSourcesTest(unittest.TestCase):
    """Every file the sync reads must be there, and must have rows.

    `knowledge_sync/config.py` names 12 source files by path across 8 table
    specs. Nothing checked they exist. A dataset renamed during a package
    revision would pass every existing test and fail at import time — in CI,
    after a merge, against production.
    """

    def test_every_declared_source_file_exists(self):
        missing = []
        for spec in TABLE_SPECS:
            for src in spec.sources:
                if not Path(src.path).exists():
                    missing.append(f"{spec.name} <- {src.path}")
        self.assertEqual(missing, [], "sync sources that do not exist:\n  "
                                      + "\n  ".join(missing))

    def test_every_source_file_has_rows(self):
        """An empty CSV imports cleanly and delivers nothing."""
        empty = []
        for spec in TABLE_SPECS:
            for src in spec.sources:
                p = Path(src.path)
                if p.exists() and len(rows(p)) == 0:
                    empty.append(f"{spec.name} <- {p.name}")
        self.assertEqual(empty, [], f"source files with no data rows: {empty}")

    def test_the_key_column_exists_in_every_source(self):
        """The key column is how change detection identifies a row."""
        bad = []
        for spec in TABLE_SPECS:
            for src in spec.sources:
                p = Path(src.path)
                if not p.exists():
                    continue
                header = rows(p)[0].keys() if rows(p) else []
                if src.key_column not in header:
                    bad.append(f"{spec.name}: {p.name} has no '{src.key_column}'")
        self.assertEqual(bad, [], "\n  ".join(bad))

    def test_every_package_with_entities_also_feeds_a_detail_table(self):
        """Entities carry identity; detail tables carry what a user reads.

        The axis is the SOURCE FILES, not `owner_package`. Package004's four
        business datasets feed `kg_businesses`, which Package008 owns — checking
        ownership would have wrongly reported Package004 as unprojected. (It did,
        on the first run of this test.)

        Package002 is genuinely absent: its 66 Institution entities reach the
        graph but no detail table, so an institution page shows a name and its
        links and nothing else. Package003 produces no entities at all. Both are
        pinned here so that fixing either registers as a change.
        """
        feeding = {part for spec in TABLE_SPECS for src in spec.sources
                   for part in Path(src.path).parts if part.startswith("Package")}
        with_entities = {r["source_package"] for r in rows(ENTITIES)}

        self.assertEqual(
            sorted(with_entities - feeding), ["Package002_Education"],
            "packages whose entities exist but whose detail rows are not projected")
        self.assertNotIn("Package003_Healthcare", with_entities,
                         "Package003 contributes no entities; if it now does, it "
                         "also needs a TableSpec")


# ═══════════════════════════════════════════ 2. something has to invoke it
class InvocationTest(unittest.TestCase):
    """A pipeline nothing calls is a pipeline that has never run."""

    @classmethod
    def setUpClass(cls):
        cls.src = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""

    def test_a_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists(),
                        "nothing in the repository invokes the import; that is why "
                        "the production tables are empty")

    def test_it_runs_when_the_research_changes(self):
        """A package edit and a live database that disagree is the bug."""
        for path in ("packages/**", "knowledge_graph/**", "knowledge_sync/**"):
            with self.subTest(path=path):
                self.assertIn(path, self.src)

    def test_it_applies_and_does_not_only_plan(self):
        """A plan-only workflow looks green and delivers nothing."""
        runs = [l.split("run:", 1)[1].strip()
                for l in self.src.splitlines() if l.strip().startswith("run:")]
        self.assertIn("scripts/run_sync.sh --plan-only", runs)
        self.assertIn("scripts/run_sync.sh", runs,
                      "the workflow must apply, not only plan")

    def test_it_fails_loudly_when_the_secrets_are_absent(self):
        """Half-running against no database is worse than not starting."""
        self.assertIn("SUPABASE_SERVICE_ROLE_KEY", self.src)
        self.assertIn("::error::Missing repository secrets", self.src)

    def test_the_service_role_key_comes_only_from_secrets(self):
        """It bypasses RLS. It must never be inlined or made public.

        Checked line by line rather than with a lookahead: `\\s*(?!...)` lets the
        `\\s*` match zero characters, so the lookahead fires against the space and
        passes on a value that is perfectly fine. It reported a false failure
        here first time round.
        """
        for line in self.src.splitlines():
            stripped = line.strip()
            if not stripped.startswith("SUPABASE_SERVICE_ROLE_KEY:"):
                continue
            value = stripped.split(":", 1)[1].strip()
            with self.subTest(line=stripped):
                self.assertTrue(
                    value.startswith("${{ secrets."),
                    f"the service role key must come from a secret, got: {value}")
        self.assertNotIn("NEXT_PUBLIC_SUPABASE_SERVICE", self.src)

    def test_verification_uses_the_anon_key(self):
        """The service role can read a schema the browser cannot.

        Verifying with it would report a healthy deployment while every page
        rendered empty — the exact failure this sprint was called to diagnose.
        """
        self.assertIn("NEXT_PUBLIC_SUPABASE_ANON_KEY", self.src)
        self.assertIn("scripts/health_check.sh", self.src)

    def test_the_checkout_fetches_full_history(self):
        """`actions/checkout@v4` defaults to depth 1, and two tests need more.

        `test_history_was_preserved_not_recopied` proves the knowledge engine was
        recovered by merge rather than re-added by copy.
        `test_no_page_lost_more_than_a_handful_of_lines` measures Step 2's own
        commit. Neither can see anything in a one-commit clone, and the first one
        failed by accusing the repository of a regression that had not happened.

        Reproduced by cloning this repository with `--depth 1` and running the
        suite: same two suites, same two failures as CI reported.
        """
        self.assertIn("fetch-depth: 0", self.src,
                      "CI must check out full history; two suites assert facts "
                      "about the past and a depth-1 clone throws it away")

    def test_two_syncs_cannot_run_at_once(self):
        self.assertIn("concurrency:", self.src)
        self.assertIn("cancel-in-progress: false", self.src)


# ═══════════════════════════════════════════ 3. coverage must not regress
class CoverageTest(unittest.TestCase):
    """What the frontend will actually be able to show, once the import runs.

    Running the import is necessary and not sufficient: 34 of 61 districts have
    no incoming edge at all, so most district pages would stay near-empty even
    on a perfectly synced database. These numbers are asserted as floors so the
    next graph change can only improve them.
    """

    @classmethod
    def setUpClass(cls):
        cls.entities = rows(ENTITIES)
        cls.rels = rows(RELATIONSHIPS)
        cls.incoming = defaultdict(list)
        for r in cls.rels:
            cls.incoming[r["to_entity"]].append(r)

    def test_the_research_that_the_import_would_publish(self):
        self.assertGreaterEqual(len(self.entities), 647)
        self.assertGreaterEqual(len(self.rels), 865)

    def test_every_expansion_card_has_research_behind_it(self):
        """Each card the frontend marks LIVE must have rows to be live with."""
        counts = Counter(r["entity_type"] for r in self.entities)
        for entity_type, floor in [
            ("Skill", 45), ("Certification", 30), ("TrainingProvider", 25),
            ("BusinessOpportunity", 45), ("Machinery", 69), ("RawMaterial", 21),
            ("ExportCountry", 29), ("Market", 11), ("FinancialInstitution", 21),
            ("Institution", 66),
        ]:
            with self.subTest(entity_type=entity_type):
                self.assertGreaterEqual(counts[entity_type], floor)

    def test_district_link_coverage_is_recorded_not_assumed(self):
        """The number that decides whether a district page has anything on it."""
        districts = [e for e in self.entities if e["entity_type"] == "District"]
        linked = [d for d in districts
                  if self.incoming[d["global_entity_id"]]]
        self.assertEqual(len(districts), 61)
        # 27 of 61 as measured. A floor, so recovery work shows as a pass.
        self.assertGreaterEqual(
            len(linked), 27,
            "districts with at least one linked record — the audit measured 27 "
            "of 61, which is why most district pages stay sparse after a sync")

    def test_the_search_terms_the_audit_checked_still_resolve(self):
        """`searchKnowledge()` ilikes canonical_name and nothing else.

        Five of the six terms the brief named return results. "Dairy" returns
        zero despite appearing in 11 package rows, because it lives in
        descriptions and category names that the entity registry does not carry.
        Asserted exactly as measured — including the miss, so that closing it
        registers as a change rather than passing unnoticed.
        """
        names = [e["canonical_name"].lower() for e in self.entities]
        for term, expected_min in [("construction", 4), ("electrician", 2),
                                   ("solar", 6), ("bakery", 1), ("robot", 6)]:
            with self.subTest(term=term):
                self.assertGreaterEqual(sum(term in n for n in names), expected_min)
        self.assertEqual(
            sum("dairy" in n for n in names), 0,
            "if this now matches, entity search reaches beyond canonical_name — "
            "update SEARCH_PIPELINE_REPORT.md and remove this assertion")


# ═══════════════════════════════════════════ 4. the scripts must actually parse
class CliContractTest(unittest.TestCase):
    """Every knowledge_sync command written in a script must be a valid command.

    THE BUG THIS EXISTS FOR
    -----------------------
    `--target` is declared on the top-level parser, before `add_subparsers()`.
    argparse therefore accepted it only BEFORE the subcommand:

        knowledge_sync --target supabase sync      works
        knowledge_sync sync --target supabase      "unrecognized arguments"

    `scripts/run_sync.sh` wrote the second form. Nothing caught it: the plan step
    uses no target flag, so it passed; the tests never invoked the script; and
    the failure surfaced at the APPLY step in CI — after tests and planning had
    both reported success, against a live database, at the last possible moment.

    Parsing is enough to catch it and costs nothing. These tests never execute a
    sync; they hand the arguments to the real parser and require it to accept
    them.
    """

    #: `python3 -m knowledge_sync <args>` as written in every operational script.
    INVOCATION = re.compile(r"python3\s+-m\s+knowledge_sync\s+([^|>\n]+)")

    #: Placeholders for shell expansions. `$FULL` is `--full` or empty, and both
    #: must parse; the empty case is the default and is covered by the others.
    SHELL_VARS = {"$FULL": "--full", '"$RUN_ID"': "20260101T000000Z-abcdef"}

    def _invocations(self):
        for script in sorted((ROOT / "scripts").glob("*.sh")):
            for m in self.INVOCATION.finditer(script.read_text(encoding="utf-8")):
                raw = m.group(1).strip()
                for var, value in self.SHELL_VARS.items():
                    raw = raw.replace(var, value)
                if "$" in raw:          # an expansion we cannot resolve safely
                    continue
                yield script.name, raw.split()

    def test_every_scripted_invocation_parses(self):
        from knowledge_sync.cli import build_parser
        bad = []
        seen = 0
        for script, argv in self._invocations():
            seen += 1
            parser = build_parser()
            try:
                parser.parse_args(argv)
            except SystemExit:
                bad.append(f"{script}: knowledge_sync {' '.join(argv)}")
        self.assertGreater(seen, 0, "no invocations found — the regex stopped matching")
        self.assertEqual(bad, [], "scripts issuing commands the CLI rejects:\n  "
                                  + "\n  ".join(bad))

    def test_target_is_accepted_on_both_sides_of_the_subcommand(self):
        """The trailing form is what everyone writes. It must work."""
        from knowledge_sync.cli import build_parser
        for argv in (["--target", "supabase", "sync"],
                     ["sync", "--target", "supabase"],
                     ["--target", "supabase", "plan"],
                     ["plan", "--target", "supabase"]):
            with self.subTest(argv=" ".join(argv)):
                build_parser().parse_args(argv)   # must not SystemExit

    def test_the_leading_form_is_not_silently_downgraded(self):
        """The subtle way this fix could go wrong, and the expensive one.

        A subparser copy of `--target` sharing `dest="target"` would overwrite
        the top-level value with its own default. `--target supabase sync` would
        then parse cleanly and write to an in-process store that is discarded —
        a green CI run and an empty database, which is strictly worse than the
        loud error it replaced.
        """
        from knowledge_sync.cli import build_parser, main
        import unittest.mock as mock

        for argv in (["--target", "supabase", "sync"], ["sync", "--target", "supabase"]):
            with self.subTest(argv=" ".join(argv)):
                with mock.patch("knowledge_sync.cli.cmd_sync") as fake:
                    fake.return_value = 0
                    main(argv)
                    resolved = fake.call_args[0][0]
                    self.assertEqual(
                        resolved.target, "supabase",
                        "the flag resolved to the wrong target — a sync that "
                        "reports success and writes nothing")

    def test_the_default_target_stays_memory(self):
        """No credentials, no accidental writes."""
        from knowledge_sync.cli import build_parser
        self.assertEqual(build_parser().parse_args(["sync"]).target, "memory")


# ═══════════════════════════════════════════ 5. the one third-party dependency
class SyncDependencyTest(unittest.TestCase):
    """Writing to Supabase needs the SDK. Nothing declared it, so nothing installed it.

    The framework imports the SDK lazily, inside the `client` property, so that
    tests, plans and dry runs never need it. That guard worked exactly as
    designed — and hid the fact that no manifest listed the package and no CI
    step installed it. The workflow reached Apply and failed with "the
    `supabase` package is not installed", after the tests and the plan had both
    reported success.
    """

    REQUIREMENTS = ROOT / "requirements-sync.txt"

    @classmethod
    def setUpClass(cls):
        cls.req = cls.REQUIREMENTS.read_text(encoding="utf-8") if cls.REQUIREMENTS.exists() else ""
        cls.workflow = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""

    def test_the_dependency_is_declared(self):
        self.assertTrue(self.REQUIREMENTS.exists(),
                        "nothing declares the Supabase SDK, so nothing installs it")
        self.assertRegex(self.req, r"(?m)^supabase[~=<>]")

    def test_it_is_pinned_not_floating(self):
        """This writes to production data on every merge to main.

        An unpinned dependency means the bytes that touch the database can
        change without a commit, and the first sign is a failed sync at 03:00 on
        a Monday.
        """
        spec = next(l.strip() for l in self.req.splitlines()
                    if l.strip().startswith("supabase"))
        self.assertRegex(spec, r"supabase~=\d+\.\d+\.\d+",
                         f"pin to a minor range; got {spec!r}")

    def test_the_workflow_installs_it(self):
        self.assertIn("requirements-sync.txt", self.workflow,
                      "the workflow must install the SDK before it applies")

    def test_it_is_installed_after_the_tests_and_before_the_plan(self):
        """Order is load-bearing in both directions.

        AFTER the tests, because the suite asserts the engine holds no database
        client and can only prove that where the SDK is absent — installing
        first would make that test pass for the wrong reason.

        BEFORE the plan, so a dependency that breaks the import graph surfaces
        at the cheap step rather than the one that writes.
        """
        def run_line(command):
            """Index of the `run:` step issuing exactly this command.

            Substring matching is wrong here: `scripts/run_sync.sh` is a prefix
            of `scripts/run_sync.sh --plan-only`, so a naive `in` check found the
            plan step twice and reported the apply as preceding itself.
            """
            for i, line in enumerate(self.workflow.splitlines()):
                stripped = line.strip()
                if stripped.startswith("run:") and stripped[4:].strip() == command:
                    return i
            self.fail(f"no step runs exactly: {command}")

        def contains(needle):
            for i, line in enumerate(self.workflow.splitlines()):
                if needle in line:
                    return i
            self.fail(f"not found in the workflow: {needle}")

        tests = run_line("python3 tests/run_all.py --quiet")
        install = contains("requirements-sync.txt")
        plan = run_line("scripts/run_sync.sh --plan-only")
        apply_ = run_line("scripts/run_sync.sh")
        self.assertLess(tests, install, "install must come after the tests")
        self.assertLess(install, plan, "install must come before the plan")
        self.assertLess(plan, apply_, "the plan must come before the apply")

    def test_the_engine_still_imports_without_the_sdk(self):
        """The lazy import is the reason the suite needs no virtualenv.

        If anything ever moves `from supabase import ...` to module scope, this
        whole suite stops running on a bare Python — and the failure would look
        like an unrelated collection error.
        """
        import importlib
        for module in ("knowledge_sync.adapters", "knowledge_sync.cli",
                       "knowledge_sync.engine", "user_intelligence.writer"):
            with self.subTest(module=module):
                importlib.import_module(module)

        for path in ("knowledge_sync/adapters.py", "user_intelligence/writer.py"):
            src = (ROOT / path).read_text(encoding="utf-8")
            for lineno, line in enumerate(src.splitlines(), 1):
                if "from supabase import" in line:
                    with self.subTest(file=path, line=lineno):
                        self.assertTrue(
                            line.startswith((" ", "\t")),
                            f"{path}:{lineno} imports the SDK at module scope; it "
                            f"must stay inside the client property")


# ═══════════════════════════════════════════ 6. the verification query
class VerificationSqlTest(unittest.TestCase):
    """`sql/verify_knowledge_schema.sql` must stay in step with the migrations.

    Its expected index and policy counts were measured against a real
    PostgreSQL 16 with these migration files applied. If a migration gains a
    table or an index and the query does not, it reports a complete deployment
    that is not one — the worst outcome for a check whose entire job is to be
    trusted before someone touches production.
    """

    SQL = ROOT / "sql" / "verify_knowledge_schema.sql"

    @classmethod
    def setUpClass(cls):
        cls.src = cls.SQL.read_text(encoding="utf-8") if cls.SQL.exists() else ""

    def test_it_exists(self):
        self.assertTrue(self.SQL.exists())

    @staticmethod
    def _statements(src):
        """Executable statements, with comments and string literals removed.

        Both removals matter. An earlier version of this test searched the raw
        text for substrings like "grant ", which made it fire on the word `grant`
        inside a quoted hint message — a false alarm about a file that cannot
        write.

        Comments come out FIRST. The other order looks equally reasonable and is
        wrong: an apostrophe in prose — "Supabase's service role" — opens a bogus
        literal that runs to the next apostrophe, swallowing real SQL along with
        any semicolons in it. That silently merged two statements here and made
        the next one appear to start with `end`.

        Doing it in this order is only safe while no literal contains `--`, so
        that is asserted rather than assumed.
        """
        no_com = re.sub(r"--[^\n]*", "", src)
        for lit in re.findall(r"'(?:[^']|'')*'", no_com):
            assert "--" not in lit, (
                f"literal contains `--`, so comments cannot be stripped first: {lit!r}")
        no_lit = re.sub(r"'(?:[^']|'')*'", "''", no_com)
        return [s.strip().lower() for s in no_lit.split(";") if s.strip()]

    def test_it_is_read_only(self):
        """It runs against production, twice. It must not be able to change anything.

        An allowlist, not a denylist: every statement has to BE a read. That
        catches a verb nobody thought to forbid, which a list of banned words
        cannot.
        """
        for stmt in self._statements(self.src):
            first = stmt.split()[0]
            with self.subTest(statement=stmt[:60]):
                self.assertIn(
                    first, ("select", "with"),
                    f"the verification query must only read; found `{first}`")

    def test_no_writing_verb_survives_literal_stripping(self):
        """The denylist as well, now that it can no longer misfire.

        Belt and braces: the allowlist above proves each statement starts as a
        read, and this proves no write is hiding inside one — a CTE that updates,
        or a `select … into`.
        """
        for stmt in self._statements(self.src):
            for verb in ("insert into", "delete from", "drop ", "alter ",
                         "create ", "truncate", "grant ", "revoke ", " into "):
                with self.subTest(statement=stmt[:40], verb=verb.strip()):
                    self.assertNotIn(verb, stmt,
                                     f"the verification query must not {verb.strip()}")

    def test_it_checks_every_table_the_migrations_create(self):
        for table in ("kg_entities", "kg_relationships", "kg_districts", "kg_skills",
                      "kg_schemes", "kg_businesses", "kg_industries", "kg_agriculture",
                      "sync_runs", "kg_vocabulary_map",
                      "user_skill_profile", "user_business_profile",
                      "user_learning_profile", "user_recommendations",
                      "user_activity_summary"):
            with self.subTest(table=table):
                self.assertIn(f"'{table}'", self.src)

    def test_it_checks_the_prerequisite_that_breaks_001(self):
        """001 fails on its last statement without this function."""
        self.assertIn("is_valueweave_admin", self.src)

    def test_it_flags_write_policies(self):
        """No write policy may exist. Any row in that block is a finding."""
        self.assertIn("cmd <> 'SELECT'", self.src)

    def test_the_table_list_matches_the_migrations(self):
        """The count in the query and the count in the SQL files must agree."""
        declared = 0
        for migration in ("knowledge_sync/migrations/001_knowledge_schema.sql",
                          "frontend/migrations/011_repair_vocabulary_crosswalk.sql",
                          "user_intelligence/migrations/001_user_intelligence.sql"):
            body = "\n".join(l.split("--", 1)[0]
                             for l in (ROOT / migration).read_text().splitlines())
            declared += len(re.findall(r"create table(?: if not exists)?\s+[\w\.]+",
                                       body, re.I))
        self.assertIn("tables_expected", self.src)
        self.assertEqual(
            declared, 15,
            "the migrations declare a different number of tables than the "
            "verification query expects; update sql/verify_knowledge_schema.sql")


if __name__ == "__main__":
    unittest.main(verbosity=2)
