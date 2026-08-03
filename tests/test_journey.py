#!/usr/bin/env python3
"""
PX Phase 9 — the first-time user journey.

WHAT PHASE 9 ACTUALLY ADDED
---------------------------
Phase 6 built the question ("Or tell us who you are") and six curated answers.
It shipped with a note in `app/start/[audience]/page.js` saying the routing and
the copy were done and that Phase 9 "adds the memory".

So these tests are about the memory and what it is allowed to do. The most
important one is `test_a_preference_can_never_outrank_a_better_match`: the
moment a search reorders itself for who you are, the risk is that it starts
answering a different question than the one you typed, and the argument that it
cannot is arithmetic that should be checked rather than believed.

WHY THESE RUN REAL JAVASCRIPT
-----------------------------
Same reason as every other frontend suite here — see tests/js_harness.py. A
Python model of the ranker would pass while the shipped one broke.
"""

import json
from collections import Counter
import re
import unittest
from pathlib import Path

from tests.js_harness import JsHarness, entities, NODE, NODE_REASON

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
JOURNEY = FE / "lib" / "journey.js"
AUDIENCES = FE / "lib" / "audiences.js"
SEARCH = FE / "lib" / "knowledge-search.js"


@unittest.skipUnless(NODE, NODE_REASON)
class JourneyMemoryTest(unittest.TestCase):
    """Storing, reading and forgetting the answer."""

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def journey(self, body):
        """Run `body` with a fake window/localStorage in scope.

        Node has no localStorage. Stubbing it is honest here because the module
        under test does nothing with storage beyond get/set/remove — the part
        worth testing is the validation and the try/catch around them, not the
        browser's implementation of a key-value store.
        """
        return self.h.run("""
            const store = new Map();
            globalThis.window = { localStorage: {
              getItem: (k) => (store.has(k) ? store.get(k) : null),
              setItem: (k, v) => store.set(k, String(v)),
              removeItem: (k) => store.delete(k),
            }};
            const J = await import("$LIB/journey.js");
            %s
        """ % body)

    def test_an_answer_survives_being_given(self):
        out = self.journey("""
            J.remember("student");
            console.log(JSON.stringify({ recalled: J.recall() }));
        """)
        self.assertEqual(out["recalled"], "student")

    def test_forget_is_a_real_delete(self):
        """The 'Not you?' control has to actually clear it. A control that
        looks like it forgets and does not is worse than no control."""
        out = self.journey("""
            J.remember("farmer");
            const before = J.recall();
            J.forget();
            console.log(JSON.stringify({ before, after: J.recall() }));
        """)
        self.assertEqual(out["before"], "farmer")
        self.assertIsNone(out["after"])

    def test_a_slug_that_is_no_longer_an_audience_reads_as_nobody(self):
        """Renaming an audience must degrade to 'ask again', not to a page
        that renders `undefined` as somebody's identity."""
        out = self.journey("""
            globalThis.window.localStorage.setItem("vw_audience", "astronaut");
            console.log(JSON.stringify({ recalled: J.recall(),
                                         audience: J.recallAudience() }));
        """)
        self.assertIsNone(out["recalled"])
        self.assertIsNone(out["audience"])

    def test_only_the_six_may_be_written(self):
        out = self.journey("""
            const ok = J.remember("astronaut");
            console.log(JSON.stringify({ ok, recalled: J.recall() }));
        """)
        self.assertFalse(out["ok"])
        self.assertIsNone(out["recalled"])

    def test_storage_that_throws_does_not_take_the_page_with_it(self):
        """Safari private mode and 'block all cookies' throw on access rather
        than returning null. A visitor with storage off gets the ordinary
        anonymous site."""
        out = self.journey("""
            globalThis.window.localStorage = {
              getItem() { throw new Error("SecurityError"); },
              setItem() { throw new Error("SecurityError"); },
              removeItem() { throw new Error("SecurityError"); },
            };
            console.log(JSON.stringify({
              recalled: J.recall(), wrote: J.remember("student"), forgot: J.forget(),
            }));
        """)
        self.assertIsNone(out["recalled"])
        self.assertFalse(out["wrote"])
        self.assertFalse(out["forgot"])


