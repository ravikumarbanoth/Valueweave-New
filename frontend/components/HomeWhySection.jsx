"use client";

import { useLanguage } from "@/lib/language";

function GapCard({ icon, title, desc }) {
  return (
    <div className="card-base p-6 hover:-translate-y-1 hover:shadow-md transition-all">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-display font-bold text-base mb-2">{title}</h3>
      <p className="text-sm text-muted leading-relaxed">{desc}</p>
    </div>
  );
}

export default function HomeWhySection() {
  const { t } = useLanguage();

  const GAP_CARDS = [
    {
      icon: "??",
      title: t("home.gap_1_title", "Talent without visibility"),
      desc: t("home.gap_1_desc", "An electrician in Warangal, a coder in Vizag, a baker in Guntur. Good at the work, unknown to the people who would hire or partner with them."),
    },
    {
      icon: "??",
      title: t("home.gap_2_title", "Ideas without teams"),
      desc: t("home.gap_2_desc", "You can have a good idea and still not know a single person nearby who can help you build it."),
    },
    {
      icon: "??",
      title: t("home.gap_3_title", "Trust without proof"),
      desc: t("home.gap_3_desc", "Job sites reward job titles. Freelance sites reward the lowest bid. Neither shows you what someone can actually do."),
    },
  ];

  return (
    <section id="why" className="bg-warm py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-teal-100 text-teal-600 mb-4">{t("home.why_chip", "WHY WE BUILT THIS")}</span>
          <h2 className="h-section">
            {t("home.why_title_1", "Skill is not the problem.")}<br />
            <span className="text-teal-500">{t("home.why_title_2", "Knowing where to take it is.")}</span>
          </h2>
          <p className="mt-5 text-muted max-w-2xl mx-auto text-base sm:text-lg leading-relaxed">
            {t("home.why_desc", "Plenty of people can do the work. Far fewer know which scheme applies to them, who is hiring nearby, or what it costs to start on their own.")}
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-5">
          {GAP_CARDS.map((card, i) => <GapCard key={i} {...card} />)}
        </div>

        <div className="text-center mt-12">
          <p className="font-display font-bold text-lg max-w-2xl mx-auto leading-snug text-ink">
            {t("home.why_summary", "So we researched it and put it in one place: what to learn, what to start, which schemes apply, and who is nearby.")}
          </p>
        </div>
      </div>
    </section>
  );
}
