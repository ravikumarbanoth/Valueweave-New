#!/usr/bin/env python3
"""
ValueWeave v1.0 — Production UX polish.

WHAT THIS SUITE IS FOR
----------------------
Every previous step of this platform was written for the person building it, and
each one left its vocabulary on the screen. By the time Step 4 finished, a
first-year student looking for a welding course in Warangal could be told:

    "The knowledge schema has not been deployed to this environment.
     Depends on: Run the migrations, expose the `knowledge` schema, then
     `scripts/run_sync.sh`. See docs/FIRST_DEPLOYMENT_CHECKLIST.md steps 5–10."

Every word true. None of it theirs.

This suite is the ratchet. The terminology test is the important one: it is not
possible to write an honest empty state without being tempted to explain the
infrastructure, and the temptation returns on every sprint. A grep in a test is
the only thing that reliably says no.

    python3 tests/run_all.py --suite production_ux
"""

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
    """Source with `//` and `/* */` comments stripped.

    A file may — and several do — explain at length which internal term it stopped
    showing. Explaining the history is how the next person avoids repeating it.
    What may not survive is the term rendering.
    """
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def public_sources():
    """Every non-admin page, component and shared library module.

    `admin/` is excluded throughout: it is tooling for a handful of operators who
    do maintain the sync and do read the checklist, and for whom "Package006" is
    the clearest available word.

    PX PHASE 2 — WHY `lib/` IS NOW IN HERE
    ---------------------------------------
    It was not, and that gap was not theoretical. `lib/knowledge.js` built the
    tooltip on the "We have not covered these yet" chips, and one of its two
    branches read "not in the vocabulary crosswalk" — the name of an internal
    lookup table. `crosswalk` has been on the BANNED list since the list
    existed. The ratchet simply was not pointed at the file.

    User-visible copy does not only live under `app/` and `components/`. Any
    module that returns a string a component renders is a page in disguise.
    """
    out = []
    for root in (APP, COMPONENTS, FE / "lib"):
        for path in sorted(root.rglob("*.js")) + sorted(root.rglob("*.jsx")):
            if "admin" in path.parts:
                continue
            out.append(path)
    return out


def rel(path):
    return str(Path(path).relative_to(FE))


