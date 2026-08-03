// Ranking. Pure functions over a list of entities — no network, no client.
//
// WHY THIS EXISTS RATHER THAN A BETTER SQL QUERY
// ----------------------------------------------
// The three things search was missing cannot be expressed in `ilike`:
//
//   relevance    `order by confidence_score` put "Retail & Local Commerce" above
//                "Artificial Intelligence" for the query "AI", because ordering
//                had nothing to do with the query.
//   word sense   `%ai%` matches Maize, Painting, Retail, Training. 31 of the 46
//                hits for "AI" were the letters a-i inside an unrelated word.
//   typos        `ilike` has no notion of distance. "electrican" returned zero.
//
// Trigram or full-text would fix the last two, and both need an extension, an
// index and a migration — schema changes this phase excludes. The corpus is 647
// entities, so ranking them in memory is neither slow nor clever; it is just the
// proportionate tool. It also removes a network round trip per keystroke, which
// on a Tier-2 mobile connection is the difference between a search box that
// feels alive and one that feels broken.
//
// THE LADDER IS THE REPOSITORY'S OWN
// ----------------------------------
// EXACT / PREFIX / ALIAS / FUZZY are the four modes in search/engine.py, with
// the same ordering rule — fuzzy always last, so an approximate hit can never
// displace a real one. This is that ladder applied to the projection, not a
// second search design.
import { expandQuery, normaliseTerm } from "./search-vocabulary.js";

export const MATCH = {
  EXACT: "EXACT",         // the whole name is what they typed
  PREFIX: "PREFIX",       // the name begins with it
  WORD: "WORD",           // a word inside the name begins with it
  CONTAINS: "CONTAINS",   // it appears somewhere in the name
  RELATED: "RELATED",     // reached through the vocabulary, not typed
  FUZZY: "FUZZY",         // close enough to be a typo
};

const SCORE = {
  [MATCH.EXACT]: 1000,
  [MATCH.PREFIX]: 700,
  [MATCH.WORD]: 500,
  [MATCH.CONTAINS]: 300,
  [MATCH.RELATED]: 220,
  [MATCH.FUZZY]: 120,
};

//: Below this length, CONTAINS is not allowed — a two-letter query has to land
//: on a word boundary. This single rule is what stops "AI" matching Maize.
const MIN_SUBSTRING_LENGTH = 4;

function words(text) {
  return normaliseTerm(text).split(" ").filter(Boolean);
}

/**
 * Levenshtein distance, capped.
 *
 * Bails out as soon as the best possible result exceeds `max`, so the common
 * case — two words that are nothing like each other — costs one row of the
 * matrix rather than all of them.
 */
export function editDistance(a, b, max = 2) {
  if (a === b) return 0;
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i += 1) {
    const row = [i];
    let best = i;
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      row[j] = Math.min(row[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
      if (row[j] < best) best = row[j];
    }
    if (best > max) return max + 1;
    prev = row;
  }
  return prev[b.length];
}

//: Longer words tolerate more typos; short ones tolerate none. "ai" must not be
//: one edit from "at", "an" or "ap".
function typoBudget(term) {
  if (term.length <= 4) return 0;
  if (term.length <= 7) return 1;
  return 2;
}

//: "GovernmentScheme" -> "government scheme". A student types the words, not
//: the identifier, and until now "schemes" matched no entity because no entity
//: is NAMED "government scheme" — it is a TYPE. Four expansions pointed at
//: nothing for exactly this reason.
export function humaniseType(entityType) {
  return normaliseTerm(String(entityType || "").replace(/([a-z])([A-Z])/g, "$1 $2"));
}

/** How well one search term matches one name. `null` when it does not. */
export function matchTerm(term, name) {
  const n = normaliseTerm(name);
  if (!n || !term) return null;

  if (n === term) return MATCH.EXACT;
  if (n.startsWith(term)) return MATCH.PREFIX;

  const nameWords = n.split(" ");
  if (nameWords.some((w) => w.startsWith(term))) return MATCH.WORD;

  // Multi-word terms are allowed to match loosely: "tiles fixing" should reach
  // "Tiles Fixing (Tile Mason)" even though the words are not adjacent there.
  const termWords = term.split(" ").filter((w) => w.length > 2);
  if (termWords.length > 1 && termWords.every((t) => n.includes(t))) {
    return MATCH.WORD;
  }

  if (term.length >= MIN_SUBSTRING_LENGTH && n.includes(term)) {
    return MATCH.CONTAINS;
  }

  const budget = typoBudget(term);
  if (budget > 0 && nameWords.some((w) => editDistance(term, w, budget) <= budget)) {
    return MATCH.FUZZY;
  }
  return null;
}

//: An alias hit is worth a little less than the same rung on the name itself.
//: "Battery" appearing in an article's keyword list is real evidence and
//: weaker evidence than an entity actually called Battery Modules.
const ALIAS_WEIGHT = 0.9;

/**
 * Score one entity against an expanded query.
 *
 * Returns `{score, match, via}` or null. `via` is the term that matched when it
 * was not the one typed — the UI uses it to say "matched: electrical wiring",
 * so a result that looks unrelated can explain itself.
 *
 * `entity._aliases` — optional, absent on every knowledge entity until
 * something attaches it — is a list of other short strings this thing answers
 * to: a scheme's short name, a research article's keywords, the Chinese
 * concept a business opportunity was adapted from. Matched after the name and
 * before the type, so it can rescue a query the title does not contain and
 * can never displace a title that does.
 */
