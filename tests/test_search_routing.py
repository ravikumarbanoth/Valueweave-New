#!/usr/bin/env python3
"""
The search ROUTE — production bug, and the test that should have existed.

WHAT HAPPENED
-------------
Search did not work on the live site. `/knowledge?q=electrician` — the URL the
homepage search box sends you to — rendered the category grid: no results, no
"nothing found", no sign the query had been received.

`TypeIndex` ACCEPTED `q` and used it for exactly one thing: appending it to the
category links. `BrowseType` did search, via `listEntities`, which ran
`ilike '%q%'` on the name — 2 rows for "electrician", nothing for "electrican",
46 rows for "AI" of which most matched the letters a-i inside Painting and
Millet. And `searchKnowledge`, with the ranking ladder, the acronyms and the
typo tolerance, had exactly one caller in the whole codebase: a client
component further down the homepage. The route never imported it.

WHY THE SUITE DID NOT CATCH IT
------------------------------
787 tests passed. tests/test_search_experience proved the ENGINE was excellent
— it ran the real JavaScript against the real graph and asserted on the
rankings. Nothing asserted that anything CALLED it.

That is the gap this file closes. A unit test on a function nobody invokes is a
test of a library, not of a product, and the difference is invisible until a
user types something.

WHAT IS STILL NOT COVERED, HONESTLY
-----------------------------------
These are static assertions over the route's source. They would have caught
this specific bug — the route not importing the engine, and the second
implementation existing at all — and they will catch it coming back.

They cannot catch a rendering fault: a page that calls searchKnowledge and then
fails to display what it returns would pass every test below. Closing THAT
needs a browser driving a real build, which this repository has no harness for.
The fix was verified that way by hand — see the commit — and a standing
browser test is the recommended follow-up.

    python3 tests/run_all.py --suite search_routing
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
ROUTE = FE / "app" / "knowledge" / "page.js"
LIB = FE / "lib" / "knowledge.js"
#: The route calls searchGrouped, which calls rankEntities. Both links of that
#: chain are asserted below — an import that reaches a module which does NOT
#: reach the ranker is the same outage in a longer coat.
UNIVERSAL = FE / "lib" / "search" / "universal.js"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


# ═══════════════════════════════════════ 1. the route uses the engine
class RouteCallsTheSearchEngineTest(unittest.TestCase):

    def setUp(self):
        self.src = code(ROUTE)

    def test_the_route_imports_the_engine(self):
        """The single assertion that would have caught the outage.

        The route now goes through lib/search/universal.js, which unions the
        graph with the research articles and hands the whole thing to the SAME
        ranker. Both links are checked: a route that imports a search module
        which does not itself reach `rankEntities` is this outage again.
        """
        self.assertIn("searchGrouped", self.src,
                      "/knowledge does not import the search engine")
        self.assertIn("lib/search/universal", self.src)
        self.assertIn("rankEntities", code(UNIVERSAL),
                      "universal.js must rank with the shared ladder, not its own")

    def test_a_query_reaches_the_engine(self):
        self.assertRegex(self.src, r"searchGrouped\(\s*q\b",
                         "the engine is imported but the query never reaches it")

    def test_a_query_is_answered_before_any_browse_or_index_branch(self):
        """`?q=` must not fall through to the category grid.

        This is the exact shape of the bug: the branch ran
        `entityType ? <BrowseType/> : <TypeIndex/>` and `q` was a passenger.
        """
        body = self.src[self.src.index("return ("):]
        self.assertIn("searching ?", body,
                      "there is no branch on whether the user is searching")
        self.assertLess(body.index("searching ?"), body.index("<TypeIndex"),
                        "the category grid is reached before the search branch")
        self.assertLess(body.index("searching ?"), body.index("<BrowseType"),
                        "the browse list is reached before the search branch")

    def test_no_component_accepts_a_query_it_cannot_answer(self):
        """`TypeIndex({ q })` took a query and silently dropped it.

        A component that accepts `q` must do one of three things with it:
        search, put it in a link, or render it back into the box so the reader
        can see and re-submit it. `SearchBar` does the third and is fine.
        Accepting `q` and doing none of them is how a broken search looks
        exactly like a working one.
        """
        USES = ("searchGrouped",            # answers it
                "guidance(q)",              # answers the absence of it
                "encodeURIComponent(q)",    # passes it on in a URL
                "defaultValue={q}",         # renders it back into the field
                "initialQuery={q}",
                "value={q}")
        offenders = []
        for name, params in re.findall(r"^(?:async )?function (\w+)\(\{([^}]*)\}\)",
                                       self.src, re.M):
            if not re.search(r"\bq\b", params):
                continue
            start = self.src.index(f"function {name}({{")
            body = self.src[start:self.src.find("\n}", start)]
            if not any(u in body for u in USES):
                offenders.append(name)
        self.assertEqual(
            offenders, [],
            "these take a query and never search with it: " + ", ".join(offenders))

    def test_a_query_with_no_type_filter_still_searches(self):
        """The homepage box sends `?q=` with no type. That was the dead path.

        The filter is now applied to the RESULTS rather than pushed into the
        query — which is what lets a filtered search that finds nothing still
        say "there are eleven of these if you drop the filter". So the thing
        to assert is that the search itself is unconditional.
        """
        block = self.src[self.src.index("async function SearchResults"):]
        block = block[:block.index("async function BrowseType")]
        self.assertNotIn("if (entityType)", block.split("searchGrouped")[0],
                         "search must run with or without a category filter")
        self.assertRegex(block, r"rows\.filter\(\(r\) => r\.entity_type === entityType\)")

    def test_the_no_match_state_offers_the_terms_that_would_have_worked(self):
        """`suggestRelatedSearches` shipped in Phase 1 with no caller here.

        `guidance` is its successor and does more: a correction, related rows
        that exist, the terms that work, and a request form. The rule is
        unchanged — a no-match page must point somewhere.
        """
        self.assertIn("guidance(q)", self.src)
        self.assertIn("relatedSearches", code(UNIVERSAL))

    def test_a_thin_result_set_is_guided_too(self):
        """One row is a coverage gap wearing the costume of an answer.

        "Dairy" returns exactly one dairy-adjacent entity. A page showing only
        that row implies we have a dairy section. Below the threshold the
        guidance renders underneath the results.
        """
        self.assertIn("THIN_RESULTS", self.src)
        self.assertRegex(self.src, r"visible\.length < THIN_RESULTS")
    def test_search_intelligence_is_attached_to_the_results_page(self):
        self.assertIn("analyzeSearchQuery", self.src)
        self.assertIn("analysis={analysis}", self.src)

# ═══════════════════════════════════════ 2. exactly one search implementation
class OneSearchPathTest(unittest.TestCase):
    """Two implementations is a coin flip about which one a user gets."""

    def test_list_entities_no_longer_searches(self):
        src = code(LIB)
        fn = src[src.index("export async function listEntities"):]
        fn = fn[:fn.index("\n}")]
        self.assertNotIn(".ilike(", fn, "listEntities is for browsing, not searching")
        self.assertNotIn("q =", fn, "the q parameter must be gone, not deprecated")

    def test_nothing_else_substring_matches_a_name(self):
        """Any new `ilike` on canonical_name is a third search path."""
        offenders = []
        for root in (FE / "app", FE / "components", FE / "lib"):
            for path in sorted(root.rglob("*.js")) + sorted(root.rglob("*.jsx")):
                if "admin" in path.parts:
                    continue
                for lineno, line in enumerate(code(path).splitlines(), 1):
                    if ".ilike(" in line and "canonical_name" in line:
                        offenders.append(f"{path.relative_to(FE)}:{lineno}")
        self.assertEqual(offenders, [], "\n  ".join(offenders))

    def test_the_engine_is_still_the_engine(self):
        """Guards the fix against being 'simplified' back into an ilike."""
        src = code(LIB)
        fn = src[src.index("export async function searchKnowledge"):]
        fn = fn[:fn.index("export async function suggestRelatedSearches")]
        self.assertIn("rankEntities(", fn)
        self.assertNotIn(".ilike(", fn)


# ═══════════════════════════════════════ 3. the entry points agree
class EntryPointsTest(unittest.TestCase):
    """Every box that takes a query must send it somewhere that searches."""

    def test_the_homepage_box_targets_the_search_route(self):
        src = code(FE / "components" / "HomeHeroSearch.jsx")
        self.assertIn("/knowledge?q=", src)

    def test_the_explorer_box_submits_a_q_parameter(self):
        """The explorer box is LiveSearch now — the same component the hero
        uses — so the assertion follows it there: it must be seeded with the
        current query and it must submit back to the search route."""
        form = code(ROUTE)[code(ROUTE).index("function SearchBar"):]
        form = form[:form.index("\n}")]
        self.assertIn("<LiveSearch", form)
        self.assertIn("initialQuery={q}", form)

        box = code(FE / "components" / "search" / "LiveSearch.jsx")
        self.assertIn("/knowledge?q=${encodeURIComponent(q)}", box)
        self.assertIn('type="submit"', box, "the Search button must survive")

    def test_the_audience_pages_send_real_queries(self):
        src = code(FE / "app" / "start" / "[audience]" / "page.js")
        self.assertIn("/knowledge?q=", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
