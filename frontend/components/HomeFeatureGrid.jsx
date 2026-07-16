import Link from "next/link";
import InfrastructureCard from "@/components/platform/InfrastructureCard";
import KnowledgeSearch from "@/components/platform/KnowledgeSearch";
import { featuredKnowledge, futureInfrastructureModules, knowledgeLabels } from "@/lib/static-knowledge";

const FEATURES = [
  {
    emoji: "📍",
    title: "District Intelligent Digital Infrastructure",
    subtitle: "Know where to build.",
    description: "Understand local economic context before choosing what to build and where to start.",
    href: "/districts",
    accent: "green",
    buttonLabel: "Explore Districts",
    items: ["District Intelligence", "Opportunity Discovery", "Resources", "Industries", "Government Schemes"],
  },
  {
    emoji: "🛠️",
    title: "Skill & Industrial Readiness",
    subtitle: "Become capable of building.",
    description: "Prepare founders, students, and operators with practical readiness pathways.",
    href: "/readiness",
    accent: "teal",
    buttonLabel: "Start Learning",
    items: ["Skill Assessment", "Learning Paths", "Training", "Internships", "Apprenticeships", "Mentors"],
  },
  {
    emoji: "🤝",
    title: "Collaboration & Capital Infrastructure",
    subtitle: "Find the right people and resources.",
    description: "Organize the human and capital network needed to turn local opportunity into execution.",
    href: "/network",
    accent: "rose",
    buttonLabel: "Build Network",
    items: ["Co-founders", "Experts", "Investors", "Institutions", "Communities"],
  },
  {
    emoji: "🏭",
    title: "Digital Manufacturing Operating System",
    subtitle: "Build and operate manufacturing businesses.",
    description: "Create the future operating layer for product, factory, machinery, and production planning.",
    href: "/manufacturing",
    accent: "amber",
    buttonLabel: "Explore Manufacturing",
    items: ["Product Discovery", "Manufacturing Guides", "Factory Planning", "Machinery", "Production"],
  },
  {
    emoji: "📈",
    title: "Industrial Scaling Resources",
    subtitle: "Grow into globally competitive manufacturers.",
    description: "Support businesses as they move from first production to scalable industrial operations.",
    href: "/scale",
    accent: "blue",
    buttonLabel: "Scale Business",
    items: ["Automation", "Robotics", "Export", "Quality", "Logistics"],
  },
  {
    emoji: "✨",
    title: "AI Intelligence Layer",
    subtitle: "Connect and optimize every decision.",
    description: "Reserved for future AI guidance across districts, readiness, manufacturing, and scaling.",
    href: "/ai",
    accent: "violet",
    buttonLabel: "View AI Layer",
    comingSoon: true,
    items: ["AI District Advisor", "AI Manufacturing Advisor", "AI Readiness Advisor", "AI Scale Advisor"],
  },
];

const JOURNEY = [
  { label: "Idea", href: "/ideas" },
  { label: "Discover Opportunity", href: "/districts" },
  { label: "Develop Skills", href: "/readiness" },
  { label: "Find Team", href: "/network" },
  { label: "Secure Funding", href: "/network" },
  { label: "Build Factory", href: "/manufacturing" },
  { label: "Manufacture", href: "/manufacturing" },
  { label: "Scale", href: "/scale" },
  { label: "Export", href: "/scale" },
  { label: "Become Mentor", href: "/network" },
];

