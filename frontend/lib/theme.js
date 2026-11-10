// Shared labels for the Research Hub. Visual design tokens live in
// globals.css / tailwind.config.js — do not duplicate them here.

// ─── The research taxonomy ──────────────────────────────────────────────────
//
// ONE list, grouped. Everything else in this file is derived from it, and
// every consumer — the article editor, the hub's filter chips, the badge on a
// card, the admin filter — reads this file, so a category added here appears
// everywhere at once.
//
// The first ten ids (agriculture … handicrafts) are the original list. Their
// ids and labels are unchanged: published articles store the id, and a
// renamed id would orphan them.
//
// Two categories that were asked for are deliberately NOT here, because each
// would have split one subject across two chips:
//   - "Renewable Energy"            → already inside `energy`
//   - "Food & Agriculture Technology" → already inside `agriculture` and
//                                       `food-processing`
// and "Arts, Crafts & Heritage" is "Arts, Culture & Heritage", so that crafts
// stay in `handicrafts` and the new one holds what handicrafts never did:
// performing arts, folk traditions, heritage sites.
//
// Districts are NOT categories. An article's place lives in its `district`
// field; a category says what it is about, not where.
export const CATEGORY_GROUPS = [
  {
    label: "Business & Livelihoods",
    items: [
      ["entrepreneurship-startups", "Entrepreneurship & Startups"],
      ["msme-small-businesses", "MSME & Small Businesses"],
      ["retail", "Retail"],
      ["employment-careers", "Employment & Careers"],
      ["skill-development-training", "Skill Development & Training"],
      ["education", "Education"],
      ["finance-financial-inclusion", "Finance & Financial Inclusion"],
    ],
  },
  {
    label: "Agriculture & Rural Economy",
    items: [
      ["agriculture", "Agriculture"],
      ["food-processing", "Food Processing"],
      ["dairy-livestock", "Dairy & Livestock"],
      ["fisheries-aquaculture", "Fisheries & Aquaculture"],
      ["rural-development", "Rural Development"],
    ],
  },
  {
    label: "Industry & Infrastructure",
    items: [
      ["manufacturing", "Manufacturing"],
      ["construction-infrastructure", "Construction & Infrastructure"],
      ["logistics", "Logistics"],
      ["energy", "Energy"],
      ["ev-battery-technology", "EV & Battery Technology"],
      ["electronics-semiconductors", "Electronics & Semiconductors"],
      ["defence-aerospace", "Defence & Aerospace"],
      ["recycling-circular-economy", "Recycling & Circular Economy"],
    ],
  },
  {
    label: "Technology & Innovation",
    items: [
      ["technology", "Technology"],
      ["ai-emerging-technologies", "Artificial Intelligence & Emerging Technologies"],
      ["software-it-services", "Software & IT Services"],
      ["biotechnology-pharmaceuticals", "Biotechnology & Pharmaceuticals"],
      ["research-innovation", "Research & Innovation"],
    ],
  },
  {
    label: "Traditional Skills & Culture",
    items: [
      ["handicrafts", "Handicrafts"],
      ["handlooms-textiles", "Handlooms & Textiles"],
      ["arts-culture-heritage", "Arts, Culture & Heritage"],
      ["tourism-hospitality", "Tourism & Hospitality"],
    ],
  },
  {
    label: "Society & Environment",
    items: [
      ["healthcare", "Healthcare"],
      ["government-schemes-public-welfare", "Government Schemes & Public Welfare"],
      ["environment-sustainability", "Environment & Sustainability"],
      ["social-impact-community-development", "Social Impact & Community Development"],
    ],
  },
];

// id → label, in taxonomy order. Same export, same shape as before.
export const CATEGORY_LABELS = Object.fromEntries(
  CATEGORY_GROUPS.flatMap((g) => g.items)
);

// ─── Custom categories ──────────────────────────────────────────────────────
//
// `research_articles.category` is free text with no constraint, and always
// was. So a custom category needs no table and no migration: a predefined
// category is stored as its id ("healthcare"), a custom one as its display
// text ("Drone Services"). Everything below exists so those two spellings —
// and the older hand-typed ones already in the table, like "Food processing" —
// resolve to one category instead of three.