@unittest.skipUnless(NODE, NODE_REASON)
class AffinityTest(unittest.TestCase):
    """What each audience is taken to care about, and where that comes from."""

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.affinity = cls.h.run("""
            const { AFFINITY } = await import("$LIB/journey.js");
            console.log(JSON.stringify(Object.fromEntries(
              Object.entries(AFFINITY).map(([k, v]) => [k, [...v]]))));
        """)

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def test_every_audience_prefers_something(self):
        """An audience with an empty affinity gets no boost at all, which would
        make the memory decorative for that persona without saying so."""
        self.assertEqual(len(self.affinity), 6)
        for slug, types in self.affinity.items():
            with self.subTest(audience=slug):
                self.assertGreater(len(types), 0)

    def test_every_preferred_type_exists_in_the_graph(self):
        """The affinity is derived from the curated `starts` links, so a typo
        in one of those would silently produce a preference for a type no
        entity has — a boost that can never fire."""
        real = {e["entity_type"] for e in entities()}
        for slug, types in self.affinity.items():
            for entity_type in types:
                with self.subTest(audience=slug, type=entity_type):
                    self.assertIn(entity_type, real)

    def test_the_affinity_is_derived_from_the_curated_pages(self):
        """Not a second hand-maintained list. If somebody edits an audience's
        start links, the ranking must follow rather than drift."""
        source = JOURNEY.read_text(encoding="utf-8")
        self.assertIn("audience.starts", source)
        self.assertIn("TYPE_BY_URL", source)

    def test_the_audiences_disagree(self):
        """If every audience preferred the same types the boost would be a
        no-op dressed up as personalisation."""
        signatures = {frozenset(v) for v in self.affinity.values()}
        self.assertGreater(len(signatures), 1)


@unittest.skipUnless(NODE, NODE_REASON)
class BoostSafetyTest(unittest.TestCase):
    """The bound that makes reordering a search for somebody defensible."""

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def tiers(self):
        """The real SCORE table, read from the shipped ranker."""
        block = re.search(r"const SCORE = \{(.*?)\};", SEARCH.read_text(encoding="utf-8"),
                          re.S).group(1)
        return sorted(int(n) for n in re.findall(r":\s*(\d+)", block))

    def test_a_preference_can_never_outrank_a_better_match(self):
        """THE test in this file.

        The boost is a multiplier on a tiered score. If it ever exceeded the
        ratio between two adjacent tiers, a merely-CONTAINS hit in a preferred
        category could overtake a WORD hit the reader actually typed — a
        personalised search confidently returning the wrong thing, which is the
        failure that would cost the most trust.

        Both numbers are read from source, so this fails if either the weight
        or the tier table moves.
        """
        tiers = self.tiers()
        narrowest = min(b / a for a, b in zip(tiers, tiers[1:]))
        weight = self.h.run("""
            const { PREFERRED_WEIGHT } = await import("$LIB/journey.js");
            console.log(JSON.stringify(PREFERRED_WEIGHT));
        """)
        self.assertLess(
            weight, narrowest,
            f"a boost of {weight} can lift a result across the narrowest tier "
            f"gap ({narrowest:.3f}), so a preferred weak match could outrank a "
            f"strong one")

    def test_an_anonymous_visitor_gets_no_boost_object_at_all(self):
        """Not `() => 1`. The ranker skips the multiply when there is no boost,
        so somebody who never answered pays nothing for the feature."""
        out = self.h.run("""
            const { boostFor } = await import("$LIB/journey.js");
            console.log(JSON.stringify({
              none: boostFor(undefined) === undefined,
              unknown: boostFor("astronaut") === undefined,
              real: typeof boostFor("student"),
            }));
        """)
        self.assertTrue(out["none"])
        self.assertTrue(out["unknown"])
        self.assertEqual(out["real"], "function")


