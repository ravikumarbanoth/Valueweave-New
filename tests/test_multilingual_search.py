#!/usr/bin/env python3
"""
Multilingual search — English, Telugu and Tanglish.

WHAT WAS WRONG
--------------
Measured against the live 647-entity graph before this landed:

    "ఎలక్ట్రిషియన్"      0 results   Telugu survives normalisation and then has
                                  nothing in common with a Latin name
    "మెదక్"             0 results   the district is right there, spelled Medak
    "పాడి పరిశ్రమ"       0 results
    "elektrishian"    0 results   four edits from "electrician"; the typo
                                  budget stops at two, correctly
    "paala parishrama" 0 results
    "raitu"           0 results

Six queries a Telugu speaker would type, and a blank page for every one. The
platform is for Telangana and Andhra Pradesh.

WHAT THESE TESTS HOLD
---------------------
Three things, in order of how badly each would fail a user:

  1  the six queries above return what their English equivalent returns
  2  the concept table cannot rot — every expansion must reach a live entity,
     and no two concepts may collapse to the same phonetic key
  3  the English behaviour that already worked is unchanged

They run the shipped JavaScript against the real graph. A Python
reimplementation would pass while the shipped code broke.

    python3 tests/run_all.py --suite multilingual
"""

import json
import unittest
from pathlib import Path

from tests.js_harness import NODE, JsHarness, entities

ROOT = Path(__file__).resolve().parent.parent
CONCEPTS = ROOT / "frontend" / "lib" / "search" / "vocabulary" / "concepts.js"

PRELUDE = """
    const ml = await import("$LIB/search/multilingual.js");
    const { rankEntities, matchTerm, humaniseType } = await import("$LIB/knowledge-search.js");
    const { expandQuery } = await import("$LIB/search-vocabulary.js");
    const CONCEPTS = (await import("$LIB/search/vocabulary/concepts.js")).default;
    const ents = JSON.parse(fs.readFileSync("$DIR/entities.json", "utf8"));
"""


@unittest.skipIf(NODE is None, "node is required — the resolver is JavaScript")
class MultilingualBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def js(self, body):
        return self.h.run(PRELUDE + body)

    def names(self, query, limit=12):
        return self.js(f'console.log(JSON.stringify(rankEntities(ents, '
                       f'{json.dumps(query)}, {{limit: {limit}}})'
                       f'.map((r) => r.canonical_name)));')


