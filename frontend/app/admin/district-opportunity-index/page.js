import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import { DISTRICTS } from "@/lib/districts-data";
import Link from "next/link";
import { MapPin, Trophy, TrendingUp, Activity, Grid } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "District Opportunity Index | ValueWeave Admin",
  robots: { index: false, follow: false },
};

// Opportunity Potential Score formula (0–100)
// Traffic × 0.15 + Demand × 0.30 + Collaborators × 0.20 + Opportunities × 0.20 + Research × 0.15
function potentialScore({ visits, demand, collabs, opps, articles }) {
  const t = Math.min(visits / 100, 1) * 15;
  const d = Math.min(demand / 50, 1) * 30;
  const c = Math.min(collabs / 20, 1) * 20;
  const o = Math.min(opps / 50, 1) * 20;
  const r = Math.min(articles / 10, 1) * 15;
  return Math.round(t + d + c + o + r);
}

async function fetchDistrictIndex() {
  try {
    const sb = createClient();

    const [
      { data: pageViewsData },
      { data: searchData },
      { data: requestData },
      { data: collabData },
      { data: oppData },
      { data: articleData },
    ] = await Promise.all([
      sb.from("page_views").select("district").not("district", "is", null).limit(10000),
      sb.from("search_events").select("district").not("district", "is", null).limit(5000),
      sb.from("user_requests").select("district").not("district", "is", null).limit(2000),
      sb.from("collaborator_profiles").select("district").not("district", "is", null).limit(1000),
      sb.from("opportunities").select("district").not("district", "is", null).limit(2000),
      sb.from("research_articles").select("district").not("district", "is", null).eq("status", "published").limit(500),
    ]);

    const count = (rows, field = "district") => {
      const m = {};
      (rows || []).forEach((r) => { if (r[field]) m[r[field]] = (m[r[field]] || 0) + 1; });
      return m;
    };

    const visitMap = count(pageViewsData);
    const searchMap = count(searchData);
    const requestMap = count(requestData);
    const collabMap = count(collabData);
    const oppMap = count(oppData);
    const articleMap = count(articleData);

    const enriched = DISTRICTS.map((d) => {
      const visits = visitMap[d.name] || 0;
      const searches = searchMap[d.name] || 0;
      const requests = requestMap[d.name] || 0;
      const demand = searches + requests * 2;
      const collabs = collabMap[d.name] || 0;
      const opps = oppMap[d.name] || 0;
      const articles = articleMap[d.name] || 0;
      const score = potentialScore({ visits, demand, collabs, opps, articles });
      return { slug: d.slug, name: d.name, state: d.state, visits, demand, collabs, opps, articles, score };
    }).sort((a, b) => b.score - a.score);

    const tsRanked = enriched.filter((d) => d.state === "Telangana");
    const apRanked = enriched.filter((d) => d.state === "Andhra Pradesh");

    return { enriched, tsRanked, apRanked };
  } catch (e) {
    console.error("District opportunity index error:", e);
    return {
      enriched: DISTRICTS.map((d, i) => ({ slug: d.slug, name: d.name, state: d.state, visits: 0, demand: 0, collabs: 0, opps: 0, articles: 0, score: 0 })),
      tsRanked: [], apRanked: [],
    };
  }
}

function ScoreRing({ score, size = "md" }) {
  const color = score >= 60 ? "text-green-600 border-green-200 bg-green-50"
    : score >= 35 ? "text-amber-600 border-amber-200 bg-amber-50"
    : "text-stone-500 border-stone-200 bg-stone-50";
  const dim = size === "lg" ? "w-16 h-16 text-xl" : "w-12 h-12 text-base";
  return (
    <div className={`rounded-full border-2 flex items-center justify-center shrink-0 font-display font-extrabold ${dim} ${color}`}>
      {score}
    </div>
  );
}

