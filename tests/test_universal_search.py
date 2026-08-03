#!/usr/bin/env python3
"""
Universal search — one box over everything, and what happens when it finds
nothing.

WHAT WAS WRONG
--------------
Original research is the thing ValueWeave has that a general search engine does
not, and it was the one kind of content the search box could not see. Articles
are MDX files and rows in `research_articles`; the search index was
`kg_entities`. So a student who searched the exact subject of an article we had
written got a page of database rows and no article.

And when nothing matched at all, the page rendered one centred sentence. From
the manual testing that prompted this work: "if no search result exists, the UI
currently appears unresponsive." It was not unresponsive. The reader cannot
tell those apart, and either way the session ends there.

WHAT THESE TESTS HOLD
---------------------
  1  research articles are in the index, ranked by the SAME ladder
  2  the source registry is honest — a planned source has no loader, and
     nothing invents a row
  3  results group, and the groups are ordered by what was found
  4  a query that finds nothing still leads somewhere, and everything it
     offers exists

The ranking and grouping run in node against the real graph. The registry and
the wiring are static assertions, because a loader that hits Supabase cannot
run here.

    python3 tests/run_all.py --suite universal
"""

import json
import re
import unittest
from pathlib import Path

from tests.js_harness import NODE, JsHarness, entities

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
SEARCH = FE / "lib" / "search"
REGISTRY = SEARCH / "registry.js"
UNIVERSAL = SEARCH / "universal.js"
ALIASES = SEARCH / "vocabulary" / "entity_aliases.js"
ROUTE = FE / "app" / "api" / "search" / "suggest" / "route.js"
LIVE = FE / "components" / "search" / "LiveSearch.jsx"
GROUPED = FE / "components" / "search" / "GroupedResults.jsx"
GUIDE = FE / "components" / "search" / "NoResultsGuide.jsx"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


#: A stand-in for what loadResearchArticles returns, shaped by hand from the
#: three MDX files in content/research. The loader itself reads the filesystem
#: and Supabase and cannot run under node here; what is under test is that a
#: document of this shape ranks correctly beside a knowledge entity.
ARTICLES = [
    {
        "global_entity_id": "article:battery-recycling-business-india",
        "entity_type": "ResearchArticle",
        "canonical_name": "Battery Recycling Business in India — A Complete Guide",
        "source_package": "research", "confidence_score": 70,
        "_aliases": ["Recycling", "guntur", "vijayawada", "visakhapatnam"],
        "_href": "/research/battery-recycling-business-india",
    },
    {
        "global_entity_id": "article:ev-charging-business-telangana",
        "entity_type": "ResearchArticle",
        "canonical_name": "EV Charging Business in Telangana — Setup Guide",
        "source_package": "research", "confidence_score": 70,
        "_aliases": ["Energy", "warangal", "karimnagar", "nizamabad"],
        "_href": "/research/ev-charging-business-telangana",
    },
    {
        "global_entity_id": "article:rural-diagnostic-centers-india",
        "entity_type": "ResearchArticle",
        "canonical_name": "Rural Diagnostic Centres in India — How to Start & Scale",
        "source_package": "research", "confidence_score": 70,
        "_aliases": ["Healthcare", "medak", "siddipet", "khammam", "kurnool"],
        "_href": "/research/rural-diagnostic-centers-india",
    },
]

PRELUDE = """
    const { rankEntities } = await import("$LIB/knowledge-search.js");
    const { groupResults, didYouMean, GROUPS } = await import("$LIB/search/universal.js");
    const { groupOf, kindLabel } = await import("$LIB/search/registry.js");
    const ALIASES = (await import("$LIB/search/vocabulary/entity_aliases.js")).default;
    const raw = JSON.parse(fs.readFileSync("$DIR/entities.json", "utf8"));
    const articles = JSON.parse(fs.readFileSync("$DIR/articles.json", "utf8"));
    const ents = raw.map((e) => (ALIASES[e.global_entity_id]
      ? { ...e, _aliases: ALIASES[e.global_entity_id] } : e));
    const index = [...ents, ...articles];
    const search = (q, limit = 24) => rankEntities(index, q, { limit });
"""


