import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import MatchActions from "./MatchActions";
import { Users, Star, MapPin, Briefcase, Zap, Info, Award, BarChart3 } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Founder Matches | ValueWeave Admin",
  robots: { index: false, follow: false },
};

// Archetype compatibility matrix (higher = more compatible)
const ARCHETYPE_COMPAT = {
  Builder: { Innovator: 90, Analyst: 85, Explorer: 75, Leader: 70, Researcher: 80, Influencer: 65, Caregiver: 60, Builder: 50 },
  Innovator: { Builder: 90, Researcher: 85, Analyst: 80, Explorer: 85, Leader: 65, Influencer: 70, Caregiver: 60, Innovator: 50 },
  Leader: { Builder: 70, Analyst: 80, Caregiver: 75, Influencer: 85, Researcher: 70, Innovator: 65, Explorer: 70, Leader: 50 },
  Analyst: { Builder: 85, Leader: 80, Researcher: 90, Innovator: 80, Explorer: 70, Influencer: 60, Caregiver: 65, Analyst: 50 },
  Caregiver: { Leader: 75, Influencer: 80, Explorer: 70, Builder: 60, Researcher: 65, Analyst: 65, Innovator: 60, Caregiver: 50 },
  Explorer: { Innovator: 85, Builder: 75, Influencer: 75, Researcher: 80, Leader: 70, Analyst: 70, Caregiver: 70, Explorer: 50 },
  Researcher: { Innovator: 85, Analyst: 90, Builder: 80, Explorer: 80, Leader: 70, Influencer: 60, Caregiver: 65, Researcher: 50 },
  Influencer: { Leader: 85, Caregiver: 80, Explorer: 75, Innovator: 70, Builder: 65, Analyst: 60, Researcher: 60, Influencer: 50 },
};

const BUDGET_COMPAT = {
  "Under ₹2L": { "Under ₹2L": 100, "₹2L – ₹5L": 70, "₹5L – ₹10L": 40, "₹10L – ₹25L": 20, "₹25L – ₹50L": 10, "₹50L – ₹1Cr": 5, "Above ₹1Cr": 5 },
  "₹2L – ₹5L": { "Under ₹2L": 70, "₹2L – ₹5L": 100, "₹5L – ₹10L": 75, "₹10L – ₹25L": 50, "₹25L – ₹50L": 30, "₹50L – ₹1Cr": 15, "Above ₹1Cr": 5 },
  "₹5L – ₹10L": { "₹2L – ₹5L": 75, "₹5L – ₹10L": 100, "₹10L – ₹25L": 80, "₹25L – ₹50L": 60, "₹50L – ₹1Cr": 40, "Under ₹2L": 40, "Above ₹1Cr": 20 },
  "₹10L – ₹25L": { "₹5L – ₹10L": 80, "₹10L – ₹25L": 100, "₹25L – ₹50L": 85, "₹50L – ₹1Cr": 65, "₹2L – ₹5L": 50, "Under ₹2L": 20, "Above ₹1Cr": 40 },
  "₹25L – ₹50L": { "₹10L – ₹25L": 85, "₹25L – ₹50L": 100, "₹50L – ₹1Cr": 85, "₹5L – ₹10L": 60, "₹2L – ₹5L": 30, "Under ₹2L": 10, "Above ₹1Cr": 60 },
  "₹50L – ₹1Cr": { "₹25L – ₹50L": 85, "₹50L – ₹1Cr": 100, "Above ₹1Cr": 80, "₹10L – ₹25L": 65, "₹5L – ₹10L": 40, "₹2L – ₹5L": 15, "Under ₹2L": 5 },
  "Above ₹1Cr": { "₹50L – ₹1Cr": 80, "Above ₹1Cr": 100, "₹25L – ₹50L": 60, "₹10L – ₹25L": 40, "₹5L – ₹10L": 20, "₹2L – ₹5L": 5, "Under ₹2L": 5 },
};

