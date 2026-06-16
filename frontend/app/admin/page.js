import Link from "next/link";
import AdminShell from "@/components/admin/AdminShell";
import AdminQuickAccess from "@/components/admin/AdminQuickAccess";
import HealthScore from "@/components/admin/HealthScore";
import { createClient } from "@/lib/supabase-server";
import {
  Users, Briefcase, UserCheck, BookOpen, MessageSquare,
  TrendingUp, MapPin, Star, Zap, ArrowRight, Bell, Search,
  Grid, Activity, BarChart3, CheckCircle, AlertCircle, Eye,
} from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Control Center | ValueWeave Admin",
  robots: { index: false, follow: false },
};

async function fetchDashboardData() {
  try {
    const sb = createClient();

    const [
      { count: totalUsers },
      { count: totalOpportunities },
      { count: totalCollaborators },
      { count: totalArticles },
      { count: totalFeedback },
      { count: totalRequests },
      { count: unreadNotifications },
      { count: pendingMatches },
      { count: totalVisitors },
      { data: oppDistricts },
      { data: collabSectors },
      { data: recentFeedback },
      { data: recentRequests },
      { data: recentArticles },
      { data: recentOpps },
      { data: recentNotifications },
      { data: topSearches },
    ] = await Promise.all([
      sb.from("profiles").select("*", { count: "exact", head: true }),
      sb.from("opportunities").select("*", { count: "exact", head: true }),
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
      sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "published"),
      sb.from("user_feedback").select("*", { count: "exact", head: true }),
      sb.from("user_requests").select("*", { count: "exact", head: true }).eq("status", "pending"),
      sb.from("admin_notifications").select("*", { count: "exact", head: true }).eq("status", "unread"),
      sb.from("founder_matches").select("*", { count: "exact", head: true }).eq("status", "pending"),
      sb.from("visitor_sessions").select("*", { count: "exact", head: true }),
      sb.from("opportunities").select("district").not("district", "is", null).limit(500),
      sb.from("collaborator_profiles").select("top_sectors").limit(500),
      sb.from("user_feedback").select("type,message,created_at,status").order("created_at", { ascending: false }).limit(5),
      sb.from("user_requests").select("title,type,sector,created_at").eq("status", "pending").order("created_at", { ascending: false }).limit(5),
      sb.from("research_articles").select("title,slug,created_at").eq("status", "published").order("created_at", { ascending: false }).limit(4),
      sb.from("opportunities").select("title,category,district").eq("status", "open").order("created_at", { ascending: false }).limit(4),
      sb.from("admin_notifications").select("type,title,body,priority,created_at").eq("status", "unread").order("created_at", { ascending: false }).limit(4),
      sb.from("search_events").select("query").limit(500),
    ]);

    // Top district by opportunity count
    const districtMap = {};
    (oppDistricts || []).forEach(({ district }) => {
      if (district) districtMap[district] = (districtMap[district] || 0) + 1;
    });
    const topDistrictEntry = Object.entries(districtMap).sort((a, b) => b[1] - a[1])[0];
    const topDistrict = topDistrictEntry?.[0] || "N/A";
    const topDistrictCount = topDistrictEntry?.[1] || 0;

    // Top sector by collaborator interest
    const sectorMap = {};
    (collabSectors || []).forEach(({ top_sectors }) => {
      (top_sectors || []).forEach((s) => {
        sectorMap[s] = (sectorMap[s] || 0) + 1;
      });
    });
    const topSectorEntry = Object.entries(sectorMap).sort((a, b) => b[1] - a[1])[0];
    const topSector = topSectorEntry?.[0] || "N/A";
    const topSectorCount = topSectorEntry?.[1] || 0;

    // Top search query
    const searchQueryMap = {};
    (topSearches || []).forEach(({ query }) => {
      if (query) searchQueryMap[query.toLowerCase()] = (searchQueryMap[query.toLowerCase()] || 0) + 1;
    });
    const topSearchEntry = Object.entries(searchQueryMap).sort((a, b) => b[1] - a[1])[0];
    const topSearch = topSearchEntry?.[0] || null;
    const topSearchCount = topSearchEntry?.[1] || 0;

    // Suggested actions based on real data
    const suggestedActions = [];
    if ((unreadNotifications || 0) > 0) suggestedActions.push({ label: `Review ${unreadNotifications} unread notifications`, href: "/admin/notifications", accent: "rose" });
    if ((totalRequests || 0) > 0) suggestedActions.push({ label: `Action ${totalRequests} pending user requests`, href: "/admin/intent", accent: "amber" });
    if ((pendingMatches || 0) > 0) suggestedActions.push({ label: `Review ${pendingMatches} founder match suggestions`, href: "/admin/matches", accent: "purple" });
    if (topSearch) suggestedActions.push({ label: `"${topSearch}" is trending — create content (${topSearchCount}×)`, href: `/admin/content-opportunities`, accent: "teal" });

    return {
      totalUsers: totalUsers || 0,
      totalOpportunities: totalOpportunities || 0,
      totalCollaborators: totalCollaborators || 0,
      totalArticles: totalArticles || 0,
      totalFeedback: totalFeedback || 0,
      totalRequests: totalRequests || 0,
      unreadNotifications: unreadNotifications || 0,
      pendingMatches: pendingMatches || 0,
      totalVisitors: totalVisitors || 0,
      topDistrict, topDistrictCount,
      topSector, topSectorCount,
      topSearch, topSearchCount,
      recentFeedback: recentFeedback || [],
      recentRequests: recentRequests || [],
      recentArticles: recentArticles || [],
      recentOpps: recentOpps || [],
      recentNotifications: recentNotifications || [],
      suggestedActions,
    };
  } catch {
    return {
      totalUsers: 0, totalOpportunities: 0, totalCollaborators: 0,
      totalArticles: 0, totalFeedback: 0, totalRequests: 0,
      unreadNotifications: 0, pendingMatches: 0, totalVisitors: 0,
      topDistrict: "N/A", topDistrictCount: 0,
      topSector: "N/A", topSectorCount: 0,
      topSearch: null, topSearchCount: 0,
      recentFeedback: [], recentRequests: [], recentArticles: [], recentOpps: [],
      recentNotifications: [], suggestedActions: [],
    };
  }
}