# ═══════════════════════════ 1. the same answer in three languages
class SameAnswerEveryLanguageTest(MultilingualBase):
    """The whole point. Not "returns something" — returns the SAME thing.

    Asserting a non-empty list would pass if Telugu resolved to the wrong
    trade, which is worse than nothing: a student cannot tell a wrong answer
    from a right one in a domain they came here to learn about.
    """

    #: (english, telugu, tanglish) — the user-facing examples from the brief.
    TRIPLES = [
        ("electrician", "ఎలక్ట్రిషియన్", "elektrishian"),
        ("robotics", "రోబోటిక్స్", None),
        ("farmer", "రైతు", "raitu"),
        ("agriculture", "వ్యవసాయం", "vyavasayam"),
    ]

    def test_the_three_spellings_agree(self):
        for english, telugu, tanglish in self.TRIPLES:
            expected = self.names(english, 6)
            self.assertTrue(expected, f"the English control found nothing: {english}")
            for variant in (telugu, tanglish):
                if not variant:
                    continue
                with self.subTest(english=english, variant=variant):
                    self.assertEqual(
                        self.names(variant, 6), expected,
                        f"'{variant}' and '{english}' must be the same search")

    def test_a_district_in_telugu_finds_the_district(self):
        """No row for Medak in the concept table, and none needed.

        Transliteration is a character pass, so all 61 districts work and none
        of them is a line somebody has to remember to add.
        """
        for telugu, english in [("మెదక్", "Medak"), ("ఖమ్మం", "Khammam")]:
            with self.subTest(telugu=telugu):
                self.assertIn(english, self.names(telugu, 6))

    def test_the_district_is_not_in_the_concept_table(self):
        """Guards the claim above. If someone "fixes" Telugu districts by
        adding rows, transliteration has silently stopped working and the
        other fifty-nine are broken."""
        source = CONCEPTS.read_text(encoding="utf-8").lower()
        for name in ("medak", "khammam", "warangal", "guntur"):
            with self.subTest(name=name):
                self.assertNotIn(f'"{name}"', source)

    def test_the_dairy_query_reaches_what_we_hold(self):
        """Telugu, Tanglish and English all land on the same thin answer.

        Thin because the graph holds one dairy-adjacent entity — see
        test_a_topic_we_barely_cover_is_not_padded in test_search_experience.
        The languages must agree even when the answer is disappointing.
        """
        english = self.names("dairy", 6)
        self.assertEqual(self.names("పాడి పరిశ్రమ", 6), english)
        self.assertEqual(self.names("paala parishrama", 6), english)

    def test_a_tanglish_typo_still_lands(self):
        """"lift technisian" is a misspelling of a Tanglish spelling.

        The leading results must agree; the fuzzy tail is allowed to differ,
        because one of the two strings is a real English word and the other is
        not, and pinning the whole list would be pinning noise.
        """
        self.assertEqual(self.names("lift technisian", 4), self.names("lift technician", 4))

    def test_mixed_script_is_one_query(self):
        """"మెదక్ electrician" is how a bilingual person actually types."""
        names = self.names("మెదక్ electrician", 10)
        joined = " | ".join(names).lower()
        self.assertIn("medak", joined)
        self.assertIn("electrician", joined)

    def test_natural_telugu_and_tanglish_sentences_find_trade_and_district(self):
        """Natural language sentences with conversational particles and locatives."""
        # 1. Natural sentence with conversational filler ("నాకు ... కావాలి")
        names1 = self.names("నాకు electrician course కావాలి", 10)
        joined1 = " | ".join(names1).lower()
        self.assertIn("electrician", joined1)

        # 2. Tanglish query with postposition ("medak lo electrician course")
        names2 = self.names("medak lo electrician course", 10)
        joined2 = " | ".join(names2).lower()
        self.assertIn("medak", joined2)
        self.assertIn("electrician", joined2)

        # 3. Telugu suffixed district ("మెదక్లో ఎలక్ట్రిషియన్ కోర్స్")
        names3 = self.names("మెదక్లో ఎలక్ట్రిషియన్ కోర్స్", 10)
        joined3 = " | ".join(names3).lower()
        self.assertIn("medak", joined3)
        self.assertIn("electrician", joined3)


