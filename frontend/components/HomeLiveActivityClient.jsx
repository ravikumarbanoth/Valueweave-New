"use client";

import { useLanguage } from "@/lib/language";

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

const PULSE_COLORS = [
  "bg-amber-400",
  "bg-teal-400",
  "bg-violet-400",
  "bg-emerald-400",
  "bg-rose-400",
];

export default function HomeLiveActivityClient({ items }) {
  const { t } = useLanguage();

  if (!items || items.length === 0) return null;

  return (
    <section className="py-16 sm:py-20 px-4 sm:px-6 bg-warm">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-10">
          <span className="chip bg-emerald-100 text-emerald-700 mb-4 inline-flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            {t("activity.chip", "LIVE ACTIVITY")}
          </span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight text-ink mb-3">
            {t("activity.title", "What's Happening Now")}
          </h2>
          <p className="text-muted text-sm">
            {t("activity.subtitle", "Anonymous activity from ValueWeave builders across India.")}
          </p>
        </div>

        <div className="card-base divide-y divide-stone-100 overflow-hidden">
          {items.map((item, i) => (
            <div key={i} className="flex items-center gap-3 px-5 py-3.5">
              <div className={`w-2 h-2 rounded-full shrink-0 ${PULSE_COLORS[i % PULSE_COLORS.length]}`} />
              <p className="text-sm text-ink flex-1">{item.text}</p>
              <span className="text-[11px] text-stone-400 shrink-0 font-semibold">
                {timeAgo(item.created_at)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