export default function HomeFeatureGrid() {
  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6 bg-warm">
      <div className="max-w-6xl mx-auto space-y-16">
        <div>
          <div className="text-center mb-12">
            <span className="chip bg-teal-100 text-teal-600 mb-4">INDIA&apos;S DIGITAL ECONOMIC INFRASTRUCTURE</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
              India&apos;s Digital Economic Infrastructure
            </h2>
            <p className="mt-4 text-muted max-w-3xl mx-auto text-base sm:text-lg leading-relaxed">
              ValueWeave is becoming the permanent gateway for district opportunity discovery, industrial readiness, collaboration, manufacturing, scaling, and future AI intelligence.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((feature) => <InfrastructureCard key={feature.href} {...feature} />)}
          </div>
        </div>

        <section className="card-base p-5 sm:p-7 overflow-hidden">
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mb-7">
            <div>
              <span className="chip bg-amber-100 text-amber-700 border border-amber-200 mb-3">THE ENTREPRENEUR JOURNEY</span>
              <h2 className="font-display font-extrabold text-2xl sm:text-3xl text-ink">Entrepreneur Journey</h2>
              <p className="text-sm sm:text-base text-muted mt-2 max-w-2xl leading-relaxed">
                A visual path from first idea to local manufacturing, export readiness, and mentoring others back into the ecosystem.
              </p>
            </div>
            <Link href="/districts" className="btn-primary shrink-0">Start with districts</Link>
          </div>

          <div className="overflow-x-auto pb-2">
            <div className="min-w-[1120px] grid grid-cols-10 gap-3 items-stretch">
              {JOURNEY.map((stage, index) => (
                <Link key={stage.label} href={stage.href} className="relative rounded-2xl bg-stone-50 border border-stone-150 p-4 hover:border-amber-300 hover:bg-amber-50 transition-colors group">
                  <span className="w-8 h-8 rounded-full bg-white border border-stone-200 flex items-center justify-center text-xs font-display font-bold text-amber-700 mb-3">
                    {index + 1}
                  </span>
                  <p className="font-display font-bold text-sm text-ink leading-tight group-hover:text-amber-700">{stage.label}</p>
                  {index < JOURNEY.length - 1 && (
                    <span className="absolute -right-3 top-1/2 -translate-y-1/2 text-amber-500 font-display font-extrabold">→</span>
                  )}
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section>
          <div className="text-center mb-10">
            <span className="chip bg-blue-100 text-blue-700 border border-blue-200 mb-4">STATIC KNOWLEDGE LAYER</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-ink">Explore Knowledge</h2>
            <p className="text-muted mt-3 max-w-2xl mx-auto leading-relaxed">
              Early static knowledge previews show how ValueWeave will connect places, sectors, learning, schemes, products, and manufacturing opportunities.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-6">
            {featuredKnowledge.map(({ label, type, slug, item }) => (
              <Link key={`${type}-${slug}`} href={`/knowledge/${type}/${slug}`} className="card-base p-5 hover:border-amber-300 hover:shadow-md hover:-translate-y-1 transition-all group">
                <span className="chip bg-stone-50 text-stone-500 border border-stone-100 mb-3">{label}</span>
                <h3 className="font-display font-bold text-lg text-ink group-hover:text-amber-700 transition-colors">{item.name}</h3>
                <p className="text-xs text-teal-700 font-display font-bold mt-1">{knowledgeLabels[type]}</p>
                <p className="text-sm text-muted mt-3 line-clamp-3 leading-relaxed">
                  {item.summary || item.description || item.purpose || item.overview}
                </p>
              </Link>
            ))}
          </div>
          <KnowledgeSearch />
        </section>

        <section>
          <div className="text-center mb-10">
            <span className="chip bg-violet-100 text-violet-700 border border-violet-200 mb-4">PLANNED MODULES</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-ink">Future Infrastructure Roadmap</h2>
            <p className="text-muted mt-3 max-w-2xl mx-auto leading-relaxed">
              These future infrastructure layers are visible for strategic clarity, but navigation is intentionally disabled until implementation begins.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {futureInfrastructureModules.map((module) => (
              <div key={module.title} className="card-base p-5 min-h-[230px] opacity-90">
                <div className="flex items-start justify-between gap-3 mb-4">
                  <h3 className="font-display font-bold text-lg text-ink leading-tight">{module.title}</h3>
                  <span className="chip bg-violet-50 text-violet-700 border border-violet-100">Planned</span>
                </div>
                <div className="grid gap-2">
                  {module.items.map((item) => (
                    <span key={item} className="flex items-center gap-2 text-sm text-muted">
                      <span className="w-1.5 h-1.5 rounded-full bg-violet-400 shrink-0" />
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
