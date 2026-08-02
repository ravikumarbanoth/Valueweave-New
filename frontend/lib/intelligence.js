// ValueWeave — User Intelligence data access (Platform v3.0, Step 2).
//
// Reads the `user_intelligence` schema written by the Python engine (Step 1.5).
// The engine is not called from here and is not reimplemented here: it writes five
// tables, this file reads them. That is the whole integration, and it is why there
// is no duplicate rule logic in JavaScript.
//
// RLS DOES THE AUTHORISATION
// --------------------------
// Every table's policy is `auth.uid() = user_id`, with no admin exception. A
// signed-in user reads their own intelligence and nothing else, enforced by
// Postgres rather than by a filter this file could forget. Passing a userId here
// that is not the caller's returns nothing.
//
// DEGRADES, NEVER THROWS
// ----------------------
// The schema is not applied to any database yet, so every function returns null or
// [] today and every component renders its "not computed yet" state. `reason`
// distinguishes NOT_DEPLOYED from NOT_COMPUTED — a UI must not say "we have
// nothing to tell you" when the truth is "nobody has run the engine".

import { createClient } from "@supabase/supabase-js";

export const INTELLIGENCE_SCHEMA = "user_intelligence";

// Must match user_intelligence/__init__.py RULES_VERSION. Rows are keyed on it, so
// a mismatch means reading nothing rather than reading stale numbers.
export const RULES_VERSION = "1.0.0";

// Mirrors user_intelligence/rules.py. The three are different claims and a UI
// should say three different things.
export const STATUS = {
  APPLIED: "APPLIED",       // computed, with signal
  NO_SIGNAL: "NO_SIGNAL",   // computed; the answer is nothing
  UNAVAILABLE: "UNAVAILABLE", // could not compute — an input is missing
};

export const NO_DATA_SOURCE = "NO_DATA_SOURCE";

function intelligenceClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  try {
    return createClient(url, key, { db: { schema: INTELLIGENCE_SCHEMA } });
  } catch {
    return null;
  }
}

async function safe(run, fallback) {
  try {
    const sb = intelligenceClient();
    if (!sb) return fallback;
    const { data, error } = await run(sb);
    if (error) return fallback;
    return data ?? fallback;
  } catch {
    return fallback;
  }
}

async function one(table, userId) {
  if (!userId) return null;
  const rows = await safe(
    (sb) =>
      sb
        .from(table)
        .select("*")
        .eq("user_id", userId)
        .eq("rules_version", RULES_VERSION)
        .limit(1),
    []
  );
  return rows[0] || null;
}

// ─── The five tables ────────────────────────────────────────────────────────
export const getSkillProfile = (userId) => one("user_skill_profile", userId);
export const getBusinessProfile = (userId) => one("user_business_profile", userId);
export const getLearningProfile = (userId) => one("user_learning_profile", userId);
export const getActivitySummary = (userId) => one("user_activity_summary", userId);

export async function getRecommendations(userId, { category, limit = 20 } = {}) {
  if (!userId) return [];
  return safe(
    (sb) => {
      let q = sb
        .from("user_recommendations")
        .select("*")
        .eq("user_id", userId)
        .eq("rules_version", RULES_VERSION)
        .order("rank", { ascending: true })
        .limit(limit);
      if (category) q = q.eq("category", category);
      return q;
    },
    []
  );
}

// One round trip for a whole dashboard rather than one per rail.
export async function getRecommendationsByCategory(userId, categories, { perCategory = 8 } = {}) {
  const rows = await getRecommendations(userId, { limit: 200 });
  const out = {};
  for (const key of categories) out[key] = [];
  for (const row of rows) {
    if (!(row.category in out)) continue;
    if (out[row.category].length < perCategory) out[row.category].push(row);
  }
  return out;
}

// ─── State, not just data ───────────────────────────────────────────────────
// Lets a page tell three situations apart. They render identically if you do not.
export async function intelligenceState(userId) {
  const rows = await safe(
    (sb) => sb.from("user_activity_summary").select("user_id").limit(1),
    null
  );
  // `reason` is for us; `message` is for the reader. They used to be the same
  // sentence, which is how "not switched on for this deployment yet" ended up on
  // a student's dashboard. The distinction between the two cases still drives
  // what the page does — NOT_DEPLOYED hides the block, NOT_COMPUTED invites the
  // user to finish their profile — it just no longer drives what they read.
  if (rows === null) {
    return {
      available: false,
      reason: "NOT_DEPLOYED",
      message: "We are still setting up personal suggestions. Check back soon.",
    };
  }
  const mine = await getActivitySummary(userId);
  if (!mine) {
    return {
      available: false,
      reason: "NOT_COMPUTED",
      message:
        "Add your skills and your district and we will suggest businesses, " +
        "courses and schemes that fit you.",
    };
  }
  return { available: true, reason: "OK", summary: mine };
}

// ─── Presentation helpers ───────────────────────────────────────────────────
// A score of null means "could not compute" and must never render as 0.
export function scoreLabel(score, status) {
  if (status === STATUS.UNAVAILABLE || score === null || score === undefined) return "—";
  return String(Math.round(Number(score)));
}

export function scoreTone(score, status) {
  if (status === STATUS.UNAVAILABLE || score === null || score === undefined) {
    return "bg-stone-100 text-stone-500 border-stone-200";
  }
  const n = Number(score);
  if (n >= 70) return "bg-teal-100 text-teal-800 border-teal-200";
  if (n >= 40) return "bg-amber-100 text-amber-800 border-amber-200";
  return "bg-stone-100 text-stone-600 border-stone-200";
}

// Matches the Knowledge Engine's ConfidenceTier so users see one vocabulary.
/**
 * How strong the source behind a fact is.
 *
 * PX PHASE 3. These labels used to be "Government-grade source", "Portal or
 * news source" and "Community or qualitative" — a taxonomy written for whoever
 * scores the research. "Community or qualitative" in particular tells a reader
 * nothing except that they have not understood something.
 *
 * They now name the source in the words a reader would use for it. The bands
 * and the thresholds are unchanged, so nothing about the scoring moved — only
 * what the chip says.
 */
export function confidenceBand(confidence) {
  const n = Number(confidence) || 0;
  if (n >= 70) return { label: "Official source", tone: "bg-teal-50 text-teal-700 border-teal-100" };
  if (n >= 55) return { label: "Published source", tone: "bg-amber-50 text-amber-700 border-amber-100" };
  if (n > 0) return { label: "Local knowledge", tone: "bg-stone-50 text-stone-600 border-stone-200" };
  return { label: "Written by our team", tone: "bg-stone-50 text-stone-500 border-stone-200" };
}

export const SCORE_LABELS = {
  skill_profile: "Skill Profile",
  business_readiness: "Business Readiness",
  learning_roadmap: "Learning Roadmap",
  district_opportunity: "District Opportunity",
  collaboration_score: "Collaboration",
  ai_readiness: "AI Readiness",
  funding_readiness: "Funding Readiness",
  startup_readiness: "Startup Readiness",
};

export const CATEGORY_LABELS = {
  business_ideas: "Business Ideas",
  government_schemes: "Government Schemes",
  courses: "Courses",
  research: "Research",
  mentors: "Mentors",
  collaborators: "Collaborators",
  events: "Events",
  markets: "Markets",
  msmes: "MSMEs",
  industries: "Industries",
};
