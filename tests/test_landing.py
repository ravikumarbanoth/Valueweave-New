#!/usr/bin/env python3
"""
Landing page — PX Phase 6.

WHAT WAS WRONG
--------------
The first screen answered "here is what we are". Two columns: a pitch, three
buttons named after our product areas — "Discover Yourself", "Explore Ideas",
"Find Collaborators" — and a 440px decorative float of emoji cards.

The search box existed and was in section five, roughly two thousand pixels down
on a phone, inside the feature grid. So a visitor who knew exactly what they
wanted — "PMEGP", "electrician", "Medak" — had no way to say so until they had
scrolled past eight screens of pitch.

WHAT THESE TESTS HOLD
---------------------
Two things, and the second is the one that will actually break.

The first is structural: the box is in the hero, it has example prompts, and the
audience row is above the fold.

The second is that every curated destination is real. A start page for farmers
that opens an empty category is worse than no start page, and there is no way to
notice that by reading the file — the href looks fine either way. So each one is
checked against the app's own route table and the built graph.

    python3 tests/run_all.py --suite landing
"""

import collections
import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
APP = FE / "app"
COMPONENTS = FE / "components"
AUDIENCES_JS = FE / "lib" / "audiences.js"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def entity_counts():
    with open(ROOT / "knowledge_graph" / "entities" / "entities.csv",
              encoding="utf-8", newline="") as fh:
        return collections.Counter(r["entity_type"] for r in csv.DictReader(fh))


def url_to_type():
    """`TYPE_BY_URL` from lib/knowledge.js — the app's own routing table."""
    src = read(FE / "lib" / "knowledge.js")
    block = src[src.index("export const TYPE_BY_URL = {"):]
    block = block[:block.index("\n};")]
    return dict(re.findall(r"(\w+):\s*\"(\w+)\"", block))


def audience_hrefs():
    src = read(AUDIENCES_JS)
    block = src[src.index("export const AUDIENCES = ["):src.index("export const AUDIENCE_BY_SLUG")]
    return re.findall(r'\{ href: "([^"]+)"', block)


def audience_slugs():
    src = read(AUDIENCES_JS)
    block = src[src.index("export const AUDIENCES = ["):src.index("export const AUDIENCE_BY_SLUG")]
    return re.findall(r'^    slug: "([a-z-]+)",', block, re.MULTILINE)


def route_exists(path):
    """Does `/a/b` resolve to an app-router page, static or dynamic?"""
    parts = [p for p in path.split("?")[0].strip("/").split("/") if p]
    node = APP
    for part in parts:
        if (node / part).is_dir():
            node = node / part
            continue
        dynamic = [d for d in node.iterdir()
                   if d.is_dir() and d.name.startswith("[") and d.name.endswith("]")]
        if not dynamic:
            return False
        node = dynamic[0]
    return (node / "page.js").exists() or (node / "page.jsx").exists()


