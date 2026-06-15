import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { TrendingUp, MapPin, Layers, Search, MessageSquare, Briefcase, Users, Zap } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Demand Index | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function ScoreBar({ score, max, color = "amber" }) {
  const pct = max > 0 ? Math.max((score / max) * 100, 2) : 2;
  const bars = { amber: "bg-amber-400", teal: "bg-teal-400", blue: "bg-blue-400" };
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-stone-100 rounded-full h-2.5 overflow-hidden">
        <div className={`${bars[color]} h-full rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[12px] font-bold text-stone-700 w-10 text-right shrink-0">{score}</span>
    </div>
  );
}

function ScoreBadge({ score }) {
  const color = score >= 80 ? "bg-green-100 text-green-700 border-green-200"
    : score >= 50 ? "bg-amber-100 text-amber-700 border-amber-200"
    : "bg-stone-100 text-stone-500 border-stone-200";
  return <span className={`chip border text-[12px] font-extrabold ${color}`}>{score}</span>;
}

// Demand Score Formula (Phase 5):
//   Searches × 1  +  Requests × 2  +  Opp Interests × 3
//   +  Collaborator Interest × 2  +  Page Views × 0.25
function computeDemandMap(searches, requests, interests, collabData, getKey, pageViews = []) {
  const map = {};
  const init = () => ({ searches: 0, requests: 0, interests: 0, collabs: 0, pageViews: 0 });

  searches.forEach((r) => {
    const k = getKey(r);
    if (!k) return;
    if (!map[k]) map[k] = init();
    map[k].searches++;
  });

  requests.forEach((r) => {
    const k = getKey(r);
    if (!k) return;
    if (!map[k]) map[k] = init();
    map[k].requests++;
  });

  interests.forEach((r) => {
    const k = getKey(r);
    if (!k) return;
    if (!map[k]) map[k] = init();
    map[k].interests++;
  });

  collabData.forEach((r) => {
    const k = getKey(r);
    if (!k) return;
    if (!map[k]) map[k] = init();
    map[k].collabs++;
  });

  pageViews.forEach((r) => {
    const k = getKey(r);
    if (!k) return;
    if (!map[k]) map[k] = init();
    map[k].pageViews++;
  });

  return Object.entries(map).map(([key, v]) => ({
    key,
    searches: v.searches,
    requests: v.requests,
    interests: v.interests,
    collabs: v.collabs,
    pageViews: v.pageViews,
    score: Math.round(
      v.searches * 1 +
      v.requests * 2 +
      v.interests * 3 +
      v.collabs * 2 +
      v.pageViews * 0.25
    ),
  })).sort((a, b) => b.score - a.score);
}

async function fetchDemandData() {
  try {
    const sb = createClient();

    const [
      { data: searches },
      { data: requests },
      { data: oppInterests },
      { data: collabSectors },
      { data: collabDistricts },
      { data: opportunities },
      { data: pvData },
    ] = await Promise.all([
      sb.from("search_events").select("query,sector,district").limit(5000),
      sb.from("user_requests").select("title,sector,district").limit(2000),
      sb.from("opportunity_interests").select("opportunity_id").limit(5000),
      sb.from("collaborator_profiles").select("top_sectors").limit(1000),
      sb.from("collaborator_profiles").select("district,state").limit(1000),
      sb.from("opportunities").select("id,category,district,state").limit(2000),
      sb.from("page_views").select("page_type,sector,district").limit(10000),
    ]);

    // Map opp interests to sector/district via joined opportunities
    const oppMap = {};
    (opportunities || []).forEach((o) => { oppMap[o.id] = o; });

    const interestsWithContext = (oppInterests || []).map((i) => {
      const opp = oppMap[i.opportunity_id] || {};
      return { sector: opp.category, district: opp.district };
    });

    // Expand collab sectors into flat rows
    const collabSectorRows = [];
    (collabSectors || []).forEach(({ top_sectors }) => {
      (top_sectors || []).forEach((s) => collabSectorRows.push({ sector: s }));
    });

    const pageViewRows = pvData || [];

    // Demand by sector (passes page_views as 6th arg for ×0.25 weighting)
    const bySector = computeDemandMap(
      searches || [], requests || [], interestsWithContext, collabSectorRows,
      (r) => r.sector || null,
      pageViewRows
    ).slice(0, 15);

    // Demand by district
    const collabDistrictRows = (collabDistricts || []).map((c) => ({ district: c.district }));
    const byDistrict = computeDemandMap(
      searches || [], requests || [], interestsWithContext, collabDistrictRows,
      (r) => r.district || null,
      pageViewRows
    ).slice(0, 15);

    // Demand by state
    const collabStateRows = (collabDistricts || []).map((c) => ({ state: c.state }));
    const byState = computeDemandMap(
      [], [], interestsWithContext, collabStateRows,
      (r) => r.state || null,
      []
    ).slice(0, 5);

    const totalSignals = (searches?.length || 0) + (requests?.length || 0) +
      (oppInterests?.length || 0) + Math.round((pageViewRows.length || 0) * 0.25);

    return { bySector, byDistrict, byState, totalSignals, hasData: totalSignals > 0 };
  } catch (e) {
    console.error("Demand index error:", e);
    return { bySector: [], byDistrict: [], byState: [], totalSignals: 0, hasData: false };
  }
}

function DemandTable({ rows, keyLabel, showBreakdown }) {
  const max = Math.max(...rows.map((r) => r.score), 1);
  if (rows.length === 0) {
    return <p className="text-sm text-stone-400 italic p-4">No demand data yet. Populates as users search and request content.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[12px]">
        <thead>
          <tr className="border-b border-stone-200">
            <th className="text-left py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">#</th>
            <th className="text-left py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">{keyLabel}</th>
            {showBreakdown && <>
              <th className="text-right py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">Searches</th>
              <th className="text-right py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">Requests</th>
              <th className="text-right py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">Interests</th>
              <th className="text-right py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">Collabs</th>
              <th className="text-right py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">Views</th>
            </>}
            <th className="text-right py-2.5 px-4 text-[10px] text-stone-400 uppercase tracking-widest">Score</th>
            <th className="py-2.5 px-4 w-32 text-[10px] text-stone-400 uppercase tracking-widest">Demand</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.key} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
              <td className="py-2.5 px-4 text-stone-400 font-bold text-[11px]">{i + 1}</td>
              <td className="py-2.5 px-4">
                <span className="font-semibold text-ink capitalize">{r.key}</span>
              </td>
              {showBreakdown && <>
                <td className="py-2.5 px-4 text-right text-stone-500">{r.searches}</td>
                <td className="py-2.5 px-4 text-right text-stone-500">{r.requests * 2} <span className="text-stone-300 text-[10px]">(×2)</span></td>
                <td className="py-2.5 px-4 text-right text-stone-500">{r.interests * 3} <span className="text-stone-300 text-[10px]">(×3)</span></td>
                <td className="py-2.5 px-4 text-right text-stone-500">{r.collabs * 2} <span className="text-stone-300 text-[10px]">(×2)</span></td>
                <td className="py-2.5 px-4 text-right text-stone-500">{Math.round(r.pageViews * 0.25)} <span className="text-stone-300 text-[10px]">(×0.25)</span></td>
              </>}
              <td className="py-2.5 px-4 text-right">
                <ScoreBadge score={r.score} />
              </td>
              <td className="py-2.5 px-4">
                <ScoreBar score={r.score} max={max} color="amber" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function DemandIndexPage() {
  const { bySector, byDistrict, byState, totalSignals, hasData } = await fetchDemandData();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-amber-100 text-amber-700 border border-amber-200">DEMAND INDEX</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Opportunity Demand Index</h1>
          <p className="text-stone-500 text-sm mt-1">
            Demand scored from actual user signals — no fake data
          </p>
        </div>

        {/* Formula */}
        <div className="card-base p-5 bg-amber-50 border-amber-200">
          <h3 className="font-display font-bold text-amber-800 text-sm mb-3 flex items-center gap-2">
            <Zap size={14} /> Demand Score Formula
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[12px] text-amber-700">
            <div className="flex items-center gap-2">
              <Search size={12} /> Searches × 1
            </div>
            <div className="flex items-center gap-2">
              <MessageSquare size={12} /> Requests × 2
            </div>
            <div className="flex items-center gap-2">
              <Briefcase size={12} /> Interests × 3
            </div>
            <div className="flex items-center gap-2">
              <Users size={12} /> Collab demand × 1
            </div>
          </div>
        </div>

        {/* Signal counts */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "Total Signals", value: totalSignals, color: "bg-amber-50 text-amber-700" },
            { label: "Top Sector Score", value: bySector[0]?.score || 0, color: "bg-teal-50 text-teal-700" },
            { label: "Top District Score", value: byDistrict[0]?.score || 0, color: "bg-blue-50 text-blue-700" },
          ].map(({ label, value, color }) => (
            <div key={label} className="card-base p-4 text-center">
              <div className={`text-2xl font-display font-extrabold rounded-lg px-2 py-1 inline-block ${color}`}>{value}</div>
              <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-1">{label}</div>
            </div>
          ))}
        </div>

        {/* Top by State */}
        {byState.length > 0 && (
          <div className="card-base overflow-hidden">
            <div className="p-5 border-b border-stone-100 flex items-center gap-2">
              <MapPin size={15} className="text-teal-500" />
              <h3 className="font-display font-bold text-ink text-sm">Demand by State</h3>
            </div>
            <div className="p-5 flex gap-6">
              {byState.map((r) => (
                <div key={r.key} className="text-center">
                  <ScoreBadge score={r.score} />
                  <p className="text-[12px] font-semibold text-ink mt-1">{r.key}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top by Sector */}
        <div className="card-base overflow-hidden">
          <div className="p-5 border-b border-stone-100 flex items-center gap-2">
            <Layers size={15} className="text-amber-500" />
            <h3 className="font-display font-bold text-ink text-sm">Top Opportunities by Sector</h3>
            <Link href="/admin/opportunity-generator" className="ml-auto text-[11px] text-amber-600 font-semibold hover:underline">
              Generate →
            </Link>
          </div>
          <DemandTable rows={bySector} keyLabel="Sector" showBreakdown={true} />
        </div>

        {/* Top by District */}
        <div className="card-base overflow-hidden">
          <div className="p-5 border-b border-stone-100 flex items-center gap-2">
            <MapPin size={15} className="text-teal-500" />
            <h3 className="font-display font-bold text-ink text-sm">Top Opportunities by District</h3>
            <Link href="/admin/districts" className="ml-auto text-[11px] text-amber-600 font-semibold hover:underline">
              District view →
            </Link>
          </div>
          <DemandTable rows={byDistrict} keyLabel="District" showBreakdown={false} />
        </div>

      </div>
    </AdminShell>
  );
}
