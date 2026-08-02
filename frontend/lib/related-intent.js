// What a reader of THIS page is actually asking, and in what order.
//
// THE PROBLEM
// -----------
// "Where this leads next" grouped the neighbours by entity type, headed each
// group with the type's plural name, and sorted the groups by how many rows were
// in them. Three consequences, all of them the same mistake:
//
//   * The order was decided by our data volume, not by the reader. On a Crop,
//     "Soil types (3)" and "Climate zones (3)" came before the industries and
//     schemes, because there happen to be more soil edges. Nobody arrives at
//     Turmeric asking about soil taxonomy first.
//   * The headings were type names. "Government schemes" is a category in our
//     model; "Schemes that can help you" is the question the reader has.
//   * Every page of a given type showed the same shape regardless of what that
//     type is FOR. A skill and a scheme are read for opposite reasons.
//
// `LEAD_RELATED` in the detail page was an attempt at the first of those, and it
// was silently discarded — RelatedEntities re-sorted by group size, so the
// intended order never survived. It had also drifted badly from the data: of the
// 46 (source type, neighbour type) pairs it promised, 20 do not exist in the
// graph at all, and 10 pairs that DO exist were missing. `Certification` was
// listed twice and appears in zero relationships.
//
// MEASURED, NOT GUESSED
// ---------------------
// Every pair below is reachable in the built graph within the two hops this
// page reads, and the test suite asserts it. Nine of them exist only at the
// second hop — District→Skill, Crop→District, Industry→GovernmentScheme and so
// on — which is exactly why the second hop is worth reading: they are among the
// most useful questions a reader of those pages has.
//
// Seven pairs were written into the first draft of this file and removed after
// checking: Skill→Certification, BusinessOpportunity→{Machinery, RawMaterial,
// Market, District}, District→BusinessOpportunity and Certification→Skill. The
// graph holds no path for any of them — `Certification` appears in zero
// relationships of any kind — so each was a heading that could never render.
// That is the same class of lie as a search expansion matching nothing, and it
// is caught the same way.
import { URL_BY_TYPE } from "./knowledge.js";

//: How much a relationship means, when the question is "what should I look at
//: next". These fifteen are the complete set in the graph — there is no
//: sixteenth to fall through to, and `DEFAULT_REL_WEIGHT` exists only so a
//: relationship added later ranks low rather than crashing.
//
//: RELATED_TO is last on purpose. It is the catch-all, it is the single largest
//: bucket (190 of 865 edges), and it is almost entirely Crop→Soil and
//: Crop→ClimateZone — true, and the least actionable thing on the page.
export const REL_WEIGHT = {
  REQUIRES_SKILL: 1.0,
  TRAINED_BY: 1.0,
  SUPPORTED_BY_SCHEME: 0.95,
  USES_MACHINERY: 0.9,
  USES_RAW_MATERIAL: 0.9,
  PROCESSES: 0.9,
  SELLS_TO: 0.85,
  EXPORTS_TO: 0.85,
  SUPPORTED_BY_BANK: 0.85,
  FUNDED_BY: 0.85,
  GENERATES_EMPLOYMENT: 0.8,
  PART_OF: 0.8,
  LOCATED_IN: 0.7,
  USES_AI: 0.6,
  RELATED_TO: 0.4,
};

export const DEFAULT_REL_WEIGHT = 0.3;

