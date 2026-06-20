// ValueWeave — MDX / CMS-lite content loader.
// Admin publishing workflow (Option A): drop an .mdx file into
// content/research/ and it appears on /research automatically at the next
// build (instantly in dev). Set `published: false` in frontmatter to
// unpublish without deleting the file.

import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { getYouTubeEmbedUrl, isValidYouTubeUrl } from "@/lib/youtube";

const CONTENT_DIR = path.join(process.cwd(), "content/research");

export function getAllArticleSlugs({ includeDrafts = false } = {}) {
  if (!fs.existsSync(CONTENT_DIR)) return [];
  return fs
    .readdirSync(CONTENT_DIR)
    .filter((f) => f.endsWith(".mdx"))
    .map((f) => f.replace(/\.mdx$/, ""))
    .filter((slug) => {
      if (includeDrafts) return true;
      const a = getArticleBySlug(slug, { includeDrafts: true });
      return a && a.published;
    });
}

export function getArticleBySlug(slug, { includeDrafts = false } = {}) {
  // Guard against path traversal — slug comes from the URL.
  if (!/^[a-z0-9-]+$/i.test(slug || "")) return null;
  const filePath = path.join(CONTENT_DIR, `${slug}.mdx`);
  if (!fs.existsSync(filePath)) return null;

  const raw = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(raw);
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
