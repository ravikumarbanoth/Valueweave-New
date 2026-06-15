import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import { Brain, Search, TrendingUp, MessageSquare, MapPin, Layers } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "User Intent | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function FrequencyTable({ rows, emptyMsg }) {
  if (!rows || rows.length === 0) {
    return <p className="text-[13px] text-stone-400 italic">{emptyMsg}</p>;
  }
  const max = Math.max(...rows.map((r) => r.count), 1);
  return (
    <div className="space-y-2">
      {rows.map((row, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="w-5 text-[11px] font-bold text-stone-400 text-center shrink-0">{i + 1}</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[13px] font-semibold text-ink capitalize truncate">{row.label}</span>
              {row.badge && (
                <span className="chip bg-stone-100 text-stone-500 text-[10px] shrink-0">{row.badge}</span>
              )}
            </div>
            <div className="bg-stone-100 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-amber-400 h-full rounded-full"
                style={{ width: `${Math.max((row.count / max) * 100, 3)}%` }}
              />
            </div>
          </div>
          <div className="w-10 text-[12px] font-bold text-stone-700 text-right shrink-0">{row.count}</div>
        </div>
      ))}
    </div>
  );
}

function SectionCard({ icon: Icon, iconColor, title, subtitle, children }) {
  return (
    <div className="card-base p-5">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={16} className={iconColor} />
        <h3 className="font-display font-bold text-ink text-sm">{title}</h3>
      </div>
      {subtitle && <p className="text-[11px] text-stone-400 mb-4">{subtitle}</p>}
      <div className="mt-4">{children}</div>
    </div>
  );
}

async function fetchIntentData() {
  try {
    const sb = createClient();

    const [
      { data: searches },
      { data: requests },
      { data: feedback },
      { data: interests },
      { data: oppDistricts },
      { data: collabSectors },
    ] = await Promise.all([
      sb.from("search_events").select("query,district,sector").order("created_at", { ascending: false }).limit(2000),
      sb.from("user_requests").select("title,type,sector,district,status").order("created_at", { ascending: false }).limit(1000),
      sb.from("user_feedback").select("type,message,page,status,created_at").order("created_at", { ascending: false }).limit(200),
      sb.from("opportunity_interests").select("opportunity_id,created_at").limit(2000),
      sb.from("opportunities").select("district").not("district", "is", null).limit(2000),
      sb.from("collaborator_profiles").select("top_sectors").limit(500),
    ]);

    // Top search keywords
    const kwMap = {};
    (searches || []).forEach(({ query }) => {
      if (query) {
        const kw = query.toLowerCase().trim();
        kwMap[kw] = (kwMap[kw] || 0) + 1;
      }
    });
    const topKeywords = Object.entries(kwMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([label, count]) => ({ label, count }));

    // Top requested topics (from user_requests)
    const reqMap = {};
    (requests || []).forEach(({ title }) => {
      const key = title.toLowerCase().trim();
      reqMap[key] = (reqMap[key] || 0) + 1;
    });
    const topRequests = Object.entries(reqMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([label, count]) => ({ label, count }));

    // Top requested by type (idea/opportunity/research etc)
    const typeMap = {};
    (requests || []).forEach(({ type }) => {
      if (type) typeMap[type] = (typeMap[type] || 0) + 1;
    });
    const topRequestTypes = Object.entries(typeMap)
      .sort((a, b) => b[1] - a[1])
      .map(([label, count]) => ({ label, count }));

    // Top district interest (from searches + requests + opportunity clicks)
    const distMap = {};
    (searches || []).forEach(({ district }) => {
      if (district) distMap[district] = (distMap[district] || 0) + 2;
    });
    (requests || []).forEach(({ district }) => {
      if (district) distMap[district] = (distMap[district] || 0) + 3;
    });
    (oppDistricts || []).forEach(({ district }) => {
      if (district) distMap[district] = (distMap[district] || 0) + 1;
    });
    const topDistricts = Object.entries(distMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, count]) => ({ label, count }));

    // Top sector interest
    const sectorMap = {};
    (searches || []).forEach(({ sector }) => {
      if (sector) sectorMap[sector] = (sectorMap[sector] || 0) + 2;
    });
    (requests || []).forEach(({ sector }) => {
      if (sector) sectorMap[sector] = (sectorMap[sector] || 0) + 3;
    });
    (collabSectors || []).forEach(({ top_sectors }) => {
      (top_sectors || []).forEach((s) => {
        sectorMap[s] = (sectorMap[s] || 0) + 1;
      });
    });
    const topSectors = Object.entries(sectorMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, count]) => ({ label, count }));

    // Unread feedback
    const unreadFeedback = (feedback || []).filter((f) => f.status === "unread");

    // Total signals
    const totalSignals =
      (searches?.length || 0) +
      (requests?.length || 0) +
      (feedback?.length || 0) +
      (interests?.length || 0);

    return {
      topKeywords,
      topRequests,
      topRequestTypes,
      topDistricts,
      topSectors,
      recentFeedback: feedback?.slice(0, 10) || [],
      unreadCount: unreadFeedback.length,
      totalSignals,
      totalSearches: searches?.length || 0,
      totalRequests: requests?.length || 0,
      totalFeedback: feedback?.length || 0,
      totalInterests: interests?.length || 0,
    };
  } catch (e) {
    console.error("Intent fetch error:", e);
    return {
      topKeywords: [], topRequests: [], topRequestTypes: [], topDistricts: [], topSectors: [],
      recentFeedback: [], unreadCount: 0, totalSignals: 0,
      totalSearches: 0, totalRequests: 0, totalFeedback: 0, totalInterests: 0,
    };
  }
}

