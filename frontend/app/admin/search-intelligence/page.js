import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { Search, TrendingUp, AlertCircle, BarChart2, MapPin, Layers, Info } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Search Intelligence | ValueWeave Admin",
  robots: { index: false, follow: false },
};

const TIME_FILTERS = [
  { label: "7 days", days: 7 },
  { label: "30 days", days: 30 },
  { label: "90 days", days: 90 },
  { label: "All time", days: 0 },
];

function BarRow({ rank, label, count, max, sub }) {
  const pct = max > 0 ? Math.max((count / max) * 100, 2) : 2;
  return (
    <div className="flex items-center gap-3">
      <div className="w-5 text-[11px] font-bold text-stone-300 text-center shrink-0">{rank}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-[13px] font-semibold text-ink truncate capitalize">{label}</span>
          {sub && <span className="chip bg-stone-100 text-stone-400 text-[10px] shrink-0">{sub}</span>}
        </div>
        <div className="bg-stone-100 rounded-full h-2 overflow-hidden">
          <div className="bg-amber-400 h-full rounded-full" style={{ width: `${pct}%` }} />
        </div>
      </div>
      <div className="w-10 text-[12px] font-bold text-stone-700 text-right shrink-0">{count}</div>
    </div>
  );
}

function SectionCard({ icon: Icon, iconColor, title, subtitle, children }) {
  return (
    <div className="card-base p-5">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={15} className={iconColor} />
        <h3 className="font-display font-bold text-ink text-sm">{title}</h3>
      </div>
      {subtitle && <p className="text-[11px] text-stone-400 mb-4">{subtitle}</p>}
      <div className="mt-4">{children}</div>
    </div>
  );
}

async function fetchSearchData(since) {
  try {
    const sb = createClient();
    let q = sb.from("search_events").select("query,page,results_count,district,sector,created_at").limit(5000);
    if (since) q = q.gte("created_at", since);

    const { data: events, count: totalCount } = await q;

    // Older window for trend comparison (same duration before `since`)
    let prevEvents = [];
    if (since) {
      const sinceDate = new Date(since);
      const windowMs = Date.now() - sinceDate.getTime();
      const prevSince = new Date(sinceDate.getTime() - windowMs).toISOString();
      const { data } = await sb
        .from("search_events")
        .select("query,created_at")
        .gte("created_at", prevSince)
        .lt("created_at", since)
        .limit(5000);
      prevEvents = data || [];
    }

    const rows = events || [];

    // Query frequency map
    const qMap = {};
    rows.forEach(({ query }) => {
      if (query) {
        const k = query.toLowerCase().trim();
        qMap[k] = (qMap[k] || 0) + 1;
      }
    });

    // Previous window map (for trend)
    const prevMap = {};
    prevEvents.forEach(({ query }) => {
      if (query) prevMap[query.toLowerCase().trim()] = (prevMap[query.toLowerCase().trim()] || 0) + 1;
    });

    const topSearches = Object.entries(qMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([kw, count]) => {
        const prev = prevMap[kw] || 0;
        const trend = prev > 0 ? ((count - prev) / prev) * 100 : null;
        return { keyword: kw, count, trend };
      });

    // Trending = biggest growth
    const trending = [...topSearches]
      .filter((s) => s.trend !== null)
      .sort((a, b) => (b.trend || 0) - (a.trend || 0))
      .slice(0, 8);

    // No-results searches
    const noResults = Object.entries(
      rows.filter((r) => r.results_count === 0 && r.query)
        .reduce((m, { query }) => {
          const k = query.toLowerCase().trim();
          m[k] = (m[k] || 0) + 1;
          return m;
        }, {})
    ).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([keyword, count]) => ({ keyword, count }));

    // By page
    const pageMap = {};
    rows.forEach(({ page }) => {
      if (page) pageMap[page] = (pageMap[page] || 0) + 1;
    });
    const byPage = Object.entries(pageMap).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([label, count]) => ({ label, count }));

    // District interest
    const distMap = {};
    rows.forEach(({ district }) => {
      if (district) distMap[district] = (distMap[district] || 0) + 1;
    });
    const byDistrict = Object.entries(distMap).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([label, count]) => ({ label, count }));

    // Sector interest
    const secMap = {};
    rows.forEach(({ sector }) => {
      if (sector) secMap[sector] = (secMap[sector] || 0) + 1;
    });
    const bySector = Object.entries(secMap).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([label, count]) => ({ label, count }));

    // Hour-of-day distribution (for heatmap)
    const hourMap = Array(24).fill(0);
    rows.forEach(({ created_at }) => {
      const h = new Date(created_at).getHours();
      hourMap[h]++;
    });

    return {
      total: rows.length,
      uniqueTerms: Object.keys(qMap).length,
      noResultsCount: rows.filter((r) => r.results_count === 0).length,
      topSearches,
      trending,
      noResults,
      byPage,
      byDistrict,
      bySector,
      hourMap,
      hasData: rows.length > 0,
    };
  } catch (e) {
    console.error("Search intelligence error:", e);
    return {
      total: 0, uniqueTerms: 0, noResultsCount: 0,
      topSearches: [], trending: [], noResults: [], byPage: [], byDistrict: [], bySector: [],
      hourMap: Array(24).fill(0), hasData: false,
    };
  }
}

