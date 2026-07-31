#!/usr/bin/env python3
"""
Platform v3.0 Step 4 — Frontend Knowledge Activation.

WHAT THESE TESTS ARE FOR
------------------------
Step 4 replaced placeholders with live knowledge. The failure mode it guards
against is not a crash — it is a regression back into a state that *looks* fine:
a "Coming Soon" chip reintroduced on a capability that works, an entity type
added to the graph with no route into it, a recommendation card that quietly
stops showing its reason.

Every one of those renders perfectly. Only a test notices.

The suite reads source rather than a rendered DOM, deliberately. The repository
has no browser-test harness and adding one for this step would be a larger
change than the step itself; `npx next build` already proves every page renders,
and these assert the things a build cannot see.

    python3 tests/run_all.py --suite frontend_activation
"""

import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
APP = FE / "app"
COMPONENTS = FE / "components"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    """`read()` with comments stripped, so absence assertions match real code.

    Both forms, because both appear in this codebase: `//` line comments, and
    `/* */` blocks — which in JSX are written `{/* */}` and are the form used to
    annotate markup. Stripping only the first produced a false positive the
    moment a component documented the placeholder it had removed.

    The leftover `{}` from a JSX comment is left in place. These assertions look
    for identifiers and string literals; a stray brace matches nothing.
    """
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def sources(*roots):
    """Every .js/.jsx under the given roots, excluding admin.

    Admin pages are internal tooling for a handful of operators. The brief is
    about what a user meets, and holding a CMS editor to the same placeholder
    rules would produce noise rather than signal.
    """
    out = []
    for root in roots:
        for path in sorted(Path(root).rglob("*.js")) + sorted(Path(root).rglob("*.jsx")):
            if "admin" in path.parts:
                continue
            out.append(path)
    return out


def rel(path):
    return str(Path(path).relative_to(FE))


# ═══════════════════════════════════════════════ 1. placeholders are gone
class PlaceholderRemovalTest(unittest.TestCase):
    """Phase 1 and the REMOVE list."""

    #: Matched against comment-stripped source, so a file may still *explain*
    #: that it used to say "Coming Soon" — several do, and that history is worth
    #: keeping. What it may not do is render it.
    BANNED = [
        (r"Coming\s+Soon", "Coming Soon"),
        (r">\s*Planned\s*<", "a bare 'Planned' chip"),
        (r"Knowledge\s+Base\s+Coming", "Knowledge Base Coming Soon"),
    ]

    def test_no_user_facing_coming_soon_remains(self):
        offenders = []
        for path in sources(APP, COMPONENTS):
            src = code(path)
            for pattern, label in self.BANNED:
                if re.search(pattern, src, re.IGNORECASE):
                    offenders.append(f"{rel(path)}: {label}")
        self.assertEqual(
            offenders, [],
            "Every capability must declare LIVE, NOT_AVAILABLE_YET or "
            "NO_DATA_SOURCE via CapabilityStatus.\n  " + "\n  ".join(offenders))

    def test_the_static_knowledge_layer_is_no_longer_displayed(self):
        """Phase 2 — replace what has a live backend equivalent.

        lib/static-knowledge.js survives as a URL-compatibility shim for 56
        indexed detail pages. Nothing may *surface* it: not the homepage, not
        search, not a card grid. The one permitted importer is the detail route
        that serves those URLs.
        """
        allowed = {"app/knowledge/[type]/[slug]/page.js"}
        importers = [
            rel(p) for p in sources(APP, COMPONENTS)
            if "static-knowledge" in code(p)
        ]
        self.assertEqual(
            sorted(set(importers) - allowed), [],
            "only the legacy detail route may read the editorial JSON layer")

    def test_the_dead_static_exports_are_gone(self):
        src = read(FE / "lib" / "static-knowledge.js")
        for symbol in ("featuredKnowledge", "futureInfrastructureModules"):
            with self.subTest(symbol=symbol):
                self.assertNotIn(f"export const {symbol}", src)

    def test_the_legacy_detail_route_says_it_is_superseded(self):
        """A page nothing links to is still reachable from a search engine."""
        src = read(APP / "knowledge" / "[type]" / "[slug]" / "page.js")
        self.assertIn("static-superseded-notice", src)

    def test_the_placeholder_district_dashboard_was_removed(self):
        self.assertFalse(
            (APP / "districts" / "components" / "DistrictModuleCards.jsx").exists(),
            "the four Coming Soon district cards were replaced by live knowledge")


