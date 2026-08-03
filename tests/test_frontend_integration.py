#!/usr/bin/env python3
"""
Platform v3.0 Step 2 — frontend integration tests.

The frontend is JavaScript; the engines are Python. Nothing in the build catches a
disagreement between them, and a disagreement is silent: a column renamed in Python
makes a Supabase query return nothing, and the page renders its empty state as
though the user simply had no data.

These tests are the contract between the two languages. They are Python because
`tests/run_all.py` is, and because the authoritative half of every fact checked
here lives in Python.

Four groups:

  1. Contract    schema names, table names, column names and RULES_VERSION agree
                 between the JS readers and the Python writers
  2. Wiring      each page imports and renders what the brief asked it to
  3. Additive    no existing component, export or query was removed
  4. Phase 8     the migration creates the four missing features and inserts
                 nothing
"""

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
sys.path.insert(0, str(ROOT))

from user_intelligence import RULES_VERSION                          # noqa: E402
from user_intelligence.config import (OUTPUT_TABLES,                 # noqa: E402
                                      RECOMMENDATION_CATEGORIES, SCORES)
from knowledge_sync.config import TABLE_SPECS, TARGET_SCHEMA         # noqa: E402


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    """`read()` with `//` line comments stripped.

    A test that asserts a symbol is ABSENT must not match the comment explaining
    why it was removed. Step 4 hit exactly that: KnowledgeSearch.jsx documents
    that it no longer reads lib/static-knowledge, and the naive assertion failed
    on its own explanation.

    Line comments only. A `//` inside a string literal or a URL would be stripped
    too, which is wrong in general and harmless here — these assertions look for
    identifiers, and no identifier survives only inside a URL.
    """
    return "\n".join(line.split("//", 1)[0] for line in read(path).splitlines())


NEW_COMPONENTS = [
    # `UnverifiedNotice.jsx` became `TrustPanel.jsx` in PX Phase 3 — see the
    # component header for why the name went with the wording.
    "ConfidenceBadge.jsx", "ProvenanceLine.jsx", "TrustPanel.jsx",
    "KnowledgeCard.jsx", "KnowledgeCardGrid.jsx", "RecommendationRail.jsx",
    "ScoreCard.jsx", "SkillGapPanel.jsx", "DistrictIntelligencePanel.jsx",
    "IntelligencePanel.jsx", "BusinessKnowledgeSection.jsx",
]


