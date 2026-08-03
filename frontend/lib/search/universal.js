// One index, one ranker, one set of rules — for every kind of content.
//
// WHAT THIS ADDS TO WHAT ALREADY WORKED
// -------------------------------------
// searchKnowledge() ranks the 647 researched entities and does it well. It
// could not see a research article, because articles are not in kg_entities;
// they are MDX files and rows in a different table. So the one thing
// ValueWeave has that a general search engine does not — original research —
// was the one thing its search box could not find. A student searching the
// exact subject of an article we had written got a page of database rows.
//
// This unions the sources declared in registry.js into one list of documents,
// attaches the aliases the packages already carry, and hands the whole thing
// to the SAME rankEntities. There is no second ranking, no merge of two
// separately-ordered lists, and no rule that applies to articles and not to
// districts.
//
// GROUPING IS A VIEW, NOT A SEARCH
// --------------------------------
// Results are ranked flat and grouped afterwards. Grouping first — running one
// search per category — would mean nine searches, nine rankings and a page
// whose sections cannot be compared with each other, because a score of 700 in
// one would not mean what 700 means in another.
//
// COST
// ----
// The knowledge index is fetched once per server process (lib/knowledge.js)
// and the article list once per process here. Ranking ~660 documents in memory
// is under a millisecond. Nothing about this adds a query per keystroke — that
// was the point of the in-memory ranker in the first place.

import { rankEntities, relatedSearches, matchTerm, editDistance } from "@/lib/knowledge-search.js";
import { resolveQuery, describeResolution, phoneticKey, normalise } from "./multilingual.js";
import { knowledgeIndex, hrefFor } from "@/lib/knowledge.js";
import { GROUPS, GROUP_LABEL, groupOf, kindLabel, loadRegisteredDocuments,
         PLANNED_SOURCES } from "./registry.js";
import ENTITY_ALIASES from "./vocabulary/entity_aliases.js";

export { GROUPS, GROUP_LABEL, groupOf, kindLabel, PLANNED_SOURCES };

//: Two characters, matching searchKnowledge's own floor. Below it the ranker
//: returns nothing, so anything less is a spinner with no answer behind it.
export const MIN_QUERY = 2;

let indexPromise = null;

/**
 * Every searchable document, from every live source.
 *
 * Cached for the life of the process and NOT cached when empty — the same rule
 * searchIndex() learned the hard way. A cold start or a paused project would
 * otherwise leave search permanently blank with no error anywhere.
 */
export async function universalIndex() {
  if (!indexPromise) {
    indexPromise = build().then((docs) => {
      if (!docs.length) indexPromise = null;
      return docs;
    });
  }
  return indexPromise;
}

async function build() {
  const [entities, registered] = await Promise.all([
    knowledgeIndex(),
    loadRegisteredDocuments(),
  ]);

  const knowledge = (entities || []).map((entity) => {
    const aliases = ENTITY_ALIASES[entity.global_entity_id];
    return aliases ? { ...entity, _aliases: aliases, _href: hrefFor(entity) }
                   : { ...entity, _href: hrefFor(entity) };
  });

  return [...knowledge, ...registered];
}

/** Drop the cache. Only for tests — a process should build this once. */
export function resetUniversalIndex() {
  indexPromise = null;
}

/**
 * Rank everything against a query.
 *
 * `boost` is passed straight through to rankEntities — the personalisation
 * seam described there. Nothing supplies one today.
 */
export async function universalSearch(query, { limit = 40, entityType, boost } = {}) {
  const q = String(query || "").trim();
  if (q.length < MIN_QUERY) return [];
  const index = await universalIndex();
  if (!index.length) return [];
  return rankEntities(index, q, { limit, entityType, boost });
}

/**
 * The same results, arranged the way a reader reads them.
 *
 * A flat list of twenty-four rows mixing districts, skills, schemes and
 * articles asks the reader to do the sorting. Nine labelled sections in a
 * fixed order lets them jump: someone who wanted a scheme reads one heading
 * and stops.
 *
 * Order between groups follows the best result in each, not the fixed list —
 * a search for "Medak" must lead with Places, and a search for "PMEGP" with
 * Government support, and no static ordering can be right for both. The fixed
 * order in registry.js breaks ties, so two groups whose best hit is equally
 * good appear in the same order every time.
 */
export function groupResults(rows, { perGroup = 6 } = {}) {
  const buckets = new Map();
  for (const row of rows || []) {
    const id = groupOf(row.entity_type);
    if (!buckets.has(id)) buckets.set(id, []);
    buckets.get(id).push(row);
  }

  const rank = Object.fromEntries(GROUPS.map((g, i) => [g.id, i]));
  return [...buckets.entries()]
    .map(([id, items]) => ({
      id,
      label: GROUP_LABEL[id] || id,
      total: items.length,
      items: items.slice(0, perGroup),
      best: items[0]?._score || 0,
    }))
    .sort((a, b) => b.best - a.best || (rank[a.id] ?? 99) - (rank[b.id] ?? 99));
}

/** Search, then group. What the results page calls. */
export async function searchGrouped(query, { limit = 60, perGroup = 6, boost } = {}) {
  const rows = await universalSearch(query, { limit, boost });
  return { rows, groups: groupResults(rows, { perGroup }) };
}

// ─── Live suggestions ───────────────────────────────────────────────────────

//: A suggestion list is read at a glance while someone is still typing. Eight
//: rows is about a phone screen; more is a wall that hides the Search button.
const SUGGEST_LIMIT = 8;

