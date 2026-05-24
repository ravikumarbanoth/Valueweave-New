// ValueWeave Idea Library — data barrel.
// The dataset is normalized into JSON files (ideas / sectors / tags / skills /
// districts / investment-ranges) so a future migration to Supabase tables is a
// drop-in. This module re-exports the SAME public names the app already imported
// from "@/lib/idea-library", so existing pages keep working unchanged.

import ideasData from "./ideas.json";
import sectorsData from "./sectors.json";
import tagsData from "./tags.json";
import skillGroups from "./skills.json";
import districtsData from "./districts.json";
import investmentRanges from "./investment-ranges.json";

// ── Buckets (execution stays inline: it's a tiny, stable enum) ──
export const BUCKETS = [
  { id: "local-physical", label: "Local Physical",      emoji: "🏪" },
  { id: "hybrid",         label: "Hybrid Tech + Local", emoji: "🔗" },
  { id: "digital",        label: "Pure Digital",        emoji: "💻" },
  { id: "future",         label: "Future Economy",      emoji: "🚀" },
];

// ── Public datasets (names preserved from the original single-file module) ──
export const IDEAS = ideasData;
export const SECTORS = sectorsData;
export const ALL_TAGS = tagsData.map((t) => t.label);
export const TAGS = tagsData; // [{ label, count }] for future tag chips
export const PRIORITY_STATES = districtsData.priority_states;
export const PRIORITY_DISTRICTS = districtsData.districts.map((d) => d.name);
export const DISTRICTS = districtsData.districts; // [{ name, state }]
export const SKILL_GROUPS = skillGroups;          // [{ group, skills[] }]
export const INVESTMENT_RANGES = investmentRanges; // [{ id, label, min, max }]

// "Execution type" is what the brief calls the bucket dimension; expose it
// under that name for the filter UI without duplicating the bucket list.
export const EXECUTION_TYPES = BUCKETS;

// ── Lookups (unchanged behavior) ──
export function getIdea(slug) {
  return IDEAS.find((i) => i.slug === slug) || null;
}
export function getSector(id) {
  return SECTORS.find((s) => s.id === id) || { id, label: id, emoji: "🌐" };
}
export function getBucket(id) {
  return BUCKETS.find((b) => b.id === id) || { id, label: id, emoji: "🌐" };
}

// ── Derived helpers for the new filters (no fabricated fields) ──
export function getInvestmentRange(idea) {
  const v = idea.investment_min;
  return INVESTMENT_RANGES.find(
    (r) => v >= r.min && (r.max == null || v < r.max)
  ) || null;
}
export function matchesInvestmentRange(idea, rangeId) {
  if (!rangeId) return true;
  const r = getInvestmentRange(idea);
  return r ? r.id === rangeId : false;
}

// ── Currency formatting (unchanged) ──
export function formatINR(n) {
  if (n == null || Number.isNaN(n)) return "—";
  if (n >= 100000) return `₹${(n / 100000).toFixed(n % 100000 === 0 ? 0 : 1)}L`;
  if (n >= 1000) return `₹${Math.round(n / 1000)}k`;
  return `₹${n}`;
}
