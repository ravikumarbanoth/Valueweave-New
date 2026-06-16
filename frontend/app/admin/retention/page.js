import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { Clock, Users, TrendingUp, Bell, ArrowRight, AlertCircle, Zap, MapPin } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Retention | ValueWeave Admin",
  robots: { index: false, follow: false },
};

async function fetchRetentionData() {
  try {
    const sb = createClient();
    const now = new Date();
    const d7   = new Date(now - 7  * 86400000).toISOString();
    const d14  = new Date(now - 14 * 86400000).toISOString();
    const d30  = new Date(now - 30 * 86400000).toISOString();
    const d60  = new Date(now - 60 * 86400000).toISOString();

    const [
      { data: allProfiles },
      { data: recentSessions },
      { data: topDistrictSearches },
      { data: topSectorSearches },
      { data: recentArticles },
      { data: recentOpps },
      { data: weeklyDigests },
    ] = await Promise.all([
      sb.from("profiles").select("id,name,email,created_at,district,top_sectors").limit(2000),
      sb.from("visitor_sessions").select("visitor_id,created_at").gte("created_at", d30).limit(5000),
      sb.from("search_events").select("district").not("district", "is", null).gte("created_at", d7).limit(1000),
      sb.from("search_events").select("sector").not("sector", "is", null).gte("created_at", d7).limit(1000),
      sb.from("research_articles").select("title,slug,district,category,created_at").eq("status", "published").order("created_at", { ascending: false }).limit(5),
      sb.from("opportunities").select("title,category,district,created_at").eq("status", "open").order("created_at", { ascending: false }).limit(5),
      sb.from("weekly_digests").select("*").order("week_start", { ascending: false }).limit(10),
    ]);

    const profiles = allProfiles || [];
    const sessions = recentSessions || [];

    // Cohort: users who registered before d7 (not brand new) but have no sessions in last 7d
    // We approximate: users registered before d7 = potentially inactive
    // (Exact per-user session tracking would need user_id in sessions, which we have as nullable)
    const registeredBefore7  = profiles.filter((p) => new Date(p.created_at) < new Date(d7)).length;
    const registeredBefore14 = profiles.filter((p) => new Date(p.created_at) < new Date(d14)).length;
    const registeredBefore30 = profiles.filter((p) => new Date(p.created_at) < new Date(d30)).length;

    // Active sessions per window
    const sessionsIn7  = sessions.filter((s) => new Date(s.created_at) >= new Date(d7)).length;
    const sessionsIn14 = sessions.filter((s) => new Date(s.created_at) >= new Date(d14)).length;
    const sessionsIn30 = sessions.length;

    // Top districts by recent search interest
    const districtMap = {};
    (topDistrictSearches || []).forEach(({ district }) => {
      districtMap[district] = (districtMap[district] || 0) + 1;
    });
    const topDistricts = Object.entries(districtMap)
      .sort((a, b) => b[1] - a[1]).slice(0, 5)
      .map(([d, count]) => ({ d, count }));

    // Top sectors by recent search interest
    const sectorMap = {};
    (topSectorSearches || []).forEach(({ sector }) => {
      sectorMap[sector] = (sectorMap[sector] || 0) + 1;
    });
    const topSectors = Object.entries(sectorMap)
      .sort((a, b) => b[1] - a[1]).slice(0, 5)
      .map(([s, count]) => ({ s, count }));

    // Generate re-engagement recommendations
    const recommendations = [];

    if (topDistricts[0]) {
      recommendations.push({
        title: `Send ${topDistricts[0].d} District Update`,
        reason: `${topDistricts[0].count} searches for ${topDistricts[0].d} in last 7 days`,
        action: "Create notification for district subscribers",
        href: "/admin/announcements",
        priority: "high",
      });
    }

    if (topSectors[0]) {
      recommendations.push({
        title: `Send ${topSectors[0].s} Opportunity Alert`,
        reason: `High search interest in ${topSectors[0].s} sector`,
        action: "Generate opportunities in this sector",
        href: "/admin/opportunity-generator",
        priority: "high",
      });
    }

    if ((recentArticles || []).length < 2) {
      recommendations.push({
        title: "Publish New Research Article",
        reason: "Low recent article count — drives returning visitor traffic",
        action: "Write and publish a new article",
        href: "/admin/research/new",
        priority: "normal",
      });
    }

    if (registeredBefore14 > 10 && sessionsIn7 < registeredBefore14 * 0.3) {
      recommendations.push({
        title: "Re-engage Older Users",
        reason: "Session rate below 30% for users registered 14+ days ago",
        action: "Send announcement about new features or content",
        href: "/admin/announcements",
        priority: "normal",
      });
    }

    recommendations.push({
      title: "Generate Weekly Digest",
      reason: "Weekly digests increase return visit rate significantly",
      action: "Preview and publish this week's digest",
      href: "/admin/engagement",
      priority: "low",
    });

    return {
      cohorts: [
        { label: "7-day inactive",  count: Math.max(0, registeredBefore7  - sessionsIn7),  total: registeredBefore7,  window: "7d"  },
        { label: "14-day inactive", count: Math.max(0, registeredBefore14 - sessionsIn14), total: registeredBefore14, window: "14d" },
        { label: "30-day inactive", count: Math.max(0, registeredBefore30 - sessionsIn30), total: registeredBefore30, window: "30d" },
      ],
      topDistricts, topSectors,
      recentArticles: recentArticles || [],
      recentOpps: recentOpps || [],
      weeklyDigests: weeklyDigests || [],
      recommendations,
      totalProfiles: profiles.length,
    };
  } catch (e) {
    console.error("Retention fetch error:", e);
    return {
      cohorts: [], topDistricts: [], topSectors: [],
      recentArticles: [], recentOpps: [], weeklyDigests: [],
      recommendations: [], totalProfiles: 0,
    };
  }
}

