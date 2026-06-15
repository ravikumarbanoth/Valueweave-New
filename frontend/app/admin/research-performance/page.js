import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { BookOpen, Eye, TrendingUp, MapPin, Briefcase, Star, ExternalLink } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Research Performance | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function MiniBar({ value, max, color = "amber" }) {
  const pct = max > 0 ? Math.max((value / max) * 100, 2) : 2;
  const bg = { amber: "bg-amber-400", teal: "bg-teal-400", blue: "bg-blue-400", green: "bg-green-400" };
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-stone-100 rounded-full h-2 overflow-hidden">
        <div className={`${bg[color]} h-full rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[12px] font-bold text-stone-700 w-8 text-right shrink-0">{value}</span>
    </div>
  );
}

async function fetchResearchPerformance() {
  try {
    const sb = createClient();

    const [
      { data: articles },
      { data: viewsBySlug },
      { count: totalArticles },
      { count: draftCount },
    ] = await Promise.all([
      sb.from("research_articles")
        .select("id,title,slug,category,district,status,views,published_at,created_at,seo_title,seo_description,keywords")
        .order("published_at", { ascending: false })
        .limit(100),
      sb.from("page_views")
        .select("page_slug,district,sector")
        .eq("page_type", "research")
        .limit(5000),
      sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "published"),
      sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "draft"),
    ]);

    // Build view counts from page_views table
    const viewCountMap = {};
    const districtInterestMap = {};
    (viewsBySlug || []).forEach(({ page_slug, district }) => {
      viewCountMap[page_slug] = (viewCountMap[page_slug] || 0) + 1;
      if (district) {
        if (!districtInterestMap[page_slug]) districtInterestMap[page_slug] = {};
        districtInterestMap[page_slug][district] = (districtInterestMap[page_slug][district] || 0) + 1;
      }
    });

    const published = (articles || []).filter((a) => a.status === "published");
    const drafts = (articles || []).filter((a) => a.status === "draft");

    // Enrich articles with computed view data
    const enriched = published.map((a) => {
      const trackedViews = viewCountMap[a.slug] || 0;
      const dbViews = a.views || 0;
      const totalViews = Math.max(trackedViews, dbViews);
      const topDistrict = Object.entries(districtInterestMap[a.slug] || {})
        .sort((x, y) => y[1] - x[1])[0]?.[0] || a.district || null;
      const seoComplete = !!(a.seo_title && a.seo_description && a.keywords?.length > 0);
      return { ...a, totalViews, topDistrict, seoComplete };
    });

    // Sort by views desc
    enriched.sort((a, b) => b.totalViews - a.totalViews);

    // Category breakdown
    const catMap = {};
    published.forEach(({ category }) => {
      if (category) catMap[category] = (catMap[category] || 0) + 1;
    });
    const topCategories = Object.entries(catMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, count]) => ({ label, count }));

    // District breakdown
    const distMap = {};
    published.forEach(({ district }) => {
      if (district) distMap[district] = (distMap[district] || 0) + 1;
    });
    const topDistricts = Object.entries(distMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, count]) => ({ label, count }));

    const totalViews = enriched.reduce((s, a) => s + a.totalViews, 0);
    const avgSEOComplete = published.length > 0
      ? Math.round((enriched.filter((a) => a.seoComplete).length / published.length) * 100)
      : 0;

    const maxViews = Math.max(...enriched.map((a) => a.totalViews), 1);

    return {
      articles: enriched,
      drafts,
      totalArticles: totalArticles || 0,
      draftCount: draftCount || 0,
      totalViews,
      avgSEOComplete,
      topCategories,
      topDistricts,
      maxViews,
    };
  } catch (e) {
    console.error("Research performance error:", e);
    return {
      articles: [], drafts: [], totalArticles: 0, draftCount: 0, totalViews: 0,
      avgSEOComplete: 0, topCategories: [], topDistricts: [], maxViews: 1,
    };
  }
}

export default async function ResearchPerformancePage() {
  const d = await fetchResearchPerformance();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-purple-100 text-purple-700 border border-purple-200">RESEARCH PERFORMANCE</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Research Performance Dashboard</h1>
            <p className="text-stone-500 text-sm mt-1">Article views, SEO completeness, and content distribution</p>
          </div>
          <Link href="/admin/research/new" className="btn-primary shrink-0">
            + New Article
          </Link>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Published", value: d.totalArticles, icon: BookOpen, color: "bg-purple-50 text-purple-700" },
            { label: "Drafts", value: d.draftCount, icon: Star, color: "bg-stone-100 text-stone-500" },
            { label: "Total Views", value: d.totalViews, icon: Eye, color: "bg-blue-50 text-blue-700" },
            { label: "SEO Complete", value: `${d.avgSEOComplete}%`, icon: TrendingUp, color: "bg-green-50 text-green-700" },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card-base p-4">
              <div className={`inline-flex p-2 rounded-lg mb-2 ${color}`}><Icon size={14} /></div>
              <div className="text-xl font-display font-extrabold text-ink">{value}</div>
              <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-0.5">{label}</div>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <Star size={14} className="text-amber-500" /> Most Popular Categories
            </h3>
            {d.topCategories.length > 0 ? (
              <div className="space-y-2.5">
                {d.topCategories.map((c) => {
                  const maxC = Math.max(...d.topCategories.map((x) => x.count), 1);
                  return (
                    <div key={c.label} className="flex items-center gap-3">
                      <div className="w-28 text-[12px] text-stone-600 capitalize shrink-0 truncate">{c.label}</div>
                      <MiniBar value={c.count} max={maxC} color="amber" />
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-stone-400 italic">No articles published yet.</p>
            )}
          </div>

          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <MapPin size={14} className="text-teal-500" /> Most Popular Districts
            </h3>
            {d.topDistricts.length > 0 ? (
              <div className="space-y-2.5">
                {d.topDistricts.map((c) => {
                  const maxC = Math.max(...d.topDistricts.map((x) => x.count), 1);
                  return (
                    <div key={c.label} className="flex items-center gap-3">
                      <div className="w-28 text-[12px] text-stone-600 capitalize shrink-0 truncate">{c.label}</div>
                      <MiniBar value={c.count} max={maxC} color="teal" />
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-stone-400 italic">No district-tagged articles yet.</p>
            )}
          </div>

        </div>

        {/* Article Performance Table */}
        <div className="card-base overflow-hidden">
          <div className="p-5 border-b border-stone-100">
            <h3 className="font-display font-bold text-ink text-sm">Article Performance</h3>
          </div>
          {d.articles.length === 0 ? (
            <div className="p-12 text-center">
              <BookOpen size={28} className="text-stone-300 mx-auto mb-3" />
              <p className="text-stone-400 text-sm">No published articles yet.</p>
              <Link href="/admin/research/new" className="text-amber-600 font-semibold text-sm hover:underline mt-2 block">
                Create your first article →
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-[12px]">
                <thead>
                  <tr className="border-b border-stone-200">
                    {["Article", "Category", "District", "Views", "SEO", "Actions"].map((h) => (
                      <th key={h} className="text-left py-3 px-4 text-[10px] font-semibold text-stone-400 uppercase tracking-widest whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {d.articles.map((a) => (
                    <tr key={a.id} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
                      <td className="py-3 px-4 max-w-[200px]">
                        <p className="font-semibold text-ink truncate">{a.title}</p>
                        <p className="text-stone-400 text-[11px] truncate">/research/{a.slug}</p>
                      </td>
                      <td className="py-3 px-4">
                        <span className="chip bg-amber-50 text-amber-700 text-[10px] capitalize">{a.category || "—"}</span>
                      </td>
                      <td className="py-3 px-4">
                        {a.topDistrict
                          ? <span className="chip bg-stone-100 text-stone-500 text-[10px]">{a.topDistrict}</span>
                          : <span className="text-stone-300">—</span>
                        }
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5">
                          <Eye size={11} className="text-stone-400" />
                          <span className="font-bold text-stone-700">{a.totalViews}</span>
                        </div>
                        <MiniBar value={a.totalViews} max={d.maxViews} color="blue" />
                      </td>
                      <td className="py-3 px-4">
                        <span className={`chip text-[10px] ${a.seoComplete ? "bg-green-100 text-green-700" : "bg-red-50 text-red-500"}`}>
                          {a.seoComplete ? "Complete" : "Incomplete"}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Link
                            href={`/admin/research/${a.id}`}
                            className="text-amber-600 hover:underline font-semibold text-[11px]"
                          >
                            Edit
                          </Link>
                          <Link
                            href={`/research/${a.slug}`}
                            target="_blank"
                            className="text-stone-400 hover:text-stone-600 transition-colors"
                          >
                            <ExternalLink size={12} />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Drafts */}
        {d.drafts.length > 0 && (
          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4">
              Drafts ({d.drafts.length})
            </h3>
            <ul className="space-y-2">
              {d.drafts.map((a) => (
                <li key={a.id} className="flex items-center gap-3">
                  <span className="chip bg-stone-100 text-stone-400 text-[10px]">DRAFT</span>
                  <span className="text-[13px] text-stone-600 flex-1 truncate">{a.title}</span>
                  <Link href={`/admin/research/${a.id}`} className="text-amber-600 hover:underline text-[12px] font-semibold shrink-0">
                    Edit
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

      </div>
    </AdminShell>
  );
}