# ═══════════════════════════════════════════════ 2. the five empty states
class EmptyStateTest(unittest.TestCase):
    """The EMPTY STATES section of the brief."""

    REQUIRED = ["NOT_DEPLOYED", "EMPTY", "NO_MATCH",
                "NOT_AVAILABLE_YET", "NO_DATA_SOURCE"]

    def setUp(self):
        self.src = read(COMPONENTS / "knowledge" / "KnowledgeEmptyState.jsx")

    def test_all_five_states_exist(self):
        for state in self.REQUIRED:
            with self.subTest(state=state):
                self.assertIn(state, self.src)

    def test_each_state_explains_why(self):
        """"Do NOT use generic messages" — every state carries a body."""
        block = self.src[self.src.index("const states = {"):]
        for state in self.REQUIRED:
            with self.subTest(state=state):
                start = block.index(f"{state}: {{")
                body = block[start:start + 700]
                self.assertIn("body:", body,
                              f"{state} must say why it is empty")

    def test_the_deployment_states_name_their_dependency(self):
        """NOT_DEPLOYED and EMPTY are our fault, so they say what to run."""
        for state in ("NOT_DEPLOYED", "EMPTY"):
            with self.subTest(state=state):
                start = self.src.index(f"{state}: {{")
                self.assertIn("dependency:", self.src[start:start + 900])

    def test_the_old_reason_name_still_resolves(self):
        """lib/knowledge.js returns SCHEMA_UNREACHABLE; callers still pass it."""
        self.assertIn("SCHEMA_UNREACHABLE", self.src)
        self.assertIn("ALIASES", self.src)

    def test_the_card_grid_shares_the_vocabulary(self):
        grid = read(COMPONENTS / "knowledge" / "KnowledgeCardGrid.jsx")
        self.assertIn("KnowledgeEmptyState", grid,
                      "two components must not define empty states separately")


# ═══════════════════════════════════════════════ 3. every type is reachable
class NavigationTest(unittest.TestCase):
    """Phase 12 — "one connected knowledge network".

    The regression this catches: a builder adds an entity type, the graph gains
    entities, and no route exists for them. `hrefFor()` falls back to a search
    URL, so nothing breaks and nothing says anything. Before Step 4 this had
    already happened to five types and fifty entities.
    """

    @classmethod
    def setUpClass(cls):
        with open(ROOT / "knowledge_graph" / "entities" / "entities.csv",
                  encoding="utf-8") as fh:
            cls.entity_types = {r["entity_type"] for r in csv.DictReader(fh)}
        cls.knowledge = read(FE / "lib" / "knowledge.js")
        block = cls.knowledge[cls.knowledge.index("export const TYPE_BY_URL"):]
        block = block[:block.index("};")]
        cls.mapped = set(re.findall(r':\s*"([A-Za-z]+)"', block))

    def test_every_graph_entity_type_has_a_url(self):
        missing = sorted(self.entity_types - self.mapped)
        self.assertEqual(
            missing, [],
            "these types have no detail route, so hrefFor() sends them to "
            f"search: {missing}")

    def test_no_url_maps_to_a_type_the_graph_does_not_have(self):
        """A route to nothing 404s for every slug and nobody notices."""
        extra = sorted(self.mapped - self.entity_types)
        self.assertEqual(extra, [], f"unused type routes: {extra}")

    def test_the_explorer_offers_every_type_that_has_entities(self):
        src = read(APP / "knowledge" / "page.js")
        block = src[src.index("const SECTIONS = ["):src.index("export default")]
        listed = set(re.findall(r'\["([A-Za-z]+)",', block))
        missing = sorted(self.entity_types - listed)
        self.assertEqual(missing, [],
                         f"not browsable from the explorer: {missing}")

    def test_related_entities_labels_every_type(self):
        """An unlabelled type renders its raw class name at the user."""
        src = read(COMPONENTS / "knowledge" / "RelatedEntities.jsx")
        block = src[src.index("const TYPE_LABELS"):src.index("const VIA")]
        labelled = set(re.findall(r"^\s*([A-Za-z]+):", block, re.MULTILINE))
        missing = sorted(self.entity_types - labelled)
        self.assertEqual(missing, [], f"unlabelled in related lists: {missing}")

    def test_recommendation_supporting_links_cover_every_type(self):
        """The rail derives entity type from the id prefix; it must know them all."""
        src = read(COMPONENTS / "knowledge" / "RecommendationRail.jsx")
        block = src[src.index("const TYPE_FROM_ID"):src.index("function supportingLinks")]
        known = set(re.findall(r':\s*"([A-Za-z]+)"', block))
        missing = sorted(self.entity_types - known)
        self.assertEqual(missing, [], f"supporting entities would not link: {missing}")