function computeMatchScore(a, b) {
  let score = 0;

  // Sector overlap (30 pts max)
  const aS = new Set(a.top_sectors || []);
  const bS = new Set(b.top_sectors || []);
  const overlap = [...aS].filter((s) => bS.has(s)).length;
  score += Math.min(overlap * 15, 30);

  // District proximity (20 pts)
  if (a.district && b.district) {
    if (a.district === b.district) score += 20;
    else if (a.state === b.state) score += 10;
  }

  // Archetype compatibility (25 pts)
  if (a.archetype && b.archetype) {
    const compat = ARCHETYPE_COMPAT[a.archetype]?.[b.archetype] || 50;
    score += Math.round((compat / 100) * 25);
  }

  // Budget compatibility (25 pts)
  if (a.budget && b.budget) {
    const budgetScore = BUDGET_COMPAT[a.budget]?.[b.budget] ?? 50;
    score += Math.round((budgetScore / 100) * 25);
  }

  return Math.min(Math.round(score), 100);
}

function determineMatchType(a, b) {
  const aRole = (a.founder_role || "").toLowerCase();
  const bRole = (b.founder_role || "").toLowerCase();
  if (aRole.includes("mentor") || bRole.includes("mentor")) return "mentor";
  if (aRole.includes("investor") || bRole.includes("investor")) return "mentor";
  if (a.archetype === b.archetype) return "team";
  return "co-founder";
}

