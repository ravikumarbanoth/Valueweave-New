const MILESTONES = [
  {
    period: "Day 1",
    title: "Answer a few questions",
    desc: "Answer a few questions and we will suggest ideas that suit you.",
    color: "bg-violet-50 border-violet-200",
    dot: "bg-violet-400",
  },
  {
    period: "Week 1",
    title: "Look around",
    desc: "Browse business ideas matched to your district, your budget and what you can do.",
    color: "bg-amber-50 border-amber-200",
    dot: "bg-amber-400",
  },
  {
    period: "Week 2",
    title: "Find people nearby",
    desc: "Find people nearby who have the skills you do not.",
    color: "bg-teal-50 border-teal-200",
    dot: "bg-teal-400",
  },
  {
    period: "Month 1",
    title: "Post what you are building",
    desc: "Post what you are building, and let people ask to join you.",
    color: "bg-emerald-50 border-emerald-200",
    dot: "bg-emerald-400",
  },
  {
    period: "Month 3",
    title: "Grow it",
    desc: "Work out where to sell, what it costs to grow, and who can fund it.",
    color: "bg-rose-50 border-rose-200",
    dot: "bg-rose-400",
  },
];

export default function HomeSuccessJourney() {
  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-14">
          <span className="chip bg-teal-100 text-teal-600 mb-4">STEP BY STEP</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            What to do next
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
