// What a person means, versus what we happened to name the row.
//
// THE PROBLEM THIS SOLVES
// -----------------------
// Search was `ilike '%query%'` on canonical_name. Measured against the real 647
// entities:
//
//   "Electrician"  ->  2 results   (misses electrical contracting, wireman work,
//                                   panel manufacturing, solar installation)
//   "Tile Mason"   ->  1 result    (misses masonry, flooring, POP, civil work)
//   "PMEGP"        ->  1 result    (misses the scheme itself — it is stored as
//                                   "Prime Minister's Employment Generation
//                                   Programme")
//   "Dairy"        ->  0 results
//   "AI"           -> 46 results, 15 of them actually about AI. The rest matched
//                     the letters a-i inside Maize, Painting, Retail, Training.
//
// A student typing "electrician" is not asking for rows whose title contains
// that string. They are asking what an electrician can learn, earn, start and
// apply for. The graph holds all of it under different words.
//
// WHY A CURATED MAP AND NOT AN EMBEDDING MODEL
// --------------------------------------------
// An embedding index would need a vector column, an extension, a build step and
// a model — schema and pipeline changes this phase explicitly excludes. It would
// also be worse at the thing that actually fails here: "PMEGP" and "ITI" are
// acronyms, not semantic neighbours, and no general-purpose model reliably maps
// "avakaya" to pickle-making. This is a domain vocabulary for a domain corpus.
//
// Every right-hand term below was checked against the live graph — an expansion
// that matches nothing is a lie that costs a query. tests/test_search_experience
// asserts that.
//
// WHERE THE OTHER TWO LANGUAGES LIVE
// ----------------------------------
// This table is English. Telugu script and Tanglish are resolved in
// lib/search/multilingual.js against lib/search/vocabulary/concepts.js, and
// the result is merged into `expandQuery` below as though it had been typed in
// English. Nothing about the tables here changed to make that work, and
// nothing downstream of `expandQuery` knows there is more than one language.

import { resolveQuery } from "./search/multilingual.js";