# ═══════════════════════════ 2. the table cannot rot
class ConceptTableIntegrityTest(MultilingualBase):

    def test_every_expansion_reaches_a_live_entity(self):
        """An expansion that matches nothing costs a query and returns silence.

        Reachable by NAME or by TYPE: no entity is called "government scheme",
        but that is the humanised GovernmentScheme type and matching it returns
        all forty. Same rule test_search_experience applies to EXPANSIONS.
        """
        dead = self.js("""
            const dead = [];
            for (const c of CONCEPTS.concepts)
              for (const t of c.expands_to || []) {
                const n = ml.normalise(t);
                const byName = ents.some((e) => matchTerm(n, e.canonical_name));
                const byType = ents.some((e) => humaniseType(e.entity_type) === n);
                if (!byName && !byType) dead.push(`${c.id} -> ${t}`);
              }
            console.log(JSON.stringify(dead));
        """)
        self.assertEqual(dead, [], f"expansions that reach nothing: {dead}")

    def test_no_two_concepts_share_a_phonetic_key(self):
        """A collision silently disables one concept's Tanglish path.

        "raitu" (farmer) and "rayiti" (subsidy) both reduce to "rt", which is
        why the skeleton has a minimum length. This is the test that noticed.
        """
        clashes = self.js("""
            const seen = new Map(), clashes = [];
            for (const c of CONCEPTS.concepts) {
              const all = [c.id, c.en_canonical, ...(c.en || []), ...(c.tanglish || []),
                           ...(c.te || []).map(ml.transliterateTelugu)];
              for (const a of all) {
                const k = ml.phoneticKey(a);
                if (!k) continue;
                if (seen.has(k) && seen.get(k) !== c.id) clashes.push(`${k}: ${seen.get(k)} / ${c.id}`);
                else if (!seen.has(k)) seen.set(k, c.id);
              }
            }
            console.log(JSON.stringify([...new Set(clashes)]));
        """)
        self.assertEqual(clashes, [], f"phonetic collisions: {clashes}")

    def test_every_concept_is_shaped_the_same(self):
        bad = self.js("""
            const bad = [];
            const ids = new Set();
            for (const c of CONCEPTS.concepts) {
              if (!c.id || !/^[a-z0-9-]+$/.test(c.id)) bad.push(`bad id: ${c.id}`);
              if (ids.has(c.id)) bad.push(`duplicate id: ${c.id}`);
              ids.add(c.id);
              if (!c.en_canonical) bad.push(`${c.id}: no en_canonical`);
              if (!(c.expands_to || []).length) bad.push(`${c.id}: no expands_to`);
              for (const k of ["en", "te", "tanglish", "expands_to"])
                if (c[k] !== undefined && !Array.isArray(c[k])) bad.push(`${c.id}.${k} is not a list`);
            }
            console.log(JSON.stringify(bad));
        """)
        self.assertEqual(bad, [], f"malformed concepts: {bad}")

    def test_the_telugu_column_is_actually_telugu(self):
        """A Latin string in `te` is a row that will never be reached that way
        and a maintainer misled about what the column is for."""
        bad = self.js("""
            const bad = [];
            for (const c of CONCEPTS.concepts)
              for (const t of c.te || [])
                if (!ml.hasTelugu(t)) bad.push(`${c.id}: ${t}`);
            console.log(JSON.stringify(bad));
        """)
        self.assertEqual(bad, [], f"non-Telugu entries in `te`: {bad}")

    def test_tanglish_does_not_repeat_what_transliteration_gives_free(self):
        """A Tanglish entry that equals a transliterated Telugu entry is a
        second place to maintain the same fact."""
        dupes = self.js("""
            const dupes = [];
            for (const c of CONCEPTS.concepts) {
              const free = new Set((c.te || []).map((t) => ml.normalise(ml.transliterateTelugu(t))));
              for (const t of c.tanglish || [])
                if (free.has(ml.normalise(t))) dupes.push(`${c.id}: ${t}`);
            }
            console.log(JSON.stringify(dupes));
        """)
        self.assertEqual(dupes, [], f"redundant tanglish rows: {dupes}")


