import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { Lightbulb, Search, TrendingUp, FileText, Briefcase, ArrowRight } from "lucide-react";
import IDEAS from "@/lib/idea-library/ideas.json";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Content Opportunities | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function scoreColor(score) {
  if (score >= 80) return "bg-green-100 text-green-700 border border-green-200";
  if (score >= 60) return "bg-amber-100 text-amber-700 border border-amber-200";
  return "bg-stone-100 text-stone-500";
}

function computeOpportunities({ searches, requests, articles, existingIdeas }) {
  // Aggregate searches
  const kwMap = {};
  searches.forEach(({ query }) => {
    if (!query) return;
    const kw = query.toLowerCase().trim();
    if (kw.length < 3) return;
    if (!kwMap[kw]) kwMap[kw] = { searches: 0, requests: 0 };
    kwMap[kw].searches += 1;
  });

  // Aggregate requests
  requests.forEach(({ title, sector }) => {
    if (!title) return;
    const kw = title.toLowerCase().trim();
    if (!kwMap[kw]) kwMap[kw] = { searches: 0, requests: 0, sector };
    kwMap[kw].requests += 1;
    if (sector && !kwMap[kw].sector) kwMap[kw].sector = sector;
  });

  // Existing content slugs/titles for matching
  const existingArticleTitles = new Set(articles.map((a) => a.title.toLowerCase()));
  const existingIdeaTitles = new Set(existingIdeas.map((i) => (i.title || "").toLowerCase()));

  const scored = Object.entries(kwMap)
    .filter(([, v]) => v.searches + v.requests >= 1)
    .map(([keyword, v]) => {
      const hasArticle = [...existingArticleTitles].some((t) => t.includes(keyword) || keyword.includes(t.split(" ")[0]));
      const hasIdea = [...existingIdeaTitles].some((t) => t.toLowerCase().includes(keyword) || keyword.includes(t.toLowerCase().split(" ")[0]));
      const existingContent = hasArticle || hasIdea;
      // Priority score: demand signals minus penalty if content exists
      const score = Math.min(
        100,
        Math.round(v.searches * 2 + v.requests * 3 - (existingContent ? 20 : 0))
      );
      return {
        keyword,
        searches: v.searches,
        requests: v.requests,
        sector: v.sector || null,
        existingContent,
        hasArticle,
        hasIdea,
        score: Math.max(0, score),
      };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, 20);

  return scored;
}

async function fetchData() {
  try {
    const sb = createClient();
    const [
      { data: searches },
      { data: requests },
      { data: articles },
    ] = await Promise.all([
      sb.from("search_events").select("query").limit(5000),
      sb.from("user_requests").select("title,sector").limit(2000),
      sb.from("research_articles").select("title,slug").eq("status", "published").limit(500),
    ]);

    const opportunities = computeOpportunities({
      searches: searches || [],
      requests: requests || [],
      articles: articles || [],
      existingIdeas: IDEAS || [],
    });

    return { opportunities, hasData: (searches?.length || 0) + (requests?.length || 0) > 0 };
  } catch (e) {
    console.error("Content opportunities error:", e);
    return { opportunities: [], hasData: false };
  }
}

// Demo data for empty-state illustration
const DEMO_ITEMS = [
  { keyword: "Diagnostic Center", searches: 41, requests: 12, existingContent: false, hasArticle: false, hasIdea: false, score: 92, sector: "healthcare" },
  { keyword: "Cold Storage Facility", searches: 28, requests: 9, existingContent: false, hasArticle: false, hasIdea: true, score: 73, sector: "agriculture" },
  { keyword: "EV Charging Station", searches: 35, requests: 5, existingContent: true, hasArticle: true, hasIdea: true, score: 55, sector: "energy" },
  { keyword: "EdTech Platform", searches: 19, requests: 7, existingContent: false, hasArticle: false, hasIdea: false, score: 59, sector: "education" },
  { keyword: "Organic Farming Cluster", searches: 22, requests: 4, existingContent: false, hasArticle: false, hasIdea: false, score: 56, sector: "agriculture" },
];

export default async function ContentOpportunitiesPage() {
  const { opportunities, hasData } = await fetchData();

  const items = hasData ? opportunities : DEMO_ITEMS;
  const isDemo = !hasData;

  return (
    <AdminShell>
      <div className="p-6 max-w-5xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-blue-100 text-blue-700 border border-blue-200">CONTENT OPPORTUNITIES</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Content Opportunity Detector</h1>
          <p className="text-stone-500 text-sm mt-1">
            Compares user demand signals against existing content to surface gaps with the highest priority score.
          </p>
        </div>

        {isDemo && (
          <div className="card-base p-4 border-l-4 border-amber-400 bg-amber-50">
            <p className="text-sm text-amber-800">
              <strong>Demo mode:</strong> Showing illustrative data. Live insights appear once users generate search events and requests.
            </p>
          </div>
        )}

        {/* Scoring Explainer */}
        <div className="card-base p-5 bg-stone-50">
          <h3 className="font-display font-bold text-ink text-sm mb-3 flex items-center gap-2">
            <Lightbulb size={15} className="text-amber-500" /> Priority Score Formula
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[12px] text-stone-600">
            <div className="flex items-center gap-2">
              <Search size={12} className="text-amber-500" /> Searches × 2
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp size={12} className="text-teal-500" /> Requests × 3
            </div>
            <div className="flex items-center gap-2">
              <FileText size={12} className="text-stone-400" /> − 20 if content exists
            </div>
          </div>
        </div>

        {/* Opportunity Cards */}
        {items.length === 0 ? (
          <div className="card-base p-12 text-center">
            <Lightbulb size={32} className="text-stone-300 mx-auto mb-3" />
            <p className="text-stone-400 text-sm">No content gaps detected yet.</p>
            <p className="text-stone-300 text-xs mt-1">Add search tracking and a user request form to populate this page.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item, i) => (
              <div key={i} className="card-base p-5 hover:shadow-md transition-shadow">
                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                  {/* Rank + keyword */}
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="text-xl font-display font-extrabold text-stone-300 w-8 shrink-0">
                      #{i + 1}
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-display font-bold text-ink text-base capitalize">{item.keyword}</h3>
                      {item.sector && (
                        <span className="chip bg-stone-100 text-stone-500 text-[10px] mt-1">{item.sector}</span>
                      )}
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 shrink-0">
                    <div className="text-center">
                      <div className="text-lg font-bold text-ink">{item.searches}</div>
                      <div className="text-[10px] text-stone-400 uppercase tracking-wide">Searches</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-ink">{item.requests}</div>
                      <div className="text-[10px] text-stone-400 uppercase tracking-wide">Requests</div>
                    </div>
                    <div className="text-center">
                      <span className={`chip text-[11px] font-bold ${item.existingContent ? "bg-stone-100 text-stone-400" : "bg-green-100 text-green-700"}`}>
                        {item.existingContent ? "EXISTS" : "MISSING"}
                      </span>
                      <div className="text-[10px] text-stone-400 uppercase tracking-wide mt-1">Content</div>
                    </div>
                    <div className="text-center">
                      <span className={`chip text-[13px] font-extrabold ${scoreColor(item.score)}`}>
                        {item.score}
                      </span>
                      <div className="text-[10px] text-stone-400 uppercase tracking-wide mt-1">Score</div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-stone-100">
                  <Link
                    href={`/admin/research/new?prefill=${encodeURIComponent(item.keyword)}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[12px] font-semibold hover:bg-purple-100 transition-colors"
                  >
                    <FileText size={12} /> Create Research Article
                  </Link>
                  <Link
                    href={`/admin/opportunity-generator?sector=${encodeURIComponent(item.sector || "")}&keyword=${encodeURIComponent(item.keyword)}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-[12px] font-semibold hover:bg-amber-100 transition-colors"
                  >
                    <Briefcase size={12} /> Create Opportunity
                  </Link>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200 text-[12px] font-semibold">
                    <ArrowRight size={12} /> Priority: {item.score >= 80 ? "High" : item.score >= 60 ? "Medium" : "Low"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminShell>
  );
}
