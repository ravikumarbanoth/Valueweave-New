import Link from "next/link";
import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import {
  Users, Briefcase, UserCheck, BookOpen, MessageSquare,
  TrendingUp, MapPin, Star, Zap, ArrowRight,
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
      { data: oppDistricts },
      { data: collabSectors },
      { data: recentFeedback },
      { data: recentRequests },
      { data: recentArticles },
      { data: recentOpps },
    ] = await Promise.all([
      sb.from("profiles").select("*", { count: "exact", head: true }),
      sb.from("opportunities").select("*", { count: "exact", head: true }),
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
      sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "published"),
      sb.from("user_feedback").select("*", { count: "exact", head: true }),
      sb.from("user_requests").select("*", { count: "exact", head: true }).eq("status", "pending"),
      sb.from("opportunities").select("district").not("district", "is", null).limit(500),
      sb.from("collaborator_profiles").select("top_sectors").limit(500),
      sb.from("user_feedback").select("type,message,created_at,status").order("created_at", { ascending: false }).limit(5),
      sb.from("user_requests").select("title,type,sector,created_at").eq("status", "pending").order("created_at", { ascending: false }).limit(5),
      sb.from("research_articles").select("title,slug,created_at").eq("status", "published").order("created_at", { ascending: false }).limit(4),
      sb.from("opportunities").select("title,category,district").eq("status", "open").order("created_at", { ascending: false }).limit(4),
    ]);

    // Top district by opportunity count
    const districtMap = {};
    (oppDistricts || []).forEach(({ district }) => {
      if (district) districtMap[district] = (districtMap[district] || 0) + 1;
    });
    const topDistrict = Object.entries(districtMap).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A";

    // Top sector by collaborator interest
    const sectorMap = {};
    (collabSectors || []).forEach(({ top_sectors }) => {
      (top_sectors || []).forEach((s) => {
        sectorMap[s] = (sectorMap[s] || 0) + 1;
      });
    });
    const topSector = Object.entries(sectorMap).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A";

    return {
      totalUsers: totalUsers || 0,
      totalOpportunities: totalOpportunities || 0,
      totalCollaborators: totalCollaborators || 0,
      totalArticles: totalArticles || 0,
      totalFeedback: totalFeedback || 0,
      totalRequests: totalRequests || 0,
      topDistrict,
      topSector,
      recentFeedback: recentFeedback || [],
      recentRequests: recentRequests || [],
      recentArticles: recentArticles || [],
      recentOpps: recentOpps || [],
    };
  } catch {
    return {
      totalUsers: 0, totalOpportunities: 0, totalCollaborators: 0,
      totalArticles: 0, totalFeedback: 0, totalRequests: 0,
      topDistrict: "N/A", topSector: "N/A",
      recentFeedback: [], recentRequests: [], recentArticles: [], recentOpps: [],
    };
  }
}

function StatCard({ icon: Icon, label, value, href, accent = "amber" }) {
  const bg = { amber: "bg-amber-50 text-amber-700", teal: "bg-teal-50 text-teal-700", blue: "bg-blue-50 text-blue-700", purple: "bg-purple-50 text-purple-700", rose: "bg-rose-50 text-rose-700", green: "bg-green-50 text-green-700" };
  const card = (
    <div className="card-base p-5 hover:shadow-md transition-shadow h-full">
      <div className={`inline-flex p-2 rounded-lg mb-3 ${bg[accent]}`}>
        <Icon size={16} />
      </div>
      <div className="text-2xl font-display font-extrabold text-ink">{value.toLocaleString()}</div>
      <div className="text-[11px] text-stone-400 font-semibold mt-1 uppercase tracking-widest">{label}</div>
    </div>
  );
  return href ? <Link href={href}>{card}</Link> : <div>{card}</div>;
}