const PRIORITY_STYLE = {
  high:   "border-l-2 border-rose-400 bg-rose-50",
  normal: "border-l-2 border-amber-300 bg-amber-50",
  low:    "border-l-2 border-stone-200 bg-stone-50",
};
const PRIORITY_BADGE = {
  high:   "bg-rose-100 text-rose-700",
  normal: "bg-amber-100 text-amber-700",
  low:    "bg-stone-100 text-stone-500",
};

export default async function RetentionPage() {
  const d = await fetchRetentionData();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-blue-100 text-blue-700 border border-blue-200">RETENTION</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2 flex items-center gap-2">
            <Clock size={22} className="text-blue-500" />
            Re-Engagement Automation
          </h1>
          <p className="text-stone-500 text-sm mt-1">
            Inactivity cohorts and automated re-engagement recommendations
          </p>
        </div>

        {/* Inactivity Cohorts */}
        <div>
          <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">
            Inactivity Cohorts (estimated)
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {d.cohorts.map(({ label, count, total, window }) => {
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              const severity = pct > 70 ? "rose" : pct > 40 ? "amber" : "green";
              const SEV = { rose: "text-rose-600 bg-rose-50", amber: "text-amber-600 bg-amber-50", green: "text-green-600 bg-green-50" };
              return (
                <div key={window} className="card-base p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Clock size={14} className="text-stone-400" />
                    <span className="text-[12px] font-semibold text-stone-500 uppercase tracking-widest">{label}</span>
                  </div>
                  <div className="text-3xl font-display font-extrabold text-ink mb-1">{count.toLocaleString()}</div>
                  <p className="text-[11px] text-stone-400">of {total} registered users</p>
                  <div className="mt-3">
                    <div className="bg-stone-100 rounded-full h-2 overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${severity === "rose" ? "bg-rose-400" : severity === "amber" ? "bg-amber-400" : "bg-green-400"}`}
                        style={{ width: `${pct}%` }} />
                    </div>
                    <span className={`text-[11px] font-bold mt-1 inline-block px-2 py-0.5 rounded-full ${SEV[severity]}`}>
                      {pct}% dormant
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recommendations */}
        <div>
          <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">
            Re-Engagement Recommendations
          </p>
          {d.recommendations.length === 0 ? (
            <div className="card-base p-6 text-center">
              <AlertCircle size={28} className="text-stone-200 mx-auto mb-3" />
              <p className="text-sm text-stone-400 italic">Recommendations appear based on real user activity data.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {d.recommendations.map((rec, i) => (
                <Link
                  key={i}
                  href={rec.href}
                  className={`flex items-start justify-between gap-4 p-4 rounded-xl ${PRIORITY_STYLE[rec.priority]} hover:shadow-sm transition-shadow group`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${PRIORITY_BADGE[rec.priority]}`}>
                        {rec.priority.toUpperCase()}
                      </span>
                      <p className="font-display font-bold text-ink text-sm">{rec.title}</p>
                    </div>
                    <p className="text-[12px] text-stone-500">{rec.reason}</p>
                    <p className="text-[11px] text-stone-400 mt-1">→ {rec.action}</p>
                  </div>
                  <ArrowRight size={14} className="text-stone-300 group-hover:text-amber-500 shrink-0 mt-1" />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Demand Signals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <MapPin size={14} className="text-teal-500" /> Top District Interest (7d)
            </h3>
            {d.topDistricts.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No district search data yet.</p>
            ) : (
              <div className="space-y-2">
                {d.topDistricts.map(({ d: dist, count }) => (
                  <div key={dist} className="flex items-center gap-3">
                    <span className="flex-1 text-[13px] text-stone-600 capitalize">{dist}</span>
                    <span className="text-[12px] font-bold text-stone-700">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <TrendingUp size={14} className="text-amber-500" /> Top Sector Interest (7d)
            </h3>
            {d.topSectors.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No sector search data yet.</p>
            ) : (
              <div className="space-y-2">
                {d.topSectors.map(({ s: sec, count }) => (
                  <div key={sec} className="flex items-center gap-3">
                    <span className="flex-1 text-[13px] text-stone-600 capitalize">{sec}</span>
                    <span className="text-[12px] font-bold text-stone-700">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Weekly Digest Preview */}
        <div className="card-base p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-bold text-ink text-sm flex items-center gap-2">
              <Zap size={14} className="text-amber-500" /> Weekly Digest Preview
            </h3>
            <span className="chip bg-stone-100 text-stone-500 text-[10px]">Auto-generated</span>
          </div>
          {d.weeklyDigests.length === 0 ? (
            <div className="bg-stone-50 rounded-xl p-4 text-center">
              <p className="text-sm text-stone-400 italic mb-2">No digests generated yet.</p>
              <p className="text-[12px] text-stone-300">Run migration 007 and digests will be stored when generated.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-[12px]">
                <thead>
                  <tr className="border-b border-stone-200">
                    {["Week", "District/Sector", "Opps", "Articles", "Collabs"].map((h) => (
                      <th key={h} className="text-left py-2 px-3 text-[10px] text-stone-400 uppercase tracking-widest">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {d.weeklyDigests.map((wd) => (
                    <tr key={wd.id} className="border-b border-stone-100">
                      <td className="py-2 px-3">{wd.week_start}</td>
                      <td className="py-2 px-3 capitalize">{wd.district || wd.sector || "—"}</td>
                      <td className="py-2 px-3 font-bold">{wd.new_opps}</td>
                      <td className="py-2 px-3 font-bold">{wd.new_articles}</td>
                      <td className="py-2 px-3 font-bold">{wd.new_collabs}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </AdminShell>
  );
}
