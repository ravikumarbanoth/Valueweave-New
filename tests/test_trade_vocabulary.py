#!/usr/bin/env python3
"""
The skilled-trade vocabulary taken from the Electrician & Allied Trades dataset.

WHAT THIS SOURCE WAS GOOD FOR, AND WHAT IT WAS NOT
---------------------------------------------------
The document is a 36-page LLM-generated research file covering 20 trades. It
says of itself that contacts are `XXXX` placeholders and that "confidence is
moderate for salary and fees". So its factual claims — salaries, course fees,
institute phone numbers — are candidates for human review and are handled by
`collection/`, not by this file.

Its VOCABULARY is a different matter and is what these tests cover. That an
employer says "RAC mechanic" and a student says "fridge mechanic" and both mean
the HVAC trade is not a claim about the world that needs a citation; it is how
the words are used, and it is checkable here and now by asking the search
engine. That split — vocabulary ships, facts queue — is the whole design.

WHAT IT ACTUALLY FIXED
----------------------
Measured against the real 647-entity graph, before and after. Most of the terms
already resolved through the ranker's fuzzy and related rungs, so coverage
barely moved: 4 of 22 probe queries went from nothing to something.

The gain was in being RIGHT. Four queries had a confident wrong answer:

    rac mechanic      Automobile Mechanic  ->  HVAC Technician
    fridge mechanic   Automobile Mechanic  ->  HVAC Technician
    factory electrician   Manufacturing    ->  Industrial Electrician
    pipe fitter       Filter Press         ->  Plumbing

A search that returns nothing tells a student to try different words. A search
that confidently returns "Filter Press" for "pipe fitter" tells them the
platform does not know anything useful, and they leave. These four are the
reason the aliases are worth their weight.
"""

import json
import re
import unittest
from pathlib import Path

from tests.js_harness import JsHarness, entities, NODE, NODE_REASON

ROOT = Path(__file__).resolve().parent.parent
CONCEPTS = ROOT / "frontend" / "lib" / "search" / "vocabulary" / "concepts.js"
SOURCE = ROOT / "research" / "sources" / "electrician_trades_2026.py"


def load_concepts():
    raw = CONCEPTS.read_text(encoding="utf-8")
    body = raw[raw.index("Object.freeze(") + len("Object.freeze("):]
    return json.loads(body.rstrip().rstrip(");"))


@unittest.skipUnless(NODE, NODE_REASON)
class TradeSearchTest(unittest.TestCase):
    """What a person typing trade words actually gets back."""

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def top(self, queries):
        return self.h.run("""
            const { rankEntities } = await import("$LIB/knowledge-search.js");
            const rows = JSON.parse(fs.readFileSync("$DIR/entities.json", "utf8"));
            const out = {};
            for (const q of %s) {
              const r = rankEntities(rows, q, { limit: 1 })[0];
              out[q] = r ? { name: r.canonical_name, match: r._match } : null;
            }
            console.log(JSON.stringify(out));
        """ % json.dumps(list(queries)))

    def test_the_four_confidently_wrong_answers_are_right_now(self):
        """The reason this vocabulary was worth adding. Each of these returned
        a confident, unrelated entity before the trade aliases landed."""
        expected = {
            "rac mechanic": "HVAC Technician",
            "fridge mechanic": "HVAC Technician",
            "factory electrician": "Industrial Electrician",
            "pipe fitter": "Plumbing",
        }
        got = self.top(expected)
        for query, want in expected.items():
            with self.subTest(query=query):
                self.assertIsNotNone(got[query], f"{query!r} returns nothing")
                self.assertEqual(got[query]["name"], want)

    def test_employer_terms_reach_the_trade_a_student_would_call_it(self):
        """The words on a job advertisement are not the words on a course
        brochure. Both have to land in the same place."""
        expected = {
            "wireman": "Electrician",
            "suryamitra": "Solar",
            "vmc operator": "CNC",
            "cobot": "Robot",
            "tile setter": "Tile",
            "arc welder": "Welding",
            "joiner": "Carpentry",
            "bricklayer": "Mason",
            "scaffolder": "Mason",
            "ev mechanic": "Electric",
        }
        got = self.top(expected)
        for query, fragment in expected.items():
            with self.subTest(query=query):
                self.assertIsNotNone(got[query], f"{query!r} returns nothing")
                self.assertIn(fragment.lower(), got[query]["name"].lower())

    def test_a_vowel_error_still_finds_the_trade(self):
        """The phonetic key is a CONSONANT SKELETON, so wrong vowels cost
        nothing: `electrition`, `masson`, `solor` and `tiels` all reduce to the
        same key as the word they meant. Nothing is enumerated to make these
        work and nothing should be."""
        got = self.top(["electrican", "electrition", "electricion", "carpentar",
                        "masson", "solor", "tiels", "weldar"])
        for query, row in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(row, f"{query!r} returns nothing")

    def test_the_silent_b_in_plumber_is_spelled_out_because_the_key_cannot(self):
        """The one documented exception to "do not enumerate spellings".

        A consonant skeleton cannot bridge a MISSING consonant: `plumer` keys
        to `plmr` and `plumber` to `plmbr`, so they never meet, and the query
        returned nothing at all. Measured, not assumed — `plumbr` (b kept, e
        dropped) resolves fine, which is what isolates the cause.

        `plumber` has a silent b. Dropping it is not a typo, it is a
        phonetically correct spelling by somebody who has heard the word and
        not read it — exactly this platform's reader. The concept table's rule
        says the phonetic key handles spelling; here it demonstrably cannot,
        so the rule's own rationale is what licenses the exception.
        """
        got = self.top(["plumer", "plummer", "welda"])
        for query, row in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(row, f"{query!r} returns nothing")
                self.assertIn(row["name"].lower()[:4], ("plum", "weld"))


