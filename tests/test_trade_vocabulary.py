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


@unittest.skipUnless(NODE, NODE_REASON)
class ConstructionSearchTest(unittest.TestCase):
    """The construction dataset's contribution, which was almost entirely
    correcting wrong answers rather than adding coverage.

    16 of 22 probe queries changed: 7 went from nothing to something, and NINE
    had a confident wrong answer. That ratio is the opposite of the electrician
    document's, and for a clear reason — the graph holds none of these fifteen
    trades as skills, so every query about them was landing on whatever the
    fuzzy rung could reach.
    """

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
              out[q] = r ? r.canonical_name : null;
            }
            console.log(JSON.stringify(out));
        """ % json.dumps(list(queries)))

    def test_crane_operator_no_longer_returns_maize(self):
        """The worst single result found in this whole exercise, and a real bug
        rather than a gap.

        `crane` and `corn` reduce to the SAME consonant skeleton — `krn` — so
        the phonetic layer resolved "crane operator" to the `maize` concept,
        whose English alias is "corn", and returned **Maize** on an EXACT
        match. Confidently, at the top, for a trade that builds the Hyderabad
        metro.

        The fix is the mechanism the vocabulary already provides: an explicit
        alias resolves through the ALIAS layer, which outranks phonetic, so the
        collision never gets a chance to fire.

        THE BARE WORD `crane` IS NOT FIXED, AND DELIBERATELY SO.
        Adding it as an alias was tried and rejected by
        `test_no_two_concepts_share_a_phonetic_key`: two concepts may not claim
        one key, because a collision silently disables one of their Tanglish
        paths. So "corn" and "crane" cannot both be aliases, and "corn" is the
        English name of a crop grown across both states — a farmer looking up
        maize outranks the one-word form of a query that works in every other
        phrasing.

        Fixing it properly means changing when the phonetic layer is allowed to
        fire, which is a search-engine change and out of scope here. Recorded
        in docs/TRADE_ENRICHMENT_REPORT.md as a known limit with its cause.
        """
        got = self.top(["crane operator", "tower crane"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertNotEqual(name, "Maize",
                                    "the corn/crane phonetic collision is back")

    def test_the_bare_word_crane_is_a_known_and_recorded_limitation(self):
        """Asserted so the trade-off stays visible. If somebody later changes
        the phonetic layer and this starts passing, the report is stale and
        should be updated — a failing test here is good news."""
        got = self.top(["crane"])
        self.assertEqual(
            got["crane"], "Maize",
            "the corn/crane collision appears to be fixed — update "
            "docs/TRADE_ENRICHMENT_REPORT.md and delete this test")

    def test_the_eight_other_confidently_wrong_answers_are_gone(self):
        """Each of these returned something unrelated with conviction."""
        was_wrong = {
            "road roller": "Microcontroller Programming",
            "jcb driver": "PLC, Drives, Sensors and Cabling",
            "pump technician": "Field Technician - Computing & Peripherals - ELE/Q4601",
            "borewell technician": "Field Technician - Computing & Peripherals - ELE/Q4601",
            "modular kitchen": "Cloud Kitchen",
            "aluminium fabricator": "Welding (MIG/TIG/Arc)",
            "pop plasterer": "Masonry & Brickwork",
        }
        got = self.top(was_wrong)
        for query, old in was_wrong.items():
            with self.subTest(query=query):
                self.assertIsNotNone(got[query], f"{query!r} returns nothing")
                self.assertNotEqual(got[query], old,
                                    f"{query!r} is back to its old wrong answer")

    def test_a_trade_reaches_the_business_the_graph_already_holds(self):
        """The gap this document exposes: five trades exist as BUSINESSES you
        could start and not as skills you could learn. Until the candidates are
        reviewed, the least a search can do is reach the business."""
        expected = {
            "gypsum": "POP Works",
            "drywall": "POP Works",
            "false ceiling": "POP Works",
            "glazier": "Aluminium Fabrication",
            "upvc window": "Aluminium Fabrication",
            "borewell technician": "Borewell Drilling Services",
            "pump technician": "Submersible Pump Installation & Repair",
        }
        got = self.top(expected)
        for query, fragment in expected.items():
            with self.subTest(query=query):
                self.assertIsNotNone(got[query], f"{query!r} returns nothing")
                self.assertIn(fragment.lower(), got[query].lower())


class ConstructionSourceTest(unittest.TestCase):
    """What the construction source module has to keep recording."""

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import construction_trades_2026     # noqa: PLC0415
        self.mod = construction_trades_2026
        self.text = (ROOT / "research" / "sources"
                     / "construction_trades_2026.py").read_text(encoding="utf-8")

    def test_all_fifteen_trades_are_new(self):
        self.assertEqual(len(self.mod.ROLES), 15)
        self.assertEqual(len(self.mod.new_roles()), 15)
        self.assertEqual(self.mod.merge_roles(), [])

    def test_the_five_business_pairings_point_at_real_entities(self):
        """"A business you cannot learn" is only a finding if the business is
        actually there."""
        known = {e["canonical_name"] for e in entities()}
        pairings = self.mod.businesses_without_a_skill()
        self.assertEqual(len(pairings), 5)
        for slug, business in pairings.items():
            with self.subTest(slug=slug):
                self.assertIn(business, known)

    def test_the_copy_pasted_aliases_were_not_carried_across(self):
        """ROLE 3 (Aluminium Fabricator) lists ROLE 4's uPVC alternative titles
        verbatim — a copy-paste defect in the source, visible because the two
        roles' own tool tables disagree. The wrong aliases must not ship."""
        aluminium = next(r for r in self.mod.ROLES
                         if r["slug"] == "aluminium-fabricator")
        for wrong in ("uPVC Window Technician", "uPVC Fitting Specialist",
                      "Fenestration Installer"):
            with self.subTest(alias=wrong):
                self.assertNotIn(wrong, aluminium["aliases"])
        self.assertIn("SOURCE DEFECT", aluminium["notes"])

    def test_it_records_that_declaring_no_limits_is_not_reassurance(self):
        """This document, unlike the electrician one, admits nothing about
        itself. That makes it less self-aware, not more reliable, and the next
        reader needs to be told so."""
        self.assertEqual(self.mod.SOURCE["self_declared_limits"], [])
        self.assertIn("Absence of a caveat is not evidence of accuracy",
                      self.text)

    def test_confidence_still_respects_the_secondary_source_ceiling(self):
        for value in re.findall(r'"confidence":\s*(\d+)', self.text):
            with self.subTest(confidence=value):
                self.assertLessEqual(int(value), 60)


