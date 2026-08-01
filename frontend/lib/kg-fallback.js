// Bridge from the legacy CMS knowledge pages to the researched knowledge graph.
//
// WHY THIS EXISTS
// ---------------
// `/schemes`, `/skills`, `/resources` and `/roadmaps` read `public.kg_*` — tables
// an admin fills by hand through the CMS. Nothing populates them, so those pages
// have always shown "will appear here after admins publish them", while the
// researched graph holds 45 skills, 40 schemes, and 112 institutions, training
// providers and banks.
//
// Two knowledge systems with colliding table names, giving a user contradictory
// answers to the same question. Recorded as backlog A1.
//
// THE RESOLUTION, AND WHICH SIDE WON
// ----------------------------------
// The researched graph is canonical. It is derived from Git, every row carries
// the package and row it came from, and CI keeps it current. The CMS is demoted
// to an editorial override: if a human has published a record it still wins,
// because a person deliberately writing something beats a projection. Nothing
// populates the CMS today, so in practice every page below is served by the
// graph.
//
// No URL changes here and no table is dropped here. Retiring the CMS tables is a
// separate, guarded migration — sql/retire_cms_knowledge_tables.sql — which
// refuses to run if any of them turn out to hold rows.
import { getEntitiesByType, getEntityBySlug, slugOf, URL_BY_TYPE } from "@/lib/knowledge";

// CMS section -> the graph entity types that back it, in priority order.
//
// `resources` maps to three. A CMS "resource" is somewhere you can go for help —
// it has provider_name, location, contact_url and cost_range — and the graph
// splits precisely that idea by who is offering the help.
//
// `roadmaps` is deliberately absent. A roadmap is an ordered sequence of steps
// with costs attached; the graph has no equivalent, and assembling one out of
// unrelated entities would be fabricating a guide nobody wrote. That page says
// so plainly instead.
const GRAPH_TYPES = {
  skills: ["Skill"],
  schemes: ["GovernmentScheme"],
  resources: ["TrainingProvider", "FinancialInstitution", "Institution"],
};

/** Shape a graph entity like a CMS row so PublicEntityList/Detail need no change. */
function asCmsRow(entity) {
  return {
    id: entity.global_entity_id,
    slug: slugOf(entity),
    name: entity.canonical_name,
    status: "published",
    _fromGraph: true,
    _urlType: URL_BY_TYPE[entity.entity_type],
    _sourcePackage: entity.source_package,
    _confidence: entity.confidence_score,
    _entity: entity,
  };
}

/** True when this section has researched data behind it at all. */
export function hasGraphBacking(cmsType) {
  return Boolean(GRAPH_TYPES[cmsType]);
}

/**
 * CMS rows if an admin has published any, otherwise the researched graph.
 * `cmsItems` is whatever `getKgEntities()` returned.
 *
 * `source` distinguishes the two empty cases, because they need different
 * sentences: EMPTY means we have this kind of information and none matched,
 * NO_DATA_SOURCE means we do not gather this kind of information yet.
 */
export async function withGraphFallback(cmsType, cmsItems, { limit = 60 } = {}) {
  if (Array.isArray(cmsItems) && cmsItems.length > 0) {
    return { items: cmsItems, source: "CMS" };
  }
  const types = GRAPH_TYPES[cmsType];
  if (!types) return { items: [], source: "NO_DATA_SOURCE" };

  // Each type is fetched with the full limit rather than a share of it, so a
  // section backed by three types is not silently cut to a third of each.
  const groups = await Promise.all(types.map((t) => getEntitiesByType(t, { limit })));
  const entities = groups.flat();
  entities.sort((a, b) => (a.canonical_name || "").localeCompare(b.canonical_name || ""));

  return {
    items: entities.slice(0, limit).map(asCmsRow),
    source: entities.length ? "GRAPH" : "EMPTY",
  };
}

/** One record: CMS first, then the graph by the same slug. */
export async function detailWithGraphFallback(cmsType, slug, cmsRow) {
  if (cmsRow) return { row: cmsRow, source: "CMS", entity: null };
  const types = GRAPH_TYPES[cmsType];
  if (!types) return { row: null, source: "NO_DATA_SOURCE", entity: null };

  // Each backing type is tried in order. This was a hardcoded
  // `graphType === "GovernmentScheme" ? "scheme" : "skill"`, which resolved
  // everything that was not a scheme to "skill" — harmless while there were two
  // types, wrong the moment `resources` mapped to three. URL_BY_TYPE is the map
  // that already exists for this and cannot drift from TYPE_BY_URL.
  for (const graphType of types) {
    const urlType = URL_BY_TYPE[graphType];
    if (!urlType) continue;
    const entity = await getEntityBySlug(urlType, slug);
    if (entity) return { row: asCmsRow(entity), source: "GRAPH", entity };
  }
  return { row: null, source: "NONE", entity: null };
}

/** Canonical detail link for a row from either source. */
export function rowHref(cmsType, row) {
  if (row?._fromGraph) {
    const urlType = row._urlType || URL_BY_TYPE[row?._entity?.entity_type];
    return urlType ? `/knowledge/${urlType}/${row.slug}` : "/knowledge";
  }
  return `/${cmsType}/${row.slug}`;
}
