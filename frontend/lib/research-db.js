// ValueWeave — Supabase-backed research articles (server-side, anon key).
// Public reads only (RLS exposes published rows to anon). Every fetcher
// fails soft — builds and pages must work even when Supabase is unreachable
// (e.g., CI builds with placeholder env vars).

import { createClient } from "@supabase/supabase-js";
import { CATEGORY_LABELS } from "@/lib/theme";
import { getYouTubeEmbedUrl, isValidYouTubeUrl } from "@/lib/youtube";

function anonClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false } });
}

// Map free-text category ("Healthcare", "food processing") to a known
// category id so cards, filters, and badges keep working.
function normalizeCategory(raw) {
  if (!raw) return "agriculture";
  const slug = String(raw).trim().toLowerCase().replace(/\s+/g, "-");
  if (CATEGORY_LABELS[slug]) return slug;
  const byLabel = Object.entries(CATEGORY_LABELS).find(
    ([, label]) => label.toLowerCase() === String(raw).trim().toLowerCase()
  );
  return byLabel ? byLabel[0] : slug;
}

function estimateReadingTime(content) {
  const words = String(content || "").trim().split(/\s+/).length;
  return Math.max(1, Math.ceil(words / 200));
}

function normalizeVideo(row) {
  if (!row?.youtube_url || !isValidYouTubeUrl(row.youtube_url)) return null;
  return {
    youtubeUrl: row.youtube_url,
    embedUrl: getYouTubeEmbedUrl(row.youtube_url),
    title: row.video_title || row.title || "ValueWeave research video",
    description: row.video_description || "",
    viewCount: row.video_view_count || 0,
  };
}

// Normalize a research_articles row to the SAME shape lib/mdx.js produces,
// so every downstream consumer (cards, template, SEO, internal links)
// works identically for both sources.
export function normalizeDbArticle(row) {
  if (!row) return null;
  const faq = Array.isArray(row.faq_json) ? row.faq_json : [];
  return {
    source: "db",
    dbId: row.id,
    slug: row.slug,
    published: row.status === "published",
    title: row.title || "",
    metaTitle: row.seo_title || row.title || "",
    metaDescription: row.seo_description || row.excerpt || "",
    category: normalizeCategory(row.category),
    sector: row.category || "Research",
    districtTags: row.district
      ? [String(row.district).trim().toLowerCase().replace(/\s+/g, "-")]
      : [],
    stateTags: [],
    investmentRange: { min: 0, max: 0, currency: "INR", label: null },
    coverImage: row.cover_image || null,
    content: row.content || "",
    faq: faq.filter((f) => f && f.question && f.answer),
    relatedIdeas: [],
    keywords: Array.isArray(row.keywords) ? row.keywords : [],
    video: normalizeVideo(row),
    publishedAt: row.published_at || row.created_at || new Date().toISOString(),
    updatedAt: row.updated_at || new Date().toISOString(),
    author: row.author || "ValueWeave Research Team",
    readingTime: estimateReadingTime(row.content),
  };
}

export async function getPublishedDbArticles() {
  try {
    const supabase = anonClient();
    if (!supabase) return [];
    const { data, error } = await supabase
      .from("research_articles")
      .select("*")
      .eq("status", "published")
      .order("published_at", { ascending: false });
    if (error) return [];
    return (data || []).map(normalizeDbArticle);
  } catch {
    return [];
  }
}

export async function getDbArticleBySlug(slug) {
  try {
    if (!/^[a-z0-9-]+$/i.test(slug || "")) return null;
    const supabase = anonClient();
    if (!supabase) return null;
    const { data, error } = await supabase
      .from("research_articles")
      .select("*")
      .eq("slug", slug)
      .eq("status", "published")
      .maybeSingle();
    if (error || !data) return null;
    return normalizeDbArticle(data);
  } catch {
    return null;
  }
}
