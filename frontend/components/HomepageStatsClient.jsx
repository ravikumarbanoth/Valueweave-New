"use client";

import { Users, Briefcase, MapPin, UserCheck, Eye } from "lucide-react";
import { useLanguage } from "@/lib/language";

function fmt(n) {
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "K+";
  return n > 0 ? n.toLocaleString() : null;
}

export default function HomepageStatsClient({ stats }) {
  const { t } = useLanguage();

  const STATS = [
    { key: "visitors", icon: Eye, label: t("stats.visitors", "Visitors"), emptyLabel: "Early access" },
    { key: "assessments", icon: Users, label: t("stats.assessments", "Discover Profiles"), emptyLabel: "Be the first" },
    { key: "opportunities", icon: Briefcase, label: t("stats.opportunities", "Open Opportunities"), emptyLabel: "None open yet" },
    { key: "collaborators", icon: UserCheck, label: t("stats.collaborators", "Collaborators"), emptyLabel: "Join us" },
    { key: "districts", icon: MapPin, label: t("stats.districts", "Districts Covered"), emptyLabel: "Expanding" },
  ];

  const hasAnyData = Object.values(stats || {}).some((v) => v > 0);

  return (
    <section className="py-14 px-4 sm:px-6 bg-ink/[0.02] border-y border-stone-200/60">
      <div className="max-w-5xl mx-auto">
        {hasAnyData ? (
          <>
            <p className="text-center text-[11px] font-semibold text-stone-400 uppercase tracking-widest mb-8">
              {t("stats.who_is_here", "Who is here so far")}
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6">
              {STATS.map(({ key, icon: Icon, label, emptyLabel }) => {
                const value = stats?.[key];
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
              {t("stats.launching_soon", "Platform launching soon — be among the first to join.")}
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