function DistrictRankCard({ rank, district, showMedal }) {
  const medals = ["🥇", "🥈", "🥉"];
  return (
    <div className="card-base p-4 flex items-center gap-3 hover:shadow-md transition-shadow">
      <div className="text-stone-300 font-bold text-[13px] w-6 text-center shrink-0">
        {showMedal && rank <= 3 ? medals[rank - 1] : `#${rank}`}
      </div>
      <ScoreRing score={district.score} />
      <div className="flex-1 min-w-0">
        <Link href={`/district/${district.slug}`} className="font-display font-bold text-ink hover:text-amber-700 transition-colors text-sm">
          {district.name}
        </Link>
        <div className="flex flex-wrap gap-1 mt-1">
          {district.opps > 0 && <span className="text-[10px] text-stone-400">{district.opps} opps</span>}
          {district.collabs > 0 && <span className="text-[10px] text-stone-400">· {district.collabs} collabs</span>}
          {district.demand > 0 && <span className="text-[10px] text-stone-400">· demand:{district.demand}</span>}
        </div>
      </div>
      <Link
        href={`/admin/opportunity-generator?district=${encodeURIComponent(district.name)}`}
        className="chip bg-amber-50 text-amber-700 border border-amber-200 text-[10px] shrink-0 hover:bg-amber-100 transition-colors"
      >
        Generate
      </Link>
    </div>
  );
}

export default async function DistrictOpportunityIndexPage({ searchParams }) {
  const view = searchParams?.view || "ts";
  const { enriched, tsRanked, apRanked } = await fetchDistrictIndex();

  const allRanked = [...enriched].sort((a, b) => b.score - a.score);
  const top3 = allRanked.slice(0, 3);

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-blue-100 text-blue-700 border border-blue-200">DISTRICT OPPORTUNITY INDEX</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">District Opportunity Index</h1>
          <p className="text-stone-500 text-sm mt-1">
            Ranked by Opportunity Potential Score = Traffic (15%) + Demand (30%) + Collaborators (20%) + Opportunities (20%) + Research (15%)
          </p>
        </div>

        {/* Top 3 podium */}
        <div className="grid grid-cols-3 gap-4">
          {top3.map((d, i) => (
            <div key={d.slug} className="card-base p-5 text-center">
              <div className="text-2xl mb-2">{["🥇", "🥈", "🥉"][i]}</div>
              <Link href={`/district/${d.slug}`} className="font-display font-bold text-ink hover:text-amber-700 transition-colors">
                {d.name}
              </Link>
              <p className="text-[11px] text-stone-400 mb-3">{d.state}</p>
              <ScoreRing score={d.score} size="lg" />
              <p className="text-[10px] text-stone-400 mt-2 uppercase tracking-wide">Potential Score</p>
            </div>
          ))}
        </div>

        {/* Formula explainer */}
        <div className="card-base p-4 bg-stone-50 flex flex-wrap gap-4 text-[12px] text-stone-600">
          {[
            { label: "Traffic", weight: "15%" },
            { label: "Demand (searches+requests)", weight: "30%" },
            { label: "Collaborators", weight: "20%" },
            { label: "Opportunities", weight: "20%" },
            { label: "Research Articles", weight: "15%" },
          ].map(({ label, weight }) => (
            <div key={label} className="flex items-center gap-1.5">
              <span className="chip bg-amber-100 text-amber-700 text-[10px]">{weight}</span>
              <span>{label}</span>
            </div>
          ))}
        </div>

        {/* State selector */}
        <div className="flex gap-2">
          {[
            { key: "ts", label: "Telangana", count: tsRanked.length },
            { key: "ap", label: "Andhra Pradesh", count: apRanked.length },
            { key: "all", label: "All Districts", count: enriched.length },
          ].map(({ key, label, count }) => (
            <Link
              key={key}
              href={`?view=${key}`}
              className={`px-4 py-2 rounded-full text-[12px] font-semibold transition-colors ${
                view === key
                  ? "bg-teal-500 text-white"
                  : "bg-white border border-stone-200 text-stone-500 hover:border-teal-400"
              }`}
            >
              {label} <span className="text-[10px] opacity-70">({count})</span>
            </Link>
          ))}
        </div>

        {/* Ranked list */}
        <div className="space-y-2">
          {(view === "ts" ? tsRanked : view === "ap" ? apRanked : allRanked).map((d, i) => (
            <DistrictRankCard key={d.slug} rank={i + 1} district={d} showMedal={true} />
          ))}
        </div>

      </div>
    </AdminShell>
  );
}
