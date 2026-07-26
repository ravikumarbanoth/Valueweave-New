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


NEW_COMPONENTS = [
    "ConfidenceBadge.jsx", "ProvenanceLine.jsx", "UnverifiedNotice.jsx",
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
        if result.returncode != 0 or not result.stdout.strip():
            self.skipTest(f"node unavailable: {result.stderr[:160]}")
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

    def test_search_uses_the_projection_without_replacing_static_search(self):
        """Phase 4 — extended, not replaced."""
        src = read(FE / "components" / "platform" / "KnowledgeSearch.jsx")
        self.assertIn("searchKnowledge", src)
        self.assertIn("getAllKnowledgeItems", src,
                      "the existing static search must survive")
        self.assertIn("search-researched", src)

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

    def test_unverified_notice_is_computed_not_hardcoded(self):
        """It must vanish on its own once verification arrives."""
        src = read(FE / "components" / "knowledge" / "UnverifiedNotice.jsx")
        self.assertIn("if (!unverified) return null", src)

    def test_score_card_never_renders_unavailable_as_zero(self):
        """The single most misleading thing this UI could do."""
        src = read(FE / "components" / "knowledge" / "ScoreCard.jsx")
        self.assertIn("scoreLabel", src)
        intel = read(FE / "lib" / "intelligence.js")
        self.assertIn('return "—"', intel)

    def test_empty_states_are_distinguished(self):
        """NO_DATA_SOURCE, NO_MATCHES and NOT_COMPUTED mean different things."""
        src = read(FE / "components" / "knowledge" / "KnowledgeCardGrid.jsx")
        for state in ("NO_DATA_SOURCE", "NOT_COMPUTED", "NOT_DEPLOYED"):
            with self.subTest(state=state):
                self.assertIn(state, src)


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

    def test_no_page_lost_more_than_a_handful_of_lines(self):
        """
        Integration should add, not rewrite.

        A deletion here is not automatically wrong — a query gains a column, a
        function becomes async — but a large one means a page was reimplemented,
        which the brief rules out.
        """
        # Committed diff first; fall back to the working tree so this is meaningful
        # before the branch is committed as well as after.
        out = subprocess.run(["git", "diff", "--numstat", "main...HEAD", "--"]
                             + self.TOUCHED, cwd=ROOT,
                             capture_output=True, text=True).stdout
        if not out.strip():
            out = subprocess.run(["git", "diff", "--numstat", "main", "--"]
                                 + self.TOUCHED, cwd=ROOT,
                                 capture_output=True, text=True).stdout
        if not out.strip():
            self.skipTest("no diff against main in either the index or the tree")
        for line in out.strip().splitlines():
            added, removed, path = line.split("\t")
            with self.subTest(file=path):
                self.assertLess(int(removed), 12,
                                f"{path} removed {removed} lines — that is a rewrite, "
                                f"not an integration")

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
            if "fetch(" in src and "knowledge" not in path.name.lower():
                offenders.append(str(path.relative_to(FE)))
        self.assertEqual(offenders, [], f"direct fetch() introduced: {offenders}")


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