@unittest.skipUnless(NODE, NODE_REASON)
class PersonalisedRankingTest(unittest.TestCase):
    """What the boost does to real results from the real graph."""

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    #: Queries a real reader arrives with, spanning skills, schemes, crops and
    #: training — so at least one preferred type is in play for each audience.
    QUERIES = ("electrician", "solar", "loan", "training", "turmeric")
    AUDIENCES = ("student", "job-seeker", "entrepreneur",
                 "farmer", "skilled-worker", "business-owner")

    def ranked(self, query, audience=None, limit=40):
        return self.h.run("""
            const { rankEntities } = await import("$LIB/knowledge-search.js");
            const { boostFor } = await import("$LIB/journey.js");
            const rows = JSON.parse(fs.readFileSync("$DIR/entities.json", "utf8"));
            const boost = %s;
            const out = rankEntities(rows, %s, { limit: %d, boost });
            console.log(JSON.stringify(out.map((r) => ({
              id: r.global_entity_id, type: r.entity_type, match: r._match }))));
        """ % ("undefined" if audience is None else f'boostFor("{audience}")',
               json.dumps(query), limit))

    def test_personalisation_is_not_a_filter(self):
        """Nothing findable becomes unfindable because you said who you are.

        Run with the limit lifted, so the comparison is of what the ranker
        MATCHED rather than of what happened to fit on a page. Identical sets
        here is the real statement: the boost changes order and nothing else.
        A farmer searching an electrician term still finds the electrician.
        """
        for query in self.QUERIES:
            for audience in self.AUDIENCES:
                with self.subTest(query=query, audience=audience):
                    plain = {r["id"] for r in self.ranked(query, limit=5000)}
                    tuned = {r["id"] for r in self.ranked(query, audience, limit=5000)}
                    self.assertEqual(plain, tuned)

    def test_a_truncated_page_swaps_peers_and_never_trades_down(self):
        """At a real limit, membership CAN change — and that is not a bug.

        Something has to be fortieth. Reordering forty rows necessarily changes
        which one falls off the end, and an earlier version of this test
        asserted set equality at limit=40 and failed: a farmer searching
        "training" saw `skill-loan-scheme` where an anonymous visitor saw
        `task-telangana-academy`. Both matched the query; one displaced the
        other at the boundary.

        So the guarantee worth holding is not "the same rows" but "rows of the
        same quality": the tier profile of a page — how many EXACT, PREFIX,
        WORD, CONTAINS, RELATED and FUZZY hits it contains — must be identical
        with and without a preference. A reader can be shown a different
        RELATED row, never a FUZZY one in place of a WORD one.
        """
        for query in self.QUERIES:
            for audience in self.AUDIENCES:
                with self.subTest(query=query, audience=audience):
                    plain = Counter(r["match"] for r in self.ranked(query))
                    tuned = Counter(r["match"] for r in self.ranked(query, audience))
                    self.assertEqual(plain, tuned)

    def test_the_match_tier_of_a_surviving_result_is_unchanged(self):
        """The boost scales a score; it must never change WHY something
        matched, because `_match` is what the UI prints to explain the row."""
        for audience in ("student", "farmer"):
            plain = {r["id"]: r["match"] for r in self.ranked("solar", limit=5000)}
            tuned = {r["id"]: r["match"]
                     for r in self.ranked("solar", audience, limit=5000)}
            with self.subTest(audience=audience):
                self.assertEqual(plain, tuned)

    def test_a_preferred_category_actually_moves_up(self):
        """The whole point. If no ordering ever changes, the memory is
        decoration and this phase delivered nothing.

        Asserted across the six audiences on one broad query rather than by
        pinning one entity id, so it survives the graph growing.
        """
        base = [r["id"] for r in self.ranked("solar")]
        moved = []
        for audience in ("student", "job-seeker", "entrepreneur",
                         "farmer", "skilled-worker", "business-owner"):
            if [r["id"] for r in self.ranked("solar", audience)] != base:
                moved.append(audience)
        self.assertTrue(
            moved,
            "no audience reordered a broad query — the boost is not reaching "
            "the ranker, or no preferred type appears in these results")


