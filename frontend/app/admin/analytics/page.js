import AdminShell from "@/components/admin/AdminShell";
import AdminQuickAccess from "@/components/admin/AdminQuickAccess";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import {
  Users, Briefcase, BookOpen, UserCheck, MessageSquare, TrendingUp,
  Eye, Monitor, Smartphone, Globe, Activity, Search, FileText,
} from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Analytics | ValueWeave Admin",
  robots: { index: false, follow: false },
};

const TIME_FILTERS = [
  { label: "7 days",  days: 7  },
  { label: "30 days", days: 30 },
  { label: "90 days", days: 90 },
  { label: "All time",days: 0  },
];

function getDateFilter(days) {
  if (!days) return null;
  return new Date(Date.now() - days * 86400000).toISOString();
}

function BarChart({ data, color = "amber" }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  const barColor = { amber: "bg-amber-400", teal: "bg-teal-400", blue: "bg-blue-400", purple: "bg-purple-400", green: "bg-green-400" };
  return (
    <div className="space-y-2">
      {data.map((item) => (
        <div key={item.label} className="flex items-center gap-3">
          <div className="w-28 shrink-0 text-[12px] text-stone-600 truncate capitalize">{item.label}</div>
          <div className="flex-1 bg-stone-100 rounded-full h-5 overflow-hidden">
            <div
              className={`${barColor[color] || "bg-amber-400"} h-full rounded-full transition-all`}
              style={{ width: `${Math.max((item.value / max) * 100, 2)}%` }}
            />
          </div>
          <div className="w-10 text-[12px] font-bold text-stone-700 text-right shrink-0">{item.value}</div>
        </div>
      ))}
    </div>
  );
}

function SectionCard({ title, icon: Icon, iconColor, children }) {
  return (
    <div className="card-base p-5">
      <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
        {Icon && <Icon size={14} className={iconColor || "text-stone-400"} />}
        {title}
      </h3>
      {children}
    </div>
  );
}

const EVENT_ICONS = {
  page_view:      { icon: Eye,        color: "text-purple-500", bg: "bg-purple-50" },
  search:         { icon: Search,     color: "text-blue-500",   bg: "bg-blue-50" },
  content_request:{ icon: FileText,   color: "text-teal-500",   bg: "bg-teal-50" },
  feedback:       { icon: MessageSquare, color: "text-rose-500", bg: "bg-rose-50" },
  visitor:        { icon: Globe,      color: "text-amber-500",  bg: "bg-amber-50" },
};

