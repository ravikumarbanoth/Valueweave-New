// ValueWeave — combined research article loader.
// Single source of truth for the public Research Hub, article pages, and
// sitemap. Database articles take priority; file-based MDX articles
// (content/research/*.mdx) remain fully supported as a fallback so the
// existing publishing workflow keeps working.

import { getAllArticles as getMdxArticles, getArticleBySlug as getMdxArticleBySlug } from "@/lib/mdx";
import { getPublishedDbArticles, getDbArticleBySlug } from "@/lib/research-db";

export async function getCombinedArticles() {
  const db = await getPublishedDbArticles();
  const dbSlugs = new Set(db.map((a) => a.slug));
  const mdx = getMdxArticles().filter((a) => !dbSlugs.has(a.slug));
  return [...db, ...mdx].sort(
    (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
  );
}

export async function getCombinedArticleBySlug(slug) {
  const db = await getDbArticleBySlug(slug);
  if (db) return db;
  return getMdxArticleBySlug(slug);
}