# ═══════════════════════════════════════ 1. the box is the first thing
class HeroSearchTest(unittest.TestCase):

    def setUp(self):
        self.page = code(APP / "page.js")
        self.hero = code(COMPONENTS / "HomeHeroSearch.jsx")
        # The box itself is LiveSearch now, shared with /knowledge. The hero
        # supplies the label, the placeholder and the testid prefix; the input
        # element lives one file down.
        self.box = code(COMPONENTS / "search" / "LiveSearch.jsx")

    def test_the_hero_renders_the_search(self):
        self.assertIn("<HomeHeroSearch", self.page)
        self.assertIn("<LiveSearch", self.hero)
        self.assertIn('testId="home-search"', self.hero)
        self.assertIn("data-testid={`${testId}-input`}", self.box,
                      "home-search-input must still exist on the page")

    def test_the_search_comes_before_every_other_section(self):
        """Being present is not the same as being first."""
        body = self.page[self.page.index("return ("):]
        first = body.index("<HomeHeroSearch")
        for later in ("<HomepageStats", "<HomeHowItWorks", "<HomeFeatureGrid",
                      "<HomeFeaturedOpportunities"):
            with self.subTest(section=later):
                self.assertLess(first, body.index(later))

    def test_the_box_asks_a_question_rather_than_naming_a_feature(self):
        """And the question is on the page, not only in the placeholder.

        The first draft put it in the placeholder and a screen-reader-only
        label. A placeholder disappears the moment anyone types, and at 390px
        it was being truncated mid-word by the submit button — so the one
        sentence the brief asks the page to open with was both temporary and
        cut in half. It is a visible <label> now.
        """
        self.assertIn("What opportunity are you looking for today?", self.hero)
        self.assertNotIn("hiddenLabel", self.hero,
                         "the hero label must stay visible")
        self.assertNotIn('className="sr-only"', self.hero,
                         "the question must be visible, not only announced")
        # The <label> itself lives in LiveSearch, bound to the input by a
        # generated id; the hero supplies its text and its class. Both halves
        # are asserted so neither can quietly become a placeholder again.
        self.assertIn("labelClassName=", self.hero)
        self.assertIn("<label", self.box)
        self.assertIn("htmlFor={`${listboxId}-input`}", self.box)

    def test_it_navigates_rather_than_querying_as_you_type(self):
        """A live index fetch in the hero is a cost on every visitor.

        KnowledgeSearch pulls the whole 647-row index on the first keystroke.
        That is right inside a page you chose to open and wrong at the top of
        the homepage — and when the projection is unreachable it would render
        an empty state above the fold.
        """
        self.assertIn("/knowledge?q=", self.hero)
        self.assertIn("encodeURIComponent", self.hero)
        self.assertNotIn("searchKnowledge", self.hero)

    def prompts(self):
        source = read(AUDIENCES_JS)
        return re.findall(r'^  "([^"]+)",',
                          source[source.index("export const HOME_PROMPTS = ["):],
                          re.MULTILINE)

    def test_the_prompts_are_offered_because_an_empty_box_is_a_wall(self):
        """PX Phase 10 changed which words these are, and why.

        This used to require "AI" and "Manufacturing". Phase 9's goals row now
        offers "AI careers" and "Manufacturing" directly beneath, so pinning
        them here would pin a duplicate: the same words in two chips on one
        screen going to two different pages.

        The requirement is now the SPLIT — these are specific things a person
        might type, the goals are areas they might want — so the named
        examples are the specific ones.
        """
        self.assertIn("HOME_PROMPTS", self.hero)
        prompts = self.prompts()
        self.assertGreaterEqual(len(prompts), 8)
        for named in ("Electrician", "Medak", "Solar", "PMEGP", "Welding"):
            with self.subTest(prompt=named):
                self.assertIn(named, prompts)

    def test_no_word_appears_in_both_the_prompt_row_and_the_goal_row(self):
        """Two chips reading "Government schemes" a centimetre apart, opening
        different pages, is not a shortcut — it is a puzzle. Found by crawling
        the built page at 390px in the Phase 10 audit."""
        source = read(AUDIENCES_JS)
        goals = re.findall(r'label:\s*"([^"]+)"', source)
        self.assertGreaterEqual(len(goals), 9, "GOALS did not parse")
        lower_goals = {g.lower() for g in goals}
        for prompt in self.prompts():
            with self.subTest(prompt=prompt):
                self.assertNotIn(prompt.lower(), lower_goals)

    def test_the_decoration_that_pushed_the_fold_down_is_gone(self):
        self.assertNotIn("FLOATING_CARDS", self.page)
        self.assertNotIn("animate-float", self.page)

    def test_the_admin_editable_labels_still_render(self):
        """Three CTA labels are settings. Demoting them is fine; dropping them
        would silently break a field the admin UI still offers."""
        for name in ("heroHeading", "heroSubheading",
                     "primaryCta", "secondaryCta", "tertiaryCta"):
            with self.subTest(setting=name):
                self.assertIn(name, self.page)


