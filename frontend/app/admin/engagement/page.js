import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import {
  Users, TrendingUp, UserCheck, BookOpen, MessageSquare,
  Star, Eye, Search, ArrowRight, Activity, Zap, Bell,
} from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Engagement Center | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function trend(current, previous) {
  if (!previous) return null;
  const pct = Math.round(((current - previous) / previous) * 100);
  return pct;
}

function TrendBadge({ pct }) {
  if (pct === null || pct === undefined) return null;
  const up = pct >= 0;
  return (
    <span className={`inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
      up ? "bg-green-50 text-green-600" : "bg-rose-50 text-rose-500"
    }`}>
      {up ? "↑" : "↓"}{Math.abs(pct)}%
    </span>
  );
}

function MetricCard({ icon: Icon, label, value, prev, accent = "amber", href }) {
  const pct = trend(value, prev);
  const ACCENT = {
    amber:  "bg-amber-50 text-amber-600",
    teal:   "bg-teal-50 text-teal-600",
    blue:   "bg-blue-50 text-blue-600",
    purple: "bg-purple-50 text-purple-600",
    rose:   "bg-rose-50 text-rose-600",
    green:  "bg-green-50 text-green-600",
  };
  const card = (
    <div className="card-base p-5 hover:shadow-md transition-shadow">
      <div className={`inline-flex p-2 rounded-lg mb-3 ${ACCENT[accent]}`}>
        <Icon size={16} />
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-display font-extrabold text-ink">{value.toLocaleString()}</span>
        <TrendBadge pct={pct} />
      </div>
      <p className="text-[11px] text-stone-400 font-semibold uppercase tracking-widest mt-1">{label}</p>
      {prev !== undefined && (
        <p className="text-[10px] text-stone-300 mt-0.5">prev period: {prev}</p>
      )}
    </div>
  );
  return href ? <Link href={href}>{card}</Link> : <div>{card}</div>;
}

