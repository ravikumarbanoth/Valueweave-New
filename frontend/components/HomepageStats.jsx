// Server component — queries real Supabase data for homepage social proof.
// Renders honest empty state if no data exists yet.

import { createClient } from "@/lib/supabase-server";
import { Users, Briefcase, MapPin, UserCheck, Eye } from "lucide-react";

async function fetchStats() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return { visitors: 0, collaborators: 0, opportunities: 0, districts: 0, assessments: 0 };
  }
  try {
    const sb = createClient();
    const [
      { count: visitors },
      { count: collaborators },
      { count: opportunities },
      { data: districtRows },
      { count: assessments },
    ] = await Promise.all([
      sb.from("visitor_sessions").select("visitor_id", { count: "exact", head: true }),
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
      sb.from("opportunities").select("*", { count: "exact", head: true }).eq("status", "open"),
      sb.from("collaborator_profiles").select("district").not("district", "is", null).limit(200),
      // Discover assessments = collaborator_profiles (completing the quiz creates a profile)
      sb.from("collaborator_profiles").select("*", { count: "exact", head: true }),
    ]);

    const districtSet = new Set((districtRows || []).map((r) => r.district).filter(Boolean));

    return {
      visitors: visitors || 0,
      collaborators: collaborators || 0,
      opportunities: opportunities || 0,
      districts: districtSet.size,
      assessments: assessments || 0,
    };
  } catch {
    return { visitors: 0, collaborators: 0, opportunities: 0, districts: 0, assessments: 0 };
  }
}

function fmt(n) {
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "K+";
  return n > 0 ? n.toLocaleString() : null;
}

const STATS = [
  { key: "visitors",     icon: Eye,       label: "Visitors",           emptyLabel: "Early access" },
  { key: "assessments",  icon: Users,     label: "Discover Profiles",  emptyLabel: "Be the first" },
  // "Coming soon" was wrong on both counts: the feature is live, and the number
  // being zero is a fact about the marketplace rather than a promise about it.
  { key: "opportunities",icon: Briefcase, label: "Open Opportunities", emptyLabel: "None open yet" },
  { key: "collaborators",icon: UserCheck, label: "Collaborators",      emptyLabel: "Join us" },
  { key: "districts",    icon: MapPin,    label: "Districts Covered",  emptyLabel: "Expanding" },
];

export default async function HomepageStats() {
  const stats = await fetchStats();
  const hasAnyData = Object.values(stats).some((v) => v > 0);

  return (
    <section className="py-14 px-4 sm:px-6 bg-ink/[0.02] border-y border-stone-200/60">
      <div className="max-w-5xl mx-auto">
        {hasAnyData ? (
          <>
            <p className="text-center text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-8">
              Who is here so far
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6">
              {STATS.map(({ key, icon: Icon, label, emptyLabel }) => {
                const value = stats[key];
                const display = fmt(value);
                return (
                  <div key={key} className="text-center group">
                    <div className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-amber-50 text-amber-600 mb-3 mx-auto group-hover:bg-amber-100 transition-colors">
                      <Icon size={18} />
                    </div>
                    {display ? (
                      <div className="font-display font-extrabold text-2xl sm:text-3xl text-ink tracking-tight">
                        {display}
                      </div>
                    ) : (
                      <div className="font-display font-bold text-base text-stone-300">{emptyLabel}</div>
                    )}
                    <div className="text-[11px] text-stone-400 font-semibold mt-1 uppercase tracking-widest">
                      {label}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="text-center py-4">
            <p className="text-[13px] text-stone-400 italic">
              Platform launching soon — be among the first to join.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