/**
 * What to show under the box after two characters.
 *
 * Deliberately not the same as the results page. A results page answers the
 * question; a suggestion list helps the reader finish asking it, so it is
 * short, it is grouped only enough to be scannable, and it carries the
 * highlight offsets the UI needs rather than making the client re-derive them.
 */
export async function suggest(query, { limit = SUGGEST_LIMIT, boost } = {}) {
  const q = String(query || "").trim();
  const resolution = resolveQuery(q);
  const ranked = await universalSearch(q, { limit, boost });

  // Ordered by score WITHIN a group, and the groups themselves by their best
  // hit. Ranking flat and printing a heading whenever the group changes gave
  // "Business opportunities / Skills / Business opportunities" down one panel
  // — three headings for two categories, which reads as a rendering fault and
  // makes the list harder to scan than no headings at all.
  const rows = groupResults(ranked, { perGroup: limit }).flatMap((g) => g.items);

  return {
    query: q,
    // "Showing results for …" when we translated something the reader cannot
    // see us translating. Null for a plain English query.
    resolved: describeResolution(resolution),
    items: rows.map((row) => ({
      id: row.global_entity_id,
      name: row.canonical_name,
      href: row._href || hrefFor(row),
      group: groupOf(row.entity_type),
      groupLabel: GROUP_LABEL[groupOf(row.entity_type)] || "",
      kind: kindLabel(row.entity_type),
      via: row._via || null,
      match: row._match,
    })),
  };
}

// ─── When there is nothing ──────────────────────────────────────────────────

//: Close enough to be worth offering as a correction. Three edits on a long
//: word is generous; on a short one it would suggest a different word
//: entirely, which is why the budget scales.
function correctionBudget(term) {
  if (term.length <= 4) return 0;
  if (term.length <= 7) return 1;
  return 2;
}

/**
 * "Did you mean …" — names from the corpus that are nearly what was typed.
 *
 * Two ways in, because they catch different mistakes. Edit distance catches a
 * slip of the finger; the phonetic key catches somebody spelling by ear, which
 * on this platform is the more common of the two and the one no typo budget
 * can reach.
 *
 * Only names we hold, so following a suggestion can never land on a second
 * empty page — the rule Phase 4 set for every empty state.
 */
export function didYouMean(index, query, { limit = 4 } = {}) {
  const q = normalise(query);
  if (q.length < 3) return [];
  const key = phoneticKey(q);
  const scored = [];

  for (const doc of index || []) {
    const name = doc.canonical_name;
    if (!name) continue;
    const words = normalise(name).split(" ");
    let best = null;

    for (const word of words) {
      if (word.length < 3) continue;
      const budget = Math.min(correctionBudget(q), correctionBudget(word));
      if (budget > 0) {
        const distance = editDistance(q, word, budget);
        if (distance <= budget) best = Math.min(best ?? 9, distance);
      }
      if (key && phoneticKey(word) === key) best = Math.min(best ?? 9, 0.5);
    }
    if (best !== null) scored.push({ doc, distance: best });
  }

  scored.sort((a, b) => a.distance - b.distance ||
                        a.doc.canonical_name.length - b.doc.canonical_name.length);

  const seen = new Set();
  const out = [];
  for (const { doc } of scored) {
    const name = doc.canonical_name;
    if (seen.has(name.toLowerCase())) continue;
    seen.add(name.toLowerCase());
    out.push({ id: doc.global_entity_id, name,
               href: doc._href || hrefFor(doc), kind: kindLabel(doc.entity_type) });
    if (out.length >= limit) break;
  }
  return out;
}

/**
 * Something to read when the query itself found nothing.
 *
 * The rule this follows is the one from Phase 4, and the question behind it is
 * the one the brief asks: if a mentor were sitting here, what would they say
 * next? Not "no results". They would say "we do not have that — here is what
 * we do have near it, and here is how to ask us for it".
 *
 * Everything offered is checked against the index first. A suggestion that
 * leads to another empty page is a second dead end and worse than silence.
 */
export async function guidance(query, { perGroup = 3, groups = 4, exclude = [] } = {}) {
  const index = await universalIndex();
  const q = String(query || "").trim();
  // Whatever the page is already showing. Offering "Cattle Dung and Farm
  // Waste" as a RELATED result directly under the one result, which was that
  // same row, is the page arguing with itself.
  const shown = new Set(exclude);

  // The terms the query expanded into that actually find something. This is
  // the existing relatedSearches, which was written for exactly this and had
  // one caller.
  const terms = relatedSearches(index, q, { limit: 8 });

  // Everything those terms reach, grouped. Not "related to the query" in the
  // abstract — related through a term we can name, so each section can say
  // which word it came from.
  const reached = new Map();
  for (const term of terms) {
    for (const doc of index) {
      if (reached.has(doc.global_entity_id) || shown.has(doc.global_entity_id)) continue;
      if (!matchTerm(normalise(term), doc.canonical_name)) continue;
      reached.set(doc.global_entity_id, { ...doc, _via: term, _score: 1 });
    }
  }

  const related = groupResults([...reached.values()], { perGroup })
    .slice(0, groups)
    .filter((group) => group.items.length > 0);

  return {
    query: q,
    resolved: describeResolution(resolveQuery(q)),
    didYouMean: didYouMean(index, q).filter((hit) => !shown.has(hit.id)),
    terms,
    related,
    // Named so the page can say "mentors are coming" rather than showing a
    // reader nothing and letting them conclude the platform is empty.
    planned: PLANNED_SOURCES.map((s) => s.label),
  };
}