# ═══════════════════════════════════════════ 1. the JS ↔ Python contract
class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge_js = read(FE / "lib" / "knowledge.js")
        cls.intel_js = read(FE / "lib" / "intelligence.js")

    def test_knowledge_schema_name_matches_the_sync_config(self):
        """A mismatch here means every knowledge query silently returns nothing."""
        self.assertIn(f'KNOWLEDGE_SCHEMA = "{TARGET_SCHEMA}"', self.knowledge_js)

    def test_intelligence_schema_name_matches_the_migration(self):
        sql = read(ROOT / "user_intelligence" / "migrations"
                   / "001_user_intelligence.sql")
        self.assertIn('INTELLIGENCE_SCHEMA = "user_intelligence"', self.intel_js)
        self.assertIn("create schema if not exists user_intelligence", sql)

    def test_rules_version_matches_the_engine(self):
        """Rows are keyed on rules_version. A drift means reading zero rows."""
        self.assertIn(f'RULES_VERSION = "{RULES_VERSION}"', self.intel_js)

    def test_every_output_table_the_engine_writes_is_read(self):
        for table in OUTPUT_TABLES:
            with self.subTest(table=table):
                self.assertIn(f'"{table}"', self.intel_js,
                              f"the engine writes {table} and nothing reads it")

    def test_knowledge_tables_queried_are_tables_the_sync_creates(self):
        created = {s.name for s in TABLE_SPECS} | {"kg_vocabulary_map"}
        queried = set(re.findall(r'\.from\("(\w+)"\)', self.knowledge_js))
        unknown = queried - created
        self.assertEqual(unknown, set(),
                         f"queries a table the sync does not create: {unknown}")

    def test_status_values_match_the_rule_engine(self):
        from user_intelligence.rules import APPLIED, NO_SIGNAL, UNAVAILABLE
        for value in (APPLIED, NO_SIGNAL, UNAVAILABLE):
            with self.subTest(status=value):
                self.assertIn(f'{value}: "{value}"', self.intel_js)

    def test_no_data_source_sentinel_matches(self):
        from user_intelligence.recommenders import NO_DATA_SOURCE
        self.assertIn(f'NO_DATA_SOURCE = "{NO_DATA_SOURCE}"', self.intel_js)

    def test_every_score_key_has_a_label(self):
        for spec in SCORES:
            with self.subTest(score=spec.key):
                self.assertIn(f"{spec.key}:", self.intel_js)

    def test_every_recommendation_category_has_a_label(self):
        for spec in RECOMMENDATION_CATEGORIES:
            with self.subTest(category=spec.key):
                self.assertIn(f"{spec.key}:", self.intel_js)

    def test_soft_delete_filter_is_applied_to_knowledge_reads(self):
        """The projection soft-deletes. Reads that ignore it show removed rows."""
        self.assertIn('const LIVE = "sync_deleted_at"', self.knowledge_js)
        self.assertGreaterEqual(self.knowledge_js.count(".is(LIVE, null)"), 4)

    def test_javascript_normalisation_matches_python(self):
        """
        The crosswalk join depends on both languages normalising identically.

        Executed rather than eyeballed: a divergence here would make every
        free-text skill lookup miss, and the page would look merely empty.
        """
        cases = ["AC Repair", "Agriculture & Allied", "  Turmeric  ", "PM-KISAN",
                 "Manufacturing (Automotive)", "Food Processing & Preservation",
                 "Café Owner", "Welding (MIG/TIG/Arc)"]
        script = (
            "import('./lib/knowledge.js').then(m=>"
            "console.log(JSON.stringify(" + json.dumps(cases) +
            ".map(c=>m.normaliseTerm(c)))))"
        )
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=FE, capture_output=True, text=True)
        # Skip ONLY when node is genuinely absent. It was skipping whenever the
        # import failed for any reason — and it did, silently, the moment
        # lib/knowledge.js gained an "@/..." import that plain node cannot
        # resolve. A parity check that reports success when it did not run is
        # worse than no parity check.
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        self.assertEqual(
            result.returncode, 0,
            "node is installed but could not import lib/knowledge.js. An "
            "unresolvable import (usually an '@/...' alias) breaks this parity "
            f"check:\n{result.stderr[:600]}")
        self.assertTrue(result.stdout.strip(), f"no output from node:\n{result.stderr[:400]}")
        # stdout only — node writes a MODULE_TYPELESS warning to stderr.
        js = json.loads(result.stdout.strip().splitlines()[-1])

        from user_intelligence.knowledge import KnowledgeSnapshot
        py = [KnowledgeSnapshot.normalise(c) for c in cases]
        self.assertEqual(js, py,
                         "JS normaliseTerm and Python normalise() disagree; every "
                         "crosswalk lookup would miss")


