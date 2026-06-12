import { getCombinedArticles } from "@/lib/research";
import { getAllDistrictSlugs } from "@/lib/districts-data";
import { getAllSegments } from "@/lib/radar-data";
import { sitemapEntry } from "@/lib/seo";
import { IDEAS } from "@/lib/idea-library";
import { MARKETPLACE_DISTRICTS, MARKETPLACE_SECTORS } from "@/lib/collab";

const stateToSlug = (stateName) => (stateName === "Telangana" ? "telangana" : "andhra-pradesh");

export default async function sitemap() {
  // Combined sources: published database articles + file-based MDX
  const articleSlugs = (await getCombinedArticles()).map((a) => a.slug);
  const districtSlugs = getAllDistrictSlugs();
  const radarSegments = getAllSegments();

  return [
    // ── Static core pages ──
    sitemapEntry("/", { changeFreq: "daily", priority: 1.0 }),
    sitemapEntry("/ideas", { changeFreq: "weekly", priority: 0.9 }),
    sitemapEntry("/research", { changeFreq: "daily", priority: 0.9 }),
    sitemapEntry("/opportunity-radar", { changeFreq: "weekly", priority: 0.9 }),
    sitemapEntry("/district", { changeFreq: "weekly", priority: 0.85 }),
    sitemapEntry("/explore", { changeFreq: "hourly", priority: 0.85 }),
    sitemapEntry("/discover", { changeFreq: "monthly", priority: 0.8 }),
    sitemapEntry("/about", { changeFreq: "monthly", priority: 0.5 }),
    sitemapEntry("/get-started", { changeFreq: "monthly", priority: 0.6 }),

    // ── Idea Library (122+) ──
    ...IDEAS.map((idea) =>
      sitemapEntry(`/ideas/${idea.slug}`, { changeFreq: "monthly", priority: 0.75 })
    ),

    // ── Research articles ──
    ...articleSlugs.map((slug) =>
      sitemapEntry(`/research/${slug}`, { changeFreq: "weekly", priority: 0.85 })
    ),

    // ── District pages ──
    ...districtSlugs.map((slug) =>
      sitemapEntry(`/district/${slug}`, { changeFreq: "weekly", priority: 0.8 })
    ),

    // ── Opportunity radar segments ──
    ...radarSegments.map((seg) =>
      sitemapEntry(`/opportunity-radar/${seg}`, { changeFreq: "weekly", priority: 0.8 })
    ),

    // ── Opportunity marketplace (state + district SEO pages) ──
    sitemapEntry("/opportunities/telangana", { changeFreq: "daily", priority: 0.85 }),
    sitemapEntry("/opportunities/andhra-pradesh", { changeFreq: "daily", priority: 0.85 }),
    ...MARKETPLACE_DISTRICTS.map((d) =>
      sitemapEntry(`/opportunities/${stateToSlug(d.state)}/${d.slug}`, { changeFreq: "daily", priority: 0.8 })
    ),

    // ── District business-idea pages ──
    ...MARKETPLACE_DISTRICTS.map((d) =>
      sitemapEntry(`/business-ideas/${d.slug}`, { changeFreq: "weekly", priority: 0.75 })
    ),

    // ── Collaborator marketplace ──
    sitemapEntry("/collaborators", { changeFreq: "daily", priority: 0.85 }),
    ...MARKETPLACE_SECTORS.map((s) =>
      sitemapEntry(`/collaborators/${s.id}`, { changeFreq: "daily", priority: 0.75 })
    ),
  ];
}
