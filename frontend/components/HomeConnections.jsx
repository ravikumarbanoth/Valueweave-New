// "Follow a connection": real paths through the knowledge graph.
//
// WHAT IS EDITORIAL AND WHAT IS DATA
// ----------------------------------
// The four STARTING POINTS below are chosen by hand — one food business, one
// energy business, one traditional craft, one health business — so the
// section shows the range of what ValueWeave covers. Everything after the
// starting point is read live from `kg_relationships` via getNeighbours(): the
// skills, schemes, industries and materials shown are exactly the edges the
// researched graph holds, in the order of their confidence. Nothing here
// asserts a relationship the data does not contain, and a starting point the
// graph cannot answer for is simply left out.
//
// If the graph is not reachable at all, getNeighbours() returns [] (it never
// throws), every trail is dropped, and the section renders nothing — not an
// empty heading.
import { getEntity, getNeighbours, hrefFor } from "@/lib/knowledge";
import HomeConnectionsClient from "@/components/HomeConnectionsClient";

export const CONNECTION_ANCHORS = [
  { id: "vw:crop:turmeric", theme: "food" },
  { id: "vw:msme:solar-rooftop-epc-contractor", theme: "energy" },
  { id: "vw:msme:handloom-and-handicraft-enterprise", theme: "heritage" },
  { id: "vw:msme:diagnostic-laboratory", theme: "health" },
];

// Which links a trail shows first. Skills and schemes answer "what do I need
// and who helps"; industry and inputs come after. Export markets, soils and
// climate zones are real edges too, but they say less to someone deciding
// what to start, so they only fill space that nothing else claims.
const PRIORITY = [
  "REQUIRES_SKILL",
  "SUPPORTED_BY_SCHEME",
  "PART_OF",
  "PROCESSES",
  "USES_RAW_MATERIAL",
  "USES_MACHINERY",
  "SUPPORTED_BY_BANK",
  "SELLS_TO",
  "EXPORTS_TO",
  "RELATED_TO",
];
const MAX_LINKS = 4;
const MIN_LINKS = 2;

/** Pure: pick and order the links one trail shows. Exported for tests. */
export function pickLinks(pairs) {
  const rank = (t) => {
    const i = PRIORITY.indexOf(t);
    return i === -1 ? PRIORITY.length : i;
  };
  const seen = new Set();
  const out = [];
  // Stable within a relationship type: getNeighbours already sorts by
  // confidence, highest first.
  const sorted = pairs
    .map((p, i) => ({ ...p, i }))
    .sort((a, b) => rank(a.edge.relationship_type) - rank(b.edge.relationship_type) || a.i - b.i);
  // One of each type before a second of any, so a trail is a path through
  // different kinds of thing rather than four schemes in a row.
  for (const pass of [0, 1]) {
    for (const p of sorted) {
      if (out.length === MAX_LINKS) break;
      const id = p.entity.global_entity_id;
      if (seen.has(id)) continue;
      const typeTaken = out.some((o) => o.relationship === p.edge.relationship_type);
      if (pass === 0 && typeTaken) continue;
      seen.add(id);
      out.push({
        relationship: p.edge.relationship_type,
        name: p.entity.canonical_name,
        type: p.entity.entity_type,
        href: hrefFor(p.entity),
      });
    }
  }
  return out;
}

export default async function HomeConnections() {
  const trails = await Promise.all(
    CONNECTION_ANCHORS.map(async ({ id, theme }) => {
      const [anchor, pairs] = await Promise.all([getEntity(id), getNeighbours(id, { direction: "out", limit: 40 })]);
      if (!anchor) return null;
      const links = pickLinks(pairs);
      if (links.length < MIN_LINKS) return null;
      return {
        theme,
        anchor: { name: anchor.canonical_name, type: anchor.entity_type, href: hrefFor(anchor) },
        links,
      };
    })
  );
  const shown = trails.filter(Boolean);
  if (shown.length === 0) return null;
  return <HomeConnectionsClient trails={shown} />;
}