class SurfaceWiringTest(unittest.TestCase):
    """The three places the memory is written, read and used."""

    def test_the_start_page_records_the_visit(self):
        """Recording on ARRIVAL and not on the homepage chip's click, because a
        shared link, a bookmark, a search engine and the 'Not quite you?' row
        all reach this page without ever touching that chip."""
        page = (FE / "app" / "start" / "[audience]" / "page.js").read_text(encoding="utf-8")
        self.assertIn("RememberAudience", page)
        island = (FE / "components" / "RememberAudience.jsx").read_text(encoding="utf-8")
        self.assertIn("return null", island)

    def test_the_homepage_reads_the_memory_after_paint_not_during_render(self):
        """localStorage is invisible to the server. Reading it during render
        would make the server HTML and the first client render disagree and
        throw a hydration error on the most important page on the site."""
        hero = (FE / "components" / "HomeHeroSearch.jsx").read_text(encoding="utf-8")
        self.assertIn("useEffect", hero)
        self.assertRegex(hero, r"useState\(null\)")
        # The call must be inside an effect, never at the top of the component.
        # Matched on the assignment rather than on the bare name: the comment
        # above it explains `recall()` in prose, and asserting on the whole
        # file would pass or fail on the explanation rather than the code.
        self.assertRegex(hero, r"useEffect\(\(\) => \{\s*setKnown\(recall\(\)\);\s*\}, \[\]\);")

    def test_the_visitor_can_take_it_back(self):
        """A platform that remembers you and offers no way to be forgotten is
        not being friendly, it is being sticky."""
        hero = (FE / "components" / "HomeHeroSearch.jsx").read_text(encoding="utf-8")
        self.assertIn("home-not-you", hero)
        self.assertIn("forget()", hero)

    def test_the_audience_travels_in_the_url_so_the_cache_stays_correct(self):
        """The suggest route is a shared public cache. A header or a cookie
        would have made a student and a farmer cache-identical, and served
        whichever arrived second the other one's ordering."""
        route = (FE / "app" / "api" / "search" / "suggest" / "route.js").read_text(encoding="utf-8")
        self.assertIn('searchParams.get("as")', route)
        self.assertIn("public, s-maxage", route)
        client = (FE / "components" / "search" / "LiveSearch.jsx").read_text(encoding="utf-8")
        self.assertIn("&as=", client)

    def test_an_unknown_audience_in_the_url_is_ignored(self):
        """`as` arrives from a URL anybody can type. It is validated against
        the six before it can reweight anything."""
        route = (FE / "app" / "api" / "search" / "suggest" / "route.js").read_text(encoding="utf-8")
        self.assertIn("isAudience(as)", route)

    def test_the_anonymous_path_is_untouched(self):
        """Nothing about this phase may change what a visitor who never
        answered sees. `boost` stays undefined and the ranker skips it."""
        route = (FE / "app" / "api" / "search" / "suggest" / "route.js").read_text(encoding="utf-8")
        self.assertRegex(route, r"isAudience\(as\)\s*\?\s*boostFor\(as\)\s*:\s*undefined")

    def test_the_boost_reaches_the_ranker(self):
        """The chain the HTTP route delegates to, asserted link by link.

        This is checked in source rather than over HTTP on purpose: the index
        `suggest` ranks comes from Supabase, so an environment without a
        projection returns an empty list for every query and an end-to-end
        assertion there would pass while proving nothing. What the boost
        actually DOES to real rows is covered against the real graph in
        PersonalisedRankingTest; this is the wiring between the two.
        """
        route = (FE / "app" / "api" / "search" / "suggest" / "route.js").read_text(encoding="utf-8")
        self.assertRegex(route, r"suggest\(q,\s*\{\s*boost\s*\}\)")

        universal = (FE / "lib" / "search" / "universal.js").read_text(encoding="utf-8")
        self.assertRegex(universal, r"export async function suggest\([^)]*boost[^)]*\)")
        self.assertRegex(universal, r"universalSearch\(q,\s*\{[^}]*boost[^}]*\}\)")
        self.assertRegex(universal, r"rankEntities\(index,\s*q,\s*\{[^}]*boost[^}]*\}\)")