# ═══════════════════════════════════════════════ 4. pages read live knowledge
class KnowledgeBindingTest(unittest.TestCase):
    """Phases 3–10 — the pages that must consume the projection."""

    #: page -> the symbols proving it reads live knowledge rather than a fixture.
    BOUND = {
        "components/HomeFeatureGrid.jsx": ["featuredByType", "typeCounts"],
        "components/platform/KnowledgeSearch.jsx": ["searchKnowledge"],
        "app/knowledge/page.js": ["listEntities", "typeCounts"],
        "app/knowledge/[type]/[slug]/page.js": ["getEntityBySlug", "getRelatedByType"],
        "app/districts/page.js": ["getEntitiesByType"],
        "app/districts/[slug]/page.js": ["getDistrictKnowledge", "resolveTerms"],
        "app/district/[slug]/page.js": ["getDistrictKnowledge", "resolveTerms"],
        "app/dashboard/page.js": ["latestKnowledge", "getRecommendationsByCategory"],
        "app/readiness/components/ReadinessSections.jsx": ["typeCounts"],
        "app/manufacturing/components/ManufacturingSections.jsx": ["typeCounts"],
        "app/scale/components/ScaleSections.jsx": ["typeCounts"],
        "app/network/components/NetworkSections.jsx": ["typeCounts"],
        "app/ai/components/AiSections.jsx": ["typeCounts"],
        "components/knowledge/BusinessKnowledgeSection.jsx": ["resolveTerms", "getNeighbours"],
    }

    def test_every_declared_page_reads_the_projection(self):
        for page, symbols in self.BOUND.items():
            src = code(FE / page)
            for symbol in symbols:
                with self.subTest(page=page, symbol=symbol):
                    self.assertIn(symbol, src)

    def test_module_dashboards_are_server_components(self):
        """They query the projection, so they must not be client components."""
        for page in ("app/readiness/components/ReadinessSections.jsx",
                     "app/manufacturing/components/ManufacturingSections.jsx",
                     "app/scale/components/ScaleSections.jsx",
                     "app/network/components/NetworkSections.jsx",
                     "app/ai/components/AiSections.jsx"):
            with self.subTest(page=page):
                src = read(FE / page)
                self.assertNotIn('"use client"', src)
                self.assertIn("export default async function", src)

    def test_the_idea_library_shows_resolved_entities_not_only_failures(self):
        """Phase 10 — it resolved skills and districts, then rendered neither."""
        src = read(COMPONENTS / "knowledge" / "BusinessKnowledgeSection.jsx")
        self.assertIn("idea-resolved", src)
        self.assertIn("skillHits?.resolved", src)
        self.assertIn("districtHits?.resolved", src)

    def test_editorial_content_was_not_removed(self):
        """Phase 10 — "Do not remove editorial content"."""
        self.assertTrue((FE / "lib" / "idea-library" / "ideas.json").exists())
        self.assertTrue((FE / "lib" / "districts-data.js").exists())
        districts = read(APP / "districts" / "page.js")
        self.assertIn("DISTRICTS", districts,
                      "the 14 written district profiles must still lead the page")
        detail = read(APP / "districts" / "[slug]" / "page.js")
        self.assertIn("district-editorial-overview", detail)


# ═══════════════════════════════════════════════ 5. capabilities are honest
class CapabilityStatusTest(unittest.TestCase):
    """Phase 2 — "If NO, change the message and include the actual dependency"."""

    def test_the_three_states_exist(self):
        src = read(COMPONENTS / "knowledge" / "CapabilityStatus.jsx")
        for state in ("LIVE", "NOT_AVAILABLE_YET", "NO_DATA_SOURCE"):
            with self.subTest(state=state):
                self.assertIn(state, src)
        self.assertIn("Not Available Yet", src)

    def test_every_unavailable_module_card_names_a_dependency(self):
        """The whole point. "Not Available Yet" alone is "Coming Soon" renamed."""
        offenders = []
        for page in sorted((APP).rglob("*Sections.jsx")):
            if "admin" in page.parts:
                continue
            src = read(page)
            # Each card object literal, split on the status field.
            for chunk in re.split(r"\{\s*\n?\s*emoji:", src)[1:]:
                chunk = chunk[:1400]
                status = re.search(r'status:\s*"([A-Z_]+)"', chunk)
                if status and status.group(1) != "LIVE" and "dependency:" not in chunk:
                    title = re.search(r'title:\s*"([^"]+)"', chunk)
                    offenders.append(f"{rel(page)}: {title.group(1) if title else '?'}")
        self.assertEqual(offenders, [],
                         "unavailable capabilities must say what they wait on:\n  "
                         + "\n  ".join(offenders))

    def test_the_brief_protected_capabilities_survive(self):
        """"DO NOT REMOVE: Mentors, Events, Startup Workspace, Team Workspace"."""
        readiness = read(APP / "readiness" / "components" / "ReadinessSections.jsx")
        network = read(APP / "network" / "components" / "NetworkSections.jsx")
        self.assertIn("Mentors", readiness)
        self.assertIn("Mentors", network)
        self.assertIn("Events", network)

    def test_the_homepage_roadmap_modules_all_carry_a_dependency(self):
        src = read(COMPONENTS / "HomeFeatureGrid.jsx")
        block = src[src.index("const FUTURE_MODULES = ["):]
        block = block[:block.index("\n];")]
        titles = re.findall(r'title:\s*"([^"]+)"', block)
        deps = re.findall(r"dependency:", block)
        self.assertEqual(len(titles), 6)
        self.assertEqual(len(deps), len(titles),
                         "every roadmap module names what it would need first")

    def test_infrastructure_card_no_longer_takes_a_boolean(self):
        """`comingSoon` could only ever say "not yet", never why."""
        src = code(COMPONENTS / "platform" / "InfrastructureCard.jsx")
        self.assertNotIn("comingSoon", src)
        self.assertIn("CapabilityChip", src)