async function fetchEngagement() {
  try {
    const sb = createClient();
    const now = new Date();
    const d7  = new Date(now - 7  * 86400000).toISOString();
    const d14 = new Date(now - 14 * 86400000).toISOString();
    const d30 = new Date(now - 30 * 86400000).toISOString();
    const d60 = new Date(now - 60 * 86400000).toISOString();

    const [
      // 7-day window
      { count: sessions7 },
      { count: searches7 },
      { count: requests7 },
      { count: feedback7 },
      { count: users7 },
      { count: collabs7 },
      { count: interests7 },
      // prev 7-day window (days 8–14)
      { count: sessionsPrev },
      { count: searchesPrev },
      { count: usersPrev },
      { count: collabsPrev },
      // 30-day
      { count: sessions30 },
      { count: users30 },
      // Returning visitor logic: visitor_ids that appear in both 0-7d and 7-14d windows
      { data: recentVisitors },
      { data: prevVisitors },
      // Top engaged content
      { data: topPages },
      { data: topSearches },
      { data: recentQuestions },
    ] = await Promise.all([
      sb.from("visitor_sessions").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("search_events").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("user_requests").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("user_feedback").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("profiles").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("opportunity_interests").select("*", { count: "exact", head: true }).gte("created_at", d7),
      // prev period (d14 to d7)
      sb.from("visitor_sessions").select("*", { count: "exact", head: true }).gte("created_at", d14).lt("created_at", d7),
      sb.from("search_events").select("*", { count: "exact", head: true }).gte("created_at", d14).lt("created_at", d7),
      sb.from("profiles").select("*", { count: "exact", head: true }).gte("created_at", d14).lt("created_at", d7),
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }).gte("created_at", d14).lt("created_at", d7),
      sb.from("visitor_sessions").select("*", { count: "exact", head: true }).gte("created_at", d30),
      sb.from("profiles").select("*", { count: "exact", head: true }).gte("created_at", d30),
      sb.from("visitor_sessions").select("visitor_id").gte("created_at", d7).limit(5000),
      sb.from("visitor_sessions").select("visitor_id").gte("created_at", d14).lt("created_at", d7).limit(5000),
      sb.from("page_views").select("page_slug,page_title").gte("created_at", d7).limit(2000),
      sb.from("search_events").select("query").gte("created_at", d7).limit(2000),
      sb.from("questions").select("id,title,answer_count,upvotes,created_at").eq("status", "open").order("created_at", { ascending: false }).limit(5),
    ]);

    // Returning visitors = visitor_ids in recent window that also appeared in prev window
    const recentSet = new Set((recentVisitors || []).map((r) => r.visitor_id));
    const prevSet   = new Set((prevVisitors   || []).map((r) => r.visitor_id));
    const returningCount = [...recentSet].filter((v) => prevSet.has(v)).length;

    // Top pages
    const pageMap = {};
    (topPages || []).forEach(({ page_slug, page_title }) => {
      pageMap[page_slug] = (pageMap[page_slug] || 0) + 1;
    });
    const topPagesArr = Object.entries(pageMap)
      .sort((a, b) => b[1] - a[1]).slice(0, 6)
      .map(([slug, count]) => ({ slug, count }));

    // Top searches
    const sqMap = {};
    (topSearches || []).forEach(({ query }) => {
      if (query) sqMap[query] = (sqMap[query] || 0) + 1;
    });
    const topSearchArr = Object.entries(sqMap)
      .sort((a, b) => b[1] - a[1]).slice(0, 6)
      .map(([q, count]) => ({ q, count }));

    return {
      sessions7: sessions7 || 0,    sessionsPrev: sessionsPrev || 0,
      searches7: searches7 || 0,    searchesPrev: searchesPrev || 0,
      requests7: requests7 || 0,
      feedback7: feedback7 || 0,
      users7:    users7    || 0,    usersPrev: usersPrev || 0,
      collabs7:  collabs7  || 0,    collabsPrev: collabsPrev || 0,
      interests7: interests7 || 0,
      returningCount,
      sessions30: sessions30 || 0,
      users30:    users30    || 0,
      topPagesArr, topSearchArr,
      recentQuestions: recentQuestions || [],
    };
  } catch (e) {
    console.error("Engagement fetch error:", e);
    return {
      sessions7: 0, sessionsPrev: 0, searches7: 0, searchesPrev: 0,
      requests7: 0, feedback7: 0, users7: 0, usersPrev: 0,
      collabs7: 0, collabsPrev: 0, interests7: 0, returningCount: 0,
      sessions30: 0, users30: 0, topPagesArr: [], topSearchArr: [],
      recentQuestions: [],
    };
  }
}