# ═══════════════════════════════════════════════════════ 2. page wiring
class WiringTest(unittest.TestCase):
    def test_all_new_components_exist(self):
        for name in NEW_COMPONENTS:
            with self.subTest(component=name):
                self.assertTrue((FE / "components" / "knowledge" / name).exists())

    def test_dashboard_renders_the_four_rails(self):
        """Phase 2."""
        src = read(FE / "app" / "dashboard" / "page.js")
        self.assertIn("RecommendationRail", src)
        self.assertIn("intelligenceState", src)
        for category in ("business_ideas", "government_schemes", "msmes", "courses"):
            with self.subTest(rail=category):
                self.assertIn(f'category: "{category}"', src)

    def test_dashboard_distinguishes_not_deployed_from_not_computed(self):
        """The two look identical on screen unless the page says otherwise."""
        src = read(FE / "app" / "dashboard" / "page.js")
        self.assertIn("NOT_DEPLOYED", src)
        self.assertIn("intelligence-unavailable", src)

    def test_profile_renders_the_five_scores_and_the_roadmap(self):
        """Phase 3."""
        page = read(FE / "app" / "profile" / "page.js")
        panel = read(FE / "components" / "knowledge" / "IntelligencePanel.jsx")
        self.assertIn("IntelligencePanel", page)
        for key in ("startup_readiness", "business_readiness", "funding_readiness",
                    "ai_readiness", "district_opportunity"):
            with self.subTest(score=key):
                self.assertIn(key, panel)
        self.assertIn("learning-roadmap", panel)
        self.assertIn("SkillGapPanel", panel)

    def test_search_reads_only_the_projection(self):
        """Phase 4, superseded by Step 4.

        Step 2 extended search rather than replacing it: the 56 static JSON
        records answered first and the 647 researched entities answered second.
        Step 4's brief says "Ensure search results come from live package data.
        Remove every mock result", so the static half is gone and this test
        asserts the reverse of what it used to.

        The strong assertion is the absence: a later change that reintroduces
        lib/static-knowledge here fails, rather than silently restoring an
        unsourced result set above a sourced one.
        """
        src = code(FE / "components" / "platform" / "KnowledgeSearch.jsx")
        self.assertIn("searchKnowledge", src)
        self.assertIn("search-researched", src)
        self.assertNotIn("static-knowledge", src,
                         "search must not read the unsourced editorial layer")
        self.assertNotIn("getAllKnowledgeItems", src,
                         "search must not read the unsourced editorial layer")

    def test_district_page_renders_the_intelligence_panel(self):
        """Phase 5."""
        src = read(FE / "app" / "district" / "[slug]" / "page.js")
        self.assertIn("DistrictIntelligencePanel", src)
        self.assertIn("getDistrictKnowledge", src)
        self.assertIn("export default async function DistrictPage", src)

    def test_district_panel_covers_the_five_required_sections(self):
        src = read(FE / "components" / "knowledge" / "DistrictIntelligencePanel.jsx")
        for entity_type in ("MSME", "Industry", "GovernmentScheme", "Institution",
                            "BusinessOpportunity"):
            with self.subTest(section=entity_type):
                self.assertIn(f'type: "{entity_type}"', src)

    def test_business_detail_spans_the_four_packages(self):
        """Phase 6."""
        page = read(FE / "app" / "ideas" / "[slug]" / "page.js")
        section = read(FE / "components" / "knowledge" / "BusinessKnowledgeSection.jsx")
        self.assertIn("BusinessKnowledgeSection", page)
        for relationship in ("PART_OF", "SUPPORTED_BY_SCHEME"):
            with self.subTest(relationship=relationship):
                self.assertIn(relationship, section)
        self.assertIn("resolveTerms", section)

    def test_connections_uses_the_engine_not_static_matching(self):
        """Phase 7."""
        src = read(FE / "app" / "connections" / "page.js")
        self.assertIn("getRecommendations", src)
        self.assertIn('category: "collaborators"', src)
        self.assertIn("skillOverlap", src)

    def test_connections_only_compares_skills_once_accepted(self):
        """Before acceptance the pair is not a working group; the comparison
        would be speculation about people who have not agreed to work together."""
        src = read(FE / "app" / "connections" / "page.js")
        self.assertIn("accepted ? skillOverlap", src)

    def test_every_knowledge_surface_shows_provenance_and_confidence(self):
        """
        The platform's first principle, checked on screen.

        Satisfied either directly or by composing KnowledgeCard, which carries both.
        Requiring a direct import would push every panel to duplicate the badge —
        the opposite of what the brief asks for.
        """
        carriers = ("ConfidenceBadge", "KnowledgeCard")
        for name in ("KnowledgeCard.jsx", "DistrictIntelligencePanel.jsx",
                     "BusinessKnowledgeSection.jsx", "RecommendationRail.jsx"):
            src = read(FE / "components" / "knowledge" / name)
            with self.subTest(component=name):
                self.assertTrue(any(c in src for c in carriers),
                                f"{name} renders knowledge without confidence")
                self.assertTrue("Provenance" in src or "KnowledgeCard" in src,
                                f"{name} renders knowledge without provenance")

    def test_knowledge_card_itself_carries_both(self):
        """The one component the others rely on must not delegate further."""
        src = read(FE / "components" / "knowledge" / "KnowledgeCard.jsx")
        self.assertIn("ConfidenceBadge", src)
        self.assertIn("ProvenanceLine", src)

    def test_the_trust_panel_is_computed_not_hardcoded(self):
        """It must not still be claiming the same thing after verification lands.

        This asserted `if (!unverified) return null` — the old notice removed
        itself entirely once `verified === total`, which is how it stayed
        honest. PX Phase 3 kept the property and moved it: the panel always
        renders, because "here is where this came from" does not expire, but
        the sentence about what to do next is chosen from the same computed
        flag. So the check is no longer "does it disappear" but "are there two
        different sentences, and is a real value choosing between them".
        """
        src = read(FE / "components" / "knowledge" / "TrustPanel.jsx")
        self.assertIn("hasUnverified === null ? Math.max(0, total - verified) > 0", src,
                      "the panel must still read the verification counts")
        self.assertIn("pending", src)
        # Two branches, and neither may be a placeholder.
        self.assertIn("check the latest details with the official authority", src)
        self.assertIn("has confirmed this against the official source", src)
        self.assertIn("data-review-state", src,
                      "support and tests need to see which sentence is showing")

    def test_no_surface_still_warns_that_a_human_has_not_read_the_row(self):
        """The Phase 3 brief in one assertion.

        "This record has not yet been reviewed by a person" was on every
        knowledge detail page, in alert amber, above the content.
        """
        banned = ("reviewed by a person", "not yet checked every line",
                  "machine-validated", "Treat it as a starting point")
        offenders = []
        for root in (FE / "app", FE / "components", FE / "lib"):
            for path in sorted(root.rglob("*.js")) + sorted(root.rglob("*.jsx")):
                if "admin" in path.parts:
                    continue
                # Comments stripped — both `//` and `/* */`, the latter because
                # a JSX comment is `{/* ... */}`. TrustPanel.jsx and the detail
                # page both quote the old copy at length, and that record is
                # precisely why it does not come back.
                body = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
                body = "\n".join(l.split("//", 1)[0] for l in body.splitlines())
                for phrase in banned:
                    if phrase in body:
                        offenders.append(f"{path.relative_to(FE)}: {phrase!r}")
        self.assertEqual(offenders, [], "\n  ".join(offenders))

    def test_score_card_never_renders_unavailable_as_zero(self):
        """The single most misleading thing this UI could do."""
        src = read(FE / "components" / "knowledge" / "ScoreCard.jsx")
        self.assertIn("scoreLabel", src)
        intel = read(FE / "lib" / "intelligence.js")
        self.assertIn('return "—"', intel)

    def test_empty_states_are_distinguished(self):
        """The five states mean different things and share one vocabulary.

        Step 2 defined three states inline in KnowledgeCardGrid. Step 4 raised
        that to the brief's five and moved the copy into KnowledgeEmptyState, so
        both components name the same thing the same way — a grid and a full-page
        state that disagree about what EMPTY means are worse than either alone.

        NOT_COMPUTED stays local to the grid: it is specific to per-user
        intelligence and has no shared-knowledge equivalent.
        """
        shared = read(FE / "components" / "knowledge" / "KnowledgeEmptyState.jsx")
        for state in ("NOT_DEPLOYED", "EMPTY", "NO_MATCH",
                      "NOT_AVAILABLE_YET", "NO_DATA_SOURCE"):
            with self.subTest(state=state):
                self.assertIn(state, shared)

        grid = read(FE / "components" / "knowledge" / "KnowledgeCardGrid.jsx")
        self.assertIn("NOT_COMPUTED", grid)
        self.assertIn("KnowledgeEmptyState", grid,
                      "the grid must share the state vocabulary, not fork it")