@unittest.skipUnless(NODE, NODE_REASON)
class ManufacturingSearchTest(unittest.TestCase):
    """The manufacturing dataset contributed the LEAST vocabulary of the three,
    and finding that out is the point.

    Its fifteen trades are machine-shop roles the graph holds almost nothing
    about. Eleven of them have no entity to point a concept at, so nine
    concepts were written, measured, and six were deleted again — see
    `test_a_concept_must_name_a_thing_not_a_sector`.

    Two survived. Both were kept because the measurement showed them helping,
    not because they seemed reasonable.
    """

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
              out[q] = r ? r.canonical_name : null;
            }
            console.log(JSON.stringify(out));
        """ % json.dumps(list(queries)))

    def test_the_lathe_trade_resolves_to_the_one_skill_it_is(self):
        """The document splits one trade across three careers — Lathe Machine
        Operator, Turner and Machinist — and even lists "Turner" as an alias of
        the first. The graph is right and the document is wrong: `Lathe
        Operation` is one Skill. All three names now reach it.

        Before: "turner" returned NOTHING and "machinist" returned *CNC
        Machining Job Shop* — a business, not a trade to learn.
        """
        got = self.top(["turner", "machinist", "lathe operator",
                        "conventional turner", "all round machinist"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "Lathe Operation")

    def test_a_press_operator_reaches_sheet_metal_not_groundnut_oil(self):
        """"press operator" returned *Cold-Pressed Groundnut/Sesame Oil (Kachi
        Ghani) Unit*. Both senses of "press" are real; only one is a factory
        job."""
        got = self.top(["press operator", "power press operator"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertIn("sheet metal", name.lower())

    def test_a_concept_must_name_a_thing_not_a_sector(self):
        """The mistake this document caught me making.

        Six concepts were given `expands_to: ["manufacturing"]` because their
        trades had no better anchor. That term matches every entity with the
        word in its name, and **"Masala Powder Manufacturing Unit" became the
        top hit for eleven separate queries** — tool and die maker, quality
        inspector, hydraulic technician, assembly line, bench fitter and more.
        Worse than the wrong answers they replaced.

        All six were deleted. An expansion has to name a THING the graph holds,
        not the sector it sits in — which is the rule document A already stated
        and this is the measurement that proves it has teeth.
        """
        by_id = {c["id"]: c for c in load_concepts()["concepts"]}
        for dropped in ("tool-and-die", "fitter", "quality-inspector",
                        "fluid-power", "moulding", "assembly-line", "milling"):
            with self.subTest(concept=dropped):
                self.assertNotIn(dropped, by_id)

        # And no TRADE concept may expand to a bare sector word. The
        # `manufacturing` concept itself is exempt: it is the sector, and
        # expanding to its own name is what it is for.
        for concept in load_concepts()["concepts"]:
            if concept["id"] == "manufacturing":
                continue
            with self.subTest(concept=concept["id"]):
                self.assertNotIn("manufacturing", concept["expands_to"],
                                 "a bare sector expansion drags in every entity "
                                 "whose name contains the word")

    def test_masala_powder_is_not_the_answer_to_a_machine_shop_question(self):
        """A named guard for the specific regression, because it was mine."""
        got = self.top(["tool and die maker", "quality inspector",
                        "hydraulic technician", "assembly line", "bench fitter"])
        for query, name in got.items():
            with self.subTest(query=query):
                if name:
                    self.assertNotIn("masala", name.lower())


class ManufacturingSourceTest(unittest.TestCase):
    """What the manufacturing source module has to keep recording."""

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import manufacturing_trades_2026    # noqa: PLC0415
        self.mod = manufacturing_trades_2026
        self.text = (ROOT / "research" / "sources"
                     / "manufacturing_trades_2026.py").read_text(encoding="utf-8")

    def test_three_roles_collapse_onto_one_lathe_skill(self):
        """The document over-splits: it presents one trade as three careers and
        separately names one of them as an alias of another."""
        self.assertEqual(len(self.mod.ROLES), 15)
        lathe = [r for r in self.mod.ROLES
                 if r["existing"] == "Lathe Operation"]
        self.assertEqual(len(lathe), 3)
        self.assertEqual({r["slug"] for r in lathe},
                         set(self.mod.COLLAPSES_ONTO_LATHE))

    def test_the_turner_copy_paste_was_not_propagated(self):
        """Role 11 (Turner) carries role 12's machinist alternative titles."""
        turner = next(r for r in self.mod.ROLES if r["slug"] == "turner")
        for wrong in ("All-round Machinist", "Machine Shop Machinist",
                      "General Machinist"):
            with self.subTest(alias=wrong):
                self.assertNotIn(wrong, turner["aliases"])
        self.assertIn("SOURCE DEFECT", turner["notes"])

    def test_the_cross_document_overlap_is_surfaced_by_hand(self):
        """`Fitter` here and `machine-maintenance-technician` from the
        electrician document share two alternative titles and are close to the
        same trade.

        `collection/dedupe.py` scores the two TITLES at 0.00 against its 0.80
        threshold — it compares titles, and these are two different words for
        one job. Nothing automatic will catch it, so the candidate says so.
        """
        fitter = next(r for r in self.mod.ROLES if r["slug"] == "fitter")
        self.assertIn("CROSS-DOCUMENT OVERLAP", fitter["notes"])
        self.assertIn("0.00", fitter["notes"])
        self.assertIn("fitter", self.mod.CROSS_DOCUMENT_OVERLAP)

    def test_the_strong_self_claim_is_recorded_and_qualified(self):
        """It claims "No statistics are invented" — the boldest of the three.
        The module has to say both that it claims this and why that is still
        not a citation."""
        flat = " ".join(self.text.split())
        self.assertIn("No statistics are invented", flat)
        self.assertIn("names no survey and links to nothing", flat)

    def test_confidence_still_respects_the_secondary_source_ceiling(self):
        for value in re.findall(r'"confidence":\s*(\d+)', self.text):
            with self.subTest(confidence=value):
                self.assertLessEqual(int(value), 60)


class ReviewerNoteTest(unittest.TestCase):
    """Every candidate must quote ITS OWN document's limits."""

    def test_each_document_gets_its_own_caveat(self):
        """A first version branched on whether the limits list was empty and
        then hard-coded the ELECTRICIAN document's caveat for every document
        that had one — so manufacturing candidates claimed their contacts were
        `XXXX` placeholders, which is the one thing that document does not do.
        """
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources.emit_candidates import (            # noqa: PLC0415
            DOCUMENTS, candidates)
        notes = {name: candidates(mod)[0].raw["_reviewer_note"]
                 for name, mod in DOCUMENTS.items()}
        self.assertIn("XXXX", notes["electrician"])
        self.assertNotIn("XXXX", notes["manufacturing"])
        self.assertNotIn("XXXX", notes["construction"])
        self.assertIn("declares no limits on itself", notes["construction"])
        self.assertIn("market surveys", notes["manufacturing"])


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
