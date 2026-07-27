// Bridge from the admin-CMS knowledge pages to the researched knowledge graph.
//
// WHY THIS EXISTS
// ---------------
// `/schemes`, `/skills`, `/resources` and `/roadmaps` read `public.kg_*` — tables
// an admin fills by hand through the CMS. Nothing populates them, so those pages
// have always shown "will appear here after admins publish them", while
// `knowledge.kg_schemes` holds 40 researched schemes and `knowledge.kg_skills`
// holds 45.
//
// Two knowledge systems with colliding table names, giving a user contradictory
// answers to the same question. Recorded as backlog A1.
//
// This module resolves it WITHOUT deleting either: the CMS stays authoritative
// when it has content, and the researched graph fills the page when it does not.
// An admin publishing a scheme still overrides. Nothing is duplicated and no
// existing URL changes.
import { getEntitiesByType, getEntityBySlug, slugOf } from "@/lib/knowledge";

//: CMS entity type -> the graph entity type that backs it.
const GRAPH_TYPE = {
  schemes: "GovernmentScheme",
  skills: "Skill",
};

/** Shape a graph entity like a CMS row so PublicEntityList/Detail need no change. */
function asCmsRow(entity) {
  return {
    id: entity.global_entity_id,
    slug: slugOf(entity),
    name: entity.canonical_name,
    status: "published",
    _fromGraph: true,
    _sourcePackage: entity.source_package,
    _confidence: entity.confidence_score,
    _entity: entity,
  };
}

/**
 * CMS rows if the admin has published any, otherwise the researched graph.
 * `cmsItems` is whatever `getKgEntities()` returned.
 */
export async function withGraphFallback(cmsType, cmsItems, { limit = 60 } = {}) {
  if (Array.isArray(cmsItems) && cmsItems.length > 0) {
    return { items: cmsItems, source: "CMS" };
  }
  const graphType = GRAPH_TYPE[cmsType];
  if (!graphType) return { items: [], source: "CMS" };

  const entities = await getEntitiesByType(graphType, { limit });
  return { items: entities.map(asCmsRow), source: entities.length ? "GRAPH" : "NONE" };
}

/** One record: CMS first, then the graph by the same slug. */
export async function detailWithGraphFallback(cmsType, slug, cmsRow) {
  if (cmsRow) return { row: cmsRow, source: "CMS", entity: null };
  const graphType = GRAPH_TYPE[cmsType];
  if (!graphType) return { row: null, source: "NONE", entity: null };

  const urlType = graphType === "GovernmentScheme" ? "scheme" : "skill";
  const entity = await getEntityBySlug(urlType, slug);
  if (!entity) return { row: null, source: "NONE", entity: null };
  return { row: asCmsRow(entity), source: "GRAPH", entity };
}

/** Canonical detail link for a row from either source. */
export function rowHref(cmsType, row) {
  if (row?._fromGraph) {
    return cmsType === "schemes" ? `/knowledge/scheme/${row.slug}` : `/knowledge/skill/${row.slug}`;
  }
  return `/${cmsType}/${row.slug}`;
}
