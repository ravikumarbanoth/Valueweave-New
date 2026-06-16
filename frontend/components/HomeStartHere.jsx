import Link from "next/link";

const CARDS = [
  {
    emoji: "🧠",
    title: "I Want to Discover Myself",
    desc: "Find your archetype, strengths, founder role and suitable opportunities.",
    btn: "Start Discovering →",
    href: "/discover",
    bg: "bg-violet-50",
    border: "border-violet-200",
    btnClass: "btn-teal",
  },
  {
    emoji: "💡",
    title: "I Need Business Ideas",
    desc: "Explore 122 curated startup and local business opportunities.",
    btn: "Browse Ideas →",
    href: "/ideas",
    bg: "bg-amber-50",
    border: "border-amber-200",
    btnClass: "btn-primary",
  },
  {
    emoji: "🤝",
    title: "I Need Collaborators",
    desc: "Find co-founders, partners and skilled people to build with.",
    btn: "Find Collaborators →",
    href: "/collaborators",
    bg: "bg-teal-50",
    border: "border-teal-200",
    btnClass: "btn-teal",
  },
];

export default function HomeStartHere() {
  return (
    <section className="py-16 sm:py-20 px-4 sm:px-6 bg-warm">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-10">
          <span className="chip bg-amber-100 text-amber-700 mb-4">START HERE</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl tracking-tight text-ink mb-3">
            Not sure where to begin?
          </h2>
          <p className="text-muted text-base sm:text-lg">
            Choose your goal and we&apos;ll guide you.
          </p>
        </div>

        <div className="grid sm:grid-cols-3 gap-5">
          {CARDS.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className={`${card.bg} border-2 ${card.border} rounded-2xl p-7 flex flex-col items-start gap-4 hover:-translate-y-1 hover:shadow-lg transition-all group min-h-[44px]`}
            >
              <div className="text-4xl">{card.emoji}</div>
              <div>
                <h3 className="font-display font-extrabold text-lg text-ink mb-2 group-hover:text-amber-700 transition-colors">
                  {card.title}
                </h3>
                <p className="text-sm text-muted leading-relaxed">{card.desc}</p>
              </div>
              <span className={`${card.btnClass} mt-auto text-sm !py-2.5 !px-5`}>
                {card.btn}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
