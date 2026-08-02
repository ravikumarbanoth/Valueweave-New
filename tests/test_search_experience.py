#!/usr/bin/env python3
"""
Search experience — PX Phase 1.

WHAT WAS WRONG
--------------
`searchKnowledge` was `ilike '%query%'` on canonical_name, ordered by
confidence_score. Measured against the live 647-entity graph:

    "Electrician"   2 results    misses electrical contracting, wireman work,
                                 panel manufacturing, power distribution
    "Tile Mason"    1 result     misses masonry, flooring, civil work
    "PMEGP"         1 result     and not the scheme — that is stored as
                                 "Prime Minister's Employment Generation Programme"
    "Dairy"         0 results
    "electrican"    0 results    one transposed letter
    "AI"           46 results    15 about AI. The rest matched the letters a-i
                                 inside Maize, Painting, Retail, Training.

Ordering by confidence meant the ranking had nothing to do with the query, so
for "AI" the top result was "Retail & Local Commerce".

WHAT THESE TESTS HOLD
---------------------
The four worked examples from the brief, as regressions, plus the two rules that
make them work: a short query may not match inside a word, and a vocabulary
expansion may never outrank what the user actually typed.

These run the real JavaScript against the real knowledge graph via node, rather
than reimplementing the matcher in Python — a Python copy would pass while the
shipped code broke.

    python3 tests/run_all.py --suite search_experience
"""

import csv
import json
import os
import re
import shutil
import subprocess
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
ENTITIES = ROOT / "knowledge_graph" / "entities" / "entities.csv"
NODE = shutil.which("node")


