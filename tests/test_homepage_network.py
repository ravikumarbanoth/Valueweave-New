#!/usr/bin/env python3
"""
The homepage network: one continuous visual system from the hero to the
footer, and a "Follow a connection" section built only from real graph edges.

What these hold:
  - every homepage section is inside the shared network layer, and the layer
    and the footer hub draw from ONE geometry module (that is what makes the
    lines meet at every seam);
  - the network costs no JavaScript and respects prefers-reduced-motion;
  - the connection trails come from getNeighbours(), start from entities that
    exist, and are chosen by a pure function that is tested here in Node;
  - the hub links only to routes that exist.
"""
import csv
import re
import unittest
from pathlib import Path

from tests.js_harness import NODE, JsHarness

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
COMP = FE / "components"
NET = COMP / "network"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def code(path):
    src = re.sub(r"/\*.*?\*/", "", read(path), flags=re.DOTALL)
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


class ContinuityTest(unittest.TestCase):

    def setUp(self):
        self.page = code(FE / "app" / "page.js")
        self.body = self.page[self.page.index("return ("):]

    def test_every_section_is_inside_the_network(self):
        sections = re.findall(r"<(Home[A-Za-z]+)", self.body)
        sections = [s for s in sections if s not in ("HomeNavClient", "HomeHeroSearch", "HomeHeroValueProps", "HomeHeroHub")]
        self.assertGreaterEqual(len(sections), 12)
        # Each section component sits between an opening and closing wrapper.
        for name in sections:
            i = self.body.index(f"<{name}")
            before = self.body[:i]
            self.assertGreater(before.count("<NetworkSection"), before.count("</NetworkSection>"), name)

    def test_one_first_and_one_last(self):
        self.assertEqual(len(re.findall(r"<NetworkSection[^>]*\bfirst\b", self.body)), 1)
        self.assertEqual(len(re.findall(r"<NetworkSection[^>]*\blast\b", self.body)), 1)
        # Hero first, final call to action last.
        self.assertLess(self.body.index("first"), self.body.index("<HomeHeroSearch"))
        self.assertGreater(self.body.rindex(" last "), self.body.rindex("<HomeSectorsSection"))

    def test_indices_are_explicit_not_a_render_counter(self):
        idx = [int(i) for i in re.findall(r"<NetworkSection index=\{(\d+)\}", self.body)]
        self.assertEqual(idx, list(range(len(idx))))

    def test_layer_and_footer_share_one_geometry(self):
        for f in ("NetworkSection.jsx", "NetworkFooterHub.jsx"):
            self.assertIn('from "./geometry"', read(NET / f), f)
        geo = read(NET / "geometry.js")
        for const in ("RAIL_LEFT", "RAIL_RIGHT", "SEAM_X", "FORK_PX"):
            self.assertIn(f"export const {const}", geo)

    def test_rails_join_without_a_kink(self):
        # Vertical tangent at both ends: the control points share the end x.
        geo = read(NET / "geometry.js")
        self.assertIn("M${x},0 C${x},25", geo)
        self.assertIn("S${x},75 ${x},100", geo)

    def test_the_forks_fit_inside_the_smallest_section_padding(self):
        fork = int(re.search(r"FORK_PX = (\d+)", read(NET / "geometry.js")).group(1))
        self.assertLess(fork, 64)  # py-16, the smallest padding on the homepage

    def test_sections_no_longer_paint_over_the_network(self):
        for f in ("HomeVideoEmbed.jsx", "HomeFeatureGrid.jsx", "HomeLiveActivityClient.jsx",
                  "HomeWhySection.jsx", "HomeSectorsSection.jsx"):
            first = re.search(r"<section[^>]*className=\"([^\"]*)\"", read(COMP / f)).group(1)
            self.assertNotIn("bg-warm", first, f)
        final = re.search(r"<section[^>]*className=\"([^\"]*)\"", read(COMP / "HomeFinalCta.jsx")).group(1)
        self.assertNotIn("bg-ink", final, "the final CTA is a panel now, not a full-width band")

    def test_an_empty_section_hides_its_layer(self):
        css = read(FE / "app" / "globals.css")
        self.assertIn(".vw-net > .vw-net-layer:first-child { display: none; }", css)
        net = read(NET / "NetworkSection.jsx")
        self.assertLess(net.index("{children}"), net.index("vw-net-layer"))


class CostAndAccessTest(unittest.TestCase):

    def test_the_layer_is_server_rendered_svg(self):
        for f in ("NetworkSection.jsx", "NetworkFooterHub.jsx", "geometry.js"):
            src = read(NET / f)
            self.assertNotIn('"use client"', src, f)
            self.assertNotIn("<canvas", src, f)
            self.assertNotRegex(src, r"\buse(State|Effect)\b", f)

    def test_it_never_takes_clicks_and_is_hidden_from_screen_readers(self):
        for f in ("NetworkSection.jsx", "NetworkFooterHub.jsx"):
            src = read(NET / f)
            self.assertIn("pointer-events-none", src, f)
            self.assertIn('aria-hidden="true"', src, f)
            self.assertIn("-z-10", src, f)

    def test_motion_is_opt_in(self):
        css = read(FE / "app" / "globals.css")
        block = css[css.index("@media (prefers-reduced-motion: no-preference)"):]
        self.assertIn(".vw-seam { animation", block)
        # No animation declared outside that media query.
        outside = css[:css.index("@media (prefers-reduced-motion: no-preference)")]
        self.assertNotRegex(outside[outside.index("Homepage network"):], r"animation\s*:")

    def test_no_new_dependency(self):
        pkg = read(FE / "package.json")
        for lib in ("three", "d3", "particles", "tsparticles", "react-force-graph", "vis-network"):
            self.assertNotIn(f'"{lib}', pkg)

    def test_footer_hub_only_on_the_homepage(self):
        src = read(COMP / "FooterClient.jsx")
        self.assertIn('usePathname() === "/"', src)
        self.assertIn("{onHome && <NetworkFooterHub />}", src)