# ═══════════════════════════════════════════════ 1. the vocabulary ratchet
class DeveloperLanguageTest(unittest.TestCase):
    """No internal vocabulary in anything a user reads."""

    #: Terms a public user must never meet. Regexes, matched case-insensitively
    #: against comment-stripped source.
    #:
    #: `sync`, `migration` and `deployment` are NOT here as bare words: they are
    #: ordinary English ("syncing your calendar") and banning them outright would
    #: produce false positives that get silenced rather than fixed. The phrases
    #: that actually leaked are banned instead.
    BANNED = [
        (r"knowledge\s+graph", "knowledge graph"),
        (r"knowledge\s+schema", "knowledge schema"),
        (r"Packages?\s*00\d", "package identifier"),
        (r"Packages\s+001", "package range"),
        (r"vocabulary\s+crosswalk", "vocabulary crosswalk"),
        (r"\bcrosswalk\b", "crosswalk"),
        (r"DEPLOYMENT_CHECKLIST", "checklist filename"),
        (r"scripts/\w+\.sh", "script path"),
        (r"rule\s+engine", "rule engine"),
        (r"not\s+switched\s+on", "\"not switched on\""),
        (r"deployed\s+to\s+this\s+environment", "deployment language"),
        (r"\.csv\b", "dataset filename"),
        (r"TABLE_SPEC", "internal spec name"),
        (r"knowledge_sync", "module name"),
        (r"unprojected", "internal jargon"),

        # ── PX Phase 2 additions ────────────────────────────────────────────
        # Everything below actually rendered before this phase. Each entry is a
        # sentence a user met, not a term we are being cautious about.
        #
        # "package" is our unit of research and means nothing to a reader. The
        # bare word is NOT banned — it is also a prop name (`package={...}` on
        # ProvenanceLine) and banning it would force a rename that changes no
        # pixel. The three prose shapes that leaked are banned instead.
        (r"\bno\s+package\b", "\"no package holds/covers\""),
        (r"\bin\s+any\s+package\b", "\"in any package\""),
        (r"\bresearch\s+package\b", "\"research package\""),
        (r"\bDepends\s+on:", "\"Depends on:\" build-plan label"),
        (r"No\s+Data\s+Source", "\"No Data Source\" chip label"),
        (r"intelligence\s+layer", "\"intelligence layer\""),
        (r"structured\s+layer", "\"structured layer\""),
        (r"prompt\s+layer", "\"prompt layer\""),
        (r"business\s+logic", "\"business logic\""),
        (r"this\s+repository", "\"this repository\""),
        (r"Buildout\s+Plan", "\"Buildout Plan\""),
        (r"Expansion\s+Cards", "\"Expansion Cards\""),
        (r"MODULE\s+AREAS", "\"MODULE AREAS\""),
        (r"backed\s+by\s+the\s+knowledge\s+base", "\"backed by the knowledge base\""),
        (r"typed\s+relationships?", "\"typed relationship\""),
        (r"admin\s+maps\b", "\"admin maps this entity\""),
        (r"\bthis\s+entity\b", "\"entity\" as a word for a page"),
    ]

    #: `packages: ["Package001_Geography"]` in the explorer is a prop VALUE handed
    #: to SourceBadge, which renders "Districts & geography research". The
    #: identifier never reaches the screen, and rewriting the data to satisfy a
    #: grep would be the test wagging the code.
    ALLOWED_IDENTIFIER_LINES = re.compile(
        r"^\s*(packages:\s*\[|source_package|sourcePackage|Package00\d\w*:\s*\")")

    def test_no_internal_vocabulary_reaches_a_user(self):
        offenders = []
        for path in public_sources():
            for lineno, line in enumerate(code(path).splitlines(), 1):
                if self.ALLOWED_IDENTIFIER_LINES.match(line):
                    continue
                for pattern, label in self.BANNED:
                    if re.search(pattern, line, re.IGNORECASE):
                        offenders.append(f"{rel(path)}:{lineno}  [{label}]  {line.strip()[:80]}")
        self.assertEqual(
            offenders, [],
            "These render to a public user. Say what they can do, not what our "
            "infrastructure is doing:\n  " + "\n  ".join(offenders))

    def test_source_labels_name_a_subject_not_a_directory(self):
        """"Package006 · Skills & Training" told a student nothing."""
        src = read(FE / "lib" / "knowledge.js")
        block = src[src.index("export const PACKAGE_LABELS"):]
        block = block[:block.index("};")]
        # The KEYS are the identifiers and have to stay — they are what the
        # database column holds. Only the values are read by a person.
        values = re.findall(r':\s*"([^"]+)"', block)
        self.assertEqual(len(values), 8, "one label per research area")
        for value in values:
            with self.subTest(label=value):
                self.assertNotRegex(value, r"Package\s*00\d",
                                    "a label must not repeat its identifier")
        for expected in ("Districts & geography", "Skills & training", "Small business"):
            with self.subTest(label=expected):
                self.assertIn(expected, values)

    def test_provenance_shows_a_sentence_not_three_ids(self):
        """It used to render `Package008_MSME · businesses.csv · B-014`."""
        src = read(COMPONENTS / "knowledge" / "ProvenanceLine.jsx")
        self.assertNotIn("parts.join", src)
        self.assertIn("From our", src)
        # The identifiers survive where support can still reach them.
        for attr in ("data-source-package", "data-source-dataset", "data-source-row"):
            with self.subTest(attr=attr):
                self.assertIn(attr, src)


