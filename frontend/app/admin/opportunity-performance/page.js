import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { Briefcase, Eye, Heart, TrendingUp, TrendingDown, MapPin, Layers, Activity } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Opportunity Performance | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function PerformanceBar({ value, max, color = "amber" }) {
  const pct = max > 0 ? Math.max((value / max) * 100, 2) : 2;
  const bars = { amber: "bg-amber-400", teal: "bg-teal-400", red: "bg-red-300", green: "bg-green-400" };
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-stone-100 rounded-full h-2 overflow-hidden">
        <div className={`${bars[color]} h-full rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[12px] font-bold text-stone-700 w-8 text-right shrink-0">{value}</span>
    </div>
  );
}

async function fetchOpportunityPerformance() {
  try {
    const sb = createClient();

    const [
      { data: opportunities },
      { data: interests },
      { data: pageViewsOpp },
      { data: oppViewsGranular },
    ] = await Promise.all([
      sb.from("opportunities")
        .select("id,title,category,district,state,status,created_by,created_at")
        .limit(500),
      sb.from("opportunity_interests")
        .select("opportunity_id,status,created_at")
        .limit(5000),
      sb.from("page_views")
        .select("page_slug,district,sector")
        .eq("page_type", "opportunity")
        .limit(10000),
      sb.from("opportunity_views")
        .select("opportunity_id,district")
        .limit(10000),
    ]);

    // Build view maps
    const viewsBySlug = {};
    (pageViewsOpp || []).forEach(({ page_slug }) => {
      viewsBySlug[page_slug] = (viewsBySlug[page_slug] || 0) + 1;
    });

    const viewsById = {};
    (oppViewsGranular || []).forEach(({ opportunity_id }) => {
      viewsById[opportunity_id] = (viewsById[opportunity_id] || 0) + 1;
    });

    // Build interest map
    const interestById = {};
    (interests || []).forEach(({ opportunity_id, status }) => {
      if (!interestById[opportunity_id]) interestById[opportunity_id] = { total: 0, pending: 0, contacted: 0, closed: 0 };
      interestById[opportunity_id].total++;
      if (status) interestById[opportunity_id][status] = (interestById[opportunity_id][status] || 0) + 1;
    });

    // Enrich opportunities
    const enriched = (opportunities || []).map((o) => {
      const views = viewsById[o.id] || viewsBySlug[o.id] || 0;
      const interest = interestById[o.id] || { total: 0 };
      const conversionRate = views > 0 ? Math.round((interest.total / views) * 100) : 0;
      return { ...o, views, interest: interest.total, conversionRate };
    });

    const topPerforming = [...enriched].sort((a, b) => b.interest - a.interest || b.views - a.views).slice(0, 10);
    const underPerforming = [...enriched]
      .filter((o) => o.views > 5 && o.interest === 0)
      .sort((a, b) => b.views - a.views)
      .slice(0, 8);

    // District performance
    const districtPerf = {};
    enriched.forEach(({ district, views, interest }) => {
      if (!district) return;
      if (!districtPerf[district]) districtPerf[district] = { views: 0, interest: 0, count: 0 };
      districtPerf[district].views += views;
      districtPerf[district].interest += interest;
      districtPerf[district].count++;
    });
    const topDistricts = Object.entries(districtPerf)
      .sort((a, b) => b[1].interest - a[1].interest || b[1].views - a[1].views)
      .slice(0, 8)
      .map(([name, d]) => ({ name, ...d }));

    // Sector performance
    const sectorPerf = {};
    enriched.forEach(({ category, views, interest }) => {
      if (!category) return;
      if (!sectorPerf[category]) sectorPerf[category] = { views: 0, interest: 0, count: 0 };
      sectorPerf[category].views += views;
      sectorPerf[category].interest += interest;
      sectorPerf[category].count++;
    });
    const topSectors = Object.entries(sectorPerf)
      .sort((a, b) => b[1].interest - a[1].interest || b[1].views - a[1].views)
      .slice(0, 8)
      .map(([name, d]) => ({ name, ...d }));

    const totalViews = enriched.reduce((s, o) => s + o.views, 0);
    const totalInterests = enriched.reduce((s, o) => s + o.interest, 0);
    const avgConversion = totalViews > 0 ? Math.round((totalInterests / totalViews) * 100) : 0;

    const maxViews = Math.max(...enriched.map((o) => o.views), 1);
    const maxInterest = Math.max(...enriched.map((o) => o.interest), 1);
    const maxDistInterest = Math.max(...topDistricts.map((d) => d.interest), 1);
    const maxSecInterest = Math.max(...topSectors.map((s) => s.interest), 1);

    return {
      total: enriched.length,
      totalViews,
      totalInterests,
      avgConversion,
      topPerforming,
      underPerforming,
      topDistricts,
      topSectors,
      maxViews,
      maxInterest,
      maxDistInterest,
      maxSecInterest,
      hasData: (opportunities?.length || 0) > 0,
    };
  } catch (e) {
    console.error("Opportunity performance error:", e);
    return {
      total: 0, totalViews: 0, totalInterests: 0, avgConversion: 0,
      topPerforming: [], underPerforming: [], topDistricts: [], topSectors: [],
      maxViews: 1, maxInterest: 1, maxDistInterest: 1, maxSecInterest: 1, hasData: false,
    };
  }
}

export default async function OpportunityPerformancePage() {
  const d = await fetchOpportunityPerformance();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-teal-100 text-teal-700 border border-teal-200">OPPORTUNITY PERFORMANCE</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Opportunity Performance Engine</h1>
            <p className="text-stone-500 text-sm mt-1">Views, interests, and conversion rates across all opportunities</p>
          </div>
          <Link href="/admin/opportunity-generator" className="btn-primary shrink-0">
            + Generate More
          </Link>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Total Opportunities", value: d.total, icon: Briefcase, color: "bg-stone-50 text-stone-700" },
            { label: "Total Views", value: d.totalViews, icon: Eye, color: "bg-blue-50 text-blue-700" },
            { label: "Total Interests", value: d.totalInterests, icon: Heart, color: "bg-rose-50 text-rose-700" },
            { label: "Avg Conversion", value: `${d.avgConversion}%`, icon: Activity, color: "bg-teal-50 text-teal-700" },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card-base p-4">
              <div className={`inline-flex p-2 rounded-lg mb-2 ${color}`}><Icon size={14} /></div>
              <div className="text-xl font-display font-extrabold text-ink">{value}</div>
              <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-0.5">{label}</div>
            </div>
          ))}
        </div>

        {/* Top Performing */}
        <div className="card-base overflow-hidden">
          <div className="p-5 border-b border-stone-100 flex items-center gap-2">
            <TrendingUp size={15} className="text-green-500" />
            <h3 className="font-display font-bold text-ink text-sm">Top Performing Opportunities</h3>
          </div>
          {d.topPerforming.length === 0 ? (
            <p className="p-6 text-sm text-stone-400 italic">No data yet. Views populate from page_views and opportunity_views tables.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-[12px]">
                <thead>
                  <tr className="border-b border-stone-200">
                    {["#", "Title", "Sector", "District", "Views", "Interests", "Conv. %"].map((h) => (
                      <th key={h} className="text-left py-3 px-4 text-[10px] text-stone-400 uppercase tracking-widest whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {d.topPerforming.map((o, i) => (
                    <tr key={o.id} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
                      <td className="py-3 px-4 text-stone-400 font-bold">{i + 1}</td>
                      <td className="py-3 px-4 max-w-[180px]">
                        <p className="font-semibold text-ink truncate">{o.title}</p>
                      </td>
                      <td className="py-3 px-4">
                        <span className="chip bg-amber-50 text-amber-700 text-[10px] capitalize">{o.category || "—"}</span>
                      </td>
                      <td className="py-3 px-4 text-stone-500 capitalize">{o.district || "—"}</td>
                      <td className="py-3 px-4 w-32">
                        <PerformanceBar value={o.views} max={d.maxViews} color="teal" />
                      </td>
                      <td className="py-3 px-4 w-32">
                        <PerformanceBar value={o.interest} max={d.maxInterest} color="amber" />
                      </td>
                      <td className="py-3 px-4">
                        <span className={`chip text-[11px] font-bold ${o.conversionRate >= 10 ? "bg-green-100 text-green-700" : "bg-stone-100 text-stone-500"}`}>
                          {o.conversionRate}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Under-performing */}
        {d.underPerforming.length > 0 && (
          <div className="card-base overflow-hidden">
            <div className="p-5 border-b border-stone-100 flex items-center gap-2">
              <TrendingDown size={15} className="text-red-400" />
              <h3 className="font-display font-bold text-ink text-sm">Underperforming (Views but No Interest)</h3>
            </div>
            <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {d.underPerforming.map((o) => (
                <div key={o.id} className="flex items-center gap-3 p-3 bg-red-50/30 rounded-xl border border-red-100">
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-semibold text-ink truncate">{o.title}</p>
                    <p className="text-[11px] text-stone-400 mt-0.5">
                      {o.views} views · 0 interests · {o.district || "no district"}
                    </p>
                  </div>
                  <span className="chip bg-red-50 text-red-500 border border-red-200 text-[10px] shrink-0">0% conv.</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* District + Sector side by side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <MapPin size={14} className="text-teal-500" /> District Performance
            </h3>
            {d.topDistricts.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No district data yet.</p>
            ) : (
              <div className="space-y-3">
                {d.topDistricts.map((dist) => (
                  <div key={dist.name}>
                    <div className="flex justify-between text-[12px] mb-1">
                      <span className="font-semibold text-ink capitalize">{dist.name}</span>
                      <span className="text-stone-500">{dist.count} opps · {dist.interest} interests</span>
                    </div>
                    <PerformanceBar value={dist.interest} max={d.maxDistInterest} color="teal" />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <Layers size={14} className="text-amber-500" /> Sector Performance
            </h3>
            {d.topSectors.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No sector data yet.</p>
            ) : (
              <div className="space-y-3">
                {d.topSectors.map((sec) => (
                  <div key={sec.name}>
                    <div className="flex justify-between text-[12px] mb-1">
                      <span className="font-semibold text-ink capitalize">{sec.name}</span>
                      <span className="text-stone-500">{sec.count} opps · {sec.interest} interests</span>
                    </div>
                    <PerformanceBar value={sec.interest} max={d.maxSecInterest} color="amber" />
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

      </div>
    </AdminShell>
  );
}