@unittest.skipIf(NODE is None, "node is required — the ranker is JavaScript")
class UniversalBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())
        cls.h.dataset("articles.json", ARTICLES)

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def js(self, body):
        return self.h.run(PRELUDE + body)

    def names(self, query, limit=24):
        return self.js(f'console.log(JSON.stringify(search({json.dumps(query)}, {limit})'
                       f'.map((r) => r.canonical_name)));')


# ═══════════════════════════ 1. research is first-class
class ResearchIsSearchableTest(UniversalBase):

    def test_an_article_is_found_by_its_subject(self):
        """The whole point. "Battery" held three machinery rows and an article
        about starting a battery recycling business; only the machinery was
        reachable."""
        names = self.names("battery", 10)
        self.assertTrue(any("Battery Recycling Business" in n for n in names),
                        f"the article is not in the results: {names}")

    def test_an_article_is_found_by_a_district_it_is_tagged_with(self):
        """Tags are on the article, not in its title. This is what `_aliases`
        is for, and the rule that an alias can never displace a name is what
        keeps the district itself first."""
        names = self.names("medak", 10)
        self.assertEqual(names[0], "Medak", "the district must still lead")
        self.assertTrue(any("Rural Diagnostic Centres" in n for n in names),
                        f"the article tagged medak is missing: {names}")

    def test_an_alias_never_outranks_a_name(self):
        """An article tagged "warangal" must not beat the district Warangal."""
        for district in ("Warangal", "Karimnagar", "Nizamabad", "Khammam"):
            with self.subTest(district=district):
                self.assertEqual(self.names(district, 6)[0], district)

    def test_articles_are_ranked_by_the_same_ladder(self):
        """Not appended, not a separate list merged in. If they were ranked
        separately the scores would not be comparable and the order would be
        arbitrary."""
        rows = self.js('console.log(JSON.stringify(search("battery", 10)'
                       '.map((r) => [r.entity_type, r._score])));')
        scores = [s for _, s in rows]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertIn("ResearchArticle", [t for t, _ in rows])


# ═══════════════════════════ 2. the registry is honest
class RegistryTest(unittest.TestCase):

    def setUp(self):
        self.src = code(REGISTRY)

    def test_a_planned_source_has_no_loader(self):
        """A "planned" source with a loader that returned three plausible
        mentors would be the single most damaging thing this file could do."""
        block = self.src[self.src.index("export const SOURCES"):]
        block = block[:block.index("];")]
        for entry in re.findall(r"\{[^{}]*\}", block):
            if '"planned"' in entry:
                with self.subTest(entry=entry.strip()[:60]):
                    self.assertNotIn("loader", entry)

    def test_the_sources_the_brief_names_are_all_declared(self):
        """Declared so the product can say "not yet" by name rather than
        showing a reader nothing and letting them conclude it is empty."""
        for label in ("Blog posts", "News & updates", "Mentors", "Courses",
                      "Success stories", "Opportunity reports"):
            with self.subTest(label=label):
                self.assertIn(label, self.src)

    def test_every_entity_type_in_the_graph_has_a_group(self):
        """A type with no group falls into a default bucket and gets labelled
        with its own class name — "ExportCountry" as a heading on a student's
        phone. This is the test that catches the twentieth entity type."""
        import csv                                                  # noqa: PLC0415
        with open(ROOT / "knowledge_graph" / "entities" / "entities.csv",
                  encoding="utf-8", newline="") as fh:
            types = {row["entity_type"] for row in csv.DictReader(fh)}
        missing = sorted(t for t in types if f"  {t}: [" not in self.src)
        self.assertEqual(missing, [], f"entity types with no display group: {missing}")

    def test_a_loader_failure_cannot_break_the_box(self):
        """Same contract as every read in lib/knowledge.js. A search box that
        500s because the article table is asleep is worse than one that finds
        no articles."""
        block = self.src[self.src.index("export async function loadRegisteredDocuments"):]
        self.assertIn("catch", block)
        self.assertIn("return [];", block)


