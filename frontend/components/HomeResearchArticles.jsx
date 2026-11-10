// Homepage: research articles. Reads the SAME loader as the Research Hub,
// article pages and sitemap (lib/research.js → getCombinedArticles), so this
// section cannot show an article those pages would not, and it adds no second
// copy of any article.
//
// WHICH ARTICLES, AND WHY THE HEADING DOES NOT SAY "MOST READ"
// ------------------------------------------------------------
// Per-article reads ARE recorded — PageTracker writes every article view to
// `page_views` — but that table's RLS lets only admins read it, and this page
// runs with the public anon key. (`research_articles.views`, which the admin
// performance page selects, is defined by no migration and written by no code.)
// So the homepage has no honest way to rank by readership, and calling the
// list "most read" would be inventing a ranking. It shows the most recent
// published articles instead — the same order the Research Hub uses for its
// own featured slot — and says so.
//
// To make it genuinely "most read": expose per-slug counts for PUBLISHED
// articles through a narrow security-definer view or RPC, sort by that here,
// and change the heading. Nothing else in this section would need to change.
//
// Drafts never appear: getPublishedDbArticles filters status = 'published'
// (and anon RLS exposes nothing else), and MDX files with `published: false`
// are dropped by lib/mdx.js.
import { getCombinedArticles } from "@/lib/research";
import HomeResearchArticlesClient from "@/components/HomeResearchArticlesClient";

const MAX_ARTICLES = 6;

export default async function HomeResearchArticles() {
  let articles = [];
  try {
    articles = await getCombinedArticles();
  } catch {
    articles = [];
  }

  const seen = new Set();
  const picked = [];
  for (const a of articles) {
    if (!a?.slug || !a.published || seen.has(a.slug)) continue;
    seen.add(a.slug);
    // Only what a card shows. The article body can be thousands of words and
    // would otherwise be serialised into the page for a client component.
    picked.push({
      slug: a.slug,
      title: a.title,
      metaDescription: a.metaDescription || "",
      category: a.category,
      categoryLabel: a.categoryLabel || null,
      coverImage: a.coverImage || null,
      districtTags: a.districtTags || [],
      video: a.video ? { youtubeUrl: a.video.youtubeUrl } : null,
      investmentRange: a.investmentRange || null,
      author: a.author || null,
      readingTime: a.readingTime || null,
    });
    if (picked.length === MAX_ARTICLES) break;
  }

  // No articles, no section — not an empty heading or a placeholder.
  if (picked.length === 0) return null;
  return <HomeResearchArticlesClient articles={picked} />;
}