class HubTest(unittest.TestCase):

    def test_hub_links_go_to_routes_that_exist(self):
        src = read(COMP / "HomeHeroHub.jsx")
        hrefs = re.findall(r'href: "([^"]+)"', src)
        self.assertEqual(len(hrefs), 8)
        for href in hrefs:
            route = href.split("?")[0].strip("/")
            self.assertTrue((FE / "app" / route / "page.js").exists(), href)

    def test_hub_keeps_the_search_and_does_not_replace_it(self):
        page = read(FE / "app" / "page.js")
        self.assertIn("<HomeHeroSearch", page)
        self.assertLess(page.index("<HomeHeroSearch"), page.index("<HomeHeroHub"))

    def test_hub_text_is_translated(self):
        lang = read(FE / "lib" / "language.js")
        for key in ("hub.title", "hub.subtitle", "hub.tagline", "hub.research", "hub.networks_desc",
                    "connections.title", "connections.note", "footer.network_line"):
            self.assertEqual(lang.count(f"'{key}':"), 2, key)


class ConnectionsDataTest(unittest.TestCase):

    def test_trails_are_read_from_the_graph(self):
        src = code(COMP / "HomeConnections.jsx")
        self.assertIn("getNeighbours(id", src)
        self.assertIn("getEntity(id)", src)
        self.assertIn("if (shown.length === 0) return null;", src)

    def test_every_anchor_exists_and_has_enough_edges(self):
        src = read(COMP / "HomeConnections.jsx")
        anchors = re.findall(r'id: "(vw:[a-z]+:[a-z0-9-]+)"', src)
        self.assertEqual(len(anchors), 4)
        ents = {r["global_entity_id"] for r in csv.DictReader(open(ROOT / "knowledge_graph/entities/entities.csv", encoding="utf-8"))}
        rels = list(csv.DictReader(open(ROOT / "knowledge_graph/relationships/relationships.csv", encoding="utf-8")))
        for a in anchors:
            self.assertIn(a, ents, a)
            self.assertGreaterEqual(sum(r["from_entity"] == a for r in rels), 2, a)


@unittest.skipIf(NODE is None, "node is required — the code under test is JavaScript")
class PickLinksTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        h = JsHarness()
        try:
            # HomeConnections.jsx is JSX; the pure function is extracted and run.
            src = read(COMP / "HomeConnections.jsx")
            body = src[src.index("const PRIORITY"):src.index("export default async function")]
            body = body.replace("export function pickLinks", "function pickLinks")
            cls.out = h.run('''
                const hrefFor = (e) => "/knowledge/x/" + e.global_entity_id;
                ''' + body + '''
                const E = (id, type) => ({ global_entity_id: id, canonical_name: id, entity_type: type });
                const P = (rel, id, type) => ({ edge: { relationship_type: rel }, entity: E(id, type) });
                const pairs = [
                  P("EXPORTS_TO", "uae", "ExportCountry"),
                  P("SUPPORTED_BY_SCHEME", "pmfme", "GovernmentScheme"),
                  P("SUPPORTED_BY_SCHEME", "pkvy", "GovernmentScheme"),
                  P("SUPPORTED_BY_SCHEME", "pmfme", "GovernmentScheme"),
                  P("REQUIRES_SKILL", "electrician", "Skill"),
                  P("PART_OF", "spices", "Industry"),
                  P("RELATED_TO", "red-soil", "Soil"),
                ];
                console.log(JSON.stringify({ links: pickLinks(pairs), empty: pickLinks([]) }));
            ''')
        finally:
            h.cleanup()

    def test_skills_and_schemes_lead(self):
        rels = [l["relationship"] for l in self.out["links"]]
        self.assertEqual(rels[:2], ["REQUIRES_SKILL", "SUPPORTED_BY_SCHEME"])

    def test_one_of_each_kind_before_a_second_of_any(self):
        rels = [l["relationship"] for l in self.out["links"]]
        self.assertEqual(rels, ["REQUIRES_SKILL", "SUPPORTED_BY_SCHEME", "PART_OF", "EXPORTS_TO"])

    def test_no_duplicates_and_at_most_four(self):
        names = [l["name"] for l in self.out["links"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertLessEqual(len(names), 4)

    def test_nothing_in_nothing_out(self):
        self.assertEqual(self.out["empty"], [])


if __name__ == "__main__":
    unittest.main()
