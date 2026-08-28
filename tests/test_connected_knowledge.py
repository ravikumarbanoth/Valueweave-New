#!/usr/bin/env python3
"""
Connected knowledge — PX Phase 5.

WHAT WAS WRONG
--------------
"Where this leads next" grouped an entity's neighbours by type, headed each
group with the type's plural name, and ordered the groups by how many rows were
in them. Three separate ways of letting the data model drive the page:

    order      decided by our row counts. On a Crop, "Soil types" and "Climate
               zones" led, because there are more soil edges than scheme edges.
    headings   "Government schemes" is a category in our model. "Schemes that
               can help you" is the question the reader arrived with.
    ranking    none. Within a group the order was whatever came back.

`LEAD_RELATED` was a per-type priority list meant to fix the first of those. It
never took effect — the renderer re-sorted by group size — and it had drifted
from the graph: 20 of the 46 pairs it named do not exist, and 10 that do exist
were missing.

AND THE MEASUREMENT THAT DROVE THE REST
---------------------------------------
Over the built graph, median directly-connected entities:

    District              1      (33 within two hops)
    BusinessOpportunity   1      (11)
    Crop                  5      (36)
    Skill                 2      ( 7)

Half of all district pages linked to exactly one thing. That is not missing
research — it is the shape of the graph. Districts connect to businesses and
institutions, and what a person wants to know about a district hangs off those.
So the page reads a second hop, and says which neighbour each one came through.

WHAT THESE TESTS HOLD
---------------------
Every intent pair is reachable in the real graph within the two hops the page
reads — the same reachability ratchet Phase 1 put on the search vocabulary,
for the same reason: a heading that can never render is a lie that costs a
section. Plus the ranking rules, run as the shipped JavaScript rather than a
Python reimplementation.

    python3 tests/run_all.py --suite connected_knowledge
"""

import collections
import csv
import json
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
GRAPH = ROOT / "knowledge_graph"
INTENT_JS = FE / "lib" / "related-intent.js"
NODE = shutil.which("node")