function StatCard({ icon: Icon, label, value, href, accent = "amber", badge }) {
  const bg = {
    amber: "bg-amber-50 text-amber-700", teal: "bg-teal-50 text-teal-700",
    blue: "bg-blue-50 text-blue-700", purple: "bg-purple-50 text-purple-700",
    rose: "bg-rose-50 text-rose-700", green: "bg-green-50 text-green-700",
    stone: "bg-stone-50 text-stone-600",
  };
  const card = (
    <div className="card-base p-5 hover:shadow-md transition-shadow h-full relative">
      {badge > 0 && (
        <span className="absolute top-3 right-3 w-4 h-4 bg-rose-500 rounded-full text-[9px] text-white font-bold flex items-center justify-center">
          {badge > 9 ? "9+" : badge}
        </span>
      )}
      <div className={`inline-flex p-2 rounded-lg mb-3 ${bg[accent]}`}>
        <Icon size={16} />
      </div>
      <div className="text-2xl font-display font-extrabold text-ink">{typeof value === "number" ? value.toLocaleString() : value}</div>
      <div className="text-[11px] text-stone-400 font-semibold mt-1 uppercase tracking-widest">{label}</div>
    </div>
  );
  return href ? <Link href={href}>{card}</Link> : <div>{card}</div>;
}

