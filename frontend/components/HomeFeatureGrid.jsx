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
    title: "Your district",
    subtitle: "See what is around you.",
    description: "What your district is known for, who employs people there, and which schemes apply.",
    href: "/districts",
    accent: "green",
    buttonLabel: "Explore Districts",
    items: ["District Intelligence", "Opportunity Discovery", "Resources", "Industries", "Government Schemes"],
  },
  {
    emoji: "🛠️",
    title: "What to learn",
    subtitle: "Skills that lead somewhere.",
    description: "Skills worth learning, how long each takes, and where you can go and learn them.",
    href: "/readiness",
    accent: "teal",
    buttonLabel: "Start Learning",
    items: ["Skill Assessment", "Learning Paths", "Training", "Internships", "Apprenticeships", "Mentors"],
  },
  {
    emoji: "🤝",
    title: "People and money",
    subtitle: "You do not have to do it alone.",
    description: "Find people to build with, and see who lends to small businesses like yours.",
    href: "/network",
    accent: "rose",
    buttonLabel: "Build Network",
    items: ["Co-founders", "Experts", "Investors", "Institutions", "Communities"],
  },
  {
    emoji: "🏭",
    title: "Making things",
    subtitle: "From an idea to a working unit.",
    description: "The machinery, raw materials and licences behind the businesses people actually start.",
    href: "/manufacturing",
    accent: "amber",
    buttonLabel: "Explore Manufacturing",
    items: ["Product Discovery", "Manufacturing Guides", "Factory Planning", "Machinery", "Production"],
  },
  {
    emoji: "📈",
    title: "Growing a business",
    subtitle: "Once it is working.",
    description: "Where to sell, where local businesses export to, and who funds the next step.",
    href: "/scale",
    accent: "blue",
    buttonLabel: "Scale Business",
    items: ["Automation", "Robotics", "Export", "Quality", "Logistics"],
  },
  {
    emoji: "✨",
    title: "How we choose what to show you",
    subtitle: "No mystery, no black box.",
    description: "We do not have an AI advisor yet. Here is what suggests things to you today, and why we show our reasoning.",
    href: "/ai",
    accent: "violet",
    buttonLabel: "See how it works",
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
    title: "Patents and innovation labs",
    description: "How research turns into a business you could run.",
    dependency: "Patents, innovation labs and how research turns into a business are being researched now.",
  },
  {
    emoji: "🎓",
    title: "University research",
    description: "What the labs near you are working on, and how to get involved.",
    dependency:
      "We list 66 universities and colleges, but not their research labs or " +
      "capabilities. Browse the institutions we do have.",
  },
  {
    emoji: "🚚",
    title: "Suppliers and storage",
    description: "Who supplies what you need, and where to keep goods before they sell.",
    dependency:
      "We list 21 raw materials businesses use, but not the firms that supply them " +
      "or where to store goods.",
  },
  {
    emoji: "🌍",
    title: "Selling abroad",
    description: "Buyers in other countries, and the paperwork it takes to reach them.",
    dependency:
      "We list 29 countries local businesses export to, but not buyers, tariffs or " +
      "the paperwork involved.",
  },
  {
    emoji: "🏦",
    title: "Loans and investors",
    description: "Who lends to a business like yours, on what terms, and who qualifies.",
    dependency:
      "We list 21 kinds of funder, but not their loan products, interest rates or " +
      "who qualifies.",
  },
  {
    emoji: "♻️",
    title: "Green manufacturing",
    description: "Recycling, solar and cutting waste — and what each one saves you.",
    dependency: "Emissions, recycling and renewable energy capacity are being researched now.",
  },
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
            <span className="chip bg-teal-100 text-teal-600 mb-4">EXPLORE</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
              What can you explore here?
            </h2>
            <p className="mt-4 text-muted max-w-3xl mx-auto text-base sm:text-lg leading-relaxed">
              Six things people come here for. Start with whichever one matches where you are today.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((feature) => <InfrastructureCard key={feature.href} {...feature} />)}
          </div>
        </div>

        {/* PX Phase 7: a ten-stage "Entrepreneur Journey" strip stood here —
            Idea → Discover Opportunity → Develop Skills → … → Become Mentor,
            inside a `min-w-[1120px]` horizontal scroller. On a 390px phone that
            is three visible stages and a sideways drag to see the rest.

            It was also the second journey on this page: HomeSuccessJourney says
            the same thing below, in five steps, with real time horizons and
            without the horizontal scroll. Two paths on one page is not twice
            the guidance, it is a question about which one to follow. Every one
            of the ten destinations is reachable from the six cards above. */}

        <section data-testid="home-researched-knowledge">
          <div className="text-center mb-10">
            <span className="chip bg-blue-100 text-blue-700 border border-blue-200 mb-4">LOOK IT UP</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-ink">Search what we have researched</h2>
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
            <span className="chip bg-violet-100 text-violet-700 border border-violet-200 mb-4">COMING NEXT</span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-ink">What we are building next</h2>
            <p className="text-muted mt-3 max-w-2xl mx-auto leading-relaxed">
              Six areas our research is moving into. Each card says what is already
              here and what is being gathered now.
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