# ═══════════════════════════════════════ 2. who you are, not what we call it
class AudienceTest(unittest.TestCase):

    def setUp(self):
        self.hero = code(COMPONENTS / "HomeHeroSearch.jsx")
        self.start = code(APP / "start" / "[audience]" / "page.js")

    def test_the_six_from_the_brief_are_all_there(self):
        slugs = audience_slugs()
        self.assertEqual(
            sorted(slugs),
            ["business-owner", "entrepreneur", "farmer", "job-seeker",
             "skilled-worker", "student"])

    def test_the_row_is_in_the_hero_not_further_down(self):
        self.assertIn('data-testid="home-audiences"', self.hero)
        self.assertIn("/start/${audience.slug}", self.hero)

    def test_each_audience_opens_a_curated_page_not_a_filtered_table(self):
        self.assertIn("audience.headline", self.start)
        self.assertIn("audience.starts", self.start)
        self.assertIn("audience.prompts", self.start)

    def test_every_start_page_offers_a_way_to_change_your_mind(self):
        """Picking the wrong chip must not be a one-way door."""
        self.assertIn('data-testid="audience-switch"', self.start)

    def test_the_start_pages_read_no_data(self):
        """They must render identically when the projection is unreachable.

        A curated start page that says "0 skills" on a bad day is worse than
        one that says nothing, so the counts in the hints are written down
        rather than queried.
        """
        for banned in ("getEntitiesByType", "typeCounts", "searchKnowledge",
                       "getConnectedKnowledge"):
            with self.subTest(call=banned):
                self.assertNotIn(banned, self.start)

    def test_every_headline_speaks_to_the_reader(self):
        src = read(AUDIENCES_JS)
        headlines = re.findall(r'^    headline:\s*$\n\s*"([^"]+)"|^    headline: "([^"]+)"',
                               src, re.MULTILINE)
        flat = [a or b for a, b in headlines]
        self.assertEqual(len(flat), 6)
        for headline in flat:
            with self.subTest(headline=headline):
                self.assertRegex(headline, r"\byou\b|\byour\b|\?",
                                 "a start page addresses a person")


# ═══════════════════════════════════════ 3. every destination is real
class DestinationTest(unittest.TestCase):
    """The failure that cannot be seen by reading the file."""

    def setUp(self):
        self.hrefs = audience_hrefs()
        self.by_url = url_to_type()
        self.counts = entity_counts()

    def test_the_scan_found_the_links(self):
        self.assertGreaterEqual(len(self.hrefs), 25)

    def test_every_route_resolves(self):
        offenders = [h for h in self.hrefs if not route_exists(h)]
        self.assertEqual(offenders, [], f"dead links on the start pages: {offenders}")

    def test_every_type_filter_is_a_type_the_app_routes(self):
        offenders = []
        for href in self.hrefs:
            match = re.search(r"[?&]type=([a-z]+)", href)
            if match and match.group(1) not in self.by_url:
                offenders.append(href)
        self.assertEqual(offenders, [], f"unknown ?type= values: {offenders}")

    def test_every_type_filter_has_entities_behind_it(self):
        """Curating someone into an empty category is worse than not curating."""
        offenders = []
        for href in self.hrefs:
            match = re.search(r"[?&]type=([a-z]+)", href)
            if not match:
                continue
            entity_type = self.by_url[match.group(1)]
            if self.counts.get(entity_type, 0) == 0:
                offenders.append(f"{href} -> {entity_type} has no entities")
        self.assertEqual(offenders, [], "\n  ".join(offenders))

    def test_the_hint_counts_match_the_graph(self):
        """"25 training centres" has to still be 25.

        These are written down rather than queried so the page survives an
        unreachable projection — which means nothing keeps them honest except
        this test.
        """
        src = read(AUDIENCES_JS)
        claims = re.findall(r'href: "/knowledge\?type=([a-z]+)"[^}]*?hint: "([^"]*?)(\d+)([^"]*)"',
                            src)
        self.assertGreaterEqual(len(claims), 5, "the hint scan found nothing")
        offenders = []
        for url_type, _before, number, _after in claims:
            actual = self.counts.get(self.by_url[url_type], 0)
            if int(number) != actual:
                offenders.append(f"?type={url_type}: page says {number}, graph has {actual}")
        self.assertEqual(offenders, [], "\n  ".join(offenders))


if __name__ == "__main__":
    unittest.main(verbosity=2)