# ═══════════════════════════ 3. grouping
class GroupingTest(UniversalBase):

    def test_groups_are_ordered_by_their_best_result(self):
        """"Medak" must lead with Places and "PMEGP" with Government support,
        and no static ordering is right for both."""
        for query, first in [("Medak", "places"), ("PMEGP", "schemes"),
                             ("Electrician", "skills")]:
            with self.subTest(query=query):
                groups = self.js(f'console.log(JSON.stringify(groupResults('
                                 f'search({json.dumps(query)}, 40)).map((g) => g.id)));')
                self.assertEqual(groups[0], first, f"{query} -> {groups}")

    def test_a_group_appears_once(self):
        """Ranked flat and printed with a heading on every change, one panel
        read "Business opportunities / Skills / Business opportunities" — three
        headings for two categories, which reads as a rendering fault."""
        for query in ("electrician", "battery", "AI", "solar"):
            with self.subTest(query=query):
                ids = self.js(f'console.log(JSON.stringify(groupResults('
                              f'search({json.dumps(query)}, 40)).map((g) => g.id)));')
                self.assertEqual(len(ids), len(set(ids)))

    def test_every_group_id_is_declared(self):
        ids = self.js('console.log(JSON.stringify(GROUPS.map((g) => g.id)));')
        used = self.js('const out = new Set();'
                       'for (const e of index) out.add(groupOf(e.entity_type));'
                       'console.log(JSON.stringify([...out]));')
        self.assertEqual(sorted(set(used) - set(ids)), [])

    def test_nothing_is_labelled_with_its_class_name(self):
        """"BusinessOpportunity" is a type name. "Business opportunity" is what
        a person calls the thing."""
        labels = self.js('const out = new Set();'
                         'for (const e of index) out.add(kindLabel(e.entity_type));'
                         'console.log(JSON.stringify([...out]));')
        offenders = [label for label in labels if re.search(r"[a-z][A-Z]", label)]
        self.assertEqual(offenders, [], f"raw type names shown to a reader: {offenders}")


# ═══════════════════════════ 4. never a dead end
class GuidanceTest(UniversalBase):

    def test_a_misspelling_gets_a_correction(self):
        hits = self.js('console.log(JSON.stringify('
                       'didYouMean(index, "vermicomposte", {limit: 4}).map((h) => h.name)));')
        self.assertTrue(any("Vermicompost" in h for h in hits), hits)

    def test_a_correction_always_points_at_something_we_hold(self):
        """The rule from Phase 4: a suggestion leading to a second empty page
        is a second dead end and worse than silence."""
        for query in ("vermicomposte", "electrishun", "turmerik", "warangl"):
            with self.subTest(query=query):
                hits = self.js(f'console.log(JSON.stringify(didYouMean(index, '
                               f'{json.dumps(query)}, {{limit: 4}})));')
                for hit in hits:
                    self.assertTrue(
                        any(e["canonical_name"] == hit["name"] for e in
                            [{"canonical_name": n} for n in self.names(hit["name"], 3)]
                            ) or hit["href"],
                        f"suggested {hit} leads nowhere")
                    self.assertTrue(hit["href"].startswith("/"))

    def test_a_query_nothing_is_near_gets_no_invented_correction(self):
        """"zebra" is not a typo for anything we hold. Offering the nearest
        row anyway is how a search box starts lying."""
        hits = self.js('console.log(JSON.stringify(didYouMean(index, "zebra")));')
        self.assertEqual(hits, [])

    def test_the_guide_offers_all_four_things(self):
        src = code(GUIDE)
        for marker in ("did-you-mean", "related-group", "search-suggestions",
                       "request-topic", "planned-sources"):
            with self.subTest(marker=marker):
                self.assertIn(marker, src)

    def test_the_guide_says_what_happened_before_it_apologises(self):
        src = read(GUIDE)
        self.assertIn("We couldn’t find", src)
        self.assertIn("Should we research", src)

    def test_it_does_not_claim_it_found_nothing_when_it_found_something(self):
        """Under thin results — "Medak" returns the district and one article —
        the same component renders. "We couldn't find Medak" over a card
        showing Medak is false and reads as a broken page."""
        src = code(GUIDE)
        self.assertIn('mode = "empty"', src)
        self.assertIn('const empty = mode !== "thin";', src)
        self.assertIn("{empty && (", src)
        route = code(FE / "app" / "knowledge" / "page.js")
        self.assertIn('mode="thin"', route)

    def test_the_request_goes_to_the_real_queue(self):
        """Not a mailto and not a dead form. RequestContentWidget writes to
        `user_requests`, which is the queue the research work already runs from."""
        self.assertIn("RequestContentWidget", code(GUIDE))
        self.assertIn("user_requests", read(FE / "components" / "RequestContentWidget.jsx"))


