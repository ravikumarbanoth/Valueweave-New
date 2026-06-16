import Link from "next/link";

const FEATURES = [
  {
    emoji: "🧠",
    title: "Discover Yourself",
    desc: "Free 7-minute assessment — find your archetype, founder role, and matched opportunities.",
    href: "/discover",
    bg: "bg-violet-50",
    border: "border-violet-200",
  },
  {
    emoji: "💡",
    title: "Explore Business Ideas",
    desc: "122 curated startup and local business ideas across 8 sectors, filtered by your budget.",
    href: "/ideas",
    bg: "bg-amber-50",
    border: "border-amber-200",
  },
  {
    emoji: "📍",
    title: "District Intelligence",
    desc: "Real opportunity demand data from 22 districts across Telangana and Andhra Pradesh.",
    href: "/district",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
  },
  {
    emoji: "📊",
    title: "Research Reports",
    desc: "Deep-dive market research reports on healthcare, agri-tech, EV and more sectors.",
    href: "/research",
    bg: "bg-blue-50",
    border: "border-blue-200",
  },
  {
    emoji: "🤝",
    title: "Collaborator Marketplace",
    desc: "Find co-founders, partners, and skilled collaborators ready to build with you.",
    href: "/collaborators",
    bg: "bg-teal-50",
    border: "border-teal-200",
  },
  {
    emoji: "🚀",
    title: "Opportunity Marketplace",
    desc: "Browse 500+ live business and startup opportunities posted by the community.",
    href: "/explore",
    bg: "bg-rose-50",
    border: "border-rose-200",
  },
];

export default function HomeFeatureGrid() {
  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6 bg-warm">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-teal-100 text-teal-600 mb-4">PLATFORM FEATURES</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            What You Can Do Here
          </h2>
          <p className="mt-4 text-muted max-w-lg mx-auto text-base sm:text-lg">
            Every tool you need to go from idea to execution.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f) => (
            <Link
              key={f.href}
              href={f.href}
              className={`${f.bg} border-2 ${f.border} rounded-2xl p-6 flex flex-col gap-3 hover:-translate-y-1 hover:shadow-md transition-all group min-h-[44px]`}
            >
              <div className="text-3xl">{f.emoji}</div>
              <div>
                <h3 className="font-display font-bold text-base text-ink mb-1 group-hover:text-amber-700 transition-colors">
                  {f.title}
                </h3>
                <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