# ═══════════════════════════════════════════════ 6. recommendation contract
class RecommendationCardTest(unittest.TestCase):
    """Phase 11 — five required elements on every recommendation."""

    def setUp(self):
        self.card = read(COMPONENTS / "knowledge" / "KnowledgeCard.jsx")
        self.rail = read(COMPONENTS / "knowledge" / "RecommendationRail.jsx")

    def test_reason_confidence_and_score_are_rendered(self):
        for prop in ("reason", "confidence", "matchScore"):
            with self.subTest(prop=prop):
                self.assertIn(prop, self.card)

    def test_source_package_is_rendered(self):
        self.assertIn("ProvenanceLine", self.card)
        self.assertIn("provenance.package", self.card)

    def test_supporting_entities_become_links(self):
        """The element that was computed and then dropped."""
        self.assertIn("related", self.card)
        self.assertIn("knowledge-card-related-link", self.card)
        self.assertIn("supportingLinks", self.rail)
        self.assertIn("supporting_entities", self.rail)

    def test_only_entity_evidence_is_linked(self):
        """profile_field and crosswalk evidence are real but not navigable."""
        self.assertIn('e?.kind === "entity"', self.rail)
        self.assertIn('startsWith("vw:")', self.rail)

    def test_related_links_are_not_nested_inside_the_card_link(self):
        """<a> inside <a> is invalid HTML and React warns at runtime."""
        self.assertIn("neither is nested inside the other", self.card)
        self.assertIn("if (relatedRow) {", self.card)


# ═══════════════════════════════════════════════ 7. nothing was duplicated
class NoDuplicationTest(unittest.TestCase):
    """"DO NOT create new pages / duplicate components / duplicate APIs"."""

    #: Routes that existed before Step 4. A new directory under app/ with a
    #: page.js is a new page, which the brief rules out.
    def test_no_new_routes_were_added(self):
        pages = {
            str(p.parent.relative_to(APP))
            for p in APP.rglob("page.js")
        }
        # Step 4 created no directory; it only edited existing page.js files.
        # This asserts the count rather than the list so a legitimate future
        # page does not have to be added in two places.
        self.assertEqual(
            len(pages), 80,
            "Step 4 must not add or remove a route; edit the existing ones")

    def test_one_district_intelligence_component_serves_both_routes(self):
        panel = COMPONENTS / "knowledge" / "DistrictIntelligencePanel.jsx"
        self.assertTrue(panel.exists())
        for route in ("app/district/[slug]/page.js", "app/districts/[slug]/page.js"):
            with self.subTest(route=route):
                self.assertIn("DistrictIntelligencePanel", read(FE / route))

    def test_one_empty_state_vocabulary(self):
        """Two components defining their own states drift within a month."""
        defining = [
            rel(p) for p in sources(APP, COMPONENTS)
            if "NOT_AVAILABLE_YET:" in code(p) or "NO_DATA_SOURCE:" in code(p)
        ]
        self.assertEqual(
            sorted(defining),
            ["components/knowledge/CapabilityStatus.jsx",
             "components/knowledge/KnowledgeEmptyState.jsx"],
            "empty-state copy belongs in the shared components only")

    def test_the_knowledge_client_is_not_reimplemented(self):
        """One createClient for the knowledge schema, in lib/knowledge.js."""
        holders = [
            rel(p) for p in sources(APP, COMPONENTS)
            if 'db: { schema: "knowledge" }' in read(p)
        ]
        self.assertEqual(holders, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