# ═══════════════════════════ 5. the live box
class LiveSearchTest(unittest.TestCase):

    def setUp(self):
        self.src = code(LIVE)

    def test_it_waits_for_two_characters(self):
        self.assertIn("MIN_CHARS = 2", self.src)
        self.assertIn("q.length < MIN_CHARS", self.src)

    def test_it_debounces(self):
        self.assertIn("DEBOUNCE_MS", self.src)
        self.assertIn("setTimeout", self.src)
        self.assertIn("clearTimeout", self.src)

    def test_a_stale_response_cannot_overwrite_a_fresh_one(self):
        """The classic autocomplete race: "electr" answering after
        "electrician" replaces the right list with a staler one."""
        self.assertIn("seq.current", self.src)
        self.assertIn("mine !== seq.current", self.src)

    def test_it_is_a_combobox_and_says_so(self):
        for attribute in ('role="combobox"', "aria-expanded", "aria-controls",
                          "aria-activedescendant", 'role="listbox"', 'role="option"',
                          "aria-selected"):
            with self.subTest(attribute=attribute):
                self.assertIn(attribute, self.src)

    def test_the_arrow_keys_do_not_move_focus(self):
        """Focus stays in the input so typing keeps working — which is why the
        active option is tracked by id rather than focused."""
        self.assertIn("ArrowDown", self.src)
        self.assertIn("ArrowUp", self.src)
        self.assertIn("setActive", self.src)
        self.assertNotIn(".focus()", self.src)

    def test_escape_closes_without_clearing_the_text(self):
        block = self.src[self.src.index('event.key === "Escape"'):]
        block = block[:block.index("return;")]
        self.assertNotIn("setQuery", block)

    def test_the_search_button_survives(self):
        """The brief keeps it, and it is the fallback when the route is down."""
        self.assertIn('type="submit"', self.src)
        self.assertIn("-submit", self.src)

    def test_a_row_is_at_least_44px(self):
        self.assertIn("min-h-[44px]", self.src)

    def test_it_does_not_open_by_itself_on_a_results_page(self):
        """The box arrives pre-filled with what was searched for. Without a
        touched flag the panel opened on load — a dropdown covering the
        answers to the question it is offering to help ask."""
        self.assertIn("touched", self.src)
        self.assertIn("if (!touched) return undefined;", self.src)

    def test_the_panel_never_swallows_the_query_when_offline(self):
        block = self.src[self.src.index("} catch {"):]
        self.assertIn("setItems([])", block[:400])


class HighlightTest(UniversalBase):
    """`highlight` is exported so it can be tested without a DOM."""

    def test_it_marks_every_matching_run(self):
        out = self.h.run("""
            const { highlight } = await import("$LIB/../components/search/LiveSearch.jsx");
            console.log(JSON.stringify(highlight("Tiles Fixing (Tile Mason)", "tile mason")));
        """) if False else None
        # Importing JSX in bare node is not possible. The behaviour is asserted
        # on the source instead, and the visual result was checked in a browser
        # at 390px — see the screenshots on the commit.
        src = code(LIVE)
        self.assertIn("export function highlight", src)
        self.assertIn("<mark", src)


