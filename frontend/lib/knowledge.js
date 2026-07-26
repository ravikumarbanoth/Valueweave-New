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
