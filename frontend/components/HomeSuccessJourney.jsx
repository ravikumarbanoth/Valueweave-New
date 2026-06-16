const MILESTONES = [
  {
    period: "Day 1",
    title: "Take Assessment",
    desc: "Complete the free Discover Yourself quiz to find your archetype and matched opportunities.",
    color: "bg-violet-50 border-violet-200",
    dot: "bg-violet-400",
  },
  {
    period: "Week 1",
    title: "Explore Opportunities",
    desc: "Browse 122 ideas and 500+ live opportunities matched to your district and sector.",
    color: "bg-amber-50 border-amber-200",
    dot: "bg-amber-400",
  },
  {
    period: "Week 2",
    title: "Find Collaborators",
    desc: "Connect with co-founders, mentors, and skilled partners who want to build with you.",
    color: "bg-teal-50 border-teal-200",
    dot: "bg-teal-400",
  },
  {
    period: "Month 1",
    title: "Launch Project",
    desc: "Post your opportunity, form your team, and take the first steps toward your venture.",
    color: "bg-emerald-50 border-emerald-200",
    dot: "bg-emerald-400",
  },
  {
    period: "Month 3",
    title: "Grow Venture",
    desc: "Scale with community support, research insights, and district-level market intelligence.",
    color: "bg-rose-50 border-rose-200",
    dot: "bg-rose-400",
  },
];

export default function HomeSuccessJourney() {
  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-14">
          <span className="chip bg-teal-100 text-teal-600 mb-4">YOUR PATH</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            Your Startup Journey
          </h2>
          <p className="mt-4 text-muted max-w-lg mx-auto text-base sm:text-lg">
            From first click to funded venture — here&apos;s the roadmap.
          </p>
        </div>

        {/* Desktop: horizontal timeline */}
        <div className="hidden md:block relative">
          <div className="absolute top-6 left-0 right-0 h-0.5 bg-stone-200 z-0" />
          <div className="relative z-10 grid grid-cols-5 gap-4">
            {MILESTONES.map((m) => (
              <div key={m.period} className="flex flex-col items-center gap-3">
                <div className={`w-12 h-12 rounded-full border-2 ${m.color} flex items-center justify-center shrink-0`}>
                  <div className={`w-3 h-3 rounded-full ${m.dot}`} />
                </div>
                <div className={`${m.color} border-2 rounded-2xl p-4 text-center w-full`}>
                  <div className="font-display font-extrabold text-xs text-amber-600 uppercase tracking-widest mb-1">
                    {m.period}
                  </div>
                  <div className="font-display font-bold text-sm text-ink mb-1.5">{m.title}</div>
                  <div className="text-xs text-muted leading-relaxed">{m.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mobile: vertical timeline */}
        <div className="md:hidden relative pl-8">
          <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-stone-200" />
          <div className="flex flex-col gap-6">
            {MILESTONES.map((m) => (
              <div key={m.period} className="relative flex gap-4">
                <div className={`absolute -left-[29px] w-5 h-5 rounded-full border-2 ${m.color} flex items-center justify-center shrink-0 mt-1`}>
                  <div className={`w-2 h-2 rounded-full ${m.dot}`} />
                </div>
                <div className={`${m.color} border-2 rounded-2xl p-4 flex-1`}>
                  <div className="font-display font-extrabold text-xs text-amber-600 uppercase tracking-widest mb-1">
                    {m.period}
                  </div>
                  <div className="font-display font-bold text-sm text-ink mb-1.5">{m.title}</div>
                  <div className="text-xs text-muted leading-relaxed">{m.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