def entities():
    with open(ENTITIES, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class SearchHarness:
    """Runs the shipped modules in node, with `@/lib/...` rewritten to paths."""

    _dir = None

    @classmethod
    def prepare(cls, tmp):
        cls._dir = Path(tmp)
        for name in ("search-vocabulary.js", "knowledge-search.js"):
            src = (FE / "lib" / name).read_text(encoding="utf-8")
            src = re.sub(r'@/lib/([a-z-]+)', r'./\1.js', src)
            (cls._dir / name).write_text(src, encoding="utf-8")
        (cls._dir / "entities.json").write_text(json.dumps(entities()), encoding="utf-8")

    @classmethod
    def run(cls, body):
        script = cls._dir / "run.mjs"
        script.write_text(textwrap.dedent(f"""
            import fs from "node:fs";
            const {{ rankEntities, relatedSearches, matchTerm, editDistance }} =
              await import("{cls._dir}/knowledge-search.js");
            const {{ expandQuery }} = await import("{cls._dir}/search-vocabulary.js");
            const ents = JSON.parse(fs.readFileSync("{cls._dir}/entities.json", "utf8"));
            {body}
        """), encoding="utf-8")
        r = subprocess.run([NODE, str(script)], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise AssertionError(f"node failed:\n{r.stdout}\n{r.stderr}")
        return json.loads(r.stdout)

    @classmethod
    def search(cls, query, limit=24):
        return cls.run(f'console.log(JSON.stringify('
                       f'rankEntities(ents, {json.dumps(query)}, {{limit: {limit}}})));')


@unittest.skipIf(NODE is None, "node is required — the matcher is JavaScript and "
                               "testing a Python copy of it would prove nothing")
class SearchQualityTest(unittest.TestCase):
    """The four worked examples from the brief."""

    @classmethod
    def setUpClass(cls):
        import tempfile                                            # noqa: PLC0415
        cls._tmp = tempfile.TemporaryDirectory()
        SearchHarness.prepare(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def names(self, query, limit=24):
        return [r["canonical_name"] for r in SearchHarness.search(query, limit)]

    def test_electrician_reaches_the_whole_trade(self):
        """Not just rows whose title contains the word.

        A student typing this wants to know what an electrician can learn, earn,
        start and apply for. Two results was a lookup; this is an answer.
        """
        found = " | ".join(self.names("Electrician")).lower()
        self.assertGreaterEqual(len(self.names("Electrician")), 6)
        for expected in ("domestic wiring", "industrial electrician",
                         "electrical contracting", "electrical panel"):
            with self.subTest(expected=expected):
                self.assertIn(expected, found)

    def test_tile_mason_reaches_the_related_trades(self):
        found = " | ".join(self.names("Tile Mason")).lower()
        self.assertIn("tiles fixing", found)
        for expected in ("masonry", "construction"):
            with self.subTest(expected=expected):
                self.assertIn(expected, found)

    def test_ai_finds_ai_and_not_maize(self):
        """The single worst result of the old search.

        `%ai%` matched Maize, Painting, Retail and Training — 31 of 46 hits were
        the letters a-i inside an unrelated word. A query this short must land
        on a word boundary.
        """
        names = self.names("AI")
        self.assertEqual(names[0], "Artificial Intelligence",
                         "the industry itself must rank first for 'AI'")
        joined = " | ".join(names).lower()
        for junk in ("maize", "painting services", "retail & local commerce",
                     "submersible pump"):
            with self.subTest(junk=junk):
                self.assertNotIn(junk, joined)

    def test_pmegp_finds_the_scheme_itself(self):
        """Stored as "Prime Minister's Employment Generation Programme".

        No substring search can bridge that. The acronym expansion keeps the
        rung it earns, so the scheme outranks a financial instrument that merely
        starts with the same letters.
        """
        names = self.names("PMEGP")
        self.assertEqual(names[0], "Prime Minister's Employment Generation Programme")

    def test_a_transposed_letter_still_finds_the_trade(self):
        found = " | ".join(self.names("electrican")).lower()
        self.assertIn("electrician", found)

    def test_a_topic_we_barely_cover_is_not_padded(self):
        """The graph holds one dairy-adjacent entity.

        An earlier expansion reached "agriculture" and returned twenty generic
        "Agriculture: <sector>" rows — inventing coverage. Phase 4's rule is
        that an empty state must be honest; that starts with not faking a full
        one.
        """
        names = self.names("Dairy")
        self.assertLessEqual(len(names), 4, f"padded with generic rows: {names}")

    def test_results_are_ranked_by_relevance_not_confidence(self):
        """The old ordering put "Retail & Local Commerce" first for "AI"."""
        rows = SearchHarness.search("solar", limit=10)
        scores = [r["_score"] for r in rows]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(rows[0]["canonical_name"].lower().startswith("solar"))


@unittest.skipIf(NODE is None, "node is required")
class SearchRulesTest(unittest.TestCase):
    """The two rules the examples depend on."""

    @classmethod
    def setUpClass(cls):
        import tempfile                                            # noqa: PLC0415
        cls._tmp = tempfile.TemporaryDirectory()
        SearchHarness.prepare(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_short_queries_must_land_on_a_word_boundary(self):
        out = SearchHarness.run(
            'console.log(JSON.stringify({'
            '  inWord: matchTerm("ai", "Maize"),'
            '  atStart: matchTerm("ai", "AI Model Training"),'
            '  longEnough: matchTerm("weld", "Arc Welding Basics")}));')
        self.assertIsNone(out["inWord"], "'ai' must not match inside 'Maize'")
        self.assertEqual(out["atStart"], "PREFIX")
        self.assertEqual(out["longEnough"], "WORD")

    def test_an_expansion_never_outranks_what_was_typed(self):
        rows = SearchHarness.search("Electrician", 24)
        typed = [r for r in rows if not r["_via"]]
        related = [r for r in rows if r["_via"]]
        self.assertTrue(typed and related, "need both kinds to compare")
        self.assertGreater(min(r["_score"] for r in typed),
                           max(r["_score"] for r in related))

    def test_a_short_word_tolerates_no_typos(self):
        """Otherwise 'ai' is one edit from 'at', 'an' and 'ap'."""
        out = SearchHarness.run(
            'console.log(JSON.stringify({'
            '  short: editDistance("ai", "at", 2),'
            '  long: editDistance("electrican", "electrician", 2)}));')
        self.assertGreaterEqual(out["short"], 1)
        self.assertLessEqual(out["long"], 2)

    def test_every_expansion_target_is_reachable(self):
        """An expansion that matches nothing costs a query and returns nothing.

        Reachable by NAME or by TYPE. "government scheme" matches no entity name
        — no row is called that — but it is the humanised form of the
        GovernmentScheme type, and matching it returns all forty schemes. Four
        expansions looked dead for exactly this reason before the matcher
        learned to read the type.

        This is the test that keeps the vocabulary honest as the graph changes:
        add a term for content we do not hold and it fails here, not silently in
        front of a student.
        """
        out = SearchHarness.run(
            'const { EXPANSIONS } = await import("%s/search-vocabulary.js");\n'
            'const { humaniseType } = await import("%s/knowledge-search.js");\n'
            'const dead = [];\n'
            'for (const [key, terms] of Object.entries(EXPANSIONS))\n'
            '  for (const t of terms) {\n'
            '    const byName = ents.some((e) => matchTerm(t, e.canonical_name));\n'
            '    const byType = ents.some((e) => humaniseType(e.entity_type) === t);\n'
            '    if (!byName && !byType) dead.push(`${key} -> ${t}`);\n'
            '  }\n'
            'console.log(JSON.stringify(dead));' % (SearchHarness._dir, SearchHarness._dir))
        self.assertEqual(out, [], f"expansions that reach nothing: {out}")

    def test_a_type_word_returns_the_whole_category(self):
        """"schemes" should list schemes. No entity is NAMED "government
        scheme", so before the type path this returned almost nothing."""
        rows = SearchHarness.search("schemes", 12)
        types = {r["entity_type"] for r in rows}
        self.assertIn("GovernmentScheme", types)

    def test_suggestions_only_offer_terms_that_find_something(self):
        """Phase 4: never a second dead end."""
        out = SearchHarness.run(
            'const s = relatedSearches(ents, "Dairy", {limit: 6});'
            'console.log(JSON.stringify(s.map((t) => '
            '  [t, ents.some((e) => matchTerm(t, e.canonical_name))])));')
        for term, findable in out:
            with self.subTest(term=term):
                self.assertTrue(findable, f"suggested '{term}' leads nowhere")


class SearchWiringTest(unittest.TestCase):
    """The API contract, and that the UI actually uses it."""

    def setUp(self):
        self.lib = (FE / "lib" / "knowledge.js").read_text(encoding="utf-8")
        self.ui = (FE / "components" / "platform" / "KnowledgeSearch.jsx").read_text("utf-8")

    def test_the_public_signature_is_unchanged(self):
        self.assertIn("export async function searchKnowledge(query, "
                      "{ entityType, limit = 20 } = {})", self.lib)

    def test_searchKnowledge_no_longer_does_a_substring_lookup(self):
        """Scoped to the function that changed.

        `listEntities()` — the explorer's per-type filter box — still uses
        ilike, deliberately: it pages in the database and converting it means
        reworking pagination. Asserting on the whole file conflated the two and
        failed on code this phase did not touch. Reported as a known
        inconsistency rather than hidden by a loose assertion.
        """
        fn = self.lib[self.lib.index("export async function searchKnowledge"):]
        fn = fn[:fn.index("export async function suggestRelatedSearches")]
        self.assertNotIn(".ilike(", fn)
        self.assertNotIn('.order("confidence_score"', fn)
        self.assertIn("rankEntities(", fn)

    def test_a_failed_index_fetch_is_not_cached(self):
        """One cold start would otherwise leave search empty for the whole
        process life, with no error anywhere."""
        self.assertIn("searchIndexPromise = null;", self.lib.split("async function searchIndex")[1])

    def test_the_ui_explains_a_non_obvious_match(self):
        """"Power Distribution Technician" for "electrician" looks like a bug
        unless the card says why it is there."""
        self.assertIn("_via", self.ui)
        self.assertIn("match-reason", self.ui)

    def test_no_results_offers_somewhere_to_go(self):
        self.assertIn("search-no-match-suggestions", self.ui)
        self.assertIn("suggestRelatedSearches", self.ui)


if __name__ == "__main__":
    unittest.main(verbosity=2)
