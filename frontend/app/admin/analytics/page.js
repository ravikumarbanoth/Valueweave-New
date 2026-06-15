import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { Users, Briefcase, BookOpen, UserCheck, MessageSquare, TrendingUp } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Analytics | ValueWeave Admin",
  robots: { index: false, follow: false },
};

const TIME_FILTERS = [
  { label: "7 days", days: 7 },
  { label: "30 days", days: 30 },
  { label: "90 days", days: 90 },
  { label: "All time", days: 0 },
];

function getDateFilter(days) {
  if (!days) return null;
  return new Date(Date.now() - days * 86400000).toISOString();
}

function BarChart({ data, color = "amber" }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  const barColor = { amber: "bg-amber-400", teal: "bg-teal-400", blue: "bg-blue-400", purple: "bg-purple-400" };
  return (
    <div className="space-y-2">
      {data.map((item) => (
        <div key={item.label} className="flex items-center gap-3">
          <div className="w-28 shrink-0 text-[12px] text-stone-600 truncate capitalize">{item.label}</div>
          <div className="flex-1 bg-stone-100 rounded-full h-5 overflow-hidden">
            <div
              className={`${barColor[color]} h-full rounded-full transition-all`}
              style={{ width: `${Math.max((item.value / max) * 100, 2)}%` }}
            />
          </div>
          <div className="w-10 text-[12px] font-bold text-stone-700 text-right shrink-0">{item.value}</div>
        </div>
      ))}
    </div>
  );
}

function SectionCard({ title, children }) {
  return (
    <div className="card-base p-5">
      <h3 className="font-display font-bold text-ink text-sm mb-4">{title}</h3>
      {children}
    </div>
  );
}

async function fetchAnalytics(since) {
  try {
    const sb = createClient();

    let usersQ = sb.from("profiles").select("*", { count: "exact", head: true });
    let oppsQ = sb.from("opportunities").select("*", { count: "exact", head: true });
    let articlesQ = sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "published");
    let collabQ = sb.from("collaborator_profiles").select("*", { count: "exact", head: true });
    let feedbackQ = sb.from("user_feedback").select("*", { count: "exact", head: true });
    let requestsQ = sb.from("user_requests").select("*", { count: "exact", head: true });

    if (since) {
      usersQ = usersQ.gte("created_at", since);
      oppsQ = oppsQ.gte("created_at", since);
      articlesQ = articlesQ.gte("published_at", since);
      collabQ = collabQ.gte("created_at", since);
      feedbackQ = feedbackQ.gte("created_at", since);
      requestsQ = requestsQ.gte("created_at", since);
    }

    const [
      { count: totalUsers },
      { count: totalOpps },
      { count: totalArticles },
      { count: totalCollabs },
      { count: totalFeedback },
      { count: totalRequests },
      { data: oppsByDistrict },
      { data: oppsByCategory },
      { data: viewsBySlug },
      { data: articles },
      { data: collabDistricts },
    ] = await Promise.all([
      usersQ,
      oppsQ,
      articlesQ,
      collabQ,
      feedbackQ,
      requestsQ,
      sb.from("opportunities").select("district").not("district", "is", null).limit(1000),
      sb.from("opportunities").select("category").not("category", "is", null).limit(1000),
      since
        ? sb.from("page_views").select("page_slug,page_title").gte("created_at", since).limit(2000)
        : sb.from("page_views").select("page_slug,page_title").limit(2000),
      sb.from("research_articles").select("title,slug,views").eq("status", "published").order("views", { ascending: false }).limit(10),
      sb.from("collaborator_profiles").select("district").not("district", "is", null).limit(500),
    ]);

    // Aggregate districts
    const distMap = {};
    (oppsByDistrict || []).forEach(({ district }) => {
      if (district) distMap[district] = (distMap[district] || 0) + 1;
    });
    const topDistricts = Object.entries(distMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, value]) => ({ label, value }));

    // Aggregate categories
    const catMap = {};
    (oppsByCategory || []).forEach(({ category }) => {
      if (category) catMap[category] = (catMap[category] || 0) + 1;
    });
    const topCategories = Object.entries(catMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([label, value]) => ({ label, value }));

    // Top viewed pages from page_views
    const viewMap = {};
    (viewsBySlug || []).forEach(({ page_slug, page_title }) => {
      if (!viewMap[page_slug]) viewMap[page_slug] = { label: page_title || page_slug, value: 0 };
      viewMap[page_slug].value += 1;
    });
    const topViewed = Object.values(viewMap)
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);

    // Top articles by views field
    const topArticles = (articles || [])
      .filter((a) => a.views > 0)
      .map((a) => ({ label: a.title, value: a.views }))
      .slice(0, 8);

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
      topDistricts,
      topCategories,
      topViewed,
      topArticles,
      topCollabDistricts,
    };
  } catch (e) {
    console.error("Analytics fetch error:", e);
    return {
      totals: { users: 0, opportunities: 0, articles: 0, collaborators: 0, feedback: 0, requests: 0 },
      topDistricts: [],
      topCategories: [],
      topViewed: [],
      topArticles: [],
      topCollabDistricts: [],
    };
  }
}