//: Query term -> terms to also search for. Matched on whole words after
//: normalisation, so "ai" expands and "maize" does not.
//
//: Kept flat and one-directional on purpose. A symmetric graph reads more
//: elegantly and behaves worse: "business" should pull in "entrepreneurship",
//: but a search for "entrepreneurship" should not drag in every business row.
export const EXPANSIONS = {
  // ── Electrical trades ────────────────────────────────────────────────────
  electrician: ["electrical", "wiring", "wireman", "domestic wiring",
                "power distribution", "electrical panel", "industrial electrician"],
  electrical: ["electrician", "wiring", "wireman", "panel", "power distribution"],
  wiring: ["electrician", "electrical", "wireman"],
  wireman: ["electrician", "electrical", "wiring"],

  // ── Construction and finishing trades ────────────────────────────────────
  "tile mason": ["tiles fixing", "masonry", "brickwork", "construction"],
  tile: ["tiles fixing", "masonry", "brickwork"],
  tiles: ["tiles fixing", "masonry", "brickwork"],
  mason: ["masonry", "brickwork", "construction"],
  masonry: ["mason", "brickwork", "construction", "tiles fixing"],
  flooring: ["tiles fixing", "masonry", "pop works", "false ceiling"],
  // No "granite"/"marble"/"civil"/"flooring" entries: the graph holds no such
  // entity, and an expansion that matches nothing costs a query and returns
  // nothing. test_every_expansion_target_exists_in_the_graph enforces this.


  plumber: ["plumbing"],
  carpenter: ["carpentry"],
  painter: ["painting"],
  welder: ["welding", "fabrication", "metal fabrication"],

  // ── AI and technology ────────────────────────────────────────────────────
  ai: ["artificial intelligence", "machine learning", "ai tooling", "automation",
       "robotics", "ai model training", "chatbot", "computer vision"],
  ml: ["machine learning", "artificial intelligence", "ai model training"],
  chatgpt: ["artificial intelligence", "generative ai", "chatbot", "ai tooling"],
  "prompt engineering": ["artificial intelligence", "generative ai", "ai tooling"],
  automation: ["robotics", "industrial automation", "ai tooling", "workflow"],
  robot: ["robotics", "industrial robotics", "automation"],
  coding: ["programming", "software", "web development", "python"],
  programmer: ["programming", "software", "python", "web development"],
  developer: ["web development", "software", "mobile app development"],
  it: ["information technology", "software", "computing"],

  // ── Schemes, finance, entrepreneurship ───────────────────────────────────
  pmegp: ["employment generation", "prime minister", "government scheme",
          "subsidy", "msme", "loan"],
  mudra: ["loan", "government scheme", "credit", "msme"],
  "pm kisan": ["kisan samman", "farmer", "government scheme"],
  scheme: ["government scheme", "subsidy", "yojana"],
  schemes: ["government scheme", "subsidy", "yojana"],
  yojana: ["government scheme", "subsidy"],
  subsidy: ["government scheme", "margin money", "loan"],
  loan: ["credit", "mudra", "bank", "finance", "margin money"],
  finance: ["bank", "loan", "credit", "financial institution"],
  business: ["entrepreneurship", "msme", "enterprise"],
  entrepreneur: ["business", "entrepreneurship", "msme", "startup"],
  startup: ["business", "entrepreneurship", "msme"],
  msme: ["business", "enterprise", "small industries"],

  // ── Agriculture ──────────────────────────────────────────────────────────
  // Deliberately narrow. "agriculture" here returned twenty generic
  // "Agriculture: <sector>" industries for a topic the graph covers with one
  // entity — padding an absence rather than admitting it.
  dairy: ["cattle"],
  farming: ["agriculture", "crop", "farmer", "organic farming"],
  farmer: ["agriculture", "farming", "crop", "kisan"],
  agriculture: ["farming", "crop", "agritech", "agro processing"],
  crop: ["agriculture", "farming"],
  organic: ["organic farming", "agriculture", "vermicompost"],
  irrigation: ["drip", "micro irrigation", "krishi sinchayee"],

  // ── Energy ───────────────────────────────────────────────────────────────
  solar: ["solar panel", "renewable energy", "rooftop", "surya ghar"],
  renewable: ["solar", "wind energy", "energy"],
  ev: ["electric vehicle", "ev technician", "charging"],

  // ── Learning and jobs ────────────────────────────────────────────────────
  course: ["training", "certification", "skill"],
  training: ["skill", "certification", "training provider", "iti"],
  certificate: ["certification", "training"],
  iti: ["industrial training institute", "training", "certification", "skill"],
  apprentice: ["apprenticeship", "training", "skill"],
  job: ["employment", "skill"],
  jobs: ["employment", "skill"],
  career: ["skill", "employment", "training"],
  salary: ["employment"],

  // ── Manufacturing ────────────────────────────────────────────────────────
  // No "factory": the graph names these "... Unit" and "... Manufacturing",
  // never "factory".
  manufacturing: ["fabrication", "production", "unit"],
  factory: ["manufacturing", "unit"],
  machine: ["machinery", "equipment", "cnc"],
  cnc: ["machining", "lathe", "machinery", "turning"],
  fabrication: ["welding", "sheet metal", "manufacturing"],

  // ── Food ─────────────────────────────────────────────────────────────────
  food: ["food processing", "agro processing", "millet", "oil", "masala"],
  pickle: ["avakaya", "food processing"],
  avakaya: ["pickle", "food processing"],
  oil: ["cold pressed", "oil expeller", "groundnut", "coconut"],
  masala: ["spice", "powder", "grinding"],
  spice: ["masala", "turmeric", "chilli", "powder"],
};

//: Acronyms and abbreviations that a substring search can never resolve,
//: because the stored name spells the words out in full.
export const ACRONYMS = {
  pmegp: "prime minister's employment generation programme",
  pmkvy: "pradhan mantri kaushal vikas yojana",
  pmay: "pradhan mantri awas yojana",
  pmfby: "pradhan mantri fasal bima yojana",
  mgnrega: "mahatma gandhi national rural employment guarantee",
  nrega: "mahatma gandhi national rural employment guarantee",
  kcc: "kisan credit card",
  cgtmse: "credit guarantee fund trust for micro and small enterprises",
  iti: "industrial training institutes",
  nsdc: "national skill development corporation",
  msme: "micro small and medium enterprises",
  ai: "artificial intelligence",
  ml: "machine learning",
  ev: "electric vehicle",
  cnc: "computer numerical control",
  fpo: "farmer producer organisation",
  odop: "one district one product",
  ondc: "open network for digital commerce",
};