const TOOLS = [
  { href: "/admin/analytics", label: "Analytics Dashboard", desc: "Users, traffic, top content by time period", chip: "INSIGHTS", accent: "amber" },
  { href: "/admin/intent", label: "User Intent", desc: "What users search, request, and click", chip: "DEMAND", accent: "teal" },
  { href: "/admin/content-opportunities", label: "Content Opportunities", desc: "Demand gaps with priority scores", chip: "SMART", accent: "blue" },
  { href: "/admin/seo", label: "SEO Command Center", desc: "Metadata, indexability, recommendations", chip: "SEO", accent: "green" },
  { href: "/admin/districts", label: "District Intelligence", desc: "Traffic, demand, and opportunities per district", chip: "DISTRICTS", accent: "purple" },
  { href: "/admin/opportunity-generator", label: "Opportunity Generator", desc: "Bulk-generate SEO-optimized opportunities", chip: "GENERATE", accent: "amber" },
  { href: "/admin/matches", label: "Founder Matches", desc: "Score-matched co-founders, teams, mentors", chip: "MATCHING", accent: "rose" },
  { href: "/admin/research-performance", label: "Research Performance", desc: "Article views, CTR, and content analytics", chip: "CONTENT", accent: "teal" },
  { href: "/admin/research", label: "Research Publisher", desc: "Create, edit, and publish articles", chip: "PUBLISH", accent: "stone" },
];

const CHIP_COLORS = {
  amber: "bg-amber-100 text-amber-700",
  teal: "bg-teal-100 text-teal-700",
  blue: "bg-blue-100 text-blue-700",
  green: "bg-green-100 text-green-700",
  purple: "bg-purple-100 text-purple-700",
  rose: "bg-rose-100 text-rose-700",
  stone: "bg-stone-100 text-stone-600",
};

export default async function AdminControlCenter() {
  const d = await fetchDashboardData();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-amber-100 text-amber-700 border border-amber-200 mb-3">
            VALUEWEAVE ADMIN · CONTROL CENTER
          </span>
          <h1 className="font-display font-extrabold text-3xl text-ink mt-2 mb-1">
            Operations Dashboard
          </h1>
          <p className="text-stone-500 text-sm">
            Opportunity Intelligence Platform — Telangana &amp; Andhra Pradesh
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatCard icon={Users} label="Users" value={d.totalUsers} href="/admin/analytics" accent="amber" />
          <StatCard icon={Briefcase} label="Opportunities" value={d.totalOpportunities} href="/admin/opportunity-generator" accent="teal" />
          <StatCard icon={UserCheck} label="Collaborators" value={d.totalCollaborators} href="/admin/matches" accent="blue" />
          <StatCard icon={BookOpen} label="Articles" value={d.totalArticles} href="/admin/research-performance" accent="purple" />
          <StatCard icon={MessageSquare} label="Feedback" value={d.totalFeedback} href="/admin/intent" accent="rose" />
          <StatCard icon={TrendingUp} label="Requests" value={d.totalRequests} href="/admin/intent" accent="green" />
        </div>

        {/* Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="card-base p-5 flex items-center gap-4">
            <div className="bg-teal-50 text-teal-700 p-3 rounded-xl">
              <MapPin size={20} />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest">Top District</p>
              <p className="font-display font-extrabold text-xl text-ink capitalize">{d.topDistrict}</p>
            </div>
          </div>
          <div className="card-base p-5 flex items-center gap-4">
            <div className="bg-amber-50 text-amber-700 p-3 rounded-xl">
              <Star size={20} />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-stone-400 uppercase tracking-widest">Top Sector</p>
              <p className="font-display font-extrabold text-xl text-ink capitalize">{d.topSector}</p>
            </div>
          </div>
        </div>

        {/* Admin Tools Grid */}
        <div>
          <h2 className="font-display font-bold text-lg text-ink mb-4 flex items-center gap-2">
            <Zap size={18} className="text-amber-500" /> Admin Tools
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {TOOLS.map(({ href, label, desc, chip, accent }) => (
              <Link
                key={href}
                href={href}
                className="card-base p-5 hover:shadow-md transition-all hover:-translate-y-0.5 group block"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className={`chip text-[10px] ${CHIP_COLORS[accent]}`}>{chip}</span>
                  <ArrowRight size={14} className="text-stone-300 group-hover:text-amber-500 transition-colors" />
                </div>
                <h3 className="font-display font-bold text-ink group-hover:text-amber-700 transition-colors text-sm">
                  {label}
                </h3>
                <p className="text-[12px] text-stone-400 mt-1 leading-relaxed">{desc}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

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
              <p className="text-sm text-stone-400 italic">No feedback yet — data appears as users submit.</p>
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
              <p className="text-sm text-stone-400 italic">No requests yet — data appears as users submit.</p>
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