# ══════════════════════════════════════ 1b. PX Phase 2: what replaced it
class HumanLanguageTest(unittest.TestCase):
    """The ratchet above only proves the old words are gone.

    A term can be deleted and leave a worse hole than it filled — a heading
    removed rather than rewritten, a fallback that now renders blank. These
    tests assert the replacement, so a future edit cannot satisfy the ban by
    deleting the sentence.

    Every check reads through `code()`. Each file below explains in a comment
    which sentence it stopped showing — that record is the reason the sentence
    stays gone, and an assertion over raw source would forbid keeping it.
    """

    def absent(self, needle, src, path):
        """`assertNotIn` on a 20 KB file prints the 20 KB file."""
        self.assertTrue(needle not in src, f"{path} still contains {needle!r}")

    def present(self, needle, src, path):
        self.assertTrue(needle in src, f"{path} no longer contains {needle!r}")

    def test_capability_states_describe_the_world_not_our_pipeline(self):
        """"No Data Source" told a student about our storage, not about mentors."""
        src = read(COMPONENTS / "knowledge" / "CapabilityStatus.jsx")
        block = src[src.index("const STATES = {"):]
        block = block[:block.index("\n};")]
        labels = dict(re.findall(r"(\w+):\s*\{\s*\n\s*label:\s*\"([^\"]+)\"", block))
        self.assertEqual(
            labels,
            {"LIVE": "Ready now",
             "NOT_AVAILABLE_YET": "Coming later",
             "NO_DATA_SOURCE": "Not researched yet"},
            "the three keys are ours and stay; the three labels are read by a user")

    def test_the_unavailable_reason_is_introduced_as_a_question_not_a_build_step(self):
        self.assertIn("Why not yet: ",
                      read(COMPONENTS / "knowledge" / "CapabilityStatus.jsx"))

    def test_the_snapshot_heading_is_a_sentence_not_a_type_name(self):
        """It rendered "Government Scheme Snapshot" — the type, used as a title."""
        path = COMPONENTS / "kg" / "PublicEntityDetail.jsx"
        src = code(path)
        self.absent("${typeLabel} Snapshot", src, rel(path))
        self.present('PANEL_TITLE[typeLabel] || "Quick overview"', src, rel(path))
        block = src[src.index("const PANEL_TITLE = {"):]
        block = block[:block.index("\n};")]
        # Every typeLabel any caller passes must have a heading written for it,
        # or the default silently becomes the only heading on that page.
        callers = set()
        for page in sorted(APP.rglob("*.js")) + sorted(APP.rglob("*.jsx")):
            callers.update(re.findall(r'<PublicEntityDetail[^>]*?typeLabel="([^"]+)"',
                                      read(page), re.DOTALL))
        self.assertTrue(callers, "no caller found — the scan is broken, not the code")
        for label in sorted(callers):
            with self.subTest(typeLabel=label):
                self.present(f'"{label}"' if " " in label else label, block, "PANEL_TITLE")

    def test_the_snapshot_rows_lost_their_notes_to_the_maintainer(self):
        """"Applicable where admin maps this entity to districts." was a row VALUE.

        Deleting the sentence is right and blanking the row would not be: the
        panel drops rows whose value is empty, so an unknown district now shows
        nothing rather than an instruction addressed to somebody else.
        """
        path = COMPONENTS / "kg" / "PublicEntityDetail.jsx"
        src = code(path)
        self.absent("admin maps", src, rel(path))
        self.absent("Use this entry with linked", src, rel(path))
        self.present('"Where it applies": entity.state || entity.location,', src, rel(path))
        panel = COMPONENTS / "geo" / "SnapshotPanel.jsx"
        self.present("if (rows.length === 0", code(panel), rel(panel))

    def test_the_detail_page_headings_name_what_the_reader_gets(self):
        path = APP / "knowledge" / "[type]" / "[slug]" / "page.js"
        src = code(path)
        self.absent(">Details<", src, rel(path))
        self.absent("Connected knowledge", src, rel(path))
        self.present("What you should know", src, rel(path))
        self.present("Where this leads next", src, rel(path))

    def test_the_two_score_tooltips_explain_the_difference_in_plain_words(self):
        """A match score and a source score are different things and looked alike."""
        card = COMPONENTS / "knowledge" / "KnowledgeCard.jsx"
        self.present("This is about you", code(card), rel(card))
        self.absent("Separate from source confidence", code(card), rel(card))
        score = COMPONENTS / "knowledge" / "ScoreCard.jsx"
        self.present("The weakest source behind this number", code(score), rel(score))
        # "rows" is the database's word for a fact.
        self.absent("among the rows behind", code(score), rel(score))

    def test_the_ai_page_says_what_exists_rather_than_what_is_reserved(self):
        """The page's whole purpose is not overclaiming. It must still be readable."""
        page = APP / "ai" / "page.js"
        self.absent("Intelligence Layer", code(page), rel(page))
        self.absent("Reserved architecture", code(page), rel(page))
        self.present("We do not have an AI advisor yet", code(page), rel(page))
        sections = APP / "ai" / "components" / "AiSections.jsx"
        src = code(sections)
        self.absent("no inference", src, rel(sections))
        self.present("fixed rules we wrote by hand", src, rel(sections))
        # The honesty is the point of this page and must not have been softened
        # away along with the jargon.
        self.present("We have not built an AI advisor", src, rel(sections))

    def test_the_homepage_tile_matches_the_page_it_opens(self):
        grid = COMPONENTS / "HomeFeatureGrid.jsx"
        src = code(grid)
        self.absent("AI Intelligence Layer", src, rel(grid))
        self.absent("View AI Layer", src, rel(grid))
        self.present('title: "AI Guidance"', src, rel(grid))

    def test_the_unresolved_chip_tooltip_names_the_gap_not_the_lookup_table(self):
        """This is the string `lib/` was not being scanned for."""
        path = FE / "lib" / "knowledge.js"
        src = code(path)
        self.absent("crosswalk\"", src, rel(path))
        self.present("We have not come across this one yet.", src, rel(path))
        self.present("we have not gathered any information about it yet", src, rel(path))