const TOOLS = [
  { href: "/admin/analytics", label: "Analytics Dashboard", desc: "Users, traffic, top content by time period", chip: "INSIGHTS", accent: "amber" },
  { href: "/admin/notifications", label: "Notifications", desc: "Auto-notifications from DB triggers", chip: "ALERTS", accent: "rose" },
  { href: "/admin/search-intelligence", label: "Search Intelligence", desc: "Top queries, trends, no-results, heatmap", chip: "SEARCH", accent: "blue" },
  { href: "/admin/demand-index", label: "Demand Index", desc: "Sector & district scores from all user signals", chip: "DEMAND", accent: "amber" },
  { href: "/admin/intent", label: "User Intent", desc: "What users search, request, and click", chip: "INTENT", accent: "teal" },
  { href: "/admin/content-opportunities", label: "Content Opportunities", desc: "Demand gaps with priority scores", chip: "SMART", accent: "blue" },
  { href: "/admin/recommendations", label: "Recommendations", desc: "Auto-recommended content from demand signals", chip: "AI", accent: "green" },
  { href: "/admin/seo", label: "SEO Command Center", desc: "Metadata, indexability, recommendations", chip: "SEO", accent: "green" },
  { href: "/admin/districts", label: "District Intelligence", desc: "Traffic, demand, and opportunities per district", chip: "DISTRICTS", accent: "purple" },
  { href: "/admin/district-opportunity-index", label: "District Opportunity Index", desc: "Ranked potential scores across all 51 districts", chip: "RANKED", accent: "blue" },
  { href: "/admin/opportunity-generator", label: "Opportunity Generator", desc: "Bulk-generate SEO-optimized opportunities", chip: "GENERATE", accent: "amber" },
  { href: "/admin/opportunity-performance", label: "Opp. Performance", desc: "Views, interests, and conversion rates", chip: "PERF", accent: "teal" },
  { href: "/admin/matches", label: "Founder Matches", desc: "Score-matched co-founders, teams, mentors", chip: "MATCHING", accent: "rose" },
  { href: "/admin/research-performance", label: "Research Performance", desc: "Article views, CTR, and content analytics", chip: "CONTENT", accent: "teal" },
  { href: "/admin/research", label: "Research Publisher", desc: "Create, edit, and publish articles", chip: "PUBLISH", accent: "stone" },
];

const CHIP_COLORS = {
  amber: "bg-amber-100 text-amber-700", teal: "bg-teal-100 text-teal-700",
  blue: "bg-blue-100 text-blue-700", green: "bg-green-100 text-green-700",
  purple: "bg-purple-100 text-purple-700", rose: "bg-rose-100 text-rose-700",
  stone: "bg-stone-100 text-stone-600",
};

const NOTIF_PRIORITY = {
  high: "border-l-2 border-rose-400",
  normal: "border-l-2 border-amber-300",
  low: "border-l-2 border-stone-200",
};

const ACTION_COLORS = {
  rose: "bg-rose-50 border-rose-200 text-rose-700 hover:bg-rose-100",
  amber: "bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100",
  purple: "bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100",
  teal: "bg-teal-50 border-teal-200 text-teal-700 hover:bg-teal-100",
};