async function fetchAnalytics(since) {
  try {
    const sb = createClient();

    // Build time-filtered queries
    const maybe = (q) => since ? q.gte("created_at", since) : q;

    const [
      { count: totalUsers },
      { count: totalOpps },
      { count: totalArticles },
      { count: totalCollabs },
      { count: totalFeedback },
      { count: totalRequests },
      // Visitor sessions
      { data: visitorSessions },
      // Page views breakdown by type
      { data: pageViews },
      // Top searches
      { data: searches },
      // Articles with views
      { data: articles },
      // Collaborator districts
      { data: collabDistricts },
      // Opportunity categories
      { data: oppCategories },
      // Activity feed (latest 50 events)
      { data: activityFeed },
    ] = await Promise.all([
      maybe(sb.from("profiles").select("*", { count: "exact", head: true })),
      maybe(sb.from("opportunities").select("*", { count: "exact", head: true })),
      maybe(sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "published")),
      maybe(sb.from("collaborator_profiles").select("*", { count: "exact", head: true })),
      maybe(sb.from("user_feedback").select("*", { count: "exact", head: true })),
      maybe(sb.from("user_requests").select("*", { count: "exact", head: true })),
      // Visitor metrics
      maybe(sb.from("visitor_sessions").select("visitor_id,device_type,browser,created_at")).limit(5000),
      // Page views
      maybe(sb.from("page_views").select("page_slug,page_title,page_type,district,sector")).limit(3000),
      // Searches
      maybe(sb.from("search_events").select("query,district,sector")).limit(3000),
      // Articles
      sb.from("research_articles").select("title,slug,views").eq("status", "published").order("views", { ascending: false }).limit(10),
      sb.from("collaborator_profiles").select("district").not("district", "is", null).limit(500),
      sb.from("opportunities").select("category").not("category", "is", null).limit(1000),
      // Activity feed (union via order)
      sb.from("activity_log").select("event_type,summary,detail,district,sector,created_at")
        .order("created_at", { ascending: false }).limit(50),
    ]);

    // Visitor metrics
    const sessions = visitorSessions || [];
    const totalSessions = sessions.length;
    const uniqueVisitors = new Set(sessions.map((s) => s.visitor_id)).size;
    const returningVisitors = sessions.filter((s) => {
      // A returning visitor has multiple sessions with same visitor_id
      const sameVisitor = sessions.filter((x) => x.visitor_id === s.visitor_id);
      return sameVisitor.length > 1;
    });
    const returningCount = new Set(returningVisitors.map((s) => s.visitor_id)).size;

    const deviceMap = {};
    sessions.forEach(({ device_type }) => {
      const d = device_type || "other";
      deviceMap[d] = (deviceMap[d] || 0) + 1;
    });
    const deviceBreakdown = Object.entries(deviceMap)
      .sort((a, b) => b[1] - a[1])
      .map(([label, value]) => ({ label, value }));

    // Top viewed pages
    const viewMap = {};
    (pageViews || []).forEach(({ page_slug, page_title }) => {
      if (!viewMap[page_slug]) viewMap[page_slug] = { label: page_title || page_slug, value: 0 };
      viewMap[page_slug].value++;
    });
    const topViewed = Object.values(viewMap)
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);

    // Page views by type
    const typeMap = {};
    (pageViews || []).forEach(({ page_type }) => {
      if (page_type) typeMap[page_type] = (typeMap[page_type] || 0) + 1;
    });
    const viewsByType = Object.entries(typeMap)
      .sort((a, b) => b[1] - a[1])
      .map(([label, value]) => ({ label, value }));

    // Top search queries
    const searchMap = {};
    (searches || []).forEach(({ query }) => {
      if (query) searchMap[query] = (searchMap[query] || 0) + 1;
    });
    const topSearches = Object.entries(searchMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, value]) => ({ label, value }));

    // Top districts from page views
    const pvDistrictMap = {};
    (pageViews || []).forEach(({ district }) => {
      if (district) pvDistrictMap[district] = (pvDistrictMap[district] || 0) + 1;
    });
    const topDistricts = Object.entries(pvDistrictMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, value]) => ({ label, value }));

    // Top categories
    const catMap = {};
    (oppCategories || []).forEach(({ category }) => {
      if (category) catMap[category] = (catMap[category] || 0) + 1;
    });
    const topCategories = Object.entries(catMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([label, value]) => ({ label, value }));

    // Top articles
    const topArticles = (articles || [])
      .filter((a) => a.views > 0)
      .map((a) => ({ label: a.title, value: a.views }));

    // Collaborator districts
    const cdMap = {};
    (collabDistricts || []).forEach(({ district }) => {
      if (district) cdMap[district] = (cdMap[district] || 0) + 1;
    });
    const topCollabDistricts = Object.entries(cdMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([label, value]) => ({ label, value }));

    return {
      totals: {
        users: totalUsers || 0,
        opportunities: totalOpps || 0,
        articles: totalArticles || 0,
        collaborators: totalCollabs || 0,
        feedback: totalFeedback || 0,
        requests: totalRequests || 0,
      },
      visitors: {
        total: totalSessions,
        unique: uniqueVisitors,
        returning: returningCount,
        deviceBreakdown,
      },
      topViewed,
      viewsByType,
      topSearches,
      topDistricts,
      topCategories,
      topArticles,
      topCollabDistricts,
      activityFeed: activityFeed || [],
    };
  } catch (e) {
    console.error("Analytics fetch error:", e);
    return {
      totals: { users: 0, opportunities: 0, articles: 0, collaborators: 0, feedback: 0, requests: 0 },
      visitors: { total: 0, unique: 0, returning: 0, deviceBreakdown: [] },
      topViewed: [], viewsByType: [], topSearches: [], topDistricts: [],
      topCategories: [], topArticles: [], topCollabDistricts: [], activityFeed: [],
    };
  }
}