export default async function EngagementPage() {
  const d = await fetchEngagement();

  const METRICS_7D = [
    { icon: Eye,          label: "Visitor Sessions (7d)",  value: d.sessions7,  prev: d.sessionsPrev, accent: "amber",  href: "/admin/analytics" },
    { icon: Users,        label: "Returning Visitors (7d)", value: d.returningCount, prev: undefined,  accent: "teal" },
    { icon: Users,        label: "New Registrations (7d)", value: d.users7,     prev: d.usersPrev,    accent: "blue",   href: "/admin/analytics" },
    { icon: UserCheck,    label: "Collab Profiles (7d)",   value: d.collabs7,   prev: d.collabsPrev,  accent: "purple", href: "/admin/matches" },
    { icon: Star,         label: "Opp. Interests (7d)",    value: d.interests7, prev: undefined,       accent: "amber",  href: "/admin/opportunity-performance" },
    { icon: Search,       label: "Searches (7d)",          value: d.searches7,  prev: d.searchesPrev, accent: "blue",   href: "/admin/search-intelligence" },
    { icon: MessageSquare,label: "Feedback (7d)",          value: d.feedback7,  prev: undefined,       accent: "rose",   href: "/admin/intent" },
    { icon: TrendingUp,   label: "Content Requests (7d)",  value: d.requests7,  prev: undefined,       accent: "green",  href: "/admin/intent" },
  ];

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-teal-100 text-teal-700 border border-teal-200">ENGAGEMENT</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2 flex items-center gap-2">
            <Activity size={22} className="text-teal-500" />
            Engagement Center
          </h1>
          <p className="text-stone-500 text-sm mt-1">
            Real user activity signals — 7-day window with week-over-week trends
          </p>
        </div>

        {/* 7-day engagement metrics */}
        <div>
          <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">
            Last 7 Days
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {METRICS_7D.map((m) => (
              <MetricCard key={m.label} {...m} />
            ))}
          </div>
        </div>

        {/* 30-day overview */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Sessions (30d)",        value: d.sessions30, icon: Eye,   accent: "amber" },
            { label: "New Users (30d)",        value: d.users30,    icon: Users, accent: "blue"  },
          ].map(({ label, value, icon: Icon, accent }) => (
            <div key={label} className="card-base p-4 sm:col-span-2">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${accent === "amber" ? "bg-amber-50 text-amber-600" : "bg-blue-50 text-blue-600"}`}>
                  <Icon size={16} />
                </div>
                <div>
                  <p className="text-2xl font-display font-extrabold text-ink">{value.toLocaleString()}</p>
                  <p className="text-[11px] text-stone-400 font-semibold uppercase tracking-widest">{label}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Top engagement content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Top Pages */}
          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <Eye size={14} className="text-purple-500" /> Top Pages (7d)
            </h3>
            {d.topPagesArr.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No page view data yet.</p>
            ) : (
              <div className="space-y-2">
                {d.topPagesArr.map(({ slug, count }) => (
                  <div key={slug} className="flex items-center gap-3">
                    <div className="flex-1 truncate text-[13px] text-stone-600 capitalize">{slug.replace(/-/g, " ")}</div>
                    <span className="text-[12px] font-bold text-stone-700 shrink-0">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Top Searches */}
          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <Search size={14} className="text-blue-500" /> Top Searches (7d)
            </h3>
            {d.topSearchArr.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No search data yet.</p>
            ) : (
              <div className="space-y-2">
                {d.topSearchArr.map(({ q, count }) => (
                  <div key={q} className="flex items-center gap-3">
                    <div className="flex-1 truncate text-[13px] text-stone-600 capitalize">{q}</div>
                    <span className="text-[12px] font-bold text-stone-700 shrink-0">{count}×</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Community Questions */}
          <div className="card-base p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-bold text-ink text-sm flex items-center gap-2">
                <MessageSquare size={14} className="text-teal-500" /> Community Questions
              </h3>
              <Link href="/questions" className="text-[11px] text-amber-600 font-semibold hover:underline">
                View all
              </Link>
            </div>
            {d.recentQuestions.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No questions yet. The community Q&A is live at <Link href="/questions" className="text-amber-600 hover:underline">/questions</Link>.</p>
            ) : (
              <ul className="space-y-2">
                {d.recentQuestions.map((q) => (
                  <li key={q.id} className="flex items-start gap-2">
                    <span className="text-[11px] font-bold text-teal-600 shrink-0 mt-0.5">{q.answer_count}A</span>
                    <p className="text-[13px] text-stone-600 line-clamp-1">{q.title}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Quick Actions */}
          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
              <Zap size={14} className="text-amber-500" /> Quick Actions
            </h3>
            <div className="space-y-2">
              {[
                { label: "Manage Announcements",   href: "/admin/announcements",  accent: "amber" },
                { label: "View Retention Cohorts", href: "/admin/retention",      accent: "teal" },
                { label: "Search Intelligence",    href: "/admin/search-intelligence", accent: "blue" },
                { label: "Content Opportunities",  href: "/admin/content-opportunities", accent: "purple" },
                { label: "Demand Index",           href: "/admin/demand-index",   accent: "green" },
              ].map(({ label, href, accent }) => (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center justify-between px-4 py-2.5 rounded-xl border border-stone-200 hover:border-amber-300 hover:bg-amber-50 transition-colors group"
                >
                  <span className="text-[13px] font-semibold text-ink group-hover:text-amber-700">{label}</span>
                  <ArrowRight size={12} className="text-stone-300 group-hover:text-amber-500" />
                </Link>
              ))}
            </div>
          </div>
        </div>

      </div>
    </AdminShell>
  );
}