export function scoreEntity(entity, expanded) {
  const name = entity?.canonical_name;
  if (!name) return null;
  const typeLabel = humaniseType(entity.entity_type);
  const aliases = Array.isArray(entity._aliases) ? entity._aliases : [];

  let best = null;
  for (const { term, weight, kind: source } of expanded) {
    // Name first. A type match is a whole-category hit — "schemes" meaning
    // every GovernmentScheme — so it is worth finding, but it must never beat
    // an entity whose own name matches, or searching "skill" would bury
    // "Skill Loan Scheme" under 45 skills.
    let kind = matchTerm(term, name);
    let byType = false;
    let byAlias = null;

    if (!kind) {
      for (const alias of aliases) {
        const hit = matchTerm(term, alias);
        if (hit) { kind = hit; byAlias = alias; break; }
      }
    }
    if (!kind && typeLabel && (typeLabel === term || matchTerm(term, typeLabel) === MATCH.EXACT)) {
      kind = MATCH.RELATED;
      byType = true;
    }
    if (!kind) continue;

    // An ACRONYM expansion keeps the rung it earned — "PMEGP" and "Prime
    // Minister's Employment Generation Programme" are the same thing, so an
    // exact hit on the long form is an exact hit. Demoting it put the scheme
    // below a financial instrument that merely started with the letters.
    //
    // A RELATED expansion is a different thing nearby, and is always reported
    // as such however well it matched, so it can never outrank what was typed.
    const effective =
      !byType && (source === "typed" || source === "acronym") ? kind : MATCH.RELATED;
    const score = SCORE[effective] * weight * (byAlias ? ALIAS_WEIGHT : 1);

    if (!best || score > best.score) {
      best = {
        score,
        match: effective,
        // What to tell the reader. The alias beats the search term here: "PMEGP"
        // is a more useful explanation of why a scheme is in the list than the
        // twelve words it stands for.
        via: byAlias || (source === "typed" && !byType ? null : term),
      };
    }
  }
  if (!best) return null;

  // Confidence breaks ties only. Scaled to stay under the gap between rungs, so
  // a well-sourced CONTAINS can never overtake a WORD.
  const confidence = Number(entity.confidence_score) || 0;
  return { ...best, score: best.score + Math.min(confidence, 100) * 0.5 };
}

/**
 * Rank entities against a raw query.
 *
 * Each result carries `_match`, `_score` and `_via` so the UI can group and
 * explain. Nothing else about the entity is altered.
 *
 * THE `boost` SEAM — PERSONALISATION, NOT YET IMPLEMENTED
 * ------------------------------------------------------
 * `boost(entity)` returns a multiplier and defaults to 1, which is exactly
 * today's behaviour. It exists so that ranking differently for a student, an
 * entrepreneur, an investor, a farmer or a working professional is a function
 * passed in at the call site rather than a rewrite of this file.
 *
 * It is a multiplier and not an additive bonus deliberately: adding points
 * could lift a FUZZY hit above an EXACT one and make a personalised search
 * return the wrong thing confidently, which is the failure mode that would
 * cost the most trust. Scaling preserves the ladder — a preferred CONTAINS
 * still cannot overtake a WORD unless the boost exceeds the gap between rungs,
 * and the rungs are far enough apart that a sane boost cannot.
 *
 * Nothing calls it with a boost today. When something does, that will be a
 * change to a caller, and this function will not need to know who the reader
 * is — which is the only way the seam stays honest.
 */
export function rankEntities(entities, query, { limit = 24, entityType, boost } = {}) {
  const expanded = expandQuery(query);
  if (!expanded.length) return [];

  const out = [];
  for (const entity of entities || []) {
    if (entityType && entity.entity_type !== entityType) continue;
    const scored = scoreEntity(entity, expanded);
    if (!scored) continue;
    const weight = boost ? Number(boost(entity)) || 1 : 1;
    out.push({
      ...entity,
      _match: scored.match,
      _score: scored.score * weight,
      _via: scored.via,
    });
  }

  out.sort((a, b) =>
    b._score - a._score ||
    String(a.canonical_name).length - String(b.canonical_name).length ||
    String(a.canonical_name).localeCompare(String(b.canonical_name)));

  return diversify(out, limit);
}

//: At most this many results may come from any one expansion term.
const MAX_PER_VIA = 3;

/**
 * Keep the list varied.
 *
 * One broad expansion can otherwise fill the page: "dairy" reached "agriculture"
 * and returned twenty rows all named "Agriculture: <sector>", which reads as a
 * table dump rather than an answer. Directly-typed matches are never capped —
 * if someone searches "solar" and we hold nine solar entities, they should see
 * them.
 *
 * Overflow is appended after the diversified set rather than discarded, so the
 * limit is still filled when there is nothing else to show.
 */
export function diversify(ranked, limit, maxPerVia = MAX_PER_VIA) {
  const kept = [];
  const overflow = [];
  const seen = new Map();
  for (const row of ranked) {
    if (!row._via) { kept.push(row); continue; }
    const n = (seen.get(row._via) || 0) + 1;
    seen.set(row._via, n);
    (n <= maxPerVia ? kept : overflow).push(row);
  }
  return [...kept, ...overflow].slice(0, limit);
}

/**
 * Terms the user could try next, drawn from what their query expanded into.
 *
 * Only terms that would actually return something — a suggestion that leads to
 * an empty page is worse than no suggestion.
 */
export function relatedSearches(entities, query, { limit = 6 } = {}) {
  const typed = normaliseTerm(query);
  const out = [];
  for (const { term, weight } of expandQuery(query)) {
    if (weight === 1 || term === typed || out.length >= limit) continue;
    if ((entities || []).some((e) => matchTerm(term, e.canonical_name))) out.push(term);
  }
  return out;
}