//: Common misspellings worth correcting outright. Deliberately short: the fuzzy
//: matcher handles the long tail, and a correction list that guesses is worse
//: than one that does not exist.
export const CORRECTIONS = {
  electrican: "electrician",
  electrition: "electrician",
  electrisian: "electrician",
  plumbar: "plumber",
  carpender: "carpenter",
  welbing: "welding",
  agricultre: "agriculture",
  buisness: "business",
  bussiness: "business",
  goverment: "government",
  govenment: "government",
  scheem: "scheme",
  mashine: "machine",
  managment: "management",
};

/** Lower-case, strip punctuation, collapse whitespace. */
export function normaliseTerm(text) {
  return String(text || "")
    .normalize("NFC")
    // Zero-width joiners. Telugu conjuncts are commonly typed with a U+200C
    // between syllables and just as commonly without, and two strings that
    // render identically must compare equal.
    .replace(/[​-‍﻿]/g, "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\p{M}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * A query term plus everything it should also look for.
 *
 * Returns [{term, weight, kind}] — kind is "typed", "acronym" or "related".
 * Weight below 1 so an expansion never outranks a
 * direct hit on what the user actually typed. A student searching "electrician"
 * should see "Electrician (Domestic Wiring)" above "Electrical Panel
 * Manufacturing", even though both are relevant.
 */
export function expandQuery(raw) {
  const q = normaliseTerm(raw);
  if (!q) return [];

  const out = new Map();
  const add = (term, weight, kind) => {
    const t = normaliseTerm(term);
    if (t && (!out.has(t) || out.get(t).weight < weight)) out.set(t, { weight, kind });
  };

  add(q, 1, "typed");

  const corrected = CORRECTIONS[q];
  if (corrected) add(corrected, 0.95, "typed");

  const base = corrected || q;

  // An acronym expansion is the SAME thing written out, so it keeps the match
  // kind it earns. Without this, "PMEGP" ranked "PMEGP Margin Money Subsidy"
  // (a PREFIX hit on the letters) above "Prime Minister's Employment Generation
  // Programme" (the scheme itself, demoted to RELATED) — and "AI" buried
  // "Artificial Intelligence" under eight "AI Tooling:" rows.
  if (ACRONYMS[base]) add(ACRONYMS[base], 0.9, "acronym");

  for (const term of EXPANSIONS[base] || []) add(term, 0.6, "related");

  // Per word, so "tile mason work" still expands on "tile" and "mason".
  const words = base.split(" ");
  if (words.length > 1) {
    for (const w of words) {
      if (w.length < 3) continue;
      if (CORRECTIONS[w]) add(CORRECTIONS[w], 0.8, "typed");
      if (ACRONYMS[w]) add(ACRONYMS[w], 0.7, "acronym");
      for (const term of EXPANSIONS[w] || []) add(term, 0.45, "related");
      // The words themselves, at a weight that cannot outrank the phrase.
      //
      // Without this, a query the graph half-covers returned nothing at all.
      // "lift technician" is the case that exposed it: we hold no lift
      // technician, but we do hold "Forklift and Material Handling
      // Equipment", and the multi-word rule in matchTerm needs EVERY word
      // present, so the phrase matched nothing and neither word was ever
      // tried on its own. Half an answer beats a blank page, and the phrase
      // still wins wherever the phrase exists.
      add(w, 0.4, "related");
    }
  }

  // Telugu and Tanglish. Merged last and only where it wins: `add` keeps the
  // higher weight, so a query already understood in English is unaffected and
  // this cannot reorder any existing result.
  for (const { term, weight, kind } of resolveQuery(raw).terms) add(term, weight, kind);

  return [...out].map(([term, { weight, kind }]) => ({ term, weight, kind }));
}

/**
 * What the query turned out to mean, for the UI to echo back.
 *
 * Separate from `expandQuery` on purpose: the ranker wants terms and the page
 * wants a sentence, and folding both into one return value would put a
 * presentation concern inside the matcher.
 */
export { resolveQuery, describeResolution } from "./search/multilingual.js";