export default async function AnalyticsPage({ searchParams }) {
  const days = parseInt(searchParams?.days) || 30;
  const since = getDateFilter(days);
  const data = await fetchAnalytics(since);

  const ACCENT = {
    amber: "bg-amber-50 text-amber-700", teal: "bg-teal-50 text-teal-700",
    purple: "bg-purple-50 text-purple-700", blue: "bg-blue-50 text-blue-700",
    rose: "bg-rose-50 text-rose-700", green: "bg-green-50 text-green-700",
    eye: "bg-violet-50 text-violet-700",
  };

  const STAT_CARDS = [
    { icon: Users,        label: "Users",         value: data.totals.users,         color: "amber" },
    { icon: Briefcase,    label: "Opportunities",  value: data.totals.opportunities,  color: "teal" },
    { icon: BookOpen,     label: "Articles",       value: data.totals.articles,       color: "purple" },
    { icon: UserCheck,    label: "Collaborators",  value: data.totals.collaborators,  color: "blue" },
    { icon: MessageSquare,label: "Feedback",       value: data.totals.feedback,       color: "rose" },
    { icon: TrendingUp,   label: "Requests",       value: data.totals.requests,       color: "green" },
  ];

  const VISITOR_CARDS = [
    { icon: Globe,     label: "Total Sessions",      value: data.visitors.total,     color: "amber" },
    { icon: Eye,       label: "Unique Visitors",     value: data.visitors.unique,    color: "purple" },
    { icon: Users,     label: "Returning Visitors",  value: data.visitors.returning, color: "teal" },
    { icon: Monitor,   label: "Desktop Share",
      value: data.visitors.deviceBreakdown.find((d) => d.label === "desktop")?.value || 0, color: "blue" },
    { icon: Smartphone,label: "Mobile Share",
      value: data.visitors.deviceBreakdown.find((d) => d.label === "mobile")?.value || 0,  color: "green" },
  ];

  function timeSince(iso) {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return `${Math.floor(diff)}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  }

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header + Time Filter */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-amber-100 text-amber-700 border border-amber-200">ANALYTICS</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Analytics Dashboard</h1>
            <p className="text-stone-500 text-sm mt-1">Real visitor data, page performance, and platform growth</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            {TIME_FILTERS.map(({ label, days: d }) => (
              <Link
                key={d}
                href={`?days=${d}`}
                className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors ${
                  days === d
                    ? "bg-amber-500 text-white"
                    : "bg-white border border-stone-200 text-stone-500 hover:border-amber-500 hover:text-amber-700"
                }`}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>

        {/* Platform Totals */}
        <div>
          <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">Platform Totals</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {STAT_CARDS.map(({ icon: Icon, label, value, color }) => (
              <div key={label} className="card-base p-4">
                <div className={`inline-flex p-2 rounded-lg mb-2 ${ACCENT[color]}`}>
                  <Icon size={15} />
                </div>
                <div className="text-xl font-display font-extrabold text-ink">{value.toLocaleString()}</div>
                <div className="text-[10px] text-stone-400 font-semibold uppercase tracking-widest mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Visitor Intelligence */}
        <div>
          <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-3">Visitor Intelligence</p>
          {data.visitors.total === 0 ? (
            <div className="card-base p-6 text-center">
              <Eye size={32} className="text-stone-200 mx-auto mb-3" />
              <p className="text-sm text-stone-400 font-medium">No visitor data yet.</p>
              <p className="text-[12px] text-stone-300 mt-1">Data populates automatically as users browse the site.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {VISITOR_CARDS.map(({ icon: Icon, label, value, color }) => (
                <div key={label} className="card-base p-4">
                  <div className={`inline-flex p-2 rounded-lg mb-2 ${ACCENT[color]}`}>
                    <Icon size={15} />
                  </div>
                  <div className="text-xl font-display font-extrabold text-ink">{value.toLocaleString()}</div>
                  <div className="text-[10px] text-stone-400 font-semibold uppercase tracking-widest mt-0.5">{label}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Charts grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <SectionCard title="Top Viewed Pages" icon={Eye} iconColor="text-purple-500">
            {data.topViewed.length > 0
              ? <BarChart data={data.topViewed} color="purple" />
              : <p className="text-sm text-stone-400 italic">No page view data yet. PageTracker fires automatically on content pages.</p>
            }
          </SectionCard>

          <SectionCard title="Views by Content Type" icon={Activity} iconColor="text-amber-500">
            {data.viewsByType.length > 0
              ? <BarChart data={data.viewsByType} color="amber" />
              : <p className="text-sm text-stone-400 italic">No data yet.</p>
            }
          </SectionCard>

          <SectionCard title="Top Search Queries" icon={Search} iconColor="text-blue-500">
            {data.topSearches.length > 0
              ? <BarChart data={data.topSearches} color="blue" />
              : <p className="text-sm text-stone-400 italic">No searches recorded yet.</p>
            }
          </SectionCard>

          <SectionCard title="Most Visited Districts" icon={Globe} iconColor="text-teal-500">
            {data.topDistricts.length > 0
              ? <BarChart data={data.topDistricts} color="teal" />
              : <p className="text-sm text-stone-400 italic">District page view data will appear here.</p>
            }
          </SectionCard>

          <SectionCard title="Top Articles by Views" icon={BookOpen} iconColor="text-purple-500">
            {data.topArticles.length > 0
              ? <BarChart data={data.topArticles} color="purple" />
              : <p className="text-sm text-stone-400 italic">Article views will populate as readers browse research pages.</p>
            }
          </SectionCard>

          <SectionCard title="Collaborator Districts" icon={UserCheck} iconColor="text-teal-500">
            {data.topCollabDistricts.length > 0
              ? <BarChart data={data.topCollabDistricts} color="teal" />
              : <p className="text-sm text-stone-400 italic">Collaborator district data populates as users complete Discover assessments.</p>
            }
          </SectionCard>

        </div>

        {/* Real-time Activity Feed */}
        <SectionCard title="Recent Activity Feed" icon={Activity} iconColor="text-green-500">
          {data.activityFeed.length === 0 ? (
            <p className="text-sm text-stone-400 italic">Activity appears here as users interact with the platform.</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
              {data.activityFeed.map((event, i) => {
                const meta = EVENT_ICONS[event.event_type] || EVENT_ICONS.visitor;
                const EventIcon = meta.icon;
                return (
                  <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-stone-50 transition-colors">
                    <div className={`shrink-0 w-7 h-7 flex items-center justify-center rounded-lg ${meta.bg}`}>
                      <EventIcon size={13} className={meta.color} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium text-ink truncate">{event.summary}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {event.district && (
                          <span className="text-[10px] text-stone-400">{event.district}</span>
                        )}
                        {event.detail && !event.district && (
                          <span className="text-[10px] text-stone-400 truncate">{event.detail}</span>
                        )}
                      </div>
                    </div>
                    <span className="text-[10px] text-stone-300 shrink-0 mt-0.5">
                      {timeSince(event.created_at)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </SectionCard>

        {/* Admin Quick Access */}
        <AdminQuickAccess currentPath="/admin/analytics" />

      </div>
    </AdminShell>
  );
}