const SMALL_WORDS = new Set(["and", "of", "in", "for", "the", "to", "on", "at", "by", "or"]);
export const CUSTOM_CATEGORY_MAX = 60;

/** Stable slug for URLs-in-state, test ids and equality. Not stored. */
export function categorySlug(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

// The key two spellings must share to count as the same category:
// "Agri-Tech", "agri tech" and "AGRITECH " all collapse to "agritech";
// "Arts & Crafts" and "arts and crafts" both to "artsandcrafts".
function matchKey(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, "");
}

const KNOWN_BY_KEY = new Map();
for (const [id, label] of Object.entries(CATEGORY_LABELS)) {
  KNOWN_BY_KEY.set(matchKey(id), id);
  KNOWN_BY_KEY.set(matchKey(label), id);
}

/**
 * Tidy what an author typed: collapse whitespace, title-case words written
 * entirely in lower case, and leave any word that already has a capital
 * alone — "EV", "AI", "MSME" and "eCommerce" are spelled the way their
 * author meant. Returns "" when nothing usable is left.
 */
export function normalizeCustomCategory(input) {
  const cleaned = String(input || "")
    .replace(/[\u0000-\u001f<>]/g, " ")
    .replace(/\s+/g, " ")
    .replace(/\s*&\s*/g, " & ")
    .trim()
    .slice(0, CUSTOM_CATEGORY_MAX)
    .trim();
  if (!cleaned) return "";
  return cleaned
    .split(" ")
    .map((word, i) => {
      if (word !== word.toLowerCase()) return word;
      if (i > 0 && SMALL_WORDS.has(word)) return word;
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}

/**
 * Whatever is stored → one category.
 *   { id, label, known }
 * `id` is the predefined id when the value is (any spelling of) a predefined
 * category, otherwise a slug of the text. `label` is what a reader sees.
 * Empty input falls back to `fallback` — the readers' side has always shown
 * uncategorised rows under Agriculture, and that is not changed here.
 */
export function resolveCategory(raw, fallback = "agriculture") {
  const text = String(raw ?? "").trim();
  if (!text) {
    return fallback
      ? { id: fallback, label: CATEGORY_LABELS[fallback] || fallback, known: true }
      : { id: "", label: "", known: false };
  }
  const knownId = KNOWN_BY_KEY.get(matchKey(text));
  if (knownId) return { id: knownId, label: CATEGORY_LABELS[knownId], known: true };
  // A custom category. Text that looks like a bare slug ("drone-services",
  // which is what an MDX file or an older row may hold) is un-slugged for
  // display; anything else is shown as its author wrote it.
  const looksLikeSlug = /^[a-z0-9]+(-[a-z0-9]+)*$/.test(text);
  const label = normalizeCustomCategory(looksLikeSlug ? text.replace(/-/g, " ") : text);
  return { id: categorySlug(text), label: label || text, known: false };
}

export function getCategoryLabel(raw) {
  return resolveCategory(raw, null).label;
}

/**
 * Validate a custom category an author typed.
 *   { ok: true,  value, existing }   value is what to store
 *   { ok: false, error }
 * `existing` says the text matched something already there — a predefined
 * category (value is its id) or a custom one another article uses (value is
 * THAT article's spelling) — so the author gets the existing category rather
 * than a near-duplicate of it. `existingCustom` is the list of custom
 * category strings already in use.
 */
export function validateCustomCategory(input, existingCustom = []) {
  const value = normalizeCustomCategory(input);
  if (!value) return { ok: false, error: "Enter a category name." };
  if (!/[a-z]/i.test(value) || value.replace(/[^a-z0-9]/gi, "").length < 2) {
    return { ok: false, error: "Use a meaningful name — at least two letters." };
  }
  const key = matchKey(value);
  const knownId = KNOWN_BY_KEY.get(key);
  if (knownId) {
    return { ok: true, value: knownId, existing: "predefined", label: CATEGORY_LABELS[knownId] };
  }
  const match = existingCustom.find((c) => matchKey(c) === key);
  if (match) return { ok: true, value: match, existing: "custom", label: getCategoryLabel(match) };
  return { ok: true, value, existing: null, label: value };
}