# ══════════════════════════════════ 1c. PX Phase 3: trust without fear
class TrustWithoutFearTest(unittest.TestCase):
    """Disclosure that helps a reader decide, rather than warning them off.

    The brief: "This record has not yet been reviewed by a person..." creates
    doubt. Replace it with a trust component that is professional, friendly and
    trustworthy.

    Two failure modes to guard, in opposite directions. The obvious one is the
    fear language coming back. The one worth writing a test for is the other:
    somebody deleting the disclosure entirely because it was in the way. A page
    that never says where a government scheme's details came from, or that they
    might have changed, is not friendlier — it is worse, and it fails silently.
    """

    PANEL = COMPONENTS / "knowledge" / "TrustPanel.jsx"

    def test_the_panel_names_the_source_before_it_asks_for_anything(self):
        src = code(self.PANEL)
        self.assertIn("Where this information comes from", src)
        self.assertIn("official public sources", src)
        self.assertIn("ValueWeave research team", src)

    def test_the_panel_tells_the_reader_what_to_do_before_they_spend_money(self):
        """The disclosure has to survive being made friendly."""
        src = code(self.PANEL)
        self.assertIn("official authority", src)
        self.assertRegex(src, r"apply for a scheme or invest money")

    def test_the_panel_is_not_styled_as_an_alert(self):
        """Amber on a page about someone's career reads as "something is wrong"."""
        src = code(self.PANEL)
        self.assertNotIn("amber", src,
                         "the trust panel is information, not a warning")

    def test_every_surface_that_carried_the_old_notice_carries_the_new_one(self):
        """Six call sites. A rename that drops one is a silent regression."""
        surfaces = [
            APP / "knowledge" / "page.js",
            APP / "dashboard" / "page.js",
            APP / "knowledge" / "[type]" / "[slug]" / "page.js",
            COMPONENTS / "knowledge" / "IntelligencePanel.jsx",
            COMPONENTS / "knowledge" / "DistrictIntelligencePanel.jsx",
            COMPONENTS / "knowledge" / "BusinessKnowledgeSection.jsx",
        ]
        for path in surfaces:
            with self.subTest(surface=rel(path)):
                src = code(path)
                self.assertIn("TrustPanel", src)

    def test_the_detail_page_puts_it_after_the_facts_not_above_them(self):
        """Position was half the problem: an alert above the content."""
        src = code(APP / "knowledge" / "[type]" / "[slug]" / "page.js")
        body = src[src.index("<EntityHeader"):]
        self.assertLess(body.index("entity-attributes"), body.index("<TrustPanel"),
                        "the reader should meet the facts before the caveat")
        self.assertNotIn("entity-unverified", src,
                         "the masthead alert is gone, not relocated inside itself")

    def test_the_header_still_answers_the_machine_question(self):
        """Removing the amber panel must not remove the fact it carried."""
        src = code(COMPONENTS / "knowledge" / "EntityHeader.jsx")
        self.assertIn("data-verification-status", src)
        self.assertIn("NEEDS_REVIEW", src)

    def test_a_source_score_is_shown_as_words_not_as_a_mark_out_of_100(self):
        """"56/100" beside an opportunity reads as a grade on the opportunity."""
        badge = COMPONENTS / "knowledge" / "ConfidenceBadge.jsx"
        src = code(badge)
        self.assertIn("{band.label}", src)
        self.assertNotIn("{n}/100", src.split("title=")[0],
                         "the number belongs in the tooltip, not on the chip")
        self.assertIn("data-confidence", src, "the number must stay machine-readable")
        # And the bands themselves must read as source descriptions.
        intel = code(FE / "lib" / "intelligence.js")
        block = intel[intel.index("export function confidenceBand"):]
        block = block[:block.index("\n}")]
        labels = re.findall(r'label:\s*"([^"]+)"', block)
        self.assertEqual(len(labels), 4)
        for label in labels:
            with self.subTest(label=label):
                self.assertNotIn("qualitative", label.lower())
                self.assertNotIn("grade", label.lower())


