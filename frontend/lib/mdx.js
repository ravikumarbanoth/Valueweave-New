// ValueWeave — MDX / CMS-lite content loader.
// Admin publishing workflow (Option A): drop an .mdx file into
// content/research/ and it appears on /research automatically at the next
// build (in dev, at the next `npm run dev`). Set `published: false` in
// frontmatter to unpublish without deleting the file.
//
// The files are read at BUILD time by scripts/build-research-registry.mjs,
// not here at request time. This module used to call fs.readdirSync and
// fs.readFileSync on every request, which cannot work on Cloudflare Workers
// (no project filesystem: every article 404'd). The registry holds the same
// frontmatter and body gray-matter produced before; everything below — the
// slug guard, the visibility rule, the field defaults — is unchanged.

import REGISTRY from "@/lib/generated/research-registry.js";
import { getYouTubeEmbedUrl, isValidYouTubeUrl } from "@/lib/youtube";

const BY_SLUG = new Map(REGISTRY.map((entry) => [entry.slug, entry]));

export function getAllArticleSlugs({ includeDrafts = false } = {}) {
  return REGISTRY
    .map((entry) => entry.slug)
    .filter((slug) => {
      if (includeDrafts) return true;
      const a = getArticleBySlug(slug, { includeDrafts: true });
      return a && a.published;
    });
}

export function getArticleBySlug(slug, { includeDrafts = false } = {}) {
  // Slug comes from the URL. There is no path to traverse any more, but the
  // same rule decides what counts as a valid article slug, as before.
  if (!/^[a-z0-9-]+$/i.test(slug || "")) return null;
  const entry = BY_SLUG.get(slug);
  if (!entry) return null;

  const { data, content } = entry;
  const published = data.published !== false;
  if (!published && !includeDrafts) return null;
  const video = data.youtubeUrl && isValidYouTubeUrl(data.youtubeUrl)
    ? {
        youtubeUrl: data.youtubeUrl,
        embedUrl: getYouTubeEmbedUrl(data.youtubeUrl),
        title: data.videoTitle || data.title || "ValueWeave research video",
        description: data.videoDescription || "",
        viewCount: 0,
      }
    : null;

  return {
    slug,
    published,
    title: data.title || "",
    metaTitle: data.metaTitle || data.title || "",
    metaDescription: data.metaDescription || "",
    category: data.category || "agriculture",
    sector: data.sector || "",
    districtTags: data.districtTags || [],
    stateTags: data.stateTags || [],
    investmentRange: data.investmentRange || { min: 0, max: 0, currency: "INR", label: "Varies" },
    coverImage: data.coverImage || null,
    content,
    faq: data.faq || [],
    relatedIdeas: data.relatedIdeas || [],
    keywords: data.keywords || [],
    video,
    publishedAt: data.publishedAt || new Date().toISOString(),
    updatedAt: data.updatedAt || new Date().toISOString(),
    author: data.author || "ValueWeave Research Team",
    readingTime: estimateReadingTime(content),
  };
}

export function getAllArticles({ includeDrafts = false } = {}) {
  return getAllArticleSlugs({ includeDrafts })
    .map((slug) => getArticleBySlug(slug, { includeDrafts }))
    .filter(Boolean)
    .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());
}

function estimateReadingTime(content) {
  const words = content.trim().split(/\s+/).length;
  return Math.ceil(words / 200); // ~200 wpm
}
