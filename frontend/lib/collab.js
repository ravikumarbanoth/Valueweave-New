// ValueWeave — Collaborator Marketplace shared data & helpers.
// Single source of truth for marketplace districts, the archetype →
// category/founder-role mappings used by the recommendation engine, and
// fail-soft server-side fetchers for the SEO pages.

import { createClient } from "@supabase/supabase-js";

// ── Marketplace districts (Phase 2 target list) ──
export const MARKETPLACE_DISTRICTS = [
  // Telangana
  { slug: "hyderabad",     name: "Hyderabad",     state: "Telangana" },
  { slug: "rangareddy",    name: "Rangareddy",    state: "Telangana" },
  { slug: "medchal",       name: "Medchal",       state: "Telangana" },
  { slug: "medak",         name: "Medak",         state: "Telangana" },
  { slug: "sangareddy",    name: "Sangareddy",    state: "Telangana" },
  { slug: "warangal",      name: "Warangal",      state: "Telangana" },
  { slug: "karimnagar",    name: "Karimnagar",    state: "Telangana" },
  { slug: "nizamabad",     name: "Nizamabad",     state: "Telangana" },
  { slug: "khammam",       name: "Khammam",       state: "Telangana" },
  { slug: "mahabubnagar",  name: "Mahabubnagar",  state: "Telangana" },
  { slug: "siddipet",      name: "Siddipet",      state: "Telangana" },
  { slug: "nalgonda",      name: "Nalgonda",      state: "Telangana" },
  // Andhra Pradesh
  { slug: "visakhapatnam", name: "Visakhapatnam", state: "Andhra Pradesh" },
  { slug: "vijayawada",    name: "Vijayawada",    state: "Andhra Pradesh" },
  { slug: "guntur",        name: "Guntur",        state: "Andhra Pradesh" },
  { slug: "tirupati",      name: "Tirupati",      state: "Andhra Pradesh" },
  { slug: "kurnool",       name: "Kurnool",       state: "Andhra Pradesh" },
  { slug: "nellore",       name: "Nellore",       state: "Andhra Pradesh" },
  { slug: "kakinada",      name: "Kakinada",      state: "Andhra Pradesh" },
  { slug: "anantapur",     name: "Anantapur",     state: "Andhra Pradesh" },
  { slug: "rajahmundry",   name: "Rajahmundry",   state: "Andhra Pradesh" },
  { slug: "kadapa",        name: "Kadapa",        state: "Andhra Pradesh" },
];

export const STATE_SLUGS = {
  telangana: "Telangana",
  "andhra-pradesh": "Andhra Pradesh",
  ap: "Andhra Pradesh", // short alias from the spec (/opportunities/ap/guntur)
};

export function getMarketplaceDistrict(slug) {
  return MARKETPLACE_DISTRICTS.find((d) => d.slug === slug) || null;
}
export function districtsForState(stateName) {
  return MARKETPLACE_DISTRICTS.filter((d) => d.state === stateName);
}

// ── Marketplace sectors (extends the existing opportunity categories;
//    `category` on the opportunities table IS the sector field) ──
export const MARKETPLACE_SECTORS = [
  { id: "healthcare",    emoji: "🏥", label: "Healthcare" },
  { id: "education",     emoji: "📚", label: "Education" },
  { id: "agri",          emoji: "🌾", label: "Agriculture" },
  { id: "ai-tech",       emoji: "🤖", label: "Technology" },
  { id: "manufacturing", emoji: "🏭", label: "Manufacturing" },
];

// ── Recommendation engine: archetype → opportunity matching ──
// Mirrors the Discover Yourself archetypes (app/discover/page.js).
export const ARCHETYPE_CATEGORY_MAP = {
  Builder:    ["manufacturing", "agri", "trades", "local-business"],
  Innovator:  ["ai-tech", "digital", "ev-electronics"],
  Leader:     ["local-business", "education", "manufacturing"],
  Analyst:    ["ai-tech", "local-business", "education"],
  Caregiver:  ["healthcare", "education", "local-business"],
  Explorer:   ["agri", "local-business", "digital"],
  Researcher: ["healthcare", "ai-tech", "agri"],
  Influencer: ["digital", "education", "local-business"],
};

export const ARCHETYPE_FOUNDER_ROLE = {
  Builder:    "Operations & Delivery Lead",
  Innovator:  "Product & Strategy Lead",
  Leader:     "CEO / Managing Director",
  Analyst:    "Finance & Research Lead",
  Caregiver:  "Community & Impact Lead",
  Explorer:   "Business Development Lead",
  Researcher: "R&D & Quality Lead",
  Influencer: "Marketing & Sales Lead",
};

// Complementary archetypes — who a founder should look for as co-founders.
export const COMPLEMENTARY_ARCHETYPES = {
  Builder:    ["Innovator", "Influencer", "Analyst"],
  Innovator:  ["Builder", "Analyst", "Influencer"],
  Leader:     ["Builder", "Analyst", "Researcher"],
  Analyst:    ["Leader", "Innovator", "Influencer"],
  Caregiver:  ["Analyst", "Builder", "Influencer"],
  Explorer:   ["Builder", "Analyst", "Caregiver"],
  Researcher: ["Influencer", "Leader", "Builder"],
  Influencer: ["Builder", "Analyst", "Researcher"],
};

// ── Fail-soft server-side fetchers (anon key, no cookies) ──
// Used by SSG/ISR SEO pages — must return empty data when Supabase is
// unreachable (e.g. CI builds with placeholder env vars).
function anonClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false } });
}

export async function getOpenOpportunities({ district, state, category, limit = 30 } = {}) {
  try {
    const supabase = anonClient();
    if (!supabase) return [];
    let q = supabase
      .from("opportunities")
      .select("*, owner:profiles!opportunities_owner_id_fkey(id,name,picture)")
      .eq("status", "open")
      .order("created_at", { ascending: false })
      .limit(limit);
    if (district) q = q.eq("district", district);
    if (state) q = q.eq("state", state);
    if (category) q = q.eq("category", category);
    const { data, error } = await q;
    if (error) return [];
    return data || [];
  } catch {
    return [];
  }
}

export async function getCollaborators({ sector, district, limit = 30 } = {}) {
  try {
    const supabase = anonClient();
    if (!supabase) return [];
    let q = supabase
      .from("collaborator_profiles")
      .select("*")
      .eq("open_to_collaborate", true)
      .order("updated_at", { ascending: false })
      .limit(limit);
    if (sector) q = q.contains("top_sectors", [sector]);
    if (district) q = q.eq("district", district);
    const { data, error } = await q;
    if (error) return [];
    return data || [];
  } catch {
    return [];
  }
}

export async function getOpportunityCountsByDistrict(stateName) {
  try {
    const supabase = anonClient();
    if (!supabase) return {};
    const { data, error } = await supabase
      .from("opportunities")
      .select("district")
      .eq("status", "open")
      .eq("state", stateName);
    if (error) return {};
    const counts = {};
    for (const row of data || []) {
      if (row.district) counts[row.district] = (counts[row.district] || 0) + 1;
    }
    return counts;
  } catch {
    return {};
  }
}