# ═══════════════════════════════════════════════ 2. the 404
class LegacyRouteTest(unittest.TestCase):
    """`/explore/<id>` was linked from the landing page and never existed."""

    def test_no_page_links_to_the_dead_route(self):
        offenders = [
            rel(p) for p in public_sources()
            if re.search(r"[\"'`]/explore/\$?\{", code(p))
        ]
        self.assertEqual(offenders, [],
                         "link opportunities to /opportunities/<id>")

    def test_the_landing_page_links_to_the_real_detail_route(self):
        src = code(COMPONENTS / "HomeFeaturedOpportunities.jsx")
        self.assertIn("/opportunities/${opp.id}", src)

    def test_the_legacy_url_still_redirects(self):
        """The bad link was live long enough to have been shared."""
        src = read(FE / "next.config.js")
        self.assertIn("redirects", src)
        # `:id+`, not `:id*`. The star modifier matches zero segments too, so it
        # redirected `/explore` — the working marketplace page — to
        # `/opportunities`. Asserting the exact modifier is the only way this
        # stays fixed; both spellings look right in a diff.
        self.assertIn("/explore/:id+", src)
        self.assertIn("/opportunities/:id+", src)
        self.assertNotIn("/explore/:id*", src,
                         "the star modifier also captures /explore itself")
        self.assertIn("permanent: true", src)

    def test_the_destination_route_exists(self):
        self.assertTrue((APP / "opportunities" / "[id]" / "page.js").exists())


# ═══════════════════════════════════════════════ 3. the snapshot rename
class SnapshotPanelTest(unittest.TestCase):
    """"AI-readable summary" described who the block was for, not what it held."""

    def test_the_old_component_is_gone(self):
        self.assertFalse((COMPONENTS / "geo" / "AiReadableSummary.jsx").exists())
        self.assertTrue((COMPONENTS / "geo" / "SnapshotPanel.jsx").exists())

    def test_nothing_still_imports_it(self):
        offenders = [rel(p) for p in public_sources() if "AiReadableSummary" in code(p)]
        self.assertEqual(offenders, [])

    def test_no_page_titles_a_section_ai_readable(self):
        offenders = [
            rel(p) for p in public_sources()
            # `data-ai-readable` is the markup answer engines read and the
            # rename kept it on purpose. Only a human-facing use is banned.
            if re.search(r"(?<!data-)AI-readable", code(p), re.IGNORECASE)
        ]
        self.assertEqual(offenders, [])

    def test_the_opportunity_pages_say_opportunity_snapshot(self):
        for page in ("app/opportunities/[id]/page.js",
                     "app/opportunities/[id]/OpportunityDetailClient.jsx"):
            with self.subTest(page=page):
                self.assertIn('title="Opportunity Snapshot"', read(FE / page))

    def test_the_machine_readable_markup_survives(self):
        """The rename was for humans. Answer engines still get their attributes."""
        src = read(COMPONENTS / "geo" / "SnapshotPanel.jsx")
        self.assertIn('data-ai-readable="true"', src)
        self.assertIn('data-ai-faq="true"', src)


