// Homepage feature grid — Platform v3.0, Step 4.
//
// TWO SECTIONS CHANGED, AND FOR OPPOSITE REASONS.
//
// "Explore Knowledge" used to render `featuredKnowledge` from
// lib/static-knowledge.js: six hard-coded slugs over 56 editorial JSON records,
// under a banner that read "STATIC KNOWLEDGE LAYER · Early static knowledge
// previews". Every one of those six types now exists as researched, sourced,
// confidence-scored data — 647 entities across Packages 001–008 — so the section
// reads the projection and shows what the platform actually holds.
//
// "Future Infrastructure Roadmap" kept its six modules but lost the "Planned"
// chip. None of them has a data source in any package, and that is a different
// and more honest statement than "planned": it says the research does not exist,
// not that the wiring is pending. Each now names the package that would have to
// exist first.
import Link from "next/link";
import InfrastructureCard from "@/components/platform/InfrastructureCard";
import KnowledgeSearch from "@/components/platform/KnowledgeSearch";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import SourceBadge from "@/components/knowledge/SourceBadge";
import CapabilityCard from "@/components/knowledge/CapabilityStatus";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";
import { featuredByType, typeCounts, hrefFor, URL_BY_TYPE } from "@/lib/knowledge";

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
    status: "NOT_AVAILABLE_YET",
    items: ["AI District Advisor", "AI Manufacturing Advisor", "AI Readiness Advisor", "AI Scale Advisor"],
  },
];

//: The types the homepage leads with, in package order. One representative each,
//: highest confidence first — see lib/knowledge.js featuredByType().
const FEATURED_TYPES = [
  "District",
  "Industry",
  "BusinessOpportunity",
  "Skill",
  "GovernmentScheme",
  "Crop",
];

const TYPE_LABEL = {
  District: "District",
  Industry: "Industry",
  BusinessOpportunity: "Business opportunity",
  Skill: "Skill",
  GovernmentScheme: "Government scheme",
  Crop: "Crop",
};

//: The six roadmap modules, each with the package that does not exist yet. The
//: dependency is the point: "Planned" told the reader nothing they could check.
const FUTURE_MODULES = [
  {
    emoji: "🔬",
    title: "Innovation Infrastructure",
    description: "Research commercialization, technology transfer, innovation labs, patent ecosystem.",
    dependency: "No package covers patents, TRLs or tech transfer. Would need a new research package.",
  },
  {
    emoji: "🎓",
    title: "Research & Technology Infrastructure",
    description: "Universities, research labs, R&D collaboration, technology readiness levels.",
    dependency:
      "We list 66 universities and colleges, but not their research labs or " +
      "capabilities. Browse the institutions we do have.",
  },
  {
    emoji: "🚚",
    title: "Digital Supply Chain Infrastructure",
    description: "Suppliers, warehousing, cold chain, procurement, traceability.",
    dependency:
      "We list 21 raw materials businesses use, but not the firms that supply them " +
      "or where to store goods.",
  },
  {
    emoji: "🌍",
    title: "Global Trade Infrastructure",
    description: "Exports, imports, international buyers, trade missions, export documentation.",
    dependency:
      "We list 29 countries local businesses export to, but not buyers, tariffs or " +
      "the paperwork involved.",
  },
  {
    emoji: "🏦",
    title: "Industrial Finance Infrastructure",
    description: "Banks, NBFCs, government grants, CSR, angel investors, VC.",
    dependency:
      "We list 21 kinds of funder, but not their loan products, interest rates or " +
      "who qualifies.",
  },
  {
    emoji: "♻️",
    title: "Sustainability Infrastructure",
    description: "Circular economy, recycling, renewable energy, carbon footprint, green manufacturing.",
    dependency: "No package covers emissions, recycling or renewable capacity.",
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

export default async function HomeFeatureGrid() {
  // Both return empty when the projection is not deployed — lib/knowledge.js
  // never throws — so the homepage renders either way and says which it is.
  const [featured, counts] = await Promise.all([
    featuredByType(FEATURED_TYPES),
    typeCounts(),
  ]);
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

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

        <section data-testid="home-researched-knowledge">
          <div className="text-center mb-10">
            <span className="chip bg-blue-100 text-blue-700 border border-blue-200 mb-4">RESEARCHED KNOWLEDGE</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-ink">Explore Knowledge</h2>
            <p className="text-muted mt-3 max-w-2xl mx-auto leading-relaxed">
              {total > 0 ? (
                <>
                  <strong className="text-ink tabular-nums">{total}</strong> things to
                  explore — districts, industries, business ideas, skills, government
                  schemes and crops. Each one checked against an official public source.
                </>
              ) : (
                <>
                  Districts, industries, business ideas, skills, government schemes and
                  crops across Telangana and Andhra Pradesh — each one checked against an
                  official public source.
                </>
              )}
            </p>
          </div>

          {featured.length > 0 ? (
            <>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-6">
                {featured.map((entity) => (
                  <Link
                    key={entity.global_entity_id}
                    href={hrefFor(entity)}
                    data-testid="home-featured-entity"
                    className="card-base p-5 hover:border-amber-300 hover:shadow-md hover:-translate-y-1 transition-all group flex flex-col"
                  >
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <span className="chip bg-stone-50 text-stone-500 border border-stone-100">
                        {TYPE_LABEL[entity.entity_type] || entity.entity_type}
                      </span>
                      <ConfidenceBadge confidence={entity.confidence_score} />
                    </div>
                    <h3 className="font-display font-bold text-lg text-ink group-hover:text-amber-700 transition-colors leading-snug">
                      {entity.canonical_name}
                    </h3>
                    <p className="text-xs text-teal-700 font-display font-bold mt-1 tabular-nums">
                      {counts[entity.entity_type] || 0} more like this
                    </p>
                    <div className="mt-auto pt-3 flex items-center justify-between gap-2">
                      <SourceBadge sourcePackage={entity.source_package} />
                      <span className="text-[13px] font-display font-bold text-amber-700">Open →</span>
                    </div>
                  </Link>
                ))}
              </div>
              <div className="flex flex-wrap justify-center gap-2 mb-6">
                {FEATURED_TYPES.filter((t) => (counts[t] || 0) > 0).map((t) => (
                  <Link
                    key={t}
                    href={`/knowledge?type=${URL_BY_TYPE[t]}`}
                    data-testid="home-browse-type"
                    className="btn-secondary text-sm"
                  >
                    All {TYPE_LABEL[t].toLowerCase()}s ({counts[t]}) →
                  </Link>
                ))}
                <Link href="/knowledge" className="btn-primary text-sm">Knowledge Explorer →</Link>
              </div>
            </>
          ) : (
            <div className="mb-6">
              <KnowledgeEmptyState reason="NOT_DEPLOYED" entityLabel="knowledge" />
            </div>
          )}

          <KnowledgeSearch />
        </section>

        <section data-testid="home-future-modules">
          <div className="text-center mb-10">
            <span className="chip bg-violet-100 text-violet-700 border border-violet-200 mb-4">NOT AVAILABLE YET</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-ink">Future Infrastructure Roadmap</h2>
            <p className="text-muted mt-3 max-w-2xl mx-auto leading-relaxed">
              We have not built these yet. Each one says what we would need to gather
              first, and what we already have.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FUTURE_MODULES.map((module) => (
              <CapabilityCard
                key={module.title}
                testId="future-module"
                emoji={module.emoji}
                title={module.title}
                description={module.description}
                status="NO_DATA_SOURCE"
                dependency={module.dependency}
              />
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
