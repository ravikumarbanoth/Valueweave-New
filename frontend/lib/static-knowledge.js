// The pre-package editorial knowledge layer — Platform v3.0, Step 4.
//
// 56 hand-written JSON records across 7 types, written before Packages 001–008
// existed. Every type here now has a researched counterpart with sources,
// provenance and confidence: 1 static district against 61 researched, 8
// industries against 78, 10 skills against 45, 6 schemes against 40.
//
// WHAT REMAINS, AND WHY
// ---------------------
// `getKnowledgeItem` and `getAllKnowledgeItems` are still used by
// /knowledge/[type]/[slug] to keep 56 indexed URLs resolving. Those pages now
// open with a notice saying they are editorial and superseded, and link to the
// researched equivalent.
//
// WHAT WENT
// ---------
// `featuredKnowledge` — six hard-coded slugs that were the homepage's "Explore
// Knowledge" section. Replaced by lib/knowledge.js `featuredByType()`, which
// shows what the platform actually holds instead of six records chosen in 2023.
//
// `futureInfrastructureModules` — six roadmap modules rendered under a "Planned"
// chip. The list moved into components/HomeFeatureGrid.jsx, where each module
// names the package that would have to exist first.
//
// Nothing in the application imports this module for display any more. It is a
// URL-compatibility shim, and when the 56 URLs stop mattering it can go.
import districts from "@/data/districts.json";
import industries from "@/data/industries.json";
import manufacturing from "@/data/manufacturing.json";
import products from "@/data/products.json";
import training from "@/data/training.json";
import skills from "@/data/skills.json";
import schemes from "@/data/schemes.json";

export const knowledgeDatasets = {
  districts,
  industries,
  manufacturing,
  products,
  training,
  skills,
  schemes,
};

export const knowledgeLabels = {
  districts: "District",
  industries: "Industry",
  manufacturing: "Manufacturing Opportunity",
  products: "Product",
  training: "Learning Path",
  skills: "Skill",
  schemes: "Government Scheme",
};

export function getKnowledgeItem(type, slug) {
  return (knowledgeDatasets[type] || []).find((item) => item.slug === slug) || null;
}

export function getAllKnowledgeItems() {
  return Object.entries(knowledgeDatasets).flatMap(([type, items]) =>
    items.map((item) => ({
      ...item,
      type,
      typeLabel: knowledgeLabels[type],
      href: `/knowledge/${type}/${item.slug}`,
      searchText: JSON.stringify(item).toLowerCase(),
    }))
  );
}