export default async function AdminControlCenter() {
  const d = await fetchDashboardData();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
          <div>
            <span className="chip bg-amber-100 text-amber-700 border border-amber-200 mb-3">
              VALUEWEAVE ADMIN · PHASE 4 · GROWTH INTELLIGENCE
            </span>
            <h1 className="font-display font-extrabold text-3xl text-ink mt-2 mb-1">
              Operations Dashboard
            </h1>
            <p className="text-stone-500 text-sm">
              Self-improving Opportunity Intelligence Platform — Telangana &amp; Andhra Pradesh
            </p>
          </div>
          <div className="flex gap-2 shrink-0">
            {d.unreadNotifications > 0 && (
              <Link href="/admin/notifications" className="relative inline-flex items-center gap-2 px-4 py-2 rounded-full bg-rose-50 text-rose-700 border border-rose-200 text-[12px] font-semibold hover:bg-rose-100 transition-colors">
                <Bell size={13} />
                {d.unreadNotifications} unread
              </Link>
            )}
            {d.pendingMatches > 0 && (
              <Link href="/admin/matches" className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[12px] font-semibold hover:bg-purple-100 transition-colors">
                <Users size={13} />
                {d.pendingMatches} match{d.pendingMatches !== 1 ? "es" : ""}
              </Link>
            )}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <StatCard icon={Eye} label="Visitor Sessions" value={d.totalVisitors} href="/admin/analytics" accent="amber" />
          <StatCard icon={Users} label="Users" value={d.totalUsers} href="/admin/analytics" accent="teal" />
          <StatCard icon={Briefcase} label="Opportunities" value={d.totalOpportunities} href="/admin/opportunity-generator" accent="blue" />
          <StatCard icon={UserCheck} label="Collaborators" value={d.totalCollaborators} href="/admin/matches" accent="purple" />
          <StatCard icon={BookOpen} label="Articles" value={d.totalArticles} href="/admin/research-performance" accent="green" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard icon={MessageSquare} label="Feedback" value={d.totalFeedback} href="/admin/intent" accent="rose" />
          <StatCard icon={TrendingUp} label="Requests" value={d.totalRequests} href="/admin/intent" accent="amber" />
          <StatCard icon={Bell} label="Unread Alerts" value={d.unreadNotifications} href="/admin/notifications" accent="rose" badge={d.unreadNotifications} />
          <StatCard icon={Users} label="Pending Matches" value={d.pendingMatches} href="/admin/matches" accent="purple" badge={d.pendingMatches} />
        </div>

        {/* Demand Highlights + Top Search */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="card-base p-5 flex items-center gap-4">
            <div className="bg-teal-50 text-teal-700 p-3 rounded-xl shrink-0">
              <MapPin size={20} />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest">Top District</p>
              <p className="font-display font-extrabold text-xl text-ink capitalize truncate">{d.topDistrict}</p>
              {d.topDistrictCount > 0 && <p className="text-[11px] text-stone-400">{d.topDistrictCount} opportunities</p>}
            </div>
          </div>
          <div className="card-base p-5 flex items-center gap-4">
            <div className="bg-amber-50 text-amber-700 p-3 rounded-xl shrink-0">
              <Star size={20} />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest">Top Sector</p>
              <p className="font-display font-extrabold text-xl text-ink capitalize truncate">{d.topSector}</p>
              {d.topSectorCount > 0 && <p className="text-[11px] text-stone-400">{d.topSectorCount} collaborators</p>}
            </div>
          </div>
          <div className="card-base p-5 flex items-center gap-4">
            <div className="bg-blue-50 text-blue-700 p-3 rounded-xl shrink-0">
              <Search size={20} />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest">Top Search</p>
              {d.topSearch ? (
                <>
                  <p className="font-display font-extrabold text-xl text-ink capitalize truncate">{d.topSearch}</p>
                  <p className="text-[11px] text-stone-400">{d.topSearchCount}× searched</p>
                </>
              ) : (
                <p className="font-display font-extrabold text-lg text-stone-300">No data yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Suggested Actions */}
        {d.suggestedActions.length > 0 && (
          <div>
            <h2 className="font-display font-bold text-sm text-ink mb-3 flex items-center gap-2">
              <CheckCircle size={15} className="text-green-500" /> Suggested Actions
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {d.suggestedActions.map(({ label, href, accent }) => (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center justify-between gap-3 px-4 py-3 rounded-xl border text-[13px] font-semibold transition-colors ${ACTION_COLORS[accent] || ACTION_COLORS.amber}`}
                >
                  <span>{label}</span>
                  <ArrowRight size={13} className="shrink-0" />
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Business Health Score */}
        <HealthScore />

        {/* Admin Tools Grid */}
        <AdminQuickAccess currentPath="/admin" />

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Recent Notifications */}
          {d.recentNotifications.length > 0 && (
            <div className="card-base p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-display font-bold text-ink flex items-center gap-2 text-sm">
                  <Bell size={15} className="text-rose-500" /> Recent Alerts
                </h3>
                <Link href="/admin/notifications" className="text-[11px] text-amber-600 font-semibold hover:underline">
                  View all
                </Link>
              </div>
              <ul className="space-y-2">
                {d.recentNotifications.map((n, i) => (
                  <li key={i} className={`p-3 rounded-lg bg-stone-50 ${NOTIF_PRIORITY[n.priority] || ""}`}>
                    <p className="text-[13px] font-semibold text-ink">{n.title}</p>
                    {n.body && <p className="text-[11px] text-stone-400 mt-0.5 line-clamp-1">{n.body}</p>}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recent Feedback */}
          <div className="card-base p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-bold text-ink flex items-center gap-2 text-sm">
                <MessageSquare size={15} className="text-rose-500" /> Recent Feedback
              </h3>
              <Link href="/admin/intent" className="text-[11px] text-amber-600 font-semibold hover:underline">
                View all
              </Link>
            </div>
            {d.recentFeedback.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No feedback yet.</p>
            ) : (
              <ul className="space-y-3">
                {d.recentFeedback.map((f, i) => (
                  <li key={i} className="flex gap-3 items-start">
                    <span className="chip bg-stone-100 text-stone-500 shrink-0 text-[10px]">{f.type}</span>
                    <p className="text-[13px] text-stone-600 line-clamp-2">{f.message}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Pending Requests */}
          <div className="card-base p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-bold text-ink flex items-center gap-2 text-sm">
                <TrendingUp size={15} className="text-teal-500" /> Pending Requests
              </h3>
              <Link href="/admin/intent" className="text-[11px] text-amber-600 font-semibold hover:underline">
                View all
              </Link>
            </div>
            {d.recentRequests.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No requests yet.</p>
            ) : (
              <ul className="space-y-3">
                {d.recentRequests.map((r, i) => (
                  <li key={i} className="flex gap-3 items-start">
                    <span className="chip bg-teal-50 text-teal-700 border border-teal-100 shrink-0 text-[10px]">{r.type}</span>
                    <p className="text-[13px] text-stone-600">{r.title}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Recent Articles */}
          <div className="card-base p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-bold text-ink flex items-center gap-2 text-sm">
                <BookOpen size={15} className="text-purple-500" /> Recent Articles
              </h3>
              <Link href="/admin/research" className="text-[11px] text-amber-600 font-semibold hover:underline">
                Publisher
              </Link>
            </div>
            {d.recentArticles.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No published articles yet.</p>
            ) : (
              <ul className="space-y-2">
                {d.recentArticles.map((a, i) => (
                  <li key={i}>
                    <Link
                      href={`/research/${a.slug}`}
                      className="text-[13px] text-stone-700 hover:text-amber-700 font-medium line-clamp-1 transition-colors"
                    >
                      {a.title}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Recent Opportunities */}
          <div className="card-base p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-bold text-ink flex items-center gap-2 text-sm">
                <Briefcase size={15} className="text-teal-500" /> Recent Opportunities
              </h3>
              <Link href="/admin/opportunity-generator" className="text-[11px] text-amber-600 font-semibold hover:underline">
                Generator
              </Link>
            </div>
            {d.recentOpps.length === 0 ? (
              <p className="text-sm text-stone-400 italic">No opportunities yet.</p>
            ) : (
              <ul className="space-y-2">
                {d.recentOpps.map((o, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="text-[13px] text-stone-700 flex-1 line-clamp-1">{o.title}</span>
                    {o.district && (
                      <span className="chip bg-stone-100 text-stone-500 text-[10px] shrink-0">{o.district}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

        </div>
      </div>
    </AdminShell>
  );
}