export default async function AnalyticsPage({ searchParams }) {
  const days = parseInt(searchParams?.days) || 30;
  const since = getDateFilter(days);
  const data = await fetchAnalytics(since);

  const STAT_CARDS = [
    { icon: Users, label: "Users", value: data.totals.users, color: "amber" },
    { icon: Briefcase, label: "Opportunities", value: data.totals.opportunities, color: "teal" },
    { icon: BookOpen, label: "Articles", value: data.totals.articles, color: "purple" },
    { icon: UserCheck, label: "Collaborators", value: data.totals.collaborators, color: "blue" },
    { icon: MessageSquare, label: "Feedback", value: data.totals.feedback, color: "rose" },
    { icon: TrendingUp, label: "Requests", value: data.totals.requests, color: "green" },
  ];

  const ACCENT = { amber: "bg-amber-50 text-amber-700", teal: "bg-teal-50 text-teal-700", purple: "bg-purple-50 text-purple-700", blue: "bg-blue-50 text-blue-700", rose: "bg-rose-50 text-rose-700", green: "bg-green-50 text-green-700" };

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header + Time Filter */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-amber-100 text-amber-700 border border-amber-200">ANALYTICS</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Analytics Dashboard</h1>
            <p className="text-stone-500 text-sm mt-1">Platform-wide metrics and content performance</p>
          </div>
          <div className="flex gap-2">
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

        {/* Summary Cards */}
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

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <SectionCard title="Top Districts (by Opportunities)">
            {data.topDistricts.length > 0
              ? <BarChart data={data.topDistricts} color="teal" />
              : <p className="text-sm text-stone-400 italic">No district data yet.</p>
            }
          </SectionCard>

          <SectionCard title="Top Opportunity Categories">
            {data.topCategories.length > 0
              ? <BarChart data={data.topCategories} color="amber" />
              : <p className="text-sm text-stone-400 italic">No category data yet.</p>
            }
          </SectionCard>

          <SectionCard title="Top Viewed Pages">
            {data.topViewed.length > 0
              ? <BarChart data={data.topViewed} color="purple" />
              : <p className="text-sm text-stone-400 italic">Page views will appear here as users browse. Integrate page_views tracking to populate this chart.</p>
            }
          </SectionCard>

          <SectionCard title="Top Articles by Views">
            {data.topArticles.length > 0
              ? <BarChart data={data.topArticles} color="blue" />
              : <p className="text-sm text-stone-400 italic">Article view counts appear once articles have a &apos;views&apos; field populated.</p>
            }
          </SectionCard>

          <SectionCard title="Collaborator Districts">
            {data.topCollabDistricts.length > 0
              ? <BarChart data={data.topCollabDistricts} color="teal" />
              : <p className="text-sm text-stone-400 italic">Collaborator district data will populate as users complete the Discover Yourself assessment.</p>
            }
          </SectionCard>

        </div>
      </div>
    </AdminShell>
  );
}
