// ValueWeave — Knowledge layer data access (Platform v3.0, Step 2).
//
// Reads the `knowledge` Postgres schema that knowledge_sync projects from Git.
// Deliberately mirrors lib/knowledge-graph.js: same anon-client pattern, same
// silent-failure contract, same naming. An engineer who knows that file will
// recognise this one.
//
// WHY THIS READS SUPABASE AND NOT AN API
// -------------------------------------
// The knowledge platform's engines are Python. This frontend makes zero fetch()
// calls and has no API-client pattern, no error-boundary convention and no
// deployment target for a Python service. Introducing all of that at once would be
// the "new backend architecture" the brief rules out.
//
// Instead the engines write to Supabase (knowledge_sync, Step 1) and the frontend
// reads it with the client it already has. Git stays the source of truth; Supabase
// is the read-optimised cache it was built to be.
//
// EVERY FUNCTION RETURNS EMPTY ON FAILURE, NEVER THROWS
// ----------------------------------------------------
// The `knowledge` schema is not applied to any database yet. Until it is, every
// call here returns [] or null and every consuming component renders its
// "not available yet" state. That is the same contract lib/knowledge-graph.js
// already uses for the kg_* tables, and it is why these pages can ship before the
// migration runs.

import { createClient } from "@supabase/supabase-js";

// The projection lives in its own schema so it cannot collide with the existing
// public.kg_* CMS tables. See docs/SYNC_ARCHITECTURE.md §2.
export const KNOWLEDGE_SCHEMA = "knowledge";

function knowledgeClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  try {
    return createClient(url, key, {
      auth: { persistSession: false },
      db: { schema: KNOWLEDGE_SCHEMA },
    });
  } catch {
    return null;
  }
}

async function safe(run, fallback) {
  try {
    const sb = knowledgeClient();
    if (!sb) return fallback;
    const { data, error } = await run(sb);
    if (error) return fallback;
    return data ?? fallback;
  } catch {
    return fallback;
  }
}

const LIVE = "sync_deleted_at";

// ─── Entities ───────────────────────────────────────────────────────────────
export async function getEntity(globalEntityId) {
  if (!globalEntityId) return null;
  const rows = await safe(
    (sb) =>
      sb
        .from("kg_entities")
        .select("*")
        .eq("global_entity_id", globalEntityId)
        .is(LIVE, null)
        .limit(1),
    []
  );
  return rows[0] || null;
}

export async function getEntitiesByType(entityType, { limit = 50, minConfidence = 0 } = {}) {
  return safe(
    (sb) => {
      let q = sb
        .from("kg_entities")
        .select("*")
        .eq("entity_type", entityType)
        .is(LIVE, null)
        .order("confidence_score", { ascending: false })
        .limit(limit);
      if (minConfidence > 0) q = q.gte("confidence_score", minConfidence);
      return q;
    },
    []
  );
}

// ─── Relationships ──────────────────────────────────────────────────────────
// `direction` is "out" (this entity is from_entity) or "in".
export async function getNeighbours(globalEntityId, { relationshipType, direction = "out", limit = 60 } = {}) {
  if (!globalEntityId) return [];
  const anchor = direction === "out" ? "from_entity" : "to_entity";
  const other = direction === "out" ? "to_entity" : "from_entity";

  const edges = await safe(
    (sb) => {
      let q = sb
        .from("kg_relationships")
        .select("*")
        .eq(anchor, globalEntityId)
        .is(LIVE, null)
        .order("confidence", { ascending: false })
        .limit(limit);
      if (relationshipType) q = q.eq("relationship_type", relationshipType);
      return q;
    },
    []
  );
  if (edges.length === 0) return [];

  // One round trip for every endpoint rather than one per edge.
  const ids = [...new Set(edges.map((e) => e[other]).filter(Boolean))];
  const nodes = await safe(
    (sb) => sb.from("kg_entities").select("*").in("global_entity_id", ids).is(LIVE, null),
    []
  );
  const byId = new Map(nodes.map((n) => [n.global_entity_id, n]));

  return edges
    .map((edge) => ({ edge, entity: byId.get(edge[other]) || null }))
    .filter((pair) => pair.entity !== null);
}

