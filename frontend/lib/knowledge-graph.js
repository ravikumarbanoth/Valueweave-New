import { createClient } from "@supabase/supabase-js";

export const KG_ENTITY_CONFIG = {
  districts: { table: "kg_district_profiles", label: "District", plural: "Districts", titleField: "name", publicPath: "/districts-cms" },
  skills: { table: "kg_skills", label: "Skill", plural: "Skills", titleField: "name", publicPath: "/skills" },
  resources: { table: "kg_resources", label: "Resource", plural: "Resources", titleField: "name", publicPath: "/resources" },
  schemes: { table: "kg_schemes", label: "Scheme", plural: "Schemes", titleField: "name", publicPath: "/schemes" },
  roadmaps: { table: "kg_roadmaps", label: "Roadmap", plural: "Roadmaps", titleField: "title", publicPath: "/roadmaps" },
};

export const KG_ENTITY_TYPES = Object.keys(KG_ENTITY_CONFIG);

function anonClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false } });
}

export function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 90);
}

export async function getKgEntities(type, { publishedOnly = true, limit = 100 } = {}) {
  const config = KG_ENTITY_CONFIG[type];
  if (!config) return [];
  try {
    const supabase = anonClient();
    if (!supabase) return [];
    let query = supabase.from(config.table).select("*").order("updated_at", { ascending: false }).limit(limit);
    if (publishedOnly) query = query.eq("status", "published");
    const { data, error } = await query;
    if (error) return [];
    return data || [];
  } catch {
    return [];
  }
}

export async function getKgEntityBySlug(type, slug) {
  const config = KG_ENTITY_CONFIG[type];
  if (!config || !/^[a-z0-9-]+$/i.test(slug || "")) return null;
  try {
    const supabase = anonClient();
    if (!supabase) return null;
    const { data, error } = await supabase
      .from(config.table)
      .select("*")
      .eq("slug", slug)
      .eq("status", "published")
      .maybeSingle();
    if (error) return null;
    return data || null;
  } catch {
    return null;
  }
}

export async function getKnowledgeGraphStats() {
  try {
    const supabase = anonClient();
    if (!supabase) return emptyStats();
    const [districts, skills, resources, schemes, roadmaps, relationships] = await Promise.all([
      supabase.from("kg_district_profiles").select("*", { count: "exact", head: true }),
      supabase.from("kg_skills").select("*", { count: "exact", head: true }),
      supabase.from("kg_resources").select("*", { count: "exact", head: true }),
      supabase.from("kg_schemes").select("*", { count: "exact", head: true }),
      supabase.from("kg_roadmaps").select("*", { count: "exact", head: true }),
      supabase.from("kg_relationships").select("relationship_type,source_type,target_type").limit(1000),
    ]);
    const relRows = relationships.data || [];
    const byType = relRows.reduce((acc, row) => {
      acc[row.relationship_type] = (acc[row.relationship_type] || 0) + 1;
      return acc;
    }, {});
    return {
      districts: districts.count || 0,
      skills: skills.count || 0,
      resources: resources.count || 0,
      schemes: schemes.count || 0,
      roadmaps: roadmaps.count || 0,
      relationships: relRows.length,
      relationshipTypes: byType,
    };
  } catch {
    return emptyStats();
  }
}

function emptyStats() {
  return { districts: 0, skills: 0, resources: 0, schemes: 0, roadmaps: 0, relationships: 0, relationshipTypes: {} };
}

export function kgStructuredData(type, entity) {
  const config = KG_ENTITY_CONFIG[type];
  const title = entity?.[config?.titleField] || entity?.name || entity?.title || "ValueWeave Knowledge Graph Entity";
  return {
    "@context": "https://schema.org",
    "@type": type === "schemes" ? "GovernmentService" : type === "resources" ? "ItemList" : "CreativeWork",
    name: title,
    description: entity?.meta_description || entity?.summary || entity?.description || "",
    url: `${process.env.NEXT_PUBLIC_BASE_URL || "https://valueweave.in"}${config?.publicPath || ""}/${entity?.slug || ""}`,
    keywords: [type, entity?.category, entity?.state, entity?.type].filter(Boolean).join(", "),
  };
}