# ═══════════════════════════════════════════════ 4. recommendations
class RecommendationMessagingTest(unittest.TestCase):
    """The brief: never show "Personalised recommendations are not switched on"."""

    def test_the_dashboard_hides_the_block_when_we_cannot_serve_it(self):
        """NOT_DEPLOYED is ours to fix and the user can do nothing about it.

        An empty panel explaining our infrastructure is worse than no panel: it
        occupies the most valuable space on the dashboard to say "not our best
        day". So the whole block is hidden and the opportunity feed moves up.
        """
        src = code(APP / "dashboard" / "page.js")
        self.assertIn('intel.reason === "NOT_COMPUTED"', src)
        self.assertRegex(src, r"intel\.available\s*\|\|\s*intel\.reason")

    def test_the_computable_case_offers_the_button_that_fixes_it(self):
        """NOT_COMPUTED is theirs to fix, so it gets a way to fix it."""
        src = read(APP / "dashboard" / "page.js")
        self.assertIn('href="/onboarding"', src)
        self.assertIn("Complete your profile", src)

    def test_the_state_messages_speak_to_a_person(self):
        src = code(FE / "lib" / "intelligence.js")
        block = src[src.index("export async function intelligenceState"):]
        # Delimited by code, not by a comment banner: `code()` strips comments,
        # so the banner this used to slice on no longer exists.
        block = block[:block.index("export function scoreLabel")]
        self.assertNotIn("deployment", block.lower())
        self.assertNotIn("switched on", block.lower())
        self.assertIn("Add your skills", block)


# ═══════════════════════════════════════════════ 5. district pages
class DistrictMessagingTest(unittest.TestCase):
    """Both district routes exposed the matching mechanism when it missed."""

    ROUTES = ["app/district/[slug]/page.js", "app/districts/[slug]/page.js"]

    def test_neither_route_mentions_how_we_match_names(self):
        for route in self.ROUTES:
            with self.subTest(route=route):
                src = code(FE / route).lower()
                self.assertNotIn("crosswalk", src)
                self.assertNotIn("vocabulary", src)

    def test_the_unmatched_message_keeps_the_editorial_profile_credible(self):
        """A reader must not conclude the profile above is also unreliable."""
        for route in self.ROUTES:
            with self.subTest(route=route):
                self.assertIn("The profile above is still accurate", read(FE / route))

    def test_the_panel_leads_with_what_is_there(self):
        src = read(COMPONENTS / "knowledge" / "DistrictIntelligencePanel.jsx")
        self.assertIn("Opportunities in {districtName}", src)
        self.assertNotIn("What the knowledge base records", src)


# ═══════════════════════════════════════════════ 6. student-first questions
class StudentFirstTest(unittest.TestCase):
    """"Every screen must answer at least one question."

    Not every page can answer all five, and forcing it would produce filler. What
    is checkable is that the pages a student actually lands on name the thing
    they came for — opportunity, skill, business, government support, people —
    somewhere in their own copy.
    """

    PAGES = {
        "app/knowledge/page.js": ["district", "skill", "business", "scheme"],
        "app/readiness/components/ReadinessSections.jsx": ["skill"],
        "app/manufacturing/components/ManufacturingSections.jsx": ["business"],
        "app/network/components/NetworkSections.jsx": ["collaborator"],
        "components/HomeFeatureGrid.jsx": ["district", "skill", "business", "scheme"],
        "components/platform/KnowledgeSearch.jsx": ["district", "skill", "business", "scheme"],
    }

    def test_each_page_names_what_a_user_came_for(self):
        for page, words in self.PAGES.items():
            src = code(FE / page).lower()
            for word in words:
                with self.subTest(page=page, word=word):
                    self.assertIn(word, src)

    def test_the_landing_page_links_to_the_youtube_channel(self):
        src = read(COMPONENTS / "HomeVideoEmbed.jsx")
        self.assertIn("youtube.com/@valueweave", src)
        self.assertIn("home-youtube-link", src)

    def test_the_search_box_suggests_what_to_type(self):
        """An empty box with no example is a wall."""
        src = read(COMPONENTS / "platform" / "KnowledgeSearch.jsx")
        self.assertIn("placeholder=", src)
        explorer = read(APP / "knowledge" / "page.js")
        self.assertIn("Try a district, a skill, or a business idea", explorer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