# ═══════════════════════════ 3. transliteration and the phonetic key
class TransliterationTest(MultilingualBase):

    def test_known_words(self):
        got = self.js("""
            const words = ["మెదక్","ఖమ్మం","లిఫ్ట్","రోబోటిక్స్","వరంగల్","నిజామాబాద్","కరీంనగర్"];
            console.log(JSON.stringify(words.map(ml.transliterateTelugu)));
        """)
        self.assertEqual(got, ["medak", "khammam", "lift", "robotiks",
                               "varangal", "nijamabad", "karinnagar"])

    def test_the_districts_that_do_not_transliterate_exactly_are_still_found(self):
        """"nijamabad" is one edit from Nizamabad and "karinnagar" one from
        Karimnagar — the anusvara assimilates to the following consonant in
        speech and the English spellings do not follow it. The fuzzy rung was
        already there for exactly this, so no table is needed."""
        for telugu, english in [("నిజామాబాద్", "Nizamabad"),
                                ("కరీంనగర్", "Karimnagar"),
                                ("వరంగల్", "Warangal")]:
            with self.subTest(telugu=telugu):
                self.assertIn(english, self.names(telugu, 6))

    def test_non_telugu_passes_through(self):
        got = self.js('console.log(JSON.stringify('
                      'ml.transliterateTelugu("Medak district 2026")));')
        self.assertEqual(got, "Medak district 2026")

    def test_the_zero_width_joiner_does_not_split_a_word(self):
        """"వైర్‌మ్యాన్" is commonly typed with a U+200C and just as commonly
        without. The two must be the same string to us."""
        same = self.js("""
            console.log(JSON.stringify(
              ml.normalise("వైర్\\u200cమ్యాన్") === ml.normalise("వైర్మ్యాన్")));
        """)
        self.assertTrue(same)

    def test_spelling_variants_share_a_key(self):
        pairs = [("electrician", "elektrishian"), ("technician", "technisian"),
                 ("khammam", "kammam"), ("medak", "medhak")]
        got = self.js(f'console.log(JSON.stringify({json.dumps(pairs)}'
                      f'.map(([a, b]) => [ml.phoneticKey(a), ml.phoneticKey(b)])));')
        for (a, b), (ka, kb) in zip(pairs, got):
            with self.subTest(pair=(a, b)):
                self.assertEqual(ka, kb, f"'{a}' and '{b}' must key alike")

    def test_a_short_word_gets_no_key(self):
        """Two letters of skeleton is not evidence — "rt" is raitu, root, rate
        and art. Those words are still reachable as exact aliases."""
        got = self.js('console.log(JSON.stringify('
                      '["ai", "ev", "raitu", "jilla"].map(ml.phoneticKey)));')
        self.assertEqual(got, ["", "", "", ""])


# ═══════════════════════════ 4. English is untouched
class EnglishUnchangedTest(MultilingualBase):
    """The brief's hard constraint: do not sacrifice the existing quality.

    test_search_experience holds the four worked examples. This holds the
    thing that would break them quietly — the resolver firing on a query it
    was never meant to see and adding terms that reorder the page.
    """

    def test_a_district_name_resolves_to_no_concept(self):
        got = self.js("""
            const out = {};
            for (const q of ["warangal", "medak", "guntur"])
              out[q] = ml.resolveQuery(q).concepts.map((c) => c.id);
            console.log(JSON.stringify(out));
        """)
        self.assertEqual(got, {"warangal": [], "medak": [], "guntur": []})

    def test_a_known_entity_still_ranks_first_for_its_own_name(self):
        """Word-level resolution fires on multi-word English too: "kisan" is
        the farmer concept and "credit" the loan one. Both are reasonable and
        neither may displace the row the user actually named."""
        for name in ("Kisan Credit Card", "Solar Panel Assembly Unit",
                     "Welding & Metal Fabrication"):
            with self.subTest(name=name):
                self.assertEqual(self.names(name, 1), [name])

    def test_the_worked_examples_still_rank_the_same(self):
        self.assertEqual(self.names("AI", 1), ["Artificial Intelligence"])
        self.assertEqual(self.names("PMEGP", 1),
                         ["Prime Minister's Employment Generation Programme"])
        self.assertEqual(self.names("Tiles", 1), ["Tiles Fixing (Tile Mason)"])

    def test_a_short_query_still_cannot_match_inside_a_word(self):
        joined = " | ".join(self.names("AI", 24)).lower()
        for junk in ("maize", "painting services", "retail & local commerce"):
            with self.subTest(junk=junk):
                self.assertNotIn(junk, joined)

    def test_the_resolution_is_reported_back(self):
        """A Telugu speaker seeing English cards has no way to tell whether we
        understood them or guessed."""
        got = self.js("""
            const out = {};
            for (const q of ["ఎలక్ట్రిషియన్", "raitu", "welding", "మెదక్"])
              out[q] = ml.describeResolution(ml.resolveQuery(q));
            console.log(JSON.stringify(out));
        """)
        self.assertEqual(got["ఎలక్ట్రిషియన్"], "electrician")
        self.assertEqual(got["raitu"], "farmer")
        self.assertEqual(got["మెదక్"], "medak")
        self.assertIsNone(got["welding"],
                          "an English synonym is not a translation — announcing "
                          "it makes the box look confused")


if __name__ == "__main__":
    unittest.main(verbosity=2)
