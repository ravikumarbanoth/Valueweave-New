import { getAllArticleSlugs } from "@/lib/mdx";
import { getAllDistrictSlugs } from "@/lib/districts-data";
import { getAllSegments } from "@/lib/radar-data";
import { sitemapEntry } from "@/lib/seo";
import { IDEAS } from "@/lib/idea-library";

export default function sitemap() {
  const articleSlugs = getAllArticleSlugs();
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
  ];
}
