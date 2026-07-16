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

export const featuredKnowledge = [
  { label: "Featured District", type: "districts", slug: "medak" },
  { label: "Featured Industry", type: "industries", slug: "food-processing" },
  { label: "Featured Manufacturing Opportunity", type: "manufacturing", slug: "millet-processing-unit" },
  { label: "Featured Learning Path", type: "training", slug: "food-processing-entrepreneur" },
  { label: "Featured Government Scheme", type: "schemes", slug: "pmegp" },
  { label: "Featured Product", type: "products", slug: "millet-snacks" },
].map((entry) => ({ ...entry, item: getKnowledgeItem(entry.type, entry.slug) }));

export const futureInfrastructureModules = [
  {
    title: "Innovation Infrastructure",
    items: ["Research commercialization", "Technology transfer", "Innovation labs", "Patent ecosystem"],
  },
  {
    title: "Research & Technology Infrastructure",
    items: ["Universities", "Research Labs", "R&D Collaboration", "Technology Readiness Levels"],
  },
  {
    title: "Digital Supply Chain Infrastructure",
    items: ["Suppliers", "Warehousing", "Cold Chain", "Procurement", "Traceability"],
  },
  {
    title: "Global Trade Infrastructure",
    items: ["Exports", "Imports", "International Buyers", "Trade Missions", "Export Documentation"],
  },
  {
    title: "Industrial Finance Infrastructure",
    items: ["Banks", "NBFCs", "Government Grants", "CSR", "Angel Investors", "VC"],
  },
  {
    title: "Sustainability Infrastructure",
    items: ["Circular Economy", "Recycling", "Renewable Energy", "Carbon Footprint", "Green Manufacturing"],
  },
];
