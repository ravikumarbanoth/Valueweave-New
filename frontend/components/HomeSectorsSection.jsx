"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/language";

export default function HomeSectorsSection() {
  const { t } = useLanguage();

  const SECTORS = [
    { e: "🤖", l: t("sector.ai_tech", "AI & Tech"), c: "bg-blue-50" },
    { e: "🏪", l: t("sector.local_biz", "Local Biz"), c: "bg-amber-50" },
    { e: "⚡", l: t("sector.ev_tech", "EV Tech"), c: "bg-green-50" },
    { e: "🚁", l: t("sector.drone", "Drone"), c: "bg-violet-50" },
    { e: "🌾", l: t("sector.agriculture", "Agriculture"), c: "bg-emerald-50" },
    { e: "🎓", l: t("sector.student", "Student"), c: "bg-rose-50" },
    { e: "🔧", l: t("sector.trades", "Trades"), c: "bg-yellow-50" },
    { e: "📱", l: t("sector.digital", "Digital"), c: "bg-sky-50" },
  ];

  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6 bg-warm">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-amber-100 text-amber-700 mb-4">{t("home.fits_chip", "WHATEVER YOU DO")}</span>
          <h2 className="h-section">
            {t("home.fits_title_1", "Whatever you already do,")} <span className="text-amber-500">{t("home.fits_title_2", "it fits here.")}</span>
          </h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {SECTORS.map((cat, i) => (
            <div key={i} className={`${cat.c} rounded-2xl p-5 text-center border border-stone-100 hover:-translate-y-1 hover:shadow-sm transition-all`}>
              <div className="text-3xl mb-2">{cat.e}</div>
              <div className="font-display font-bold text-sm">{cat.l}</div>
            </div>
          ))}
        </div>
        <div className="text-center mt-10">
          <Link href="/explore" className="btn-secondary">{t("home.explore_opps", "Explore opportunities →")}</Link>
        </div>
      </div>
    </section>
  );
}
