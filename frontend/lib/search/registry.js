// Everything one search box can reach, and everything it is meant to reach.
//
// WHY A REGISTRY AND NOT A SECOND QUERY IN THE PAGE
// -------------------------------------------------
// "Search everything from one box" is easy to write and easy to get wrong. The
// wrong version is a page that queries the knowledge graph, then queries the
// research articles, then merges two lists it ranked by different rules —
// which is how this repository got two search implementations the first time.
//
// So there is one list. A source declares what it is, where its rows come from
// and how to turn one into a searchable document. Adding mentors later is one
// object in this file and a loader; it is not a change to the ranker, the API
// route, the grouping, or the page.
//
// WHAT A DOCUMENT IS
// ------------------
// The shape `rankEntities` already scores: `canonical_name`, `entity_type`,
// `confidence_score`. A research article is projected into that shape rather
// than the ranker being taught about articles — one ranking ladder, one set of
// rules about what beats what, for every kind of content on the platform.
//
// Documents may also carry `_aliases`: other short strings the thing answers
// to. That is how an article is found by its keywords and a scheme by its
// short name, without the title having to contain the word.
//
// THE SOURCES THAT ARE NOT LIVE YET
// ---------------------------------
// Blogs, news, mentors, courses and success stories are declared here with
// `status: "planned"` and no loader. They are in this file because the brief
// names them and because a reader who searches for a mentor should be told
// that mentors are coming, not shown an empty page — see NoResultsGuide, which
// reads this list.
//
// They return nothing. Nothing here fabricates a row: a planned source with a
// loader that invented three plausible mentors would be the single most
// damaging thing this file could do.

import { getCombinedArticles } from "@/lib/research.js";

//: The order groups appear in on a results page. Places first because a
//: student almost always has one in mind; research last because it is reading
//: rather than doing, and a reader who wants it will scroll.
export const GROUPS = [
  { id: "places", label: "Places" },
  { id: "business", label: "Business opportunities" },
  { id: "skills", label: "Skills & training" },
  { id: "schemes", label: "Government support" },
  { id: "agriculture", label: "Agriculture" },
  { id: "industry", label: "Industries & companies" },
  { id: "education", label: "Education" },
  { id: "inputs", label: "Machinery & materials" },
  { id: "research", label: "Research & guides" },
];

export const GROUP_LABEL = Object.fromEntries(GROUPS.map((g) => [g.id, g.label]));

//: Which group each knowledge entity type belongs to, and what one row of it
//: is called in a sentence. The type name is an implementation detail;
//: "Government scheme" is what a person calls the thing.
export const TYPE_GROUP = {
  District: ["places", "District"],
  State: ["places", "State"],
  Country: ["places", "Country"],
  ExportCountry: ["places", "Export destination"],

  BusinessOpportunity: ["business", "Business opportunity"],
  MSME: ["business", "Small business"],

  Skill: ["skills", "Skill"],
  Certification: ["skills", "Certification"],
  TrainingProvider: ["skills", "Training provider"],

  GovernmentScheme: ["schemes", "Government scheme"],
  FinancialInstitution: ["schemes", "Bank or lender"],

  Crop: ["agriculture", "Crop"],
  Soil: ["agriculture", "Soil type"],
  ClimateZone: ["agriculture", "Climate zone"],

  Industry: ["industry", "Industry"],
  Market: ["industry", "Market channel"],

  Institution: ["education", "Institution"],

  Machinery: ["inputs", "Machinery"],
  RawMaterial: ["inputs", "Raw material"],

  ResearchArticle: ["research", "Research article"],
};

/** The group a document belongs to, with a sane fallback for a new type. */
export function groupOf(entityType) {
  return (TYPE_GROUP[entityType] || ["industry", entityType])[0];
}

/** What one row of this type is called, in words a reader uses. */
export function kindLabel(entityType) {
  return (TYPE_GROUP[entityType] || [null, entityType])[1];
}

// ─── Sources ────────────────────────────────────────────────────────────────

//: Articles have no confidence_score — the concept does not apply to an essay.
//: 70 places them among the better-sourced knowledge rows without letting them
//: win a tie against a verified fact, and confidence only ever breaks ties.
const ARTICLE_CONFIDENCE = 70;

/**
 * Research articles, from both places they live.
 *
 * `getCombinedArticles` already unions the `research_articles` table with the
 * MDX files in content/research and de-duplicates by slug — the Research Hub
 * and the sitemap both read it, so search reading it too means search cannot
 * disagree with the page it links to.
 *
 * WHY THIS IS THE ONE THAT MATTERED MOST
 * --------------------------------------
 * Original research is the thing ValueWeave has that a search engine does not,
 * and it was the one kind of content the search box could not see. An article
 * was reachable only by browsing /research. Someone searching the exact subject
 * of an article we had written got a page of database rows and no article.
 */
async function loadResearchArticles() {
  const articles = await getCombinedArticles();
  return articles.map((article) => ({
    global_entity_id: `article:${article.slug}`,
    entity_type: "ResearchArticle",
    canonical_name: article.title,
    source_package: "research",
    confidence_score: ARTICLE_CONFIDENCE,
    // Everything short and specific enough to be worth matching. NOT the body:
    // a 2,000-word essay matches every query and would swamp the page.
    _aliases: [
      ...(article.keywords || []),
      ...(article.districtTags || []),
      article.sector,
    ].map((s) => String(s || "").replace(/-/g, " ").trim()).filter((s) => s.length > 2),
    _href: `/research/${article.slug}`,
    _summary: article.metaDescription || "",
    _published_at: article.publishedAt || null,
  }));
}

/**
 * The registry.
 *
 * `status` is "live" or "planned". A planned source has no loader and
 * contributes nothing; it exists so the product can say "not yet" by name
 * instead of showing a blank page, and so the next person can see the shape a
 * new source has to fit.
 */
export const SOURCES = [
  {
    id: "knowledge",
    label: "Researched knowledge",
    status: "live",
    // Loaded by lib/knowledge.js rather than here: it owns the Supabase client,
    // the process-lifetime cache and the soft-delete filter, and duplicating
    // any of that would be a second way for the index to be wrong.
    loader: null,
    note: "districts, states, countries, industries, business opportunities, "
        + "MSMEs, skills, certifications, training providers, crops, soils, "
        + "climate zones, government schemes, banks, machinery, raw materials, "
        + "market channels, export destinations and institutions",
  },
  {
    id: "research",
    label: "Research articles & editorial guides",
    status: "live",
    loader: loadResearchArticles,
  },

  // ── Declared, not yet written. No loaders, and deliberately so. ───────────
  { id: "blogs", label: "Blog posts", status: "planned" },
  { id: "news", label: "News & updates", status: "planned" },
  { id: "mentors", label: "Mentors", status: "planned" },
  { id: "courses", label: "Courses", status: "planned" },
  { id: "stories", label: "Success stories", status: "planned" },
  { id: "reports", label: "Opportunity reports", status: "planned" },
];

export const LIVE_SOURCES = SOURCES.filter((s) => s.status === "live");
export const PLANNED_SOURCES = SOURCES.filter((s) => s.status === "planned");

/** Every document from every source that has a loader. Never throws. */
export async function loadRegisteredDocuments() {
  const loaded = await Promise.all(
    SOURCES.filter((s) => s.loader).map(async (source) => {
      try {
        return await source.loader();
      } catch {
        // Same contract as lib/knowledge.js: a source that cannot be read
        // returns nothing and the rest of search still works. A search box
        // that 500s because the article table is asleep is worse than a
        // search box that finds no articles.
        return [];
      }
    })
  );
  return loaded.flat();
}