export default async function UserIntentPage() {
  const d = await fetchIntentData();

  const EMPTY = "No data yet — signals will populate as users search, request, and interact with content.";

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-teal-100 text-teal-700 border border-teal-200">USER INTENT</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">User Intent Dashboard</h1>
          <p className="text-stone-500 text-sm mt-1">
            Understand what users actually want — then build it.
          </p>
        </div>

        {/* Signal Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Search Events", value: d.totalSearches, icon: Search, color: "amber" },
            { label: "Requests", value: d.totalRequests, icon: TrendingUp, color: "teal" },
            { label: "Feedback", value: d.totalFeedback, icon: MessageSquare, color: "rose" },
            { label: "Opp. Interests", value: d.totalInterests, icon: Brain, color: "blue" },
          ].map(({ label, value, icon: Icon, color }) => {
            const bg = { amber: "bg-amber-50 text-amber-700", teal: "bg-teal-50 text-teal-700", rose: "bg-rose-50 text-rose-700", blue: "bg-blue-50 text-blue-700" };
            return (
              <div key={label} className="card-base p-4">
                <div className={`inline-flex p-2 rounded-lg mb-2 ${bg[color]}`}><Icon size={14} /></div>
                <div className="text-xl font-display font-extrabold text-ink">{value.toLocaleString()}</div>
                <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-0.5">{label}</div>
              </div>
            );
          })}
        </div>

        {/* What should I publish next? */}
        <div className="card-base p-5 border-l-4 border-amber-400 bg-amber-50">
          <h3 className="font-display font-bold text-amber-800 mb-2 flex items-center gap-2">
            <Brain size={16} /> What should I publish next?
          </h3>
          {d.totalSignals === 0 ? (
            <p className="text-sm text-amber-700">
              No user signals yet. As users search and request content, the top opportunity will appear here automatically.
            </p>
          ) : (
            <div className="space-y-1">
              {d.topRequests.slice(0, 3).map((r, i) => (
                <p key={i} className="text-sm text-amber-800">
                  <strong>#{i + 1}</strong> &quot;{r.label}&quot; — requested {r.count} time{r.count !== 1 ? "s" : ""}
                </p>
              ))}
            </div>
          )}
        </div>

        {/* Main Grids */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <SectionCard
            icon={Search}
            iconColor="text-amber-500"
            title="Top Searched Keywords"
            subtitle="Most frequent search queries across all pages"
          >
            <FrequencyTable rows={d.topKeywords} emptyMsg={EMPTY} />
          </SectionCard>

          <SectionCard
            icon={TrendingUp}
            iconColor="text-teal-500"
            title="Top Requested Topics"
            subtitle="What users explicitly request via the Request form"
          >
            <FrequencyTable rows={d.topRequests} emptyMsg={EMPTY} />
          </SectionCard>

          <SectionCard
            icon={MapPin}
            iconColor="text-blue-500"
            title="Top District Interest"
            subtitle="Districts most mentioned in searches and requests"
          >
            <FrequencyTable rows={d.topDistricts} emptyMsg={EMPTY} />
          </SectionCard>

          <SectionCard
            icon={Layers}
            iconColor="text-purple-500"
            title="Top Sector Interest"
            subtitle="Sectors most searched, requested, and selected in profiles"
          >
            <FrequencyTable rows={d.topSectors} emptyMsg={EMPTY} />
          </SectionCard>

          <SectionCard
            icon={MessageSquare}
            iconColor="text-rose-500"
            title="Recent Feedback"
            subtitle="Latest user feedback sorted by recency"
          >
            {d.recentFeedback.length === 0 ? (
              <p className="text-[13px] text-stone-400 italic">{EMPTY}</p>
            ) : (
              <ul className="space-y-3">
                {d.recentFeedback.map((f, i) => (
                  <li key={i} className="flex gap-3 items-start border-b border-stone-100 pb-3 last:border-0 last:pb-0">
                    <span className={`chip text-[10px] shrink-0 ${f.status === "unread" ? "bg-rose-50 text-rose-600 border border-rose-200" : "bg-stone-100 text-stone-500"}`}>
                      {f.status === "unread" ? "NEW" : f.status}
                    </span>
                    <div>
                      <p className="text-[13px] text-stone-700">{f.message}</p>
                      {f.page && <p className="text-[11px] text-stone-400 mt-0.5">Page: {f.page}</p>}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>

          <SectionCard
            icon={Layers}
            iconColor="text-stone-500"
            title="Request Types Breakdown"
            subtitle="Distribution of what type of content users request"
          >
            <FrequencyTable rows={d.topRequestTypes} emptyMsg={EMPTY} />
          </SectionCard>

        </div>
      </div>
    </AdminShell>
  );
}