//: Source entity type -> the questions its reader has, in the order they ask
//: them. Only pairs the graph can actually produce.
export const INTENT = {
  Skill: [
    { type: "TrainingProvider", heading: "Where to learn this" },
    { type: "BusinessOpportunity", heading: "Businesses you could start with it" },
    { type: "MSME", heading: "Businesses that need this skill" },
    { type: "Industry", heading: "Industries that hire for it" },
    { type: "GovernmentScheme", heading: "Schemes that can help you" },
  ],
  BusinessOpportunity: [
    { type: "Skill", heading: "Skills you will need" },
    { type: "GovernmentScheme", heading: "Schemes that can help you start" },
    { type: "FinancialInstitution", heading: "Who might fund it" },
    { type: "Industry", heading: "The wider industry" },
  ],
  MSME: [
    { type: "Skill", heading: "Skills it runs on" },
    { type: "GovernmentScheme", heading: "Schemes behind it" },
    { type: "Machinery", heading: "Equipment it uses" },
    { type: "RawMaterial", heading: "What it buys in" },
    { type: "Crop", heading: "What it processes" },
    { type: "Market", heading: "Where it sells" },
    { type: "ExportCountry", heading: "Where it exports" },
    { type: "FinancialInstitution", heading: "Who funds businesses like it" },
    { type: "District", heading: "Where it employs people" },
  ],
  GovernmentScheme: [
    { type: "BusinessOpportunity", heading: "Businesses you could start with it" },
    { type: "MSME", heading: "Businesses already using it" },
    { type: "Skill", heading: "Skills it supports" },
    { type: "Crop", heading: "Crops it covers" },
    { type: "FinancialInstitution", heading: "Who administers the money" },
  ],
  District: [
    { type: "Institution", heading: "Where you can study here" },
    { type: "MSME", heading: "Businesses running here" },
    { type: "GovernmentScheme", heading: "Schemes that apply here" },
    { type: "Skill", heading: "Skills in demand here" },
    { type: "Crop", heading: "What grows here" },
    { type: "Industry", heading: "Industries here" },
    { type: "State", heading: "Part of" },
  ],
  Industry: [
    { type: "BusinessOpportunity", heading: "Businesses in this industry" },
    { type: "Skill", heading: "Skills it hires for" },
    { type: "Crop", heading: "Crops it works with" },
    { type: "Institution", heading: "Where it is taught" },
    { type: "Industry", heading: "Industries it overlaps with" },
    { type: "MSME", heading: "Businesses already doing it" },
    { type: "GovernmentScheme", heading: "Schemes for this industry" },
  ],
  Crop: [
    { type: "Industry", heading: "What it becomes" },
    { type: "MSME", heading: "Businesses that process it" },
    { type: "GovernmentScheme", heading: "Schemes for growers" },
    { type: "ExportCountry", heading: "Where it is exported" },
    { type: "Soil", heading: "Soil it needs" },
    { type: "ClimateZone", heading: "Climate it needs" },
    { type: "District", heading: "Districts that grow it" },
    { type: "Machinery", heading: "Equipment for it" },
  ],
  TrainingProvider: [{ type: "Skill", heading: "What you can learn here" }],
  Institution: [
    { type: "District", heading: "Where it is" },
    { type: "Industry", heading: "Industries it feeds" },
  ],
  Machinery: [{ type: "MSME", heading: "Businesses that use it" }],
  RawMaterial: [{ type: "MSME", heading: "Businesses that use it" }],
  Market: [{ type: "MSME", heading: "Businesses that sell here" }],
  ExportCountry: [
    { type: "MSME", heading: "Businesses that export here" },
    { type: "Crop", heading: "Crops exported here" },
  ],
  FinancialInstitution: [
    { type: "MSME", heading: "Businesses it backs" },
    { type: "GovernmentScheme", heading: "Schemes it administers" },
  ],
  Soil: [{ type: "Crop", heading: "What grows in it" }],
  ClimateZone: [{ type: "Crop", heading: "What grows in it" }],
  State: [
    { type: "District", heading: "Districts in this state" },
    { type: "Country", heading: "Part of" },
  ],
  Country: [{ type: "State", heading: "States" }],
};

//: Anything the graph returns that the intent list did not anticipate. Pooled
//: into ONE trailing section rather than dropped, and rather than one section
//: per type — the first draft gave Warangal seven consecutive headings all
//: reading "Also connected", which is worse than either alternative.
//:
//: Shown at all because a section we forgot to name is still information, and
//: silently hiding it to tidy the page would be the wrong trade.
export const FALLBACK_HEADING = "Also connected";

//: Per section. "NOT everything from the package" — a reader scanning on a
//: phone will not reach the fortieth chip, and the overflow link goes to the
//: full category anyway.
export const MAX_PER_SECTION = 6;

/** One entity's score within its section. Higher is shown first. */
export function scoreNeighbour(entity) {
  const relWeight = REL_WEIGHT[entity?._via] ?? DEFAULT_REL_WEIGHT;
  // Edge confidence is how sure we are of the LINK; entity confidence is how
  // good the source for the thing at the other end is. The first decides the
  // order, the second breaks ties — a strong link to a moderately sourced
  // entity is still a better next step than a weak link to a well-sourced one.
  const edge = Number(entity?._edge?.confidence);
  const linkConfidence = Number.isFinite(edge) ? Math.min(edge, 100) / 100 : 0.5;
  const own = Math.min(Number(entity?.confidence_score) || 0, 100) / 100;
  return relWeight * (0.5 + 0.5 * linkConfidence) + own * 0.05;
}

/**
 * Turn `getRelatedByType()` output into ordered, question-headed sections.
 *
 * Returns `[{ type, heading, items, overflow, href }]`. `items` is capped;
 * `overflow` is how many were held back, and `href` opens the whole category
 * so the cap never loses anything.
 */
export function intentSections(grouped, sourceType, { max = MAX_PER_SECTION } = {}) {
  const groups = grouped || {};
  const planned = INTENT[sourceType] || [];
  const seen = new Set();
  const out = [];

  const push = (type, heading) => {
    const rows = groups[type];
    if (!rows || rows.length === 0 || seen.has(type)) return;
    seen.add(type);
    const ranked = [...rows].sort(
      (a, b) =>
        scoreNeighbour(b) - scoreNeighbour(a) ||
        String(a.canonical_name).localeCompare(String(b.canonical_name))
    );
    const url = URL_BY_TYPE[type];
    out.push({
      type,
      heading,
      items: ranked.slice(0, max),
      overflow: Math.max(0, ranked.length - max),
      href: url ? `/knowledge?type=${url}` : null,
    });
  };

  for (const { type, heading } of planned) push(type, heading);

  // Everything the intent list did not name, pooled and ranked together. No
  // `href`: the section spans several types, so there is no single category to
  // open — the individual chips are the way in.
  const rest = Object.keys(groups)
    .filter((type) => !seen.has(type) && groups[type]?.length)
    .flatMap((type) => groups[type])
    .sort(
      (a, b) =>
        scoreNeighbour(b) - scoreNeighbour(a) ||
        String(a.canonical_name).localeCompare(String(b.canonical_name))
    );
  if (rest.length > 0) {
    out.push({
      type: "OTHER",
      heading: FALLBACK_HEADING,
      items: rest.slice(0, max),
      overflow: Math.max(0, rest.length - max),
      href: null,
    });
  }
  return out;
}