def rows(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def entity_types():
    return {e["global_entity_id"]: e["entity_type"]
            for e in rows(GRAPH / "entities" / "entities.csv")}


def adjacency():
    """Undirected, by entity id. The page reads both directions."""
    types = entity_types()
    out = collections.defaultdict(set)
    for r in rows(GRAPH / "relationships" / "relationships.csv"):
        a, b = r["from_entity"], r["to_entity"]
        if a in types and b in types:
            out[a].add(b)
            out[b].add(a)
    return types, out


def reachable_within_two_hops():
    """source entity TYPE -> neighbour types reachable in one or two hops."""
    types, adj = adjacency()
    out = collections.defaultdict(set)
    for node, source_type in types.items():
        for near in adj[node]:
            out[source_type].add(types[near])
            for far in adj[near]:
                if far != node:
                    out[source_type].add(types[far])
    return out


def parse_intent():
    """`INTENT` from the shipped module, without executing it.

    Reading the real file rather than a fixture is the point: a pair added to
    the module and not to the graph has to fail here.
    """
    src = INTENT_JS.read_text(encoding="utf-8")
    block = src[src.index("export const INTENT = {"):src.index("export const FALLBACK_HEADING")]
    intent = collections.OrderedDict()
    current = None
    for line in block.splitlines():
        opened = re.match(r"\s{2}(\w+): \[", line)
        if opened:
            current = opened.group(1)
            intent.setdefault(current, [])
        for entity_type, heading in re.findall(r'\{ type: "(\w+)", heading: "([^"]+)" \}', line):
            intent[current].append((entity_type, heading))
    return intent


# ═══════════════════════════════════════════ 1. the config matches the graph
class IntentReachabilityTest(unittest.TestCase):
    """No section may promise a link the graph cannot produce."""

    @classmethod
    def setUpClass(cls):
        cls.intent = parse_intent()
        cls.reachable = reachable_within_two_hops()

    def test_the_config_parsed(self):
        """A silent parse failure would make every test below vacuous."""
        self.assertGreaterEqual(len(self.intent), 15)
        self.assertTrue(all(v for v in self.intent.values()))

    def test_every_intent_pair_exists_in_the_graph(self):
        offenders = []
        for source, pairs in self.intent.items():
            for entity_type, heading in pairs:
                if entity_type not in self.reachable.get(source, set()):
                    offenders.append(f"{source} -> {entity_type}  ({heading!r})")
        self.assertEqual(
            offenders, [],
            "These headings can never render — the graph holds no path:\n  "
            + "\n  ".join(offenders))

    def test_the_dead_pairs_from_the_first_draft_stay_out(self):
        """Named individually, because each was written in good faith once."""
        dead = [("Skill", "Certification"), ("Certification", "Skill"),
                ("BusinessOpportunity", "Machinery"), ("BusinessOpportunity", "Market"),
                ("BusinessOpportunity", "RawMaterial"), ("BusinessOpportunity", "District"),
                ("District", "BusinessOpportunity")]
        for source, entity_type in dead:
            with self.subTest(pair=f"{source}->{entity_type}"):
                self.assertNotIn(entity_type,
                                 [t for t, _ in self.intent.get(source, [])])

    def test_certification_has_no_relationships_at_all(self):
        """The reason two of those pairs could not work, stated as a fact.

        If a later package gives Certification some edges, this fails and the
        intent sections for it can be written — which is the right prompt.
        """
        types, adj = adjacency()
        certs = [i for i, t in types.items() if t == "Certification"]
        self.assertTrue(certs, "the graph should still hold Certification entities")
        self.assertEqual(
            sum(len(adj[i]) for i in certs), 0,
            "Certification now has edges — add its intent sections")

    def test_headings_are_questions_not_type_names(self):
        """The whole point of the phase, as a grep."""
        type_names = {"Skill", "Skills", "Government schemes", "Districts",
                      "Business opportunities", "Industries", "MSMEs", "Crops",
                      "Machinery", "Markets", "Raw materials"}
        offenders = [f"{s}: {h}" for s, pairs in self.intent.items()
                     for _, h in pairs if h in type_names]
        self.assertEqual(offenders, [], "\n  ".join(offenders))

    def test_the_relationship_weights_cover_every_relationship_in_the_graph(self):
        """A weight table missing a live relationship silently demotes it."""
        src = INTENT_JS.read_text(encoding="utf-8")
        block = src[src.index("export const REL_WEIGHT = {"):src.index("export const DEFAULT_REL_WEIGHT")]
        weighted = set(re.findall(r"^  (\w+):", block, re.MULTILINE))
        live = {r["relationship_type"]
                for r in rows(GRAPH / "relationships" / "relationships.csv")}
        self.assertEqual(live - weighted, set(),
                         "relationships in the graph with no weight")
        self.assertEqual(weighted - live, set(),
                         "weights for relationships that do not exist")


# ═══════════════════════════════════════════ 2. the shape of the real graph
class GraphShapeTest(unittest.TestCase):
    """The measurement the second hop exists to answer.

    If the graph ever gets dense enough that one hop is sufficient, this fails
    and the second hop can be reconsidered rather than carried forever.
    """

    def median_neighbours(self, entity_type, hops):
        types, adj = adjacency()
        ids = [i for i, t in types.items() if t == entity_type]
        counts = []
        for i in ids:
            near = set(adj[i])
            if hops == 2:
                far = set()
                for n in near:
                    far |= adj[n]
                near = (near | far) - {i}
            counts.append(len(near))
        counts.sort()
        return counts[len(counts) // 2] if counts else 0

    def test_one_hop_is_not_enough_for_a_district(self):
        self.assertLessEqual(self.median_neighbours("District", 1), 3)
        self.assertGreaterEqual(self.median_neighbours("District", 2), 15)

    def test_one_hop_is_not_enough_for_a_business_opportunity(self):
        self.assertLessEqual(self.median_neighbours("BusinessOpportunity", 1), 3)
        self.assertGreaterEqual(self.median_neighbours("BusinessOpportunity", 2), 6)


# ═══════════════════════════════════════════ 3. the shipped ranking, in node
@unittest.skipIf(NODE is None, "node is required — the ranking is JavaScript, and "
                               "testing a Python copy of it would prove nothing")
class RankingTest(unittest.TestCase):
    """`intentSections` and `scoreNeighbour`, executed."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        src = INTENT_JS.read_text(encoding="utf-8")
        # The module imports URL_BY_TYPE from lib/knowledge.js, which pulls in
        # @supabase/supabase-js. Stub it: the ranking does not touch the network
        # and the map is only used to build an overflow href.
        src = src.replace('import { URL_BY_TYPE } from "./knowledge.js";',
                          "const URL_BY_TYPE = { Skill: 'skill', MSME: 'msme', "
                          "GovernmentScheme: 'scheme', Industry: 'industry' };")
        (cls.dir / "related-intent.js").write_text(src, encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def run_js(self, body):
        script = self.dir / "run.mjs"
        # Use a file:// URI for the import so Node's ESM loader accepts it on Windows
        import_uri = Path(self.dir).as_uri()
        script.write_text(textwrap.dedent(f"""
            const {{ intentSections, scoreNeighbour, MAX_PER_SECTION }} =
              await import("{import_uri}/related-intent.js");
            {body}
        """), encoding="utf-8")
        r = subprocess.run([NODE, str(script)], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise AssertionError(f"node failed:\n{r.stdout}\n{r.stderr}")
        return json.loads(r.stdout)

    @staticmethod
    def node(name, entity_type, via, confidence=80, edge=80, hop=1, bridge=None):
        return {"global_entity_id": f"vw:{entity_type.lower()}:{name}",
                "canonical_name": name, "entity_type": entity_type,
                "confidence_score": confidence, "_via": via,
                "_edge": {"confidence": edge}, "_hop": hop, "_bridge": bridge}

    def test_sections_follow_the_readers_order_not_the_row_counts(self):
        """A Skill page leads with where to learn it, however few there are."""
        grouped = {
            "MSME": [self.node(f"m{i}", "MSME", "REQUIRES_SKILL") for i in range(20)],
            "TrainingProvider": [self.node("ITI Warangal", "TrainingProvider", "TRAINED_BY")],
        }
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'Skill')));")
        self.assertEqual([s["type"] for s in out], ["TrainingProvider", "MSME"])
        self.assertEqual(out[0]["heading"], "Where to learn this")

    def test_a_strong_relationship_outranks_a_generic_one(self):
        grouped = {"Skill": [self.node("Generic", "Skill", "RELATED_TO", edge=100),
                             self.node("Required", "Skill", "REQUIRES_SKILL", edge=60)]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual([e["canonical_name"] for e in out[0]["items"]],
                         ["Required", "Generic"])

    def test_link_confidence_breaks_ties_within_a_relationship(self):
        grouped = {"Skill": [self.node("Weak", "Skill", "REQUIRES_SKILL", edge=20),
                             self.node("Strong", "Skill", "REQUIRES_SKILL", edge=95)]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual([e["canonical_name"] for e in out[0]["items"]],
                         ["Strong", "Weak"])

    def test_entity_confidence_cannot_overturn_the_relationship(self):
        """A well-sourced afterthought is still an afterthought."""
        grouped = {"Skill": [self.node("Sourced", "Skill", "RELATED_TO", confidence=100),
                             self.node("Needed", "Skill", "REQUIRES_SKILL", confidence=10)]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual(out[0]["items"][0]["canonical_name"], "Needed")

    def test_a_section_is_capped_and_says_how_many_it_held_back(self):
        """"NOT everything from the package"."""
        grouped = {"Skill": [self.node(f"s{i}", "Skill", "REQUIRES_SKILL") for i in range(15)]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual(len(out[0]["items"]), 6)
        self.assertEqual(out[0]["overflow"], 9)
        self.assertEqual(out[0]["href"], "/knowledge?type=skill")

    def test_an_unplanned_type_is_shown_last_rather_than_dropped(self):
        """Losing data to tidy the page would be the wrong trade."""
        grouped = {"Soil": [self.node("Black Cotton", "Soil", "RELATED_TO")],
                   "Skill": [self.node("Welding", "Skill", "REQUIRES_SKILL")]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual([s["type"] for s in out], ["Skill", "OTHER"])
        self.assertEqual(out[-1]["heading"], "Also connected")
        self.assertEqual([e["canonical_name"] for e in out[-1]["items"]], ["Black Cotton"])

    def test_the_unplanned_types_share_one_section(self):
        """The first draft gave Warangal seven consecutive "Also connected"s.

        Every unnamed type became its own section with the same heading, which
        reads as a rendering bug even though every row was correct.
        """
        grouped = {
            "Soil": [self.node("Black Cotton", "Soil", "RELATED_TO")],
            "ClimateZone": [self.node("Tropical", "ClimateZone", "RELATED_TO")],
            "Country": [self.node("India", "Country", "LOCATED_IN")],
        }
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["heading"], "Also connected")
        self.assertEqual(len(out[0]["items"]), 3)
        self.assertIsNone(out[0]["href"],
                          "a pooled section spans types and has no one category")

    def test_no_type_is_rendered_twice(self):
        grouped = {"Skill": [self.node("Welding", "Skill", "REQUIRES_SKILL")]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'MSME')));")
        self.assertEqual(len(out), 1)

    def test_an_unknown_source_type_still_renders_everything(self):
        """A type with no intent entry must degrade, not disappear."""
        grouped = {"Skill": [self.node("Welding", "Skill", "REQUIRES_SKILL")]}
        out = self.run_js(f"console.log(JSON.stringify("
                          f"intentSections({json.dumps(grouped)}, 'Nonsense')));")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["heading"], "Also connected")


# ═══════════════════════════════════════════ 4. the wiring
class WiringTest(unittest.TestCase):

    def test_the_detail_page_uses_the_intent_sections(self):
        src = (FE / "app" / "knowledge" / "[type]" / "[slug]" / "page.js").read_text(encoding="utf-8")
        self.assertIn("intentSections(related, entity.entity_type)", src)
        self.assertIn("<IntentSections", src)

    def test_lead_related_is_gone(self):
        """It never took effect and had drifted from the graph."""
        body = (FE / "app" / "knowledge" / "[type]" / "[slug]" / "page.js").read_text(encoding="utf-8")
        code = "\n".join(l.split("//", 1)[0] for l in body.splitlines())
        self.assertNotIn("LEAD_RELATED", code)

    def test_the_page_reads_the_second_hop(self):
        src = (FE / "app" / "knowledge" / "[type]" / "[slug]" / "page.js").read_text(encoding="utf-8")
        self.assertIn("getConnectedKnowledge", src)

    def test_a_second_hop_link_says_which_neighbour_it_came_through(self):
        """Otherwise the page claims a relationship that does not exist."""
        src = (FE / "components" / "knowledge" / "RelatedEntities.jsx").read_text(encoding="utf-8")
        self.assertIn("_bridge", src)
        self.assertIn('data-hop', src)

    def test_the_second_hop_never_displaces_a_direct_neighbour(self):
        src = (FE / "lib" / "knowledge.js").read_text(encoding="utf-8")
        block = src[src.index("export async function getConnectedKnowledge"):]
        block = block[:block.index("\n}")]
        self.assertIn("if (merged[type]?.length) continue;", block)

    def test_the_second_hop_costs_two_queries_not_n(self):
        """One per neighbour would be forty round trips on a busy page."""
        src = (FE / "lib" / "knowledge.js").read_text(encoding="utf-8")
        block = src[src.index("export async function getSecondHop"):]
        block = block[:block.index("\nexport async function getConnectedKnowledge")]
        self.assertIn(".in(", block)
        self.assertNotIn("for (const id of ids)", block)


if __name__ == "__main__":
    unittest.main(verbosity=2)
