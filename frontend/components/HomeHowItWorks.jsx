import Link from "next/link";

const STEPS = [
  {
    emoji: "🧠",
    label: "Discover Yourself",
    desc: "Find your founder archetype and strengths",
    href: "/discover",
    color: "bg-violet-50 border-violet-200",
    iconBg: "bg-violet-100 text-violet-700",
  },
  {
    emoji: "💡",
    label: "Get Personalized Ideas",
    desc: "122 curated ideas matched to your profile",
    href: "/ideas",
    color: "bg-amber-50 border-amber-200",
    iconBg: "bg-amber-100 text-amber-700",
  },
  {
    emoji: "📍",
    label: "Explore District Opportunities",
    desc: "Real opportunities in your own district",
    href: "/district",
    color: "bg-emerald-50 border-emerald-200",
    iconBg: "bg-emerald-100 text-emerald-700",
  },
  {
    emoji: "🤝",
    label: "Find Collaborators",
    desc: "Connect with co-founders and partners",
    href: "/collaborators",
    color: "bg-teal-50 border-teal-200",
    iconBg: "bg-teal-100 text-teal-700",
  },
  {
    emoji: "🚀",
    label: "Build Your Venture",
    desc: "Launch your project from your hometown",
    href: "/explore",
    color: "bg-rose-50 border-rose-200",
    iconBg: "bg-rose-100 text-rose-700",
  },
];

export default function HomeHowItWorks() {
  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <span className="chip bg-amber-100 text-amber-700 mb-4">HOW VALUEWEAVE WORKS</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            How ValueWeave Works
          </h2>
          <p className="mt-4 text-muted max-w-lg mx-auto text-base sm:text-lg">
            Five steps from self-discovery to launching your venture.
          </p>
        </div>

        {/* Desktop: horizontal flow */}
        <div className="hidden md:flex items-start gap-0">
          {STEPS.map((step, i) => (
            <div key={step.label} className="flex items-start flex-1 min-w-0">
              <Link
                href={step.href}
                className={`flex-1 min-w-0 border-2 rounded-2xl p-5 flex flex-col items-center text-center gap-3 hover:-translate-y-1 hover:shadow-md transition-all ${step.color}`}
              >
                <div className={`w-14 h-14 rounded-full flex items-center justify-center text-2xl ${step.iconBg} shrink-0`}>
                  {step.emoji}
                </div>
                <div>
                  <div className="font-display font-bold text-sm text-ink mb-1">{step.label}</div>
                  <div className="text-xs text-muted leading-relaxed">{step.desc}</div>
                </div>
              </Link>
              {i < STEPS.length - 1 && (
                <div className="flex items-center justify-center w-8 shrink-0 mt-7">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-stone-300">
                    <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Mobile: vertical flow */}
        <div className="md:hidden flex flex-col items-center gap-0">
          {STEPS.map((step, i) => (
            <div key={step.label} className="flex flex-col items-center w-full max-w-xs">
              <Link
                href={step.href}
                className={`w-full border-2 rounded-2xl p-5 flex items-center gap-4 hover:shadow-md transition-all ${step.color}`}
              >
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl shrink-0 ${step.iconBg}`}>
                  {step.emoji}
                </div>
                <div>
                  <div className="font-display font-bold text-sm text-ink mb-0.5">{step.label}</div>
                  <div className="text-xs text-muted leading-relaxed">{step.desc}</div>
                </div>
              </Link>
              {i < STEPS.length - 1 && (
                <div className="py-2">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-stone-300 rotate-90">
                    <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