async function fetchMatchData() {
  try {
    const sb = createClient();

    const [{ data: collabs }, { data: savedMatches }] = await Promise.all([
      sb.from("collaborator_profiles")
        .select("user_id,archetype,secondary_archetype,founder_role,district,state,top_sectors,budget,ep_score,open_to_collaborate")
        .eq("open_to_collaborate", true)
        .limit(200),
      sb.from("founder_matches")
        .select("id,user1_id,user2_id,match_score,match_type,status,sector,district")
        .order("match_score", { ascending: false })
        .limit(50),
    ]);

    // Compute new potential matches (only if not already saved)
    const savedPairs = new Set(
      (savedMatches || []).map((m) => `${m.user1_id}|${m.user2_id}`)
    );

    const candidates = collabs || [];
    const newMatches = [];

    for (let i = 0; i < candidates.length; i++) {
      for (let j = i + 1; j < candidates.length; j++) {
        const a = candidates[i];
        const b = candidates[j];
        const pairKey = `${a.user_id}|${b.user_id}`;
        const pairKeyRev = `${b.user_id}|${a.user_id}`;
        if (savedPairs.has(pairKey) || savedPairs.has(pairKeyRev)) continue;

        const score = computeMatchScore(a, b);
        if (score >= 50) {
          newMatches.push({
            user1_id: a.user_id,
            user2_id: b.user_id,
            match_score: score,
            match_type: determineMatchType(a, b),
            sector: ([...new Set([...(a.top_sectors || []), ...(b.top_sectors || [])])]).slice(0, 1)[0] || null,
            district: a.district === b.district ? a.district : null,
            status: "pending",
          });
        }

        if (newMatches.length >= 50) break;
      }
      if (newMatches.length >= 50) break;
    }

    // Auto-save new matches above threshold 60
    const highQuality = newMatches.filter((m) => m.match_score >= 60);
    if (highQuality.length > 0) {
      await sb.from("founder_matches").upsert(highQuality, { onConflict: "user1_id,user2_id", ignoreDuplicates: true });
    }

    // Re-fetch all matches after upsert
    const { data: allMatches } = await sb
      .from("founder_matches")
      .select("id,user1_id,user2_id,match_score,match_type,status,sector,district,notes")
      .order("match_score", { ascending: false })
      .limit(50);

    // Fetch profile names for display
    const userIds = new Set();
    (allMatches || []).forEach((m) => { userIds.add(m.user1_id); userIds.add(m.user2_id); });
    const { data: profiles } = await sb
      .from("profiles")
      .select("id,name,email,city")
      .in("id", [...userIds].filter(Boolean).slice(0, 100));

    const profileMap = {};
    (profiles || []).forEach((p) => { profileMap[p.id] = p; });

    const collabMap = {};
    (collabs || []).forEach((c) => { collabMap[c.user_id] = c; });

    const enrichedMatches = (allMatches || []).map((m) => ({
      ...m,
      user1: profileMap[m.user1_id] || { name: "User", email: "" },
      user2: profileMap[m.user2_id] || { name: "User", email: "" },
      collab1: collabMap[m.user1_id] || {},
      collab2: collabMap[m.user2_id] || {},
    }));

    const pendingCount = enrichedMatches.filter((m) => m.status === "pending").length;
    const approvedCount = enrichedMatches.filter((m) => m.status === "approved").length;
    const ignoredCount = enrichedMatches.filter((m) => m.status === "ignored").length;
    const contactedCount = enrichedMatches.filter((m) => m.status === "contacted").length;

    // Success rate = approved / (approved + ignored)
    const decided = approvedCount + ignoredCount;
    const successRate = decided > 0 ? Math.round((approvedCount / decided) * 100) : null;

    // Best archetype combos (from approved matches)
    const archetypeComboMap = {};
    enrichedMatches.filter((m) => m.status === "approved").forEach((m) => {
      const a1 = m.collab1.archetype;
      const a2 = m.collab2.archetype;
      if (a1 && a2) {
        const combo = [a1, a2].sort().join(" + ");
        archetypeComboMap[combo] = (archetypeComboMap[combo] || 0) + 1;
      }
    });
    const bestArchetypes = Object.entries(archetypeComboMap)
      .sort((a, b) => b[1] - a[1]).slice(0, 5).map(([combo, count]) => ({ combo, count }));

    // Best sectors by approval count
    const sectorMap2 = {};
    enrichedMatches.forEach((m) => {
      if (!m.sector) return;
      if (!sectorMap2[m.sector]) sectorMap2[m.sector] = { approved: 0, total: 0 };
      sectorMap2[m.sector].total++;
      if (m.status === "approved") sectorMap2[m.sector].approved++;
    });
    const bestSectors = Object.entries(sectorMap2)
      .sort((a, b) => b[1].approved - a[1].approved || b[1].total - a[1].total)
      .slice(0, 5).map(([sector, v]) => ({ sector, approved: v.approved, total: v.total }));

    // Best districts by approval count
    const districtMap2 = {};
    enrichedMatches.forEach((m) => {
      if (!m.district) return;
      if (!districtMap2[m.district]) districtMap2[m.district] = { approved: 0, total: 0 };
      districtMap2[m.district].total++;
      if (m.status === "approved") districtMap2[m.district].approved++;
    });
    const bestDistricts = Object.entries(districtMap2)
      .sort((a, b) => b[1].approved - a[1].approved || b[1].total - a[1].total)
      .slice(0, 5).map(([district, v]) => ({ district, approved: v.approved, total: v.total }));

    return {
      matches: enrichedMatches,
      pendingCount, approvedCount, ignoredCount, contactedCount,
      successRate, bestArchetypes, bestSectors, bestDistricts,
      totalCandidates: candidates.length,
    };
  } catch (e) {
    console.error("Matches error:", e);
    return {
      matches: [], pendingCount: 0, approvedCount: 0, ignoredCount: 0, contactedCount: 0,
      successRate: null, bestArchetypes: [], bestSectors: [], bestDistricts: [],
      totalCandidates: 0,
    };
  }
}

function scoreColor(score) {
  if (score >= 80) return "bg-green-100 text-green-700 border border-green-200";
  if (score >= 65) return "bg-amber-100 text-amber-700 border border-amber-200";
  return "bg-stone-100 text-stone-500";
}