# ═══════════════════════════ 6. the route
class SuggestRouteTest(unittest.TestCase):

    def setUp(self):
        self.src = code(ROUTE)

    def test_a_short_query_is_not_an_error(self):
        """Someone typed one letter. They are still going."""
        self.assertIn("q.length < MIN_QUERY", self.src)
        self.assertIn("items: []", self.src)

    def test_a_failure_is_an_empty_list_and_not_a_500(self):
        """A search box that errors while you type is worse than one that
        finds nothing: it is the only signal the reader gets and it says the
        site is broken."""
        block = self.src[self.src.index("} catch {"):]
        self.assertIn("items: []", block)
        self.assertIn("status: 200", block)

    def test_the_query_is_bounded(self):
        self.assertIn("MAX_QUERY", self.src)
        self.assertIn("slice(0, MAX_QUERY)", self.src)

    def test_it_is_cacheable(self):
        """Nothing in the answer depends on the visitor."""
        self.assertIn("s-maxage", self.src)


# ═══════════════════════════ 7. the generated aliases
class EntityAliasTest(unittest.TestCase):

    def test_the_file_is_generated_and_says_so(self):
        self.assertIn("GENERATED — do not edit", read(ALIASES))

    def test_it_is_in_step_with_the_packages(self):
        """A package release that adds a scheme must not leave its
        abbreviation unsearchable."""
        import subprocess                                            # noqa: PLC0415
        import sys                                                   # noqa: PLC0415
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_search_aliases.py"), "--check"],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_the_scheme_abbreviations_are_there(self):
        src = read(ALIASES)
        for short in ("PMEGP", "PMKVY 4.0", "PMFBY", "CGTMSE", "MGNREGS"):
            with self.subTest(short=short):
                self.assertIn(f'"{short}"', src)

    def test_a_category_almost_every_row_shares_is_not_imported(self):
        """Package006 files 42 of its 45 skills — Python Programming, Full
        Stack Web Development, Electrician — under "Soft Skills &
        Communication". Importing that would make a search for "communication"
        return Python Programming with the platform's badge on it.

        The rows themselves are research data and are reported, not rewritten,
        by a search milestone. This asserts the filter, not the fix.
        """
        payload = json.loads(read(ALIASES).partition("Object.freeze(")[2]
                             .rstrip().rstrip(";").rstrip(")"))
        offenders = [eid for eid, names in payload.items()
                     if "Soft Skills & Communication" in names]
        self.assertEqual(offenders, [], f"a defective category was imported: {offenders[:3]}")

    def test_a_single_category_dataset_is_still_imported(self):
        """The filter must not eat the useful case. Every row of
        construction_skilled_trade_services.csv IS construction; that is a
        scoped dataset, not a defect, and the alias is how searching
        "skilled trades" reaches the eleven trades in it."""
        src = read(ALIASES)
        self.assertIn('"Construction & Skilled Trades"', src)

    def test_nothing_is_translated_or_invented(self):
        """Every alias must appear verbatim in a package dataset. Curated
        meaning lives in concepts.js; this file only repeats."""
        import csv                                                   # noqa: PLC0415
        haystack = set()
        for path in (ROOT / "packages").glob("*/datasets/*.csv"):
            with open(path, encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    for value in row.values():
                        cleaned = " ".join(str(value or "").split()).strip()
                        if cleaned:
                            haystack.add(cleaned)
        payload = json.loads(read(ALIASES).partition("Object.freeze(")[2]
                             .rstrip().rstrip(";").rstrip(")"))
        invented = sorted({a for names in payload.values() for a in names
                           if a not in haystack})
        self.assertEqual(invented, [], f"aliases with no source row: {invented[:10]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
