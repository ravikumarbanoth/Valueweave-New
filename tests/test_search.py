#!/usr/bin/env python3
"""Work Package 6 — Search engine tests.

Two things are being protected here. The first is that each match mode does what
it claims. The second, and the one that actually matters in use, is that the modes
stay in their lane: an exact match must never be displaced by a fuzzy one, and a
caller who asks for EXACT must never receive an approximation.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from search.engine import MatchMode, Scope, SearchEngine     # noqa: E402
from search.index import SearchIndex, normalise              # noqa: E402


class NormalisationTest(unittest.TestCase):
    def test_case_and_punctuation_are_collapsed(self):
        self.assertEqual(normalise("PM-KISAN"), "pm kisan")
        self.assertEqual(normalise("  Turmeric  "), "turmeric")

    def test_ampersand_becomes_and(self):
        """The v2.0 bug: `Agriculture & Allied` and `Agriculture and Allied`
        became two nodes, and a named query silently returned nothing."""
        self.assertEqual(normalise("Agriculture & Allied"), normalise("Agriculture and Allied"))

    def test_parentheticals_are_kept(self):
        """Opposite choice from the Resolver, and deliberately so: a user who
        searches for the qualified name means the qualified thing."""
        self.assertNotEqual(normalise("Manufacturing"), normalise("Manufacturing (Automotive)"))


class IndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = SearchIndex()

    def test_all_five_scopes_are_populated(self):
        for scope in SearchIndex.SCOPES:
            with self.subTest(scope=scope):
                self.assertTrue(self.index.scope(scope), f"{scope} scope is empty")

    def test_entity_count_matches_the_graph(self):
        import csv
        with open(ROOT / "knowledge_graph" / "entities" / "entities.csv",
                  newline="", encoding="utf-8") as f:
            expected = len(list(csv.DictReader(f)))
        self.assertEqual(len(self.index.scope("entity")), expected)

    def test_placeholder_package_is_not_indexed(self):
        """Package006_Skills holds a README and no datasets; it is not a package."""
        ids = {d.doc_id for d in self.index.scope("package")}
        self.assertNotIn("Package006_Skills", ids)
        self.assertIn("Package006_Skills_and_Training", ids)

    def test_aliases_resolve_to_a_real_entity(self):
        for d in self.index.scope("alias"):
            with self.subTest(alias=d.title):
                self.assertIsNotNone(self.index.entity(d.entity_id))


class MatchModeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SearchEngine()

    def test_exact_match_wins(self):
        results = self.engine.search("Turmeric", scopes="entity")
        self.assertEqual(results[0].match_mode, MatchMode.EXACT)
        self.assertEqual(results[0].document.title, "Turmeric")

    def test_prefix_match(self):
        titles = [r.document.title for r in self.engine.search("Millet", scopes="entity")]
        self.assertTrue(any(t.startswith("Millet") or "Millet" in t for t in titles))

    def test_alias_match_resolves_to_its_entity(self):
        results = self.engine.search("PM-KISAN", scopes="alias")
        self.assertTrue(results)
        self.assertEqual(results[0].match_mode, MatchMode.ALIAS)
        self.assertTrue(results[0].document.entity_id.startswith("vw:governmentscheme:"))

    def test_fuzzy_catches_a_typo(self):
        results = self.engine.search("Manufactring", scopes="entity")
        self.assertTrue(results, "a single-letter typo found nothing")
        self.assertEqual(results[0].match_mode, MatchMode.FUZZY)
        self.assertEqual(results[0].document.title, "Manufacturing")

    def test_exact_only_returns_no_approximation(self):
        self.assertEqual(self.engine.search("Manufactring", scopes="entity",
                                            modes=["EXACT"]), [])

    def test_fuzzy_threshold_is_configurable(self):
        loose = self.engine.search("agricultur", scopes="entity", fuzzy_threshold=0.3)
        strict = self.engine.search("agricultur", scopes="entity", fuzzy_threshold=0.99)
        self.assertGreaterEqual(len(loose), len(strict))

    def test_threshold_override_does_not_leak(self):
        before = self.engine.fuzzy_threshold
        self.engine.search("anything", fuzzy_threshold=0.1)
        self.assertEqual(self.engine.fuzzy_threshold, before)

    def test_nonsense_returns_nothing(self):
        self.assertEqual(self.engine.search("qzxwvnothinghere"), [])

    def test_empty_query_returns_nothing(self):
        self.assertEqual(self.engine.search("   "), [])

    def test_results_are_ranked_by_mode_strength(self):
        results = self.engine.search("Python", scopes="entity")
        ranks = [r.rank for r in results]
        self.assertEqual(ranks, sorted(ranks, reverse=True))

    def test_a_document_appears_at_most_once(self):
        results = self.engine.search("scheme", limit=None)
        keys = [(r.document.doc_id, r.document.scope) for r in results]
        self.assertEqual(len(keys), len(set(keys)))

    def test_suggest_excludes_fuzzy(self):
        modes = {r.match_mode for r in self.engine.suggest("mill")}
        self.assertNotIn(MatchMode.FUZZY, modes)


class FilterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SearchEngine()

    def test_entity_type_filter(self):
        for r in self.engine.search("millet", scopes="entity", entity_type="Crop"):
            self.assertEqual(r.document.entity_type, "Crop")

    def test_package_filter(self):
        for r in self.engine.search("scheme", source_package="Package007_Government_Schemes"):
            self.assertEqual(r.document.source_package, "Package007_Government_Schemes")

    def test_min_confidence_filter(self):
        for r in self.engine.search("crop", min_confidence=75):
            self.assertGreaterEqual(r.document.confidence, 75)

    def test_limit_is_respected(self):
        self.assertLessEqual(len(self.engine.search("a", limit=3)), 3)


class ParsingTest(unittest.TestCase):
    def test_unknown_mode_raises_with_a_useful_message(self):
        with self.assertRaises(ValueError) as ctx:
            MatchMode.parse("SEMANTIC")
        self.assertIn("EXACT", str(ctx.exception))

    def test_unknown_scope_raises(self):
        with self.assertRaises(ValueError):
            Scope.parse("everything")

    def test_enum_members_round_trip(self):
        self.assertEqual(MatchMode.parse(MatchMode.EXACT), [MatchMode.EXACT])
        self.assertEqual(Scope.parse(Scope.ENTITY), [Scope.ENTITY])

    def test_all_expands(self):
        self.assertEqual(len(MatchMode.parse("all")), 4)
        self.assertEqual(len(Scope.parse(None)), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
