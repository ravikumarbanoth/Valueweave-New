import { createClient } from "@/lib/supabase-server";
import { Activity } from "lucide-react";

async function computeHealthScore() {
  try {
    const sb = createClient();
    const d7 = new Date(Date.now() - 7 * 86400000).toISOString();

    const [
      { count: collabCount },
      { count: oppCount },
      { data: districts },
      { count: articleCount },
      { count: sessions7 },
      { count: userCount },
      { count: questionsCount },
      { count: feedbackCount },
      { count: requestsCount },
    ] = await Promise.all([
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
      sb.from("opportunities").select("*", { count: "exact", head: true }).eq("status", "open"),
      sb.from("opportunities").select("district").not("district", "is", null).limit(1000),
      sb.from("research_articles").select("*", { count: "exact", head: true }).eq("status", "published"),
      sb.from("visitor_sessions").select("*", { count: "exact", head: true }).gte("created_at", d7),
      sb.from("profiles").select("*", { count: "exact", head: true }),
      sb.from("questions").select("*", { count: "exact", head: true }).eq("status", "open"),
      sb.from("user_feedback").select("*", { count: "exact", head: true }),
      sb.from("user_requests").select("*", { count: "exact", head: true }),
    ]);

    const uniqueDistricts = new Set((districts || []).map((d) => d.district)).size;
    const totalUsers = userCount || 0;
    const sessionRate = totalUsers > 0 ? (sessions7 || 0) / totalUsers : 0;
    const communitySignals = (questionsCount || 0) + (feedbackCount || 0) + (requestsCount || 0);

    // Score each dimension (max 100 total)
    const c = collabCount  || 0;
    const o = oppCount     || 0;
    const a = articleCount || 0;

    const scoreCollabs  = c >= 100 ? 20 : c >= 50 ? 15 : c >= 20 ? 10 : c >= 5 ? 5  : 0;
    const scoreOpps     = o >= 500 ? 20 : o >= 200 ? 15 : o >= 50 ? 10 : o >= 10 ? 5 : 0;
    const scoreDistricts = uniqueDistricts >= 20 ? 15 : uniqueDistricts >= 10 ? 10 : uniqueDistricts >= 5 ? 7 : uniqueDistricts >= 2 ? 3 : 0;
    const scoreArticles = a >= 50  ? 15 : a >= 20 ? 10  : a >= 10 ? 7  : a >= 3  ? 3  : 0;
    const scoreEngagement = sessionRate >= 2 ? 15 : sessionRate >= 1 ? 10 : sessionRate >= 0.5 ? 7 : sessionRate >= 0.1 ? 3 : 0;
    const scoreCommunity  = communitySignals >= 100 ? 15 : communitySignals >= 50 ? 10 : communitySignals >= 20 ? 7 : communitySignals >= 5 ? 3 : 0;

    const total = scoreCollabs + scoreOpps + scoreDistricts + scoreArticles + scoreEngagement + scoreCommunity;

    return {
      total,
      dimensions: [
        { label: "Collaborators",  score: scoreCollabs,    max: 20, value: c },
        { label: "Opportunities",  score: scoreOpps,       max: 20, value: o },
        { label: "Districts",      score: scoreDistricts,  max: 15, value: uniqueDistricts },
        { label: "Articles",       score: scoreArticles,   max: 15, value: a },
        { label: "Engagement",     score: scoreEngagement, max: 15, value: `${(sessionRate * 100).toFixed(0)}%` },
        { label: "Community",      score: scoreCommunity,  max: 15, value: communitySignals },
      ],
    };
  } catch {
    return { total: 0, dimensions: [] };
  }
}

function scoreColor(pct) {
  if (pct >= 80) return { ring: "text-green-600", bar: "bg-green-400", badge: "bg-green-100 text-green-700" };
  if (pct >= 60) return { ring: "text-teal-600",  bar: "bg-teal-400",  badge: "bg-teal-100 text-teal-700" };
  if (pct >= 40) return { ring: "text-amber-600", bar: "bg-amber-400", badge: "bg-amber-100 text-amber-700" };
  return           { ring: "text-rose-600",   bar: "bg-rose-400",   badge: "bg-rose-100 text-rose-700" };
}

function scoreLabel(pct) {
  if (pct >= 80) return "Excellent";
  if (pct >= 60) return "Good";
  if (pct >= 40) return "Growing";
  return "Early Stage";
}

export default async function HealthScore() {
  const { total, dimensions } = await computeHealthScore();
  const colors = scoreColor(total);

  return (
    <div className="card-base p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-bold text-ink text-sm flex items-center gap-2">
          <Activity size={14} className="text-teal-500" />
          Business Health Score
        </h3>
        <span className={`chip text-[10px] font-bold ${colors.badge}`}>
          {scoreLabel(total)}
        </span>
      </div>

      {/* Score circle */}
      <div className="flex items-center gap-6 mb-5">
        <div className={`w-20 h-20 rounded-full border-4 flex items-center justify-center flex-col shrink-0 ${total >= 80 ? "border-green-400" : total >= 60 ? "border-teal-400" : total >= 40 ? "border-amber-400" : "border-rose-400"}`}>
          <span className={`font-display font-extrabold text-2xl leading-none ${colors.ring}`}>{total}</span>
          <span className="text-[9px] text-stone-400 font-semibold">/100</span>
        </div>
        <div className="flex-1 space-y-1">
          {dimensions.map(({ label, score, max, value }) => {
            const pct = max > 0 ? Math.round((score / max) * 100) : 0;
            const dimColors = scoreColor(pct);
            return (
              <div key={label}>
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-[11px] text-stone-500 font-semibold">{label}</span>
                  <span className="text-[10px] text-stone-400">{score}/{max}</span>
                </div>
                <div className="bg-stone-100 rounded-full h-1.5 overflow-hidden">
                  <div className={`h-full rounded-full ${dimColors.bar}`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <p className="text-[11px] text-stone-400 leading-relaxed">
        Formula: Collaborators (20) + Opportunities (20) + Districts (15) + Articles (15) + Weekly Engagement (15) + Community Signals (15)
      </p>
    </div>
  );
}