const TYPE_CHIP = {
  "co-founder": "bg-purple-100 text-purple-700",
  "team": "bg-blue-100 text-blue-700",
  "mentor": "bg-teal-100 text-teal-700",
};

export default async function FounderMatchesPage() {
  const {
    matches, pendingCount, approvedCount, ignoredCount, contactedCount,
    successRate, bestArchetypes, bestSectors, bestDistricts, totalCandidates,
  } = await fetchMatchData();

  return (
    <AdminShell>
      <div className="p-6 max-w-5xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-rose-100 text-rose-700 border border-rose-200">FOUNDER MATCHING</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Founder Matching Engine</h1>
          <p className="text-stone-500 text-sm mt-1">
            Deterministic scoring based on sector overlap, district proximity, archetype compatibility, and budget alignment.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: "Candidates", value: totalCandidates, color: "bg-blue-50 text-blue-700" },
            { label: "Total Matches", value: matches.length, color: "bg-purple-50 text-purple-700" },
            { label: "Pending", value: pendingCount, color: "bg-amber-50 text-amber-700" },
            { label: "Approved", value: approvedCount, color: "bg-green-50 text-green-700" },
            { label: "Contacted", value: contactedCount, color: "bg-teal-50 text-teal-700" },
            { label: "Success Rate", value: successRate !== null ? `${successRate}%` : "—", color: "bg-rose-50 text-rose-700" },
          ].map(({ label, value, color }) => (
            <div key={label} className="card-base p-4 text-center">
              <div className={`text-xl font-display font-extrabold inline-block px-3 py-1 rounded-lg ${color}`}>{value}</div>
              <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-2">{label}</div>
            </div>
          ))}
        </div>

        {/* Match Quality Engine */}
        {(bestArchetypes.length > 0 || bestSectors.length > 0 || bestDistricts.length > 0) && (
          <div className="card-base overflow-hidden">
            <div className="p-5 border-b border-stone-100 flex items-center gap-2">
              <Award size={15} className="text-amber-500" />
              <h3 className="font-display font-bold text-ink text-sm">Match Quality Engine</h3>
              <span className="chip bg-amber-50 text-amber-700 text-[10px] ml-auto">From approved matches</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-0 divide-y sm:divide-y-0 sm:divide-x divide-stone-100">

              {/* Best archetype combos */}
              <div className="p-5">
                <h4 className="text-[11px] font-bold text-stone-400 uppercase tracking-widest mb-3">Best Archetype Combos</h4>
                {bestArchetypes.length === 0 ? (
                  <p className="text-[12px] text-stone-300 italic">Appears after approvals</p>
                ) : (
                  <div className="space-y-2">
                    {bestArchetypes.map(({ combo, count }) => (
                      <div key={combo} className="flex items-center justify-between">
                        <span className="text-[12px] font-semibold text-ink">{combo}</span>
                        <span className="chip bg-purple-50 text-purple-700 text-[11px]">{count}×</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Best sectors */}
              <div className="p-5">
                <h4 className="text-[11px] font-bold text-stone-400 uppercase tracking-widest mb-3">Top Sectors</h4>
                {bestSectors.length === 0 ? (
                  <p className="text-[12px] text-stone-300 italic">Appears after matches with sectors</p>
                ) : (
                  <div className="space-y-2">
                    {bestSectors.map(({ sector, approved, total }) => (
                      <div key={sector} className="flex items-center justify-between">
                        <span className="text-[12px] font-semibold text-ink capitalize">{sector}</span>
                        <div className="flex gap-1">
                          <span className="chip bg-green-50 text-green-700 text-[10px]">{approved} approved</span>
                          <span className="chip bg-stone-100 text-stone-400 text-[10px]">{total} total</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Best districts */}
              <div className="p-5">
                <h4 className="text-[11px] font-bold text-stone-400 uppercase tracking-widest mb-3">Top Districts</h4>
                {bestDistricts.length === 0 ? (
                  <p className="text-[12px] text-stone-300 italic">Appears after same-district matches</p>
                ) : (
                  <div className="space-y-2">
                    {bestDistricts.map(({ district, approved, total }) => (
                      <div key={district} className="flex items-center justify-between">
                        <span className="text-[12px] font-semibold text-ink capitalize">{district}</span>
                        <div className="flex gap-1">
                          <span className="chip bg-teal-50 text-teal-700 text-[10px]">{approved} approved</span>
                          <span className="chip bg-stone-100 text-stone-400 text-[10px]">{total} total</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
          </div>
        )}

        {/* Scoring Info */}
        <div className="card-base p-4 bg-stone-50 flex items-start gap-3">
          <Info size={15} className="text-stone-400 mt-0.5 shrink-0" />
          <div className="text-[12px] text-stone-500 space-y-0.5">
            <p><strong className="text-ink">Score components:</strong> Sector overlap (30pts) + District proximity (20pts) + Archetype compatibility (25pts) + Budget alignment (25pts)</p>
            <p>Matches ≥ 60 are auto-saved. Use Approve / Contact Both / Ignore to action each match.</p>
          </div>
        </div>

        {/* Match Cards */}
        {matches.length === 0 ? (
          <div className="card-base p-12 text-center">
            <Users size={32} className="text-stone-300 mx-auto mb-3" />
            <p className="text-stone-400 text-sm">No matches yet.</p>
            <p className="text-stone-300 text-xs mt-1">Matches are generated automatically as collaborators join via the Discover Yourself assessment.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((m) => (
              <div key={m.id} className="card-base p-5">
                <div className="flex flex-col sm:flex-row sm:items-start gap-4">

                  {/* Match score + type */}
                  <div className="flex flex-col items-center gap-2 shrink-0">
                    <span className={`chip text-[14px] font-extrabold ${scoreColor(m.match_score)}`}>
                      {m.match_score}
                    </span>
                    <span className={`chip text-[10px] ${TYPE_CHIP[m.match_type] || "bg-stone-100 text-stone-500"}`}>
                      {m.match_type}
                    </span>
                  </div>

                  {/* Users */}
                  <div className="flex-1 min-w-0">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                      {[
                        { user: m.user1, collab: m.collab1, label: "Person A" },
                        { user: m.user2, collab: m.collab2, label: "Person B" },
                      ].map(({ user, collab, label }) => (
                        <div key={label} className="bg-stone-50 rounded-xl p-3">
                          <p className="font-display font-bold text-ink text-sm">{user.name || "User"}</p>
                          <p className="text-[11px] text-stone-400">{user.email}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {collab.archetype && (
                              <span className="chip bg-purple-50 text-purple-700 text-[10px]">{collab.archetype}</span>
                            )}
                            {collab.district && (
                              <span className="chip bg-stone-100 text-stone-500 text-[10px]">
                                <MapPin size={9} className="inline" /> {collab.district}
                              </span>
                            )}
                            {collab.budget && (
                              <span className="chip bg-amber-50 text-amber-700 text-[10px]">{collab.budget}</span>
                            )}
                          </div>
                          {collab.top_sectors?.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {collab.top_sectors.slice(0, 2).map((s) => (
                                <span key={s} className="chip bg-teal-50 text-teal-700 text-[10px]">{s}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Context */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {m.sector && (
                        <span className="chip bg-amber-50 text-amber-700 border border-amber-100 text-[10px]">
                          <Briefcase size={9} className="inline mr-0.5" /> {m.sector}
                        </span>
                      )}
                      {m.district && (
                        <span className="chip bg-teal-50 text-teal-700 border border-teal-100 text-[10px]">
                          <MapPin size={9} className="inline mr-0.5" /> {m.district}
                        </span>
                      )}
                    </div>

                    {/* Actions */}
                    <MatchActions matchId={m.id} initialStatus={m.status} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminShell>
  );
}
