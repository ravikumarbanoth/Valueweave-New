"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/language";

export default function HomeDiscoverSection() {
  const { t } = useLanguage();

  const DISCOVER_CARDS = [
    { emoji: "💡", label: t("archetype.innovator", "Innovator"), desc: t("archetype.innovator_desc", "Product & Strategy Lead — spots opportunities others miss."), bg: "bg-violet-50", border: "border-violet-200" },
    { emoji: "👑", label: t("archetype.leader", "Leader"), desc: t("archetype.leader_desc", "CEO / Managing Director — sets direction and owns outcomes."), bg: "bg-rose-50", border: "border-rose-200" },
    { emoji: "⚙️", label: t("archetype.builder", "Builder"), desc: t("archetype.builder_desc", "Operations & Delivery Lead — makes things actually run."), bg: "bg-amber-50", border: "border-amber-200" },
    { emoji: "📣", label: t("archetype.influencer", "Influencer"), desc: t("archetype.influencer_desc", "Marketing & Sales Lead — tells the story, builds the brand."), bg: "bg-pink-50", border: "border-pink-200" },
  ];

  return (
    <section id="discover" className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        <div>
          <span className="chip bg-teal-100 text-teal-600 mb-4">{t("home.discover_chip", "FREE ASSESSMENT")}</span>
          <h2 className="h-section mb-5">
            {t("home.discover_heading_1", "Not sure what suits you?")}<br />
            <span className="text-teal-500">{t("home.discover_heading_2", "Answer a few questions.")}</span>
          </h2>
          <p className="text-muted text-base sm:text-lg leading-relaxed mb-6 max-w-md">
            {t("home.discover_desc", "Seven minutes, free. Tell us your district, what you are interested in and what you could invest, and we will suggest business ideas that fit.")}
          </p>
          <ul className="flex flex-col gap-2.5 mb-7">
            {[
              ["🎯", t("home.discover_bullet_1", "Which kind of work suits you — building, leading, selling or planning")],
              ["📍", t("home.discover_bullet_2", "Business ideas that suit your district")],
              ["💰", t("home.discover_bullet_3", "Only ideas you could actually afford, from ₹30,000 upwards")],
              ["🤝", t("home.discover_bullet_4", "Post your best idea and let people ask to join you")],
            ].map(([icon, text], i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-muted">
                <span className="text-base">{icon}</span>
                <span className="leading-relaxed">{text}</span>
              </li>
            ))}
          </ul>
          <Link href="/discover" data-testid="section-cta-discover" className="btn-teal">
            {t("home.take_assessment", "Take the free assessment →")}
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {DISCOVER_CARDS.map((card, i) => (
            <div key={i} className={`${card.bg} border ${card.border} rounded-2xl p-5 hover:-translate-y-1 hover:shadow-md transition-all`}>
              <div className="text-3xl mb-2">{card.emoji}</div>
              <div className="font-display font-bold text-sm mb-1">{card.label}</div>
              <div className="text-xs text-muted leading-relaxed">{card.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