// ─── District intelligence ──────────────────────────────────────────────────
// Everything the graph links to one district, grouped by entity type. Powers the
// district page and the dashboard's district rail.
export async function getDistrictKnowledge(districtEntityId) {
  const pairs = await getNeighbours(districtEntityId, { direction: "in", limit: 200 });
  const grouped = {};
  for (const { entity, edge } of pairs) {
    const type = entity.entity_type;
    if (!grouped[type]) grouped[type] = [];
    grouped[type].push({ ...entity, _via: edge.relationship_type, _edge: edge });
  }
  return grouped;
}

// ─── Vocabulary crosswalk (Step 0) ──────────────────────────────────────────
// The only bridge from free-text profile skills to graph entities.
// `NO_COUNTERPART` rows are returned too: a term we have no data for is a fact
// worth showing, not a row to hide.
export async function resolveTerms(termKind, terms) {
  const list = (terms || []).map((t) => String(t || "").trim()).filter(Boolean);
  if (list.length === 0) return { resolved: [], unresolved: [] };

  const normalised = list.map(normaliseTerm);
  const rows = await safe(
    (sb) =>
      sb
        .from("kg_vocabulary_map")
        .select("*")
        .eq("term_kind", termKind)
        .in("normalised_term", normalised),
    []
  );

  const byNorm = new Map(rows.map((r) => [r.normalised_term, r]));
  const resolved = [];
  const unresolved = [];
  list.forEach((term, i) => {
    const row = byNorm.get(normalised[i]);
    if (row && row.match_method !== "NO_COUNTERPART" && row.global_entity_id) {
      resolved.push({ term, ...row });
    } else {
      unresolved.push({
        term,
        reason: row
          ? "recognised, but the knowledge base has no researched data for it yet"
          : "not in the vocabulary crosswalk",
      });
    }
  });
  return { resolved, unresolved };
}

