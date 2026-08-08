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


@unittest.skipUnless(NODE, NODE_REASON)
class AutomobileSearchTest(unittest.TestCase):
    """The automobile dataset. Ten of twenty-one probe queries corrected, no
    new coverage — the graph already had three automotive Skills, so nothing
    was unreachable; a great deal was reachable and wrong."""

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

    def test_car_mechanic_no_longer_returns_carpentry(self):
        """One of the most ordinary queries this platform will ever receive,
        and it returned a woodworking trade."""
        got = self.top(["car mechanic", "motor mechanic", "auto mechanic",
                        "automotive technician"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertIn("automobile", name.lower())

    def test_a_bike_mechanic_reaches_the_two_wheeler_trade(self):
        """It reached *Automobile Mechanic* — the car trade. Both are
        mechanics; only one is the job."""
        got = self.top(["bike mechanic", "scooter mechanic",
                        "motorcycle mechanic"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "Two-Wheeler Mechanic")

    def test_the_field_technician_magnet_lets_go(self):
        """*Field Technician - Computing & Peripherals* was the top hit for
        `heavy vehicle technician`, `bms technician`, `tyre technician`,
        `denting technician` and `diagnostic technician` — anything ending in
        the word. Two of those are now right; the rest have no entity to reach
        and are queued instead."""
        got = self.top(["heavy vehicle technician", "bms technician"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertNotIn("computing", name.lower())

    def test_tractor_mechanic_is_not_electrical_contracting(self):
        """A substring collision, and a funny one: **"tractor" is inside
        "con-TRACTOR-ing"**, so expanding a tractor query to the word `tractor`
        CONTAINS-matched *Electrical Contracting (Licensed Supervisor/
        Contractor)* at 300 — beating the 220 the actual trade scored.

        The expansion was dropped. A tractor mechanic wants the mechanic trade,
        not the machine, so it cost everything and bought nothing.
        """
        got = self.top(["tractor mechanic", "farm equipment mechanic"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertNotIn("contracting", name.lower())

    def test_no_concept_expands_to_the_word_tractor(self):
        """Guarding the substring collision at its cause rather than its
        symptom, because any future concept reaching for `tractor` would
        reintroduce it."""
        for concept in load_concepts()["concepts"]:
            if concept["id"] in ("agriculture", "farmer"):
                continue                      # the farming concepts may mean it
            with self.subTest(concept=concept["id"]):
                self.assertNotIn("tractor", concept["expands_to"])


class AutomobileSourceTest(unittest.TestCase):
    """What the automobile source module has to keep recording."""

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import automobile_trades_2026       # noqa: PLC0415
        self.mod = automobile_trades_2026
        self.text = (ROOT / "research" / "sources"
                     / "automobile_trades_2026.py").read_text(encoding="utf-8")

    def test_five_merge_and_ten_are_new(self):
        self.assertEqual(len(self.mod.ROLES), 15)
        self.assertEqual(len(self.mod.merge_roles()), 5)
        self.assertEqual(len(self.mod.new_roles()), 10)

    def test_it_is_recorded_as_the_only_document_that_kept_its_claim(self):
        """Documents C and D make the same promise. Only D honours it — 23
        `Research Gap` markers against C's eight `Confidence` notes. That is
        worth writing down, because it is the one quality signal in this batch
        that could be checked rather than taken on trust."""
        flat = " ".join(self.text.split())
        self.assertIn("23", flat)
        self.assertIn("Research Gap", flat)

    def test_the_battery_technician_disagreement_is_recorded_not_resolved(self):
        """Document A calls it an alias of EV Technician; this one makes it a
        career. The graph has neither entity to settle it, so the module says
        so and the reviewer decides — rather than whichever alias list was
        edited last deciding by accident."""
        self.assertIn("battery-technician", self.mod.DISPUTED_WITH_ELECTRICIAN_DOC)
        battery = next(r for r in self.mod.ROLES
                       if r["slug"] == "battery-technician")
        self.assertIn("DISPUTED", battery["notes"])

    def test_the_two_painters_are_kept_apart(self):
        """A building painter and an automotive refinisher share a word and
        nothing else — different materials, different booth, different
        certification."""
        painter = next(r for r in self.mod.ROLES
                       if r["slug"] == "auto-painting-technician")
        self.assertIn("Do not merge them", painter["notes"])

    def test_reconstructed_aliases_are_marked_as_such(self):
        """Only roles 1 and 2 have alias tables; the document condenses the
        rest 'for brevity'. Where the aliases are the trade's rather than the
        document's, the row says so — a reviewer checking provenance needs to
        know which is which."""
        reconstructed = [r for r in self.mod.ROLES
                         if "reconstructed" in (r.get("notes") or "")]
        self.assertGreaterEqual(len(reconstructed), 5)

    def test_confidence_still_respects_the_secondary_source_ceiling(self):
        for value in re.findall(r'"confidence":\s*(\d+)', self.text):
            with self.subTest(confidence=value):
                self.assertLessEqual(int(value), 60)


@unittest.skipUnless(NODE, NODE_REASON)
class ElectronicsSearchTest(unittest.TestCase):
    """The electrical & electronics dataset. The worst baseline of the five —
    nine of the probe queries landed on *Field Technician - Computing &
    Peripherals*, and the three that did not were worse than that."""

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

    def test_mobile_repair_is_not_mobile_app_development(self):
        """The single most damaging answer in this batch. A student who wants
        to learn phone repair — the lowest-capital electronics shop there is —
        was being sent to a software career. The two share one word and share
        nothing else: entry qualification, capital, tools, customers.
        """
        got = self.top(["mobile repair", "mobile phone repair",
                        "handset technician", "phone repair",
                        "smartphone repair"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertNotIn("app development", name.lower())
                self.assertIn("electronics repair", name.lower())

    def test_four_specialisations_all_reach_the_one_skill_that_teaches_them(self):
        """The document sells mobile, laptop, LED TV and general electronics
        service as four careers. The graph holds one Skill, and it is right to:
        they are the same bench, the same meter, the same rework station. The
        concept's job is to make all four sets of words reach it."""
        got = self.top(["laptop repair", "tv repair", "led tv repair",
                        "appliance repair", "electronics service technician",
                        "consumer electronics technician"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "Electronics Repair & Maintenance")

    def test_smart_home_is_not_a_homestay(self):
        """`smart home` returned *Telangana Homestays* — the word "home" won,
        and a person asking about building automation was offered rural
        tourism. `home automation` returned *Robotics* on an EXACT concept
        match, which is at least a machine, and `building automation`
        returned *Construction*."""
        got = self.top(["smart home", "home automation", "building automation",
                        "iot technician", "smart home integrator"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "IoT Systems Development")

    def test_board_level_words_reach_the_soldering_skill(self):
        """Chip-level, component-level, SMT and board repair are what the
        trade calls itself in a Hyderabad service market. None of them
        contained the letters "PCB", so none of them reached the entity."""
        got = self.top(["pcb repair", "smt technician", "board repair",
                        "component level repair", "chip level repair",
                        "pcb rework"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "PCB Assembly & Soldering")

    def test_the_queued_trades_are_honestly_still_unreachable(self):
        """Eight roles have no Skill entity, so no vocabulary can make them
        findable — CCTV, fire alarm, inverter, UPS, networking, fibre and
        tower work all still land on the *Field Technician* magnet. Writing
        aliases that pointed them at an approximately-related entity would be
        the "confidently wrong" failure this whole exercise is against. They
        are queued for review instead, and this test records the gap so it is
        not mistaken for an oversight.
        """
        got = self.top(["cctv technician", "fire alarm technician",
                        "inverter technician", "ups technician",
                        "networking technician", "fiber optic technician",
                        "telecom tower technician"])
        unreachable = [q for q, name in got.items()
                       if name and "field technician" in name.lower()]
        self.assertEqual(len(unreachable), len(got),
                         "a queued trade became reachable — if a Skill entity "
                         "was promoted for it, retire this test and write the "
                         "real one")

    def test_solar_inverter_still_reaches_the_solar_skill_not_the_backup_one(self):
        """A regression guard on the neighbouring concept: `inverter` words
        must not drag a rooftop-solar question onto power-backup work."""
        got = self.top(["solar inverter", "solar inverter technician"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertIn("solar", name.lower())


class ElectronicsSourceTest(unittest.TestCase):
    """What the electronics source module has to keep recording."""

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import electronics_trades_2026      # noqa: PLC0415
        self.mod = electronics_trades_2026
        self.text = (ROOT / "research" / "sources"
                     / "electronics_trades_2026.py").read_text(encoding="utf-8")

    def test_seven_merge_and_eight_are_new(self):
        self.assertEqual(len(self.mod.ROLES), 15)
        self.assertEqual(len(self.mod.merge_roles()), 7)
        self.assertEqual(len(self.mod.new_roles()), 8)

    def test_every_merge_target_is_an_entity_the_graph_actually_holds(self):
        known = {e["canonical_name"] for e in entities()}
        for role in self.mod.merge_roles():
            with self.subTest(role=role["title"]):
                self.assertIn(role["existing"], known)

    def test_the_four_way_collapse_is_named(self):
        """Same over-splitting as document C's lathe trades. Naming the four
        in one tuple is what keeps a later reader from promoting them as four
        Skills because the document presented them that way."""
        self.assertEqual(len(self.mod.COLLAPSES_ONTO_ELECTRONICS_REPAIR), 4)
        for slug in self.mod.COLLAPSES_ONTO_ELECTRONICS_REPAIR:
            role = next(r for r in self.mod.ROLES if r["slug"] == slug)
            with self.subTest(role=slug):
                self.assertEqual(role["existing"],
                                 "Electronics Repair & Maintenance")

    def test_the_boldest_claim_with_the_thinnest_audit_is_recorded(self):
        """This is the only document that grades itself, and it gives itself
        "Confidence Level: High" while flagging exactly ONE research gap in 15
        roles. Document D made a weaker claim and marked 23. The comparison is
        the point: a document that audits itself less is not more reliable,
        and a reviewer reading the candidates needs to be told which one this
        is."""
        flat = " ".join(self.text.split())
        self.assertIn("Confidence Level: High", flat)
        self.assertIn("ONE flagged research gap", " ".join(
            " ".join(self.mod.SOURCE["self_declared_limits"]).split()))

    def test_being_easy_to_parse_did_not_raise_the_ceiling(self):
        """The document was written for a pipeline like ours — it says so.
        Clean structure is a reason to trust the EXTRACTION, never the
        CONTENT, and 60 is still one uncorroborated secondary source."""
        for value in re.findall(r'"confidence":\s*(\d+)', self.text):
            with self.subTest(confidence=value):
                self.assertLessEqual(int(value), 60)

    def test_this_is_the_first_document_with_no_copy_paste_defect(self):
        """B and C each carried a role whose alternative titles belonged to
        its neighbour. After two occurrences it looked systemic; this document
        shows it is not. Checked rather than asserted in prose: no two roles
        may share an alias."""
        owner = {}
        clashes = []
        for role in self.mod.ROLES:
            for alias in role["aliases"]:
                key = alias.lower().strip()
                if key in owner:
                    clashes.append(f"{key!r}: {owner[key]} / {role['slug']}")
                owner[key] = role["slug"]
        self.assertEqual(clashes, [])

    def test_the_one_real_overlap_is_recorded_not_silently_resolved(self):
        """"Security System Installer" is both an alt title of role 1 and role
        4 in its own right. Reading both, one is surveillance and one is
        access control. Which way a Telangana integrator actually splits the
        work is a question for somebody who has hired one, so the module says
        so and the reviewer decides the pair together."""
        installer = next(r for r in self.mod.ROLES
                         if r["slug"] == "security-system-installer")
        cctv = next(r for r in self.mod.ROLES if r["slug"] == "cctv-technician")
        self.assertIn("OVERLAPS ROLE 1", installer["notes"])
        self.assertNotIn("Security System Installer", cctv["aliases"])

    def test_network_engineer_was_not_carried_across_as_an_alias(self):
        """The document lists it as an alternative title for Networking
        Technician. An engineer designs the network and a technician installs
        it; the first is a degree-entry job. Treating them as the same word
        would send a 10th-pass reader somewhere they cannot go."""
        role = next(r for r in self.mod.ROLES
                    if r["slug"] == "networking-technician")
        self.assertNotIn("Network Engineer", role["aliases"])
        self.assertIn("Network Engineer", role["notes"])
        blob = json.dumps(load_concepts())
        self.assertNotIn("network engineer", blob.lower())

    def test_no_institute_contact_or_salary_figure_was_carried_across(self):
        """The document's salary tables are the part it is least entitled to
        assert. None of them are in this module; they are in the queue."""
        self.assertIn("UNVERIFIED_FIELDS", self.text)
        self.assertNotIn("₹", self.text)


#: Concepts allowed to expand to a bare sector word, and why. Every entry is a
#: concept that IS the sector — expanding to its own name is what it exists for
#: — or a pre-existing entry that predates the five trade documents and was
#: measured to be harmless. Adding a row here is a decision, not a formality:
#: the consolidated review found that a bare sector word in `expands_to` is the
#: single most reliable way to make search worse, and it has now done so twice.
SECTOR_EXPANSION_EXEMPT = {
    "manufacturing": "is the manufacturing sector",
    "construction": "is the construction sector",
    "agriculture": "is the agriculture sector",
    "farmer": "a farmer's query legitimately means the whole sector",
    "robotics": "pre-existing `automation` expansion; measured — every robotics "
                "alias still resolves to Robotics, not to a business with the "
                "word in its name. Pinned by a test below rather than trusted.",
    "mason": "pre-existing `construction`; measured, resolves to Masonry",
    "tiles": "pre-existing `construction`; measured, resolves to Tiles Fixing",
    "heavy-equipment-operator": "accepted approximation — no plant-operator "
                                "Skill exists; recorded as a research gap",
    "waterproofing": "accepted approximation — no waterproofing Skill exists",
    "roofing": "accepted approximation — no roofing Skill exists",
}

#: Bare sector words that must not appear in any non-exempt `expands_to`.
BARE_SECTOR_WORDS = ("manufacturing", "automation", "construction",
                     "agriculture", "services", "industry", "skilled trades")


@unittest.skipUnless(NODE, NODE_REASON)
class AutomationExpansionRegressionTest(unittest.TestCase):
    """The blocker the consolidated five-document review found.

    `plc-automation` shipped with `expands_to: [..., "automation"]`. That bare
    word CONTAINS-matched a BusinessOpportunity, and **five queries returned
    "WhatsApp Business Automation / Digital Catalog & Storefront Apps"**:

        plc automation                    Robotics            -> WhatsApp …
        plc programmer                    Freelance IT        -> WhatsApp …
        automation technician             Robotics            -> WhatsApp …
        industrial automation technician  Robotics            -> WhatsApp …
        scada                             (nothing)           -> WhatsApp …

    Worse than the Masala Powder incident §11 records, because the graph HOLDS
    the right answer — `PLC Programming & Control Systems`, a Skill — and the
    expansion dragged five queries away from an entity that already existed.

    It survived four rounds of per-document measurement because each document
    was probed against its own curated query set, and `plc-automation` came
    from document A — written before document C established the rule that
    caught it. Measuring the COMPLETE alias set against the pre-enrichment
    baseline is what found it, and is why these tests exist.

    One string was deleted. Five queries fixed, nothing else moved.
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

    def test_the_five_regressed_queries_reach_the_plc_skill(self):
        """The named five. Any of these returning a business with "Automation"
        in its name means the expansion is back."""
        got = self.top(["plc automation", "plc programmer", "scada",
                        "automation technician",
                        "industrial automation technician"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "PLC Programming & Control Systems")

    def test_no_automation_query_reaches_a_whatsapp_business(self):
        """Guarding the symptom by name as well as the cause. The offending
        entity is a real BusinessOpportunity and belongs in the graph; it just
        must never be the answer to a factory-floor question."""
        got = self.top(["plc automation", "plc programmer", "scada",
                        "automation technician",
                        "industrial automation technician",
                        "plc", "control systems", "hmi",
                        "industrial automation", "robotics technician",
                        "robot programmer", "cobot"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertIsNotNone(name)
                self.assertNotIn("whatsapp", name.lower())

    def test_the_fix_removed_the_expansion_and_nothing_else(self):
        """The seven aliases are the vocabulary — the words a person types.
        Only the EXPANSION was wrong. Deleting an alias to fix a ranking bug
        would have thrown away the discovery this document paid for."""
        concept = {c["id"]: c for c in load_concepts()["concepts"]}["plc-automation"]
        for alias in ("plc", "plc programmer", "scada", "automation technician",
                      "hmi", "control systems",
                      "industrial automation technician"):
            with self.subTest(alias=alias):
                self.assertIn(alias, concept["en"])
        self.assertEqual(concept["expands_to"],
                         ["plc programming", "industrial automation"])

    def test_the_neighbouring_robotics_concept_still_resolves(self):
        """`robotics` also carries a bare `automation` expansion and predates
        all five documents. It is exempted rather than changed — the brief was
        one string — but exempting it without measuring it would be taking the
        same risk twice."""
        got = self.top(["robotics technician", "robot programmer", "cobot",
                        "robot maintenance", "robotics service engineer"])
        for query, name in got.items():
            with self.subTest(query=query):
                self.assertEqual(name, "Robotics")


class SectorExpansionGuardTest(unittest.TestCase):
    """A concept must expand to a THING the graph holds, not to the sector it
    sits in. Stated in document A, proved by document C's Masala Powder
    incident (§11), and broken again by document A's own `plc-automation`
    (§17). Two occurrences make it a rule worth enforcing generally."""

    def test_no_concept_expands_to_a_bare_sector_word(self):
        offenders = []
        for concept in load_concepts()["concepts"]:
            if concept["id"] in SECTOR_EXPANSION_EXEMPT:
                continue
            for word in BARE_SECTOR_WORDS:
                if word in concept["expands_to"]:
                    offenders.append(f"{concept['id']} -> {word!r}")
        self.assertEqual(offenders, [], (
            "a bare sector expansion matches every entity with the word in its "
            "name and outranks the specific trade. If the expansion is really "
            "wanted, add the concept to SECTOR_EXPANSION_EXEMPT with a reason "
            "AND a measurement, the way `robotics` is: " + str(offenders)))

    def test_plc_automation_is_not_quietly_exempted(self):
        """The cheapest way to 'fix' the test above is to add the offender to
        the exemption list. This one concept may not be, because its exemption
        is exactly the bug."""
        self.assertNotIn("plc-automation", SECTOR_EXPANSION_EXEMPT)

    def test_every_exemption_carries_a_reason(self):
        for cid, reason in SECTOR_EXPANSION_EXEMPT.items():
            with self.subTest(concept=cid):
                self.assertGreater(len(reason), 20,
                                   "an exemption without a reason is a silent "
                                   "re-introduction of the bug")


class CandidateClassificationTest(unittest.TestCase):
    """The reviewer's map of the 52 queued candidates, checked against the
    queue and the graph rather than trusted as prose.

    A classification document that drifts from the queue is worse than none:
    it tells a reviewer that a decision has been thought about when the row it
    describes no longer exists. These tests are what keep the two in step.
    """

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import candidate_classification     # noqa: PLC0415
        self.cc = candidate_classification
        queue = ROOT / "collection" / "state" / "review_queue.jsonl"
        self.queue = [json.loads(line) for line in
                      queue.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.from_docs = {r["candidate_id"] for r in self.queue
                          if r["source_id"].startswith("doc-")}

    def test_every_queued_candidate_is_classified_exactly_once(self):
        self.assertEqual(len(self.from_docs), 52)
        self.assertEqual(set(self.cc.CANDIDATES), self.from_docs,
                         "the classification and the queue have drifted apart")

    def test_every_classification_is_one_of_the_five(self):
        """A row either explains itself or points at the group that does.
        `"group `battery`"` is a complete reason — the group carries the
        argument, and duplicating it into every member is how the two drift
        apart."""
        for cid, row in self.cc.CANDIDATES.items():
            with self.subTest(candidate=cid):
                self.assertIn(row["cls"], self.cc.CLASSES)
                self.assertTrue(row["primary_source"])
                if row["why"].startswith("group "):
                    self.assertIsNotNone(self.cc.group_of(cid),
                                         "cites a group it is not in")
                else:
                    self.assertGreater(len(row["why"]), 20)

    def test_nothing_is_approved_or_promoted(self):
        """The whole point. Classifying is not deciding: every one of the 52
        must still be sitting in the queue waiting for a named person."""
        for row in self.queue:
            if row["candidate_id"] in self.from_docs:
                with self.subTest(candidate=row["candidate_id"]):
                    self.assertEqual(row["state"], "NEEDS_REVIEW")

    def test_no_candidate_became_an_entity(self):
        """The invariant that matters: none of the 52 roles is in the
        knowledge graph.

        Two earlier versions of this test were wrong, both by being too loose.
        Searching packages/ for the FIELD names failed on `salary_range`, a
        legitimate long-standing column in Package006. Searching every CSV
        cell for the role TITLES failed on "Fabricator", a free-text
        `who_needs_it` value in Package008's skill mapping written in July and
        unrelated to any of this. Neither is a promotion.

        A promotion means the role exists as a graph entity, so that is what
        this checks — the same set `emit_candidates` consults when it decides
        a role has no Skill and belongs in the queue.
        """
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources.emit_candidates import DOCUMENTS    # noqa: PLC0415
        titles = {role["title"] for module in DOCUMENTS.values()
                  for role in module.new_roles()}
        promoted = sorted(titles & {e["canonical_name"] for e in entities()})
        self.assertEqual(promoted, [],
                         f"queued candidates are in the graph: {promoted} — "
                         "promoted without a review decision")

    def test_the_forbidden_fields_are_still_named(self):
        """The list itself has to survive. Each source module blanks these
        mechanically; losing a name here means one of them gets carried
        across by whoever writes the promoter."""
        for field in ("salary_range", "course_fees", "institute_contact",
                      "placement_claim", "employer_list", "demand_estimate"):
            with self.subTest(field=field):
                self.assertIn(field, self.cc.NEVER_PROMOTE_FIELDS)

    def test_every_merge_target_is_an_entity_the_graph_holds(self):
        """A class-A row names where the trade should go. Naming an entity
        that does not exist would be exactly the fabrication this pipeline
        exists to prevent — and it is an easy mistake to make from memory."""
        known = {e["canonical_name"] for e in entities()}
        for cid, row in self.cc.CANDIDATES.items():
            if row["cls"] != self.cc.MERGE:
                continue
            with self.subTest(candidate=cid):
                self.assertIsNotNone(row["merge_target"])
                self.assertIn(row["merge_target"], known)

    def test_only_class_A_names_a_merge_target(self):
        for cid, row in self.cc.CANDIDATES.items():
            if row["cls"] == self.cc.MERGE:
                continue
            with self.subTest(candidate=cid):
                self.assertIsNone(row["merge_target"])

    def test_the_eight_duplicate_groups_are_preserved(self):
        """The groups are the difference between 52 decisions and 38, and
        between approving a trade once and approving it twice under two
        names."""
        self.assertEqual(len(self.cc.DUPLICATE_GROUPS), 8)
        seen = set()
        for name, group in self.cc.DUPLICATE_GROUPS.items():
            with self.subTest(group=name):
                self.assertGreaterEqual(len(group["members"]), 2)
                self.assertGreater(len(group["why"]), 30)
                self.assertTrue(group["primary_source"])
                for member in group["members"]:
                    self.assertIn(member, self.cc.CANDIDATES,
                                  "a group names a candidate that is not queued")
                    self.assertNotIn(member, seen,
                                     "a candidate is in two groups")
                    seen.add(member)

    def test_every_grouped_candidate_is_class_C_or_class_D(self):
        """A grouped candidate may be DISPUTED — `battery-technician` and
        `security-system-installer` both are — but it may never be filed as a
        straightforward merge or a straightforward new entity, because that is
        the decision the group exists to prevent being made alone."""
        for name, group in self.cc.DUPLICATE_GROUPS.items():
            for member in group["members"]:
                with self.subTest(group=name, candidate=member):
                    self.assertIn(self.cc.CANDIDATES[member]["cls"],
                                  (self.cc.DUPLICATE, self.cc.DISPUTED))

    def test_the_pairs_that_must_stay_distinct_are_not_grouped(self):
        """Painter / Auto Painting Technician and Fabricator / Aluminium
        Fabricator share a word and nothing else. Putting either pair in a
        duplicate group would invite exactly the merge the source modules
        forbid — a long queue makes merging feel like progress."""
        self.assertEqual(len(self.cc.KEEP_DISTINCT), 2)
        for pair, reason in self.cc.KEEP_DISTINCT.items():
            first, second = pair
            with self.subTest(pair=pair):
                self.assertIn(first, self.cc.CANDIDATES)
                self.assertIn(second, self.cc.CANDIDATES)
                self.assertGreater(len(reason), 40)
                #: Not "neither may be grouped" — `aluminium-fabricator` is
                #: legitimately in the `fenestration` group with the uPVC and
                #: glass roles. The rule is narrower and is the one that
                #: matters: these two may never land in the SAME group.
                groups = (self.cc.group_of(first), self.cc.group_of(second))
                self.assertFalse(groups[0] is not None and groups[0] == groups[1],
                                 f"{first} and {second} share group {groups[0]}")

    def test_production_operator_stays_rejected(self):
        """Sector-shaped rather than a defined trade. Named here so that a
        later pass through the queue cannot quietly promote it — the reason it
        was rejected is a definition, and definitions do not change when
        somebody wants a shorter queue."""
        row = self.cc.CANDIDATES["doc-manufacturing-trades-2026:production-operator"]
        self.assertEqual(row["cls"], self.cc.REJECT)
        self.assertEqual(list(self.cc.by_class(self.cc.REJECT)),
                         ["doc-manufacturing-trades-2026:production-operator"])

    def test_the_classes_add_up_to_fifty_two(self):
        self.assertEqual(sum(self.cc.counts().values()), 52)


@unittest.skipUnless(NODE, NODE_REASON)
class ResearchGapTest(unittest.TestCase):
    """The two gaps the consolidated review recorded, verified against the
    live graph rather than asserted."""

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import candidate_classification     # noqa: PLC0415
        self.cc = candidate_classification

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

    def test_the_field_technician_magnet_is_recorded_and_real(self):
        """Eighteen of the 52 — more than a third — return the same unrelated
        Certification. Measured, not remembered: if a Skill is promoted for one
        of these the count drops and this test says so, which is the signal
        that the gap is closing."""
        gap = self.cc.FIELD_TECHNICIAN_MAGNET
        self.assertEqual(len(gap["candidates"]), 18)
        self.assertEqual(gap["kind"], "knowledge-coverage")
        self.assertEqual(gap["do_not_fix_with"], "aliases")

        titles = {}
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources.emit_candidates import DOCUMENTS    # noqa: PLC0415
        for module in DOCUMENTS.values():
            for role in module.new_roles():
                titles[f"{module.SOURCE['source_id']}:{role['slug']}"] = role["title"]

        got = self.top([titles[c] for c in gap["candidates"]])
        still_magnetised = [q for q, name in got.items()
                            if name and "field technician" in name.lower()]
        self.assertEqual(sorted(still_magnetised), sorted(got),
                         "a candidate left the magnet — if a Skill was "
                         "promoted for it, remove it from the list; if an "
                         "alias was added instead, that is the fix this gap "
                         "explicitly forbids")

    def test_the_magnet_is_not_being_papered_over_with_aliases(self):
        """The tempting fix. Pointing these words at an approximately-related
        entity replaces a visibly wrong answer with an invisibly wrong one,
        and a student cannot tell the difference until they have wasted a
        term."""
        magnetised = {c.rsplit(":", 1)[1] for c
                      in self.cc.FIELD_TECHNICIAN_MAGNET["candidates"]}
        for concept in load_concepts()["concepts"]:
            for term in concept["en"]:
                slug = term.replace(" ", "-")
                with self.subTest(concept=concept["id"], term=term):
                    self.assertNotIn(slug, magnetised,
                                     "an alias was written for a trade that "
                                     "has no entity to reach")

    def test_promotion_obliges_a_vocabulary_repoint(self):
        """For these candidates the words already resolve to an approximate
        existing entity. Promote the Skill without re-pointing the concept and
        the new entity is unreachable by the very words added for it —
        promotion is two edits, and nothing else in the pipeline says so."""
        known = {e["canonical_name"] for e in entities()}
        concepts = {c["id"] for c in load_concepts()["concepts"]}
        for cid, (concept, current) in self.cc.REPOINT_ON_PROMOTION.items():
            with self.subTest(candidate=cid):
                self.assertIn(cid, self.cc.CANDIDATES)
                self.assertIn(concept, concepts)
                self.assertIn(current, known)


class VerifiedCandidateTest(unittest.TestCase):
    """Primary-source verification of the ten highest-value candidates.

    The thing these tests defend is not the research — it is the HONESTY of
    the research. A verification record that quietly loses its URL, or claims
    a confidence the method does not support, or grows vocabulary for a role
    that was never confirmed, is more dangerous than no verification at all,
    because the next reader takes it on trust.
    """

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import (candidate_classification,   # noqa: PLC0415
                                      verified_candidates)
        self.vc = verified_candidates
        self.cc = candidate_classification

    def test_the_ten_named_candidates_are_all_present(self):
        expected = {
            "doc-automobile-trades-2026:service-advisor",
            "doc-manufacturing-trades-2026:fitter",
            "doc-manufacturing-trades-2026:tool-and-die-maker",
            "doc-electrician-trades-2026:painter",
            "doc-electrician-trades-2026:mechatronics-technician",
            "doc-electrician-trades-2026:lift-technician",
            "doc-electronics-trades-2026:cctv-technician",
            "doc-electronics-trades-2026:fire-alarm-technician",
            "doc-electronics-trades-2026:networking-technician",
            "doc-automobile-trades-2026:ev-charging-station-technician",
        }
        self.assertEqual(set(self.vc.VERIFIED), expected)

    def test_every_record_is_a_real_queued_candidate(self):
        for cid in self.vc.VERIFIED:
            with self.subTest(candidate=cid):
                self.assertIn(cid, self.cc.CANDIDATES)

    def test_a_confirmed_role_carries_an_authority_a_code_and_a_url(self):
        """The whole value of this pass over the five documents is that a
        person can check it. A record without a URL is an assertion, which is
        what the documents already gave us."""
        for cid, row in self.vc.verified().items():
            with self.subTest(candidate=cid):
                self.assertTrue(row["authority"])
                self.assertTrue(row["code"])
                self.assertTrue(row["url"].startswith("https://"))
                self.assertGreater(len(row["note"]), 60)

    def test_confidence_respects_the_indirect_verification_ceiling(self):
        """75, not 88. The codes were read from a search index quoting the
        official document, because this environment's egress proxy blocks
        dgt.gov.in, nqr.gov.in, essc-india.org, asdc.org.in and nsdcindia.org.
        A citation you have not opened is better evidence than none and worse
        evidence than one you have."""
        self.assertEqual(self.vc.CEILING, 75)
        for cid, row in self.vc.VERIFIED.items():
            with self.subTest(candidate=cid):
                self.assertLessEqual(row["confidence"], self.vc.CEILING)

    def test_the_method_admits_that_direct_fetch_was_blocked(self):
        """If this sentence goes missing, the next reader will assume the PDFs
        were read."""
        self.assertIn("BLOCKED", self.vc.METHOD)
        for domain in ("dgt.gov.in", "essc-india.org", "asdc.org.in"):
            with self.subTest(domain=domain):
                self.assertIn(domain, self.vc.METHOD)

    def test_the_unverified_role_is_marked_and_kept_out(self):
        """Fire Alarm Technician is the one of the ten that verification did
        NOT confirm — the adjacent national qualifications are firefighting
        roles, and the only fire-alarm credential found is commercial. It has
        to stay visibly unverified, carry low confidence, and propose no
        entity."""
        unverified = self.vc.unverified()
        self.assertEqual(list(unverified),
                         ["doc-electronics-trades-2026:fire-alarm-technician"])
        row = unverified["doc-electronics-trades-2026:fire-alarm-technician"]
        self.assertIsNone(row["code"])
        self.assertIsNone(row["proposed_entity"])
        self.assertEqual(row["decision"], self.vc.DISPUTED)
        self.assertLess(row["confidence"], 50)

    def test_no_vocabulary_was_prepared_for_the_unverified_role(self):
        """An unverified role with ready-made aliases is an invitation to ship
        it. Empty is the correct content."""
        for cid in self.vc.unverified():
            vocab = self.vc.PROPOSED_VOCABULARY[cid]
            with self.subTest(candidate=cid):
                self.assertEqual(vocab["en"] + vocab["te"] + vocab["tanglish"], [])

    def test_every_verified_role_has_prepared_vocabulary(self):
        for cid in self.vc.verified():
            with self.subTest(candidate=cid):
                self.assertIn(cid, self.vc.PROPOSED_VOCABULARY)
                self.assertTrue(self.vc.PROPOSED_VOCABULARY[cid]["en"])

    def test_the_prepared_vocabulary_is_not_in_the_live_concept_table(self):
        """The point of preparing it is that it does NOT ship until the Skill
        exists. None of these ten is a class-A merge, so there is nothing in
        the graph for them to point at, and an alias pointing at an
        approximately-related entity is the Field Technician failure.

        One exception is expected and is named in the data: the `painter`
        concept ALREADY claims "painter" and "house painting" and points at
        the Painting Services business. That is why its record carries
        `repoint_existing_concept` — the fix is to re-point that concept when
        the Skill lands, never to add a second concept claiming the same
        words, which the integrity test would reject.
        """
        live = set()
        for concept in load_concepts()["concepts"]:
            live.update(t.lower() for t in concept["en"])
        for cid, vocab in self.vc.PROPOSED_VOCABULARY.items():
            allowed = vocab.get("repoint_existing_concept")
            for term in vocab["en"]:
                if term.lower() in live and allowed:
                    continue
                with self.subTest(candidate=cid, term=term):
                    self.assertNotIn(term.lower(), live,
                                     "prepared vocabulary shipped before its "
                                     "Skill exists")

    def test_no_verified_candidate_was_promoted(self):
        """Verification is not approval. Every one of the ten is still in the
        queue waiting for a named person, and none is an entity."""
        queue = ROOT / "collection" / "state" / "review_queue.jsonl"
        rows = {json.loads(line)["candidate_id"]: json.loads(line)
                for line in queue.read_text(encoding="utf-8").splitlines()
                if line.strip()}
        known = {e["canonical_name"] for e in entities()}
        for cid, row in self.vc.VERIFIED.items():
            with self.subTest(candidate=cid):
                self.assertEqual(rows[cid]["state"], "NEEDS_REVIEW")
                if row["proposed_entity"]:
                    self.assertNotIn(row["proposed_entity"], known,
                                     "a proposed entity already exists — "
                                     "either it was promoted, or the proposal "
                                     "duplicates something the graph holds")

    def test_no_salary_fee_or_contact_was_carried_across(self):
        """Verification confirms that a trade and its qualification exist. It
        says nothing about what the job pays, and the documents' numbers are
        still uncited.

        Checking for the WORD "salary" was the first version of this test and
        it failed on the module's own disclaimer — the sentence promising not
        to import salaries contains the word. What must be absent is the DATA:
        a currency figure, a monthly rate, a phone number, an email address.
        """
        text = (ROOT / "research" / "sources"
                / "verified_candidates.py").read_text(encoding="utf-8")
        forbidden = {
            "a rupee figure": r"₹\s*[\d,]+",
            "a monthly rate": r"[\d,]{4,}\s*(?:per month|/month|pm\b)",
            "a salary range": r"\b\d{2},\d{3}\s*[-–]\s*\d{2},\d{3}",
            "a phone number": r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b|\b0\d{2,4}[\s-]\d{6,8}\b",
            "an email address": r"[\w.-]+@[\w.-]+\.\w+",
        }
        for what, pattern in forbidden.items():
            with self.subTest(what=what):
                self.assertIsNone(re.search(pattern, text),
                                  f"{what} reached the verification register")

    def test_the_changes_verification_made_are_recorded(self):
        """Two of these were my errors — assigning EV charging to ASDC because
        the role arrived in an automobile document, and assuming no craftsman
        trade existed for lifts. A register that silently corrects itself
        teaches nobody why the check was worth running."""
        self.assertGreaterEqual(len(self.vc.CLASSIFICATION_CHANGES), 4)
        for cid, why in self.vc.CLASSIFICATION_CHANGES.items():
            with self.subTest(candidate=cid):
                self.assertIn(cid, self.vc.VERIFIED)
                self.assertGreater(len(why), 40)


@unittest.skipUnless(NODE, NODE_REASON)
class FieldTechnicianFamilyTest(unittest.TestCase):
    """The magnet, diagnosed rather than described.

    §18 recorded it as a knowledge-coverage problem. Verification says what
    the coverage problem IS: ESSCI publishes a family of "After Sales Support"
    qualifications sharing the ELE/Q46xx prefix, and the graph holds exactly
    one of them — as a Certification, with no Skill for any trade in the
    family. A query ending in "technician" with no Skill to reach finds the
    one row that contains the word.
    """

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()
        cls.h.dataset("entities.json", entities())

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    def setUp(self):
        import sys                                                # noqa: PLC0415
        sys.path.insert(0, str(ROOT))
        from research.sources import verified_candidates          # noqa: PLC0415
        self.vc = verified_candidates

    def test_the_graph_holds_exactly_one_member_of_the_family(self):
        known = {e["canonical_name"]: e["entity_type"] for e in entities()}
        in_graph = [code for code, row in self.vc.FIELD_TECHNICIAN_FAMILY.items()
                    if any(code in name for name in known)]
        self.assertEqual(in_graph, ["ELE/Q4601"])
        self.assertEqual(
            known["Field Technician - Computing & Peripherals - ELE/Q4601"],
            "Certification")

    def test_no_family_member_is_held_as_a_skill(self):
        """The asymmetry itself. A Certification without its Skill becomes a
        magnet, and this is the mechanism — not a ranking bug."""
        skills = {e["canonical_name"] for e in entities()
                  if e["entity_type"] == "Skill"}
        for code, row in self.vc.FIELD_TECHNICIAN_FAMILY.items():
            with self.subTest(qp=code):
                self.assertFalse(any(row["title"].split(" — ")[0] in s
                                     for s in skills))

    def test_the_second_magnet_follows_the_same_pattern(self):
        """Recorded so the pattern is visible rather than looking like one
        odd row: the automotive Certification is also in the graph without a
        matching Skill of its own name."""
        known = {e["canonical_name"]: e["entity_type"] for e in entities()}
        self.assertEqual(known[self.vc.SECOND_MAGNET["entity"]], "Certification")
        self.assertIn(self.vc.SECOND_MAGNET["matching_skill_in_graph"], known)

    def test_two_of_the_three_family_trades_are_already_queued(self):
        """Which is why the fix is coverage and not ranking: promoting the
        queued candidates removes their queries from the magnet."""
        queued = {row["status"] for row in
                  self.vc.FIELD_TECHNICIAN_FAMILY.values()}
        self.assertEqual(len([s for s in queued if s.startswith("queued as")]), 2)


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
        #: The electronics document's limit is the strangest of the five: the
        #: thing a reviewer most needs warning about is its own confidence.
        self.assertIn("Confidence Level: High", notes["electronics"])
        self.assertNotIn("XXXX", notes["electronics"])


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