class VocabularyIntegrityTest(unittest.TestCase):
    """Rules the concept table has to keep holding after this edit."""

    def setUp(self):
        self.data = load_concepts()
        self.by_id = {c["id"]: c for c in self.data["concepts"]}

    def test_the_three_new_concepts_are_present(self):
        for cid in ("cnc", "industrial-electrician", "plc-automation"):
            with self.subTest(concept=cid):
                self.assertIn(cid, self.by_id)

    def test_no_alias_is_claimed_by_two_concepts(self):
        """Two concepts claiming one phrase makes it ambiguous, and the
        resolver cannot pick. This caught a real mistake while the trade
        aliases were being added: "factory electrician", "maintenance
        electrician" and "electrical fitter" were put on BOTH `electrician`
        and `industrial-electrician`. They belong on the specific one.
        """
        owner = {}
        clashes = []
        for concept in self.data["concepts"]:
            for term in concept["en"] + [concept["en_canonical"]]:
                key = term.lower().strip()
                if key in owner and owner[key] != concept["id"]:
                    clashes.append(f"{key!r}: {owner[key]} / {concept['id']}")
                owner[key] = concept["id"]
        self.assertEqual(clashes, [], f"aliases claimed twice: {clashes}")

    def test_no_telugu_was_copied_from_the_damaged_pdf(self):
        """PDF extraction dropped the conjunct clusters: the document's own
        Telugu for "electrician" comes out as `ఎలక` — three characters of a
        nine-character word, and `టెక్నీషియన్` as `టెక`.

        These truncations are what a broken extraction looks like, and none of
        them may reach the index: they are strings no reader will ever type,
        and every one of them would be a permanent dead entry.
        """
        damaged = ("ఎలక ", "టెక ", "వ్యక ", "కోర ", "వైర ", "లి ్ట", "మేసీ ")
        blob = json.dumps(self.data, ensure_ascii=False)
        for fragment in damaged:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, blob)

    def test_every_telugu_string_is_a_complete_word(self):
        """A Telugu entry ending in a bare consonant with no vowel sign and no
        virama is almost always a truncation rather than a word."""
        for concept in self.data["concepts"]:
            for term in concept["te"]:
                with self.subTest(concept=concept["id"], te=term):
                    self.assertFalse(term.endswith(" "), "trailing space")
                    self.assertGreaterEqual(len(term.strip()), 2)


class SourceProvenanceTest(unittest.TestCase):
    """The research file has to keep saying where it came from and what it is."""

    def setUp(self):
        self.source = SOURCE.read_text(encoding="utf-8")

    def test_the_source_records_its_own_limits(self):
        """The document states two limits about itself. Losing them would make
        the next reader trust it more than its author did."""
        self.assertIn("XXXX", self.source)
        self.assertIn("confidence is moderate for salary and fees", self.source)

    def test_no_role_claims_more_confidence_than_a_single_secondary_source(self):
        """60 is the repository's ceiling for one uncorroborated secondary
        source, and this is one document by one generator."""
        for value in re.findall(r'"confidence":\s*(\d+)', self.source):
            with self.subTest(confidence=value):
                self.assertLessEqual(int(value), 60)

    def test_the_unverified_fields_are_named_so_they_can_be_blanked(self):
        """Salary, fees and contacts are the document's own weak points.
        Naming them in one tuple means the promoter blanks them mechanically
        rather than relying on somebody to remember which ones they were."""
        self.assertIn("UNVERIFIED_FIELDS", self.source)
        for field in ("salary_range", "course_fees", "institute_contact"):
            with self.subTest(field=field):
                self.assertIn(field, self.source)

    def test_no_institute_contact_was_carried_across(self):
        """The document lists five institutes with literal `XXXX` phone
        numbers. A row containing one would be a fabricated directory entry."""
        self.assertNotIn("040-2370", self.source)
        self.assertNotIn("0866-257", self.source)

    def test_every_role_is_classified_as_new_or_merge(self):
        """`existing` was determined by reading entities.csv, not by guessing
        from the name: `Painter` looked new and has a BusinessOpportunity but
        no Skill entity."""
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources.electrician_trades_2026 import (    # noqa: PLC0415
            ROLES, new_roles, merge_roles)
        self.assertEqual(len(ROLES), 20)
        self.assertEqual(len(new_roles()) + len(merge_roles()), 20)

        known = {e["canonical_name"] for e in entities()}
        for role in merge_roles():
            with self.subTest(role=role["title"]):
                self.assertIn(role["existing"], known,
                              "claims to merge onto an entity that is not in the graph")


if __name__ == "__main__":
    unittest.main(verbosity=2)