export default async function SearchIntelligencePage({ searchParams }) {
  const days = parseInt(searchParams?.days) || 30;
  const since = days > 0 ? new Date(Date.now() - days * 86400000).toISOString() : null;
  const d = await fetchSearchData(since);

  const EMPTY = "No data yet. Add trackSearch() calls from search inputs using lib/search-tracking.js.";
  const maxTop = Math.max(...d.topSearches.map((s) => s.count), 1);
  const maxDist = Math.max(...d.byDistrict.map((s) => s.count), 1);
  const maxSec = Math.max(...d.bySector.map((s) => s.count), 1);
  const maxHour = Math.max(...d.hourMap, 1);

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header + Time Filter */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-blue-100 text-blue-700 border border-blue-200">SEARCH INTELLIGENCE</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Search Intelligence Engine</h1>
            <p className="text-stone-500 text-sm mt-1">Every search performed across Ideas, Research, Districts, Opportunities, and Collaborators</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            {TIME_FILTERS.map(({ label, days: d }) => (
              <Link
                key={d}
                href={`?days=${d}`}
                className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors ${
                  days === d ? "bg-amber-500 text-white" : "bg-white border border-stone-200 text-stone-500 hover:border-amber-500"
                }`}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>

        {/* Integration note */}
        {!d.hasData && (
          <div className="card-base p-4 bg-blue-50 border-blue-200 flex items-start gap-3">
            <Info size={15} className="text-blue-500 mt-0.5 shrink-0" />
            <div className="text-[12px] text-blue-800 space-y-1">
              <p><strong>How to activate search tracking:</strong> Import <code>trackSearch</code> from <code>lib/search-tracking.js</code> and call it in your client components&apos; search handlers.</p>
              <p className="font-mono text-[11px] bg-blue-100 rounded px-2 py-1 mt-1">
                {"import { trackSearch } from '@/lib/search-tracking';"}<br />
                {"await trackSearch({ query, page: 'ideas', resultsCount });"}
              </p>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Total Searches", value: d.total, color: "bg-blue-50 text-blue-700", icon: Search },
            { label: "Unique Terms", value: d.uniqueTerms, color: "bg-teal-50 text-teal-700", icon: BarChart2 },
            { label: "No-Result Searches", value: d.noResultsCount, color: "bg-red-50 text-red-700", icon: AlertCircle },
            { label: "Active Pages", value: d.byPage.length, color: "bg-purple-50 text-purple-700", icon: Layers },
          ].map(({ label, value, color, icon: Icon }) => (
            <div key={label} className="card-base p-4">
              <div className={`inline-flex p-2 rounded-lg mb-2 ${color}`}><Icon size={14} /></div>
              <div className="text-xl font-display font-extrabold text-ink">{value}</div>
              <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-0.5">{label}</div>
            </div>
          ))}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <SectionCard icon={Search} iconColor="text-amber-500" title="Top Searches" subtitle="Most frequent queries across all pages">
            {d.topSearches.length === 0 ? <p className="text-sm text-stone-400 italic">{EMPTY}</p> : (
              <div className="space-y-2.5">
                {d.topSearches.map((s, i) => (
                  <BarRow key={s.keyword} rank={i + 1} label={s.keyword} count={s.count} max={maxTop}
                    sub={s.trend !== null ? `${s.trend >= 0 ? "+" : ""}${Math.round(s.trend)}%` : null} />
                ))}
              </div>
            )}
          </SectionCard>

          <SectionCard icon={TrendingUp} iconColor="text-teal-500" title="Trending Searches" subtitle="Biggest growth vs. previous period">
            {d.trending.length === 0 ? <p className="text-sm text-stone-400 italic">Need two periods of data to compute trends.</p> : (
              <div className="space-y-2.5">
                {d.trending.map((s, i) => (
                  <BarRow key={s.keyword} rank={i + 1} label={s.keyword} count={s.count} max={maxTop}
                    sub={s.trend !== null ? `↑${Math.round(s.trend)}%` : null} />
                ))}
              </div>
            )}
          </SectionCard>

          <SectionCard icon={AlertCircle} iconColor="text-red-500" title="No-Results Searches" subtitle="Queries that returned zero results — content gaps">
            {d.noResults.length === 0 ? <p className="text-sm text-stone-400 italic">No zero-result searches recorded.</p> : (
              <div className="space-y-2.5">
                {d.noResults.map((s, i) => (
                  <div key={s.keyword} className="flex items-center gap-3">
                    <div className="w-5 text-[11px] font-bold text-stone-300 text-center shrink-0">{i + 1}</div>
                    <div className="flex-1 flex items-center gap-2">
                      <span className="text-[13px] font-semibold text-ink capitalize">{s.keyword}</span>
                      <Link href={`/admin/content-opportunities`} className="text-[10px] text-amber-600 hover:underline font-semibold">Create content →</Link>
                    </div>
                    <div className="w-10 text-[12px] font-bold text-red-600 text-right shrink-0">{s.count}×</div>
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          <SectionCard icon={Layers} iconColor="text-purple-500" title="Searches by Page" subtitle="Which section of the site has the most search activity">
            {d.byPage.length === 0 ? <p className="text-sm text-stone-400 italic">{EMPTY}</p> : (
              <div className="space-y-2.5">
                {d.byPage.map((p, i) => {
                  const max = Math.max(...d.byPage.map((x) => x.count), 1);
                  return <BarRow key={p.label} rank={i + 1} label={p.label} count={p.count} max={max} />;
                })}
              </div>
            )}
          </SectionCard>

          <SectionCard icon={MapPin} iconColor="text-teal-500" title="District Search Interest" subtitle="Districts most mentioned in search queries">
            {d.byDistrict.length === 0 ? <p className="text-sm text-stone-400 italic">{EMPTY}</p> : (
              <div className="space-y-2.5">
                {d.byDistrict.map((s, i) => <BarRow key={s.label} rank={i + 1} label={s.label} count={s.count} max={maxDist} />)}
              </div>
            )}
          </SectionCard>

          <SectionCard icon={Layers} iconColor="text-blue-500" title="Sector Search Interest" subtitle="Sectors most mentioned in search queries">
            {d.bySector.length === 0 ? <p className="text-sm text-stone-400 italic">{EMPTY}</p> : (
              <div className="space-y-2.5">
                {d.bySector.map((s, i) => <BarRow key={s.label} rank={i + 1} label={s.label} count={s.count} max={maxSec} />)}
              </div>
            )}
          </SectionCard>

        </div>

        {/* Hourly Heatmap */}
        <div className="card-base p-5">
          <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
            <BarChart2 size={14} className="text-stone-400" /> Search Activity by Hour (UTC)
          </h3>
          <div className="flex items-end gap-1 h-16">
            {d.hourMap.map((count, h) => {
              const pct = maxHour > 0 ? (count / maxHour) * 100 : 0;
              return (
                <div key={h} className="flex-1 flex flex-col items-center gap-1" title={`${h}:00 — ${count} searches`}>
                  <div
                    className="w-full bg-amber-400 rounded-t-sm"
                    style={{ height: `${Math.max(pct, 2)}%`, minHeight: count > 0 ? "4px" : "2px", opacity: count > 0 ? 1 : 0.2 }}
                  />
                  {(h % 6 === 0) && <span className="text-[8px] text-stone-400">{h}h</span>}
                </div>
              );
            })}
          </div>
          {!d.hasData && <p className="text-[11px] text-stone-400 mt-2 italic">Heatmap populates once search tracking is active.</p>}
        </div>

      </div>
    </AdminShell>
  );
}
