// What ValueWeave remembers about a first-time visitor, and what it does with it.
//
// WHY THIS EXISTS
// ---------------
// Phase 6 gave the homepage a first question — "Or tell us who you are" — and
// six answers, each opening a curated `/start/<audience>` page. It left a note
// in `app/start/[audience]/page.js` saying the routing and the copy were done
// and "Phase 9 turns the same six into an onboarding flow. This is the routing
// and the copy; that adds the memory."
//
// This is the memory. Before it, answering the question was worth exactly one
// page view: navigate anywhere else and the platform had forgotten, so a
// returning visitor was asked who they were every single time. Being asked the
// same question by something that claims to know you is the specific way
// software feels like software rather than like a person who remembers.
//
// WHY LOCALSTORAGE AND NOT THE PROFILE TABLE
// -------------------------------------------
// The whole point of the audience row is that it works before anybody signs
// in — it is the one path into real knowledge that costs a first-generation
// student nothing. Writing this to `profiles` would put it behind Google
// OAuth and defeat the thing it exists to serve. A signed-in reader already
// has `profiles.looking_for`, which `/onboarding` writes; this is the
// anonymous half and it deliberately does not sync. One is an account
// setting; this is a hint that any visitor can give and withdraw in one tap.
//
// Nothing here is personal data. It is one of six public slugs, chosen by the
// reader, readable only by this origin, and `forget()` is a real delete.
//
// WHAT IT IS NOT
// --------------
// Not a filter. A remembered audience never removes a result, never hides a
// category and never changes what a search finds — only the order within a
// tier of equally-good matches. A student who searches "turmeric" still gets
// turmeric. See `boostFor` for why that is arithmetic and not a promise.

import { AUDIENCES, AUDIENCE_BY_SLUG } from "@/lib/audiences";
import { TYPE_BY_URL } from "@/lib/knowledge";

//: Namespaced like the existing `vw_intent` that `/get-started` writes, so
//: everything this origin stores is greppable by one prefix.
export const STORAGE_KEY = "vw_audience";

/**
 * Which entity types each audience came here for.
 *
 * DERIVED, NOT DECLARED. Every audience already names its starting points in
 * `lib/audiences.js` as `/knowledge?type=<slug>` links, and those were chosen
 * by hand against categories the graph actually holds. Reading the affinity
 * out of them means the ranking can never drift from the curated page: change
 * a start link and the boost follows it. A second hand-maintained list would
 * have gone stale the first time somebody edited one and not the other.
 */
export const AFFINITY = Object.fromEntries(
  AUDIENCES.map((audience) => [
    audience.slug,
    new Set(
      audience.starts
        .map((start) => {
          const query = String(start.href).split("?")[1] || "";
          return new URLSearchParams(query).get("type");
        })
        .filter(Boolean)
        .map((urlType) => TYPE_BY_URL[urlType])
        .filter(Boolean)
    ),
  ])
);

/**
 * How much a preferred type is worth.
 *
 * The ranker's tiers are 1000 / 700 / 500 / 300 / 220 / 120 (EXACT, PREFIX,
 * WORD, CONTAINS, RELATED, FUZZY). The narrowest ratio between adjacent tiers
 * is 300/220 ≈ 1.364, so any multiplier strictly below that CANNOT lift a
 * weaker kind of match above a stronger one — it can only reorder entities
 * that matched the query equally well.
 *
 * That bound is the whole safety argument for personalising a search at all,
 * so it is asserted in tests/test_journey.py against the real tier constants
 * rather than trusted to this comment.
 */
export const PREFERRED_WEIGHT = 1.25;

/**
 * A `boost` function for `rankEntities`, or undefined for an unknown audience.
 *
 * Undefined rather than `() => 1` on purpose: the ranker skips the multiply
 * entirely when there is no boost, so an anonymous visitor pays nothing and
 * gets byte-identical results to before this file existed.
 */
export function boostFor(slug) {
  const preferred = AFFINITY[slug];
  if (!preferred || preferred.size === 0) return undefined;
  return (entity) => (preferred.has(entity?.entity_type) ? PREFERRED_WEIGHT : 1);
}

/** True for one of the six slugs, false for anything else. */
export function isAudience(slug) {
  return Boolean(slug) && Object.hasOwn(AUDIENCE_BY_SLUG, slug);
}

/**
 * Who this visitor said they were, or null.
 *
 * Null on the server, null when storage is unavailable, and null for a slug
 * that is no longer one of the six — so renaming an audience degrades to "ask
 * again" rather than to a broken page.
 */
export function recall() {
  if (typeof window === "undefined") return null;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return isAudience(stored) ? stored : null;
  } catch {
    // Safari private mode and "block all cookies" both throw on access rather
    // than returning null. A visitor with storage off should get the ordinary
    // anonymous site, not an error.
    return null;
  }
}

/** Record the answer. Returns whether it stuck. */
export function remember(slug) {
  if (typeof window === "undefined" || !isAudience(slug)) return false;
  try {
    window.localStorage.setItem(STORAGE_KEY, slug);
    return true;
  } catch {
    // Quota or a blocked store. The click still navigated to the right page;
    // only the memory is lost, which is the degradation this whole module is
    // designed to survive.
    return false;
  }
}

/** Forget. A real delete, wired to a visible control — see HomeHeroSearch. */
export function forget() {
  if (typeof window === "undefined") return false;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
    return true;
  } catch {
    return false;
  }
}

/** The full audience record for the remembered slug, or null. */
export function recallAudience() {
  const slug = recall();
  return slug ? AUDIENCE_BY_SLUG[slug] : null;
}