# ═══════════════════════════════════════════════ 3. additive, not a rewrite
class AdditiveTest(unittest.TestCase):
    TOUCHED = [
        "frontend/app/dashboard/page.js",
        "frontend/app/profile/page.js",
        "frontend/app/connections/page.js",
        "frontend/app/district/[slug]/page.js",
        "frontend/app/ideas/[slug]/page.js",
        "frontend/components/platform/KnowledgeSearch.jsx",
    ]

    STEP_COMMIT_SUBJECT = ("Platform v3.0 Step 2: end-to-end application "
                           "integration")

    def test_no_page_lost_more_than_a_handful_of_lines(self):
        """
        Integration should add, not rewrite.

        A deletion here is not automatically wrong — a query gains a column, a
        function becomes async — but a large one means a page was reimplemented,
        which the brief rules out.

        Measured against Step 2's own commit rather than `main...HEAD`. A branch
        diff is empty once the branch merges, so the test would then pass by
        examining nothing — which is worse than having no test, because it reports
        confidence it never earned. The step's commit is fixed in history, so the
        claim keeps being checked for as long as the repository exists.
        """
        out = self._numstat_for_step_commit()
        if out is None:
            # Before the step is committed there is no commit to point at, so fall
            # back to the working tree. This branch is the only one that can go
            # unmeasured, and only while the work is uncommitted.
            out = subprocess.run(["git", "diff", "--numstat", "main", "--"]
                                 + self.TOUCHED, cwd=ROOT,
                                 capture_output=True, text=True).stdout
        if not out.strip():
            # Still a failure — a test that examines nothing must not report a
            # pass. But distinguish "the claim is false" from "the evidence was
            # thrown away by the checkout", because they need opposite responses.
            shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                                     cwd=ROOT, capture_output=True,
                                     text=True).stdout.strip() == "true"
            depth = subprocess.run(["git", "rev-list", "--count", "HEAD"],
                                   cwd=ROOT, capture_output=True, text=True).stdout.strip()
            self.fail(
                f"no diff found for Step 2 ({self.STEP_COMMIT_SUBJECT!r}) in either "
                f"its commit or the working tree.\n"
                + (f"  CAUSE: SHALLOW clone — {depth} commit(s). The commit exists in "
                   f"history; this checkout does not have it. CI must use "
                   f"`fetch-depth: 0`.\n" if shallow else
                   "  History is complete, so the commit is genuinely missing.\n")
                + "  This test cannot verify anything and must not pass.")
        for line in out.strip().splitlines():
            added, removed, path = line.split("\t")
            with self.subTest(file=path):
                self.assertLess(int(removed), 12,
                                f"{path} removed {removed} lines — that is a rewrite, "
                                f"not an integration")

    def _numstat_for_step_commit(self):
        """`--numstat` for the touched files in Step 2's commit, or None if absent."""
        log = subprocess.run(["git", "log", "--all", "--format=%H%x09%s"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        sha = next((line.split("\t", 1)[0] for line in log.splitlines()
                    if line.split("\t", 1)[-1].strip() == self.STEP_COMMIT_SUBJECT),
                   None)
        if sha is None:
            return None
        return subprocess.run(["git", "diff", "--numstat", f"{sha}^", sha, "--"]
                              + self.TOUCHED, cwd=ROOT,
                              capture_output=True, text=True).stdout

    def test_existing_default_exports_survive(self):
        for rel in self.TOUCHED:
            src = read(ROOT / rel)
            with self.subTest(file=rel):
                self.assertRegex(src, r"export default (async )?function",
                                 "the page lost its default export")

    def test_existing_test_ids_survive(self):
        """data-testid attributes are a contract with whatever tests the app has."""
        expected = {
            "frontend/app/dashboard/page.js": ["dashboard-greeting", "feed-list",
                                               "dashboard-search"],
            "frontend/app/profile/page.js": [],
            # `tab-${k}` is a template literal, so the rendered id is dynamic and
            # the literal string never appears in the source.
            "frontend/app/connections/page.js": ["tab-${k}", "connections-empty",
                                                 "conn-status-${c.id}"],
        }
        for rel, ids in expected.items():
            src = read(ROOT / rel)
            for tid in ids:
                with self.subTest(file=rel, testid=tid):
                    self.assertIn(tid, src)

    def test_no_new_runtime_dependency(self):
        """The brief: no new backend architecture. Nor a new client library."""
        pkg = json.loads(read(FE / "package.json"))
        expected = {
            "@supabase/ssr", "@supabase/supabase-js", "clsx", "gray-matter",
            "lucide-react", "marked", "next", "next-mdx-remote", "react",
            "react-dom", "remark-gfm",
        }
        self.assertEqual(set(pkg["dependencies"]), expected,
                         "a runtime dependency was added")

    def test_frontend_still_makes_no_direct_http_calls_to_a_python_service(self):
        """
        The engines stay behind Supabase.

        Calling a Python service from here would be the "new backend architecture"
        the brief rules out, and would need a deployment, auth and a CORS surface
        that do not exist.
        """
        offenders = []
        for path in list((FE / "app").rglob("*.js")) + \
                list((FE / "components").rglob("*.jsx")) + \
                list((FE / "lib").rglob("*.js")):
            src = read(path)
            if "fetch(" not in src or "knowledge" in path.name.lower():
                continue
            # A same-origin relative fetch is this app calling its own route
            # handler, which is not a service and has no deployment, auth or
            # CORS surface of its own. LiveSearch does exactly one of these,
            # to /api/search/suggest, because the search index has to stay in
            # server memory. Anything absolute is what this test is about.
            calls = re.findall(r'fetch\(\s*[`"\']([^`"\']*)', src)
            if any(not c.startswith("/") for c in calls) or not calls:
                offenders.append(str(path.relative_to(FE)))
        self.assertEqual(offenders, [], f"direct fetch() to a service: {offenders}")

    def test_the_api_surface_is_one_handler(self):
        """A frontend with an API surface can grow a backend by accident.

        `/api/search/suggest` is the only one, and it exists for a measured
        reason — the search index has to stay in server memory, see the file.
        `/auth/callback` is Supabase's OAuth return and predates all of this.
        A third appearing without a conversation is the drift this guards.
        """
        routes = sorted(str(p.relative_to(FE)) for p in (FE / "app").rglob("route.js"))
        self.assertEqual(routes, ["app/api/search/suggest/route.js",
                                  "app/auth/callback/route.js"])


# ═══════════════════════════════════════════════════ 4. Phase 8 migration
class MissingFeaturesMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = FE / "migrations" / "010_missing_application_features.sql"
        cls.sql = read(cls.path)

    def test_migration_exists(self):
        self.assertTrue(self.path.exists())

    def test_all_four_missing_features_get_a_table(self):
        for table in ("assessment_results", "mentor_profiles", "events", "teams",
                      "team_members"):
            with self.subTest(table=table):
                self.assertIn(f"create table if not exists public.{table}", self.sql)

    def test_no_seed_data_is_inserted(self):
        """
        The core rule of this phase.

        A fabricated mentor is an unsourced claim about a person, and a fabricated
        event is an unsourced claim about the world. Both would make the
        intelligence engine's NO_DATA_SOURCE categories start returning rows that
        describe nobody.
        """
        statements = "\n".join(line.split("--", 1)[0]
                               for line in self.sql.lower().splitlines())
        for forbidden in ("insert into", "copy ", "values ("):
            with self.subTest(statement=forbidden):
                self.assertNotIn(forbidden, statements)

    def test_rls_is_enabled_on_every_new_table(self):
        for table in ("assessment_results", "mentor_profiles", "events", "teams",
                      "team_members"):
            with self.subTest(table=table):
                self.assertIn(f"alter table public.{table} enable row level security",
                              self.sql)

    def test_assessment_and_mentor_rows_are_owner_scoped(self):
        self.assertIn("auth.uid() = user_id", self.sql)

    def test_mentors_are_opt_in_not_inferred(self):
        """The engine refused to infer a mentor. The schema must not either."""
        self.assertIn("is_active         boolean     not null default false", self.sql)

    def test_no_existing_table_is_altered_or_dropped(self):
        statements = "\n".join(line.split("--", 1)[0]
                               for line in self.sql.lower().splitlines())
        self.assertNotIn("drop table", statements)
        self.assertNotIn("alter table public.profiles add", statements)
        self.assertNotIn("alter table public.connections", statements)

    def test_engine_still_reports_these_inputs_as_missing(self):
        """
        A migration file is not a deployed table.

        Until it is applied and populated, the engine must keep saying so — a
        written migration that flipped the capability report would be a lie about
        what the product can do.
        """
        from user_intelligence.config import INPUTS, MISSING
        for name in ("assessment_results", "teams"):
            with self.subTest(input=name):
                self.assertEqual(INPUTS[name].status, MISSING)


if __name__ == "__main__":
    unittest.main(verbosity=2)


# ═══════════════════════════════════════════════════ 5. Step 3 — knowledge UI
class KnowledgeUiTest(unittest.TestCase):
    """
    Platform v3.0 Step 3 — the pages that let a user actually read Packages001–008.

    Step 2 proved the frontend could reach the knowledge schema. Step 3 is where a
    person can browse it, open a record, and walk the graph from one entity to the
    next. These tests protect the two properties that make that work:

      * **Every knowledge item names its source package.** The brief's general
        requirement, and the platform's first principle on screen.
      * **Every knowledge item links somewhere.** A detail page nothing links to is
        a page nobody reaches, and the graph stops feeling connected.
    """

    STEP3_COMPONENTS = [
        "SourceBadge.jsx", "AttributeGrid.jsx", "RelatedEntities.jsx",
        "EntityHeader.jsx", "KnowledgePagination.jsx", "KnowledgeEmptyState.jsx",
        "IntelligenceSummaryCard.jsx", "LatestKnowledgeCard.jsx",
        "GraphSourceNote.jsx",
    ]

    @classmethod
    def setUpClass(cls):
        cls.klib = read(FE / "lib" / "knowledge.js")
        cls.detail = read(FE / "app" / "knowledge" / "[type]" / "[slug]" / "page.js")
        cls.explorer = read(FE / "app" / "knowledge" / "page.js")
        cls.dashboard = read(FE / "app" / "dashboard" / "page.js")

    # ── the data layer ──────────────────────────────────────────────────────
    def test_step3_readers_exist(self):
        for fn in ("getEntityBySlug", "getEntityDetail", "getRelatedByType",
                   "listEntities", "typeCounts", "latestKnowledge", "hrefFor",
                   "entityIdFor", "slugOf"):
            with self.subTest(fn=fn):
                self.assertIn(f"export async function {fn}",
                              self.klib.replace("export function", "export async function"),
                              f"lib/knowledge.js is missing {fn}")

    def test_detail_tables_match_the_sync_specs(self):
        """
        A detail page reads a per-type table by name. If knowledge_sync renames one,
        the page returns nothing and renders an empty state — the exact silent
        failure this suite exists to prevent.
        """
        declared = {t.name for t in TABLE_SPECS}
        for table in ("kg_districts", "kg_skills", "kg_schemes", "kg_businesses",
                      "kg_industries", "kg_agriculture"):
            with self.subTest(table=table):
                self.assertIn(table, declared, f"{table} is not a synced table")
                self.assertIn(f'"{table}"', self.klib,
                              f"lib/knowledge.js never reads {table}")

    def test_detail_attribute_columns_exist_in_the_synced_tables(self):
        """Every column the detail page renders must be one the sync projects."""
        by_table = {t.name: set(t.columns) for t in TABLE_SPECS}
        checks = [
            ("kg_schemes", ["ministry", "financial_assistance", "application_mode",
                            "official_portal", "objective"]),
            ("kg_skills", ["nsqf_level", "demand_level", "automation_risk",
                           "learning_duration"]),
            ("kg_businesses", ["investment_range", "minimum_investment",
                               "risk_level", "ai_readiness"]),
            ("kg_districts", ["population", "literacy_rate_pct", "mandal_count"]),
        ]
        for table, columns in checks:
            for column in columns:
                with self.subTest(table=table, column=column):
                    self.assertIn(column, by_table[table],
                                  f"{table}.{column} is rendered but not synced")
                    # Either a quoted grid key or direct property access — the
                    # official portal is a call-to-action button, not a table row,
                    # and pinning the syntax would make the test about style.
                    used = (f'"{column}"' in self.detail
                            or f".{column}" in self.detail)
                    self.assertTrue(used,
                                    f"{column} is synced but the detail page never reads it")

    def test_entity_id_scheme_matches_the_graph_builder(self):
        """
        Slug -> id reconstruction assumes `vw:<type_lowercase>:<slug>`. If the
        builder's scheme changed, every detail page would 404 while the data was
        present — so the assumption is checked against build_graph.py, not trusted.
        """
        builder = read(ROOT / "knowledge_graph" / "build_graph.py")
        self.assertIn('f"vw:{TYPE_SLUG[etype]}:{slug(canonical_name)}"', builder)
        self.assertIn("`vw:${type.toLowerCase()}:${slug}`", self.klib)

    # ── pages ───────────────────────────────────────────────────────────────
    def test_step3_components_exist(self):
        for name in self.STEP3_COMPONENTS:
            with self.subTest(component=name):
                self.assertTrue((FE / "components" / "knowledge" / name).exists(),
                                f"missing component {name}")

    def test_explorer_browses_every_package(self):
        """Priority 2: browse Packages 001, 004, 005, 006, 007, 008."""
        for pkg in ("Package001_Geography", "Package004_Industries",
                    "Package005_Agriculture", "Package006_Skills_and_Training",
                    "Package007_Government_Schemes", "Package008_MSME"):
            with self.subTest(package=pkg):
                self.assertIn(pkg, self.explorer)

    def test_explorer_paginates_rather_than_dumping_every_row(self):
        self.assertIn("KnowledgePagination", self.explorer)
        self.assertIn("PAGE_SIZE", self.explorer)

    def test_detail_page_keeps_the_static_route_working(self):
        """
        The graph namespace is singular, the pre-existing static namespace plural.
        Losing the static branch would 404 the 56 pages that already worked.
        """
        self.assertIn("getKnowledgeItem", self.detail)
        self.assertIn("generateStaticParams", self.detail)
        self.assertIn("StaticDetail", self.detail)

    def test_graph_and_static_type_namespaces_do_not_collide(self):
        static_types = set(re.findall(r"^\s{2}(\w+):", read(FE / "lib" / "static-knowledge.js"), re.M))
        graph_types = set(re.findall(r"^\s{2}(\w+):\s*\"", self.klib, re.M))
        overlap = static_types & graph_types
        self.assertEqual(overlap, set(),
                         f"a URL type resolves to both namespaces: {overlap}")

    def test_dashboard_covers_every_priority_one_card(self):
        for category in ("business_ideas", "government_schemes", "courses",
                         "msmes", "industries", "markets"):
            with self.subTest(category=category):
                self.assertIn(f'category: "{category}"', self.dashboard)
        self.assertIn("IntelligenceSummaryCard", self.dashboard)
        self.assertIn("LatestKnowledgeCard", self.dashboard)

    # ── the two general requirements ────────────────────────────────────────
    def test_every_knowledge_surface_names_its_source_package(self):
        surfaces = {
            "app/knowledge/page.js": "explorer",
            "components/knowledge/EntityHeader.jsx": "detail header",
            "components/knowledge/LatestKnowledgeCard.jsx": "latest knowledge",
        }
        for rel, label in surfaces.items():
            with self.subTest(surface=label):
                self.assertIn("SourceBadge", read(FE / rel),
                              f"{label} does not name the source package")

    def test_every_recommendation_category_can_reach_a_detail_page(self):
        """
        Priority 1: "each card must link to a detailed page". Graph-backed
        categories previously returned null from HREF_BUILDERS, so their cards were
        dead ends even though the engine emits a global_entity_id.
        """
        rail = read(FE / "components" / "knowledge" / "RecommendationRail.jsx")
        self.assertIn("graphHref", rail)
        for category in ("government_schemes", "msmes", "industries", "markets", "courses"):
            with self.subTest(category=category):
                self.assertRegex(rail, rf"{category}:\s*graphHref",
                                 f"{category} cards do not link anywhere")

    def test_recommendation_item_ids_are_graph_ids(self):
        """`hrefFor` assumes item_id is the global_entity_id. Verified in Python."""
        recommenders = read(ROOT / "user_intelligence" / "recommenders.py")
        self.assertIn('item_id=sid', recommenders)

    def test_search_supports_type_filters(self):
        search = read(FE / "components" / "platform" / "KnowledgeSearch.jsx")
        self.assertIn("SEARCH_FILTERS", search)
        self.assertIn("entityType: typeFilter", search)
        for entity_type in ("BusinessOpportunity", "Skill", "GovernmentScheme",
                            "District", "Industry", "Crop", "MSME"):
            with self.subTest(entity_type=entity_type):
                self.assertIn(f'"{entity_type}"', search)

    def test_search_results_link_to_detail_pages(self):
        self.assertIn("hrefFor(e)", read(FE / "components" / "platform" / "KnowledgeSearch.jsx"))

    def test_district_panel_covers_every_priority_six_group(self):
        panel = read(FE / "components" / "knowledge" / "DistrictIntelligencePanel.jsx")
        for entity_type in ("Industry", "MSME", "BusinessOpportunity", "GovernmentScheme",
                            "Institution", "TrainingProvider", "Crop"):
            with self.subTest(entity_type=entity_type):
                self.assertIn(f'type: "{entity_type}"', panel)
        self.assertIn("hrefFor(row)", panel)

    def test_empty_states_distinguish_their_three_causes(self):
        """
        NOT_DEPLOYED, EMPTY and NO_MATCH look identical to a user and mean opposite
        things. Collapsing them is the easiest way this platform could mislead.
        """
        empty = read(FE / "components" / "knowledge" / "KnowledgeEmptyState.jsx")
        for reason in ("SCHEMA_UNREACHABLE", "EMPTY", "NO_MATCH"):
            with self.subTest(reason=reason):
                self.assertIn(reason, empty)

    def test_sentinels_are_never_rendered_to_a_user(self):
        grid = read(FE / "components" / "knowledge" / "AttributeGrid.jsx")
        self.assertIn("PENDING_VERIFICATION", grid)
        self.assertIn("PENDING_GEOCODING", grid)
        self.assertIn("SENTINELS", grid)

    # ── still additive ──────────────────────────────────────────────────────
    def test_the_cms_pages_still_prefer_the_cms(self):
        """
        `/schemes` and `/skills` fall back to the graph. They must not *replace* the
        CMS: an admin who publishes a scheme still overrides the researched row.
        """
        fallback = read(FE / "lib" / "kg-fallback.js")
        self.assertIn("cmsItems.length > 0", fallback)
        self.assertIn('source: "CMS"', fallback)

    def test_no_new_runtime_dependency(self):
        pkg = json.loads(read(FE / "package.json"))
        expected = {
            "@supabase/ssr", "@supabase/supabase-js", "clsx", "gray-matter",
            "lucide-react", "marked", "next", "next-mdx-remote", "react",
            "react-dom", "remark-gfm",
        }
        self.assertEqual(set(pkg["dependencies"]), expected,
                         "Step 3 added a runtime dependency")
