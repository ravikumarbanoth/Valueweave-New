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

const LOW_INVESTMENT_LIMIT = 100000;

// ── Buckets (execution stays inline: it's a tiny, stable enum) ──
export const BUCKETS = [
  { id: "local-physical", label: "Local Physical",      emoji: "🏪" },
  { id: "hybrid",         label: "Hybrid Tech + Local", emoji: "🔗" },
  { id: "digital",        label: "Pure Digital",        emoji: "💻" },
  { id: "future",         label: "Future Economy",      emoji: "🚀" },
];

export const DISCOVERY_FILTERS = [
  { id: "featured", label: "Featured", emoji: "✨" },
  { id: "trending", label: "Trending", emoji: "📈" },
  { id: "beginner", label: "Beginner Friendly", emoji: "🌱" },
  { id: "low-investment", label: "Below ₹1 Lakh", emoji: "💰" },
  { id: "women-led", label: "Women-Led", emoji: "💐" },
  { id: "student", label: "Student Friendly", emoji: "🎓" },
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

const arr = (v) => (Array.isArray(v) ? v : []);
const hasTag = (idea, tag) => arr(idea.tags).includes(tag);
const normalized = (value) => String(value || "").toLowerCase();

export function isLowInvestmentIdea(idea) {
  return Number(idea.investment_min || 0) < LOW_INVESTMENT_LIMIT;
}

export function isWomenLedIdea(idea) {
  return idea.sector === "women-led" || hasTag(idea, "Women-Led") || arr(idea.ideal_for).some((v) => normalized(v).includes("women"));
}

export function isStudentFriendlyIdea(idea) {
  return hasTag(idea, "Student Friendly") || arr(idea.ideal_for).some((v) => normalized(v).includes("student"));
}

export function isTrendingIdea(idea) {
  return hasTag(idea, "High Growth") || hasTag(idea, "Tech Enabled") || hasTag(idea, "Export Potential") || Number(idea.monthly_revenue_max || 0) >= 200000;
}

export function isFeaturedIdea(idea) {
  const practical = idea.beginner_friendly || isLowInvestmentIdea(idea) || hasTag(idea, "Evergreen") || hasTag(idea, "Skill-Based");
  const highSignal = isTrendingIdea(idea) || isWomenLedIdea(idea) || isStudentFriendlyIdea(idea) || hasTag(idea, "Rural Opportunity");
  return practical && highSignal;
}

export function matchesDiscoveryFilter(idea, filterId) {
  if (!filterId) return true;
  if (filterId === "featured") return isFeaturedIdea(idea);
  if (filterId === "trending") return isTrendingIdea(idea);
  if (filterId === "beginner") return !!idea.beginner_friendly;
  if (filterId === "low-investment") return isLowInvestmentIdea(idea);
  if (filterId === "women-led") return isWomenLedIdea(idea);
  if (filterId === "student") return isStudentFriendlyIdea(idea);
  return true;
}

export function getIdeaSearchText(idea) {
  const sector = getSector(idea.sector);
  const bucket = getBucket(idea.bucket);
  return [
    idea.title,
    idea.short_description,
    idea.problem_solved,
    sector.label,
    sector.id,
    bucket.label,
    ...arr(idea.tags),
    ...arr(idea.skills_needed),
    ...arr(idea.ideal_for),
    ...arr(idea.district_fit),
  ].filter(Boolean).join(" ").toLowerCase();
}

export function getRelatedIdeas(idea, limit = 3) {
  if (!idea) return [];
  const sourceTags = new Set(arr(idea.tags));
  const sourceRange = getInvestmentRange(idea)?.id;

  return IDEAS
    .filter((candidate) => candidate.slug !== idea.slug)
    .map((candidate) => {
      const tagOverlap = arr(candidate.tags).filter((tag) => sourceTags.has(tag)).length;
      const sameRange = sourceRange && getInvestmentRange(candidate)?.id === sourceRange;
      const score =
        (candidate.sector === idea.sector ? 5 : 0) +
        (candidate.bucket === idea.bucket ? 2 : 0) +
        (sameRange ? 3 : 0) +
        tagOverlap;
      return { idea: candidate, score };
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || a.idea.investment_min - b.idea.investment_min)
    .slice(0, limit)
    .map((item) => item.idea);
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