// Must match search/index.py and governance/vocabulary/build_crosswalk.py exactly,
// or a term resolved on the server will miss on the client.
export function normaliseTerm(text) {
  return String(text || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

// ─── Search ─────────────────────────────────────────────────────────────────
// Postgres FTS + trigram over the projection. Not a reimplementation of the
// Python SearchEngine's four-mode ladder — see docs/SEARCH_GUIDE.md — and the UI
// does not claim parity.
export async function searchKnowledge(query, { entityType, limit = 20 } = {}) {
  const q = String(query || "").trim();
  if (q.length < 2) return [];
  return safe(
    (sb) => {
      let sel = sb
        .from("kg_entities")
        .select("*")
        .is(LIVE, null)
        .ilike("canonical_name", `%${q.replace(/[%,]/g, "")}%`)
        .order("confidence_score", { ascending: false })
        .limit(limit);
      if (entityType) sel = sel.eq("entity_type", entityType);
      return sel;
    },
    []
  );
}

// ─── Availability ───────────────────────────────────────────────────────────
// Lets a page distinguish "the projection is empty" from "the projection is not
// deployed" — two situations that look identical and mean different things.
export async function knowledgeAvailable() {
  const rows = await safe(
    (sb) => sb.from("kg_entities").select("global_entity_id").limit(1),
    null
  );
  if (rows === null) return { available: false, reason: "SCHEMA_UNREACHABLE" };
  if (rows.length === 0) return { available: false, reason: "EMPTY" };
  return { available: true, reason: "OK" };
}

// ═══════════════════════════════════════════════════════════════════════════
// Step 3 — detail pages, explorer, and the type registry that binds them.
// ═══════════════════════════════════════════════════════════════════════════

// Entity ids are `vw:<entity_type_slug>:<canonical_name_slug>` and the builder
// generates them deterministically (knowledge_graph/build_graph.py:slug). A URL
// slug therefore reconstructs an id without a lookup — the detail pages need one
// query, not two, and a 404 costs nothing.
//
// Step 4 completed this map. It previously held 14 of the graph's 19 entity types,
// so `hrefFor()` sent ExportCountry, Soil, ClimateZone, State and Country — 50
// entities — to a search URL instead of a detail page. A knowledge network with
// dead ends in it is a list, so the remaining five are here.
export const TYPE_BY_URL = {
  district: "District",
  industry: "Industry",
  business: "BusinessOpportunity",
  msme: "MSME",
  skill: "Skill",
  scheme: "GovernmentScheme",
  crop: "Crop",
  certification: "Certification",
  institution: "Institution",
  provider: "TrainingProvider",
  machinery: "Machinery",
  market: "Market",
  bank: "FinancialInstitution",
  material: "RawMaterial",
  export: "ExportCountry",
  soil: "Soil",
  climate: "ClimateZone",
  state: "State",
  country: "Country",
};

export const URL_BY_TYPE = Object.fromEntries(
  Object.entries(TYPE_BY_URL).map(([url, type]) => [type, url])
);

//: entity_type -> the projected detail table and the column its rows are keyed by.
//: kg_businesses holds both kinds, keyed differently, because Package008 keys on
//: `business_id` and Package004 on `id` (see knowledge_sync/config.py).
const DETAIL_TABLE = {
  District: ["kg_districts", "dist_id"],
  Skill: ["kg_skills", "skill_id"],
  GovernmentScheme: ["kg_schemes", "scheme_id"],
  BusinessOpportunity: ["kg_businesses", "id"],
  MSME: ["kg_businesses", "business_id"],
  Industry: ["kg_industries", "category_id"],
  Crop: ["kg_agriculture", "crop_id"],
};

export const PACKAGE_LABELS = {
  Package001_Geography: "Package001 · Geography",
  Package002_Education: "Package002 · Education",
  Package003_Healthcare: "Package003 · Healthcare",
  Package004_Industries: "Package004 · Industries",
  Package005_Agriculture: "Package005 · Agriculture",
  Package006_Skills_and_Training: "Package006 · Skills & Training",
  Package007_Government_Schemes: "Package007 · Government Schemes",
  Package008_MSME: "Package008 · MSME",
};

/** `vw:skill:welding` -> `welding`. Returns "" for anything unexpected. */
export function slugOf(entityOrId) {
  const id = typeof entityOrId === "string" ? entityOrId : entityOrId?.global_entity_id;
  const parts = String(id || "").split(":");
  return parts.length === 3 ? parts[2] : "";
}

/** The canonical in-app link for an entity. Unknown types fall back to search. */
export function hrefFor(entity) {
  const url = URL_BY_TYPE[entity?.entity_type];
  const slug = slugOf(entity);
  if (!url || !slug) return `/knowledge?q=${encodeURIComponent(entity?.canonical_name || "")}`;
  return `/knowledge/${url}/${slug}`;
}

/** Rebuild the graph id from a URL pair. No query needed. */
export function entityIdFor(urlType, slug) {
  const type = TYPE_BY_URL[urlType];
  if (!type || !slug) return null;
  return `vw:${type.toLowerCase()}:${slug}`;
}

export async function getEntityBySlug(urlType, slug) {
  return getEntity(entityIdFor(urlType, slug));
}

/**
 * The rich attribute row behind an entity — investment range, eligibility, NSQF
 * level. `kg_entities` carries graph identity only; everything a user reads on a
 * detail page lives in the per-type table, joined on `package_local_id`.
 */
export async function getEntityDetail(entity) {
  const spec = DETAIL_TABLE[entity?.entity_type];
  if (!spec || !entity?.package_local_id) return null;
  const [table, keyColumn] = spec;
  const rows = await safe(
    (sb) =>
      sb.from(table).select("*").eq(keyColumn, entity.package_local_id).is(LIVE, null).limit(1),
    []
  );
  return rows[0] || null;
}

/**
 * Everything the graph connects to an entity, in both directions, grouped by the
 * neighbour's type. Two queries per direction, not one per edge.
 */
export async function getRelatedByType(globalEntityId, { limit = 120 } = {}) {
  const [out, incoming] = await Promise.all([
    getNeighbours(globalEntityId, { direction: "out", limit }),
    getNeighbours(globalEntityId, { direction: "in", limit }),
  ]);
  const grouped = {};
  for (const [pairs, direction] of [[out, "out"], [incoming, "in"]]) {
    for (const { entity, edge } of pairs) {
      const bucket = (grouped[entity.entity_type] ||= []);
      if (bucket.some((e) => e.global_entity_id === entity.global_entity_id)) continue;
      bucket.push({ ...entity, _via: edge.relationship_type, _edge: edge, _direction: direction });
    }
  }
  return grouped;
}

/**
 * One page of entities of a type, with a total count for the pager.
 * `count: "exact"` rides on the same request — a second round trip for a number
 * the first one can return is the kind of duplicate query the brief rules out.
 */
export async function listEntities(entityType, { page = 1, pageSize = 24, q = "" } = {}) {
  const from = Math.max(0, (page - 1) * pageSize);
  const term = String(q || "").trim().replace(/[%,]/g, "");
  const res = await safe(
    async (sb) => {
      let sel = sb
        .from("kg_entities")
        .select("*", { count: "exact" })
        .eq("entity_type", entityType)
        .is(LIVE, null);
      if (term.length >= 2) sel = sel.ilike("canonical_name", `%${term}%`);
      const out = await sel
        .order("confidence_score", { ascending: false })
        .order("canonical_name", { ascending: true })
        .range(from, from + pageSize - 1);
      return { data: { rows: out.data || [], total: out.count ?? 0 }, error: out.error };
    },
    { rows: [], total: 0 }
  );
  return res;
}

/** Per-type counts for the explorer index. One query, grouped client-side. */
export async function typeCounts() {
  const rows = await safe(
    (sb) => sb.from("kg_entities").select("entity_type").is(LIVE, null).limit(5000),
    []
  );
  const counts = {};
  for (const r of rows) counts[r.entity_type] = (counts[r.entity_type] || 0) + 1;
  return counts;
}

/**
 * One representative entity per type, highest confidence first — Step 4.
 *
 * Replaces the six hand-picked `featuredKnowledge` entries in
 * lib/static-knowledge.js on the homepage. Those named specific slugs, so they
 * showed the same six records forever and said nothing about what the platform
 * actually holds.
 *
 * ONE query for every type rather than one per type: `.in()` plus a client-side
 * first-per-type pass. Six round trips on the homepage would be six round trips
 * on every homepage render.
 */
export async function featuredByType(entityTypes, { perType = 1 } = {}) {
  const types = (entityTypes || []).filter(Boolean);
  if (types.length === 0) return [];

  const rows = await safe(
    (sb) =>
      sb
        .from("kg_entities")
        .select("*")
        .in("entity_type", types)
        .is(LIVE, null)
        .order("confidence_score", { ascending: false })
        .order("canonical_name", { ascending: true })
        .limit(types.length * perType * 12),
    []
  );

  const picked = new Map();
  for (const row of rows) {
    const bucket = picked.get(row.entity_type) || [];
    if (bucket.length >= perType) continue;
    bucket.push(row);
    picked.set(row.entity_type, bucket);
  }
  // Ordered by the caller's list, not by the database — the homepage decides
  // which package leads.
  return types.flatMap((t) => picked.get(t) || []);
}

/**
 * Newest rows in the projection, for the dashboard's "Latest knowledge" card.
 * Ordered by the sync's own timestamp so it reflects what actually landed, not
 * when a package was authored.
 */
export async function latestKnowledge({ limit = 8 } = {}) {
  return safe(
    (sb) =>
      sb
        .from("kg_entities")
        .select("*")
        .is(LIVE, null)
        .order("sync_updated_at", { ascending: false, nullsFirst: false })
        .limit(limit),
    []
  );
}