@unittest.skipUnless(NODE, NODE_REASON)
class PopularGoalsTest(unittest.TestCase):
    """The second row: what you came for, for people who already know.

    The Phase 9 brief listed nine options mixing two questions — "Looking for
    a Job" is who you are, "Government Schemes" is what you want. The six
    personas answer the first. These answer the second, so somebody who came
    for PM Kisan does not have to describe themselves to reach it.
    """

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())
        cls.goals = cls.h.run("""
            const { GOALS } = await import("$LIB/audiences.js");
            console.log(JSON.stringify(GOALS));
        """)

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def test_all_nine_goals_from_the_brief_are_present(self):
        self.assertEqual(len(self.goals), 9)

    def test_every_typed_goal_opens_a_category_the_graph_holds(self):
        """A goal chip that opens an empty page is worse than no chip — the
        same rule the curated `starts` links are held to."""
        from urllib.parse import urlparse, parse_qs                  # noqa: PLC0415
        counts = {}
        for row in entities():
            counts[row["entity_type"]] = counts.get(row["entity_type"], 0) + 1
        type_by_url = self.h.run("""
            const { TYPE_BY_URL } = await import("$LIB/knowledge.js");
            console.log(JSON.stringify(TYPE_BY_URL));
        """)
        for goal in self.goals:
            params = parse_qs(urlparse(goal["href"]).query)
            url_type = (params.get("type") or [None])[0]
            if not url_type:
                continue
            with self.subTest(goal=goal["label"]):
                entity_type = type_by_url.get(url_type)
                self.assertIsNotNone(entity_type, f"unknown ?type={url_type}")
                self.assertGreater(counts.get(entity_type, 0), 0)

    def test_every_free_text_goal_actually_returns_something(self):
        """`?q=AI` and `?q=manufacturing` are not category links, so the only
        way to know they land on results is to run the real ranker."""
        from urllib.parse import urlparse, parse_qs                  # noqa: PLC0415
        checked = 0
        for goal in self.goals:
            params = parse_qs(urlparse(goal["href"]).query)
            query = (params.get("q") or [None])[0]
            if not query:
                continue
            checked += 1
            found = self.h.run("""
                const { rankEntities } = await import("$LIB/knowledge-search.js");
                const rows = JSON.parse(fs.readFileSync("$DIR/entities.json", "utf8"));
                console.log(JSON.stringify(rankEntities(rows, %s, { limit: 200 }).length));
            """ % json.dumps(query))
            with self.subTest(goal=goal["label"]):
                self.assertGreater(found, 0)
        self.assertGreater(checked, 0, "no free-text goals were checked")

    def test_a_goal_never_claims_to_know_who_you_are(self):
        """Tapping "Agriculture" must not silently mark somebody a farmer.
        Inferring an identity from one tap is what makes personalisation feel
        like surveillance rather than help."""
        hero = (FE / "components" / "HomeHeroSearch.jsx").read_text(encoding="utf-8")
        goals_block = hero[hero.index('data-testid="home-goals"'):]
        self.assertNotIn("remember(", goals_block)

    def test_the_goals_are_offered_to_everyone(self):
        """Knowing somebody is a farmer does not mean they are not here to
        look up a scheme today, so the row is outside the welcome-back
        branch."""
        hero = (FE / "components" / "HomeHeroSearch.jsx").read_text(encoding="utf-8")
        self.assertLess(hero.index('data-testid="home-welcome-back"'),
                        hero.index('data-testid="home-goals"'))
        self.assertIn("Popular goals", hero)


class ExploreWithoutAnAccountTest(unittest.TestCase):
    """Phase 9 says "after one click, personalize" — not "after one click,
    authenticate". Every path off /get-started used to end at Google."""

    def page(self):
        return (FE / "app" / "get-started" / "page.js").read_text(encoding="utf-8")

    def test_the_knowledge_is_reachable_without_signing_in(self):
        page = self.page()
        self.assertIn("getstarted-explore-free", page)
        self.assertIn('href="/knowledge"', page)

    def test_it_no_longer_calls_itself_step_one_of_three(self):
        """A three-step funnel in front of a student who only wanted to know
        whether we hold anything about welding."""
        self.assertNotIn("STEP 1 OF 3", self.page())

    def test_signing_in_still_works(self):
        """The refinement removes the WALL, not the door. This page is still
        the signup path and people who want an account still get one."""
        page = self.page()
        self.assertIn("signInWithOAuth", page)
        self.assertIn("getstarted-signin-link", page)


class TransparentPersonalisationTest(unittest.TestCase):
    """Lightweight, explained, and easy to leave."""

    def hero(self):
        return (FE / "components" / "HomeHeroSearch.jsx").read_text(encoding="utf-8")

    def test_the_greeting_is_friendly(self):
        self.assertIn("Welcome back", self.hero())

    def test_the_page_says_what_the_memory_does(self):
        """A reader should never have to wonder why one row is above another,
        and "we nudge these up, nothing is hidden" is the whole truth."""
        hero = self.hero()
        self.assertIn("nudge", hero)
        self.assertIn("Nothing is hidden", hero)

    def test_there_is_a_way_to_change_and_a_way_to_be_forgotten(self):
        """Two controls because they are two intentions: somebody who is now a
        business owner, and somebody who wants us to stop knowing. Offering
        only the first would make the memory impossible to leave."""
        hero = self.hero()
        self.assertIn("home-change-audience", hero)
        self.assertIn("home-not-you", hero)
        self.assertIn("forget()", hero)

    def test_changing_your_mind_does_not_lose_the_answer_you_gave(self):
        """"Change" reopens the six WITHOUT forgetting first, so a visitor who
        opens it and backs out still has their audience."""
        hero = self.hero()
        self.assertRegex(hero, r'data-testid="home-change-audience"[\s\S]{0,200}?setChoosing\(true\)')
        change_at = hero.index('data-testid="home-change-audience"')
        window = hero[change_at:change_at + 300]
        self.assertNotIn("forget()", window)


if __name__ == "__main__":
    unittest.main(verbosity=2)
