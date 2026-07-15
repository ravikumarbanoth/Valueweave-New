import InfrastructureCard from "@/components/platform/InfrastructureCard";

const FEATURES = [
  {
    emoji: "📍",
    title: "District Intelligence",
    description: "Discover where opportunities exist across districts through local industries, resources, skills, infrastructure, and schemes.",
    href: "/districts",
    accent: "green",
    items: ["Districts", "Industries", "Schemes", "Skills"],
  },
  {
    emoji: "🛠️",
    title: "Industrial Readiness",
    description: "Prepare before starting through skill assessment, learning paths, certifications, internships, mentors, and exposure.",
    href: "/readiness",
    accent: "teal",
    items: ["Skills", "Courses", "Mentors", "Visits"],
  },
  {
    emoji: "🤝",
    title: "Collaboration",
    description: "Find co-founders, experts, mentors, investors, institutions, and communities through the network layer.",
    href: "/network",
    accent: "rose",
    items: ["Co-founders", "Mentors", "Investors"],
  },
  {
    emoji: "🏭",
    title: "Manufacturing",
    description: "Create a future path from product discovery to factory planning, machinery, raw materials, suppliers, and compliance.",
    href: "/manufacturing",
    accent: "amber",
    items: ["Products", "Machinery", "Suppliers"],
  },
  {
    emoji: "📈",
    title: "Industrial Scaling",
    description: "Support growth through automation, robotics, ERP, quality, export, logistics, energy, and industrial resources.",
    href: "/scale",
    accent: "blue",
    items: ["Automation", "Quality", "Export", "Logistics"],
  },
  {
    emoji: "✨",
    title: "AI Intelligence",
    description: "A reserved AI-first layer for future district, manufacturing, readiness, and scale advisory experiences.",
    href: "/ai",
    accent: "violet",
    items: ["Future", "Advisory", "AI-first"],
  },
];

export default function HomeFeatureGrid() {
  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6 bg-warm">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-teal-100 text-teal-600 mb-4">DIGITAL ECONOMIC INFRASTRUCTURE</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            Six Infrastructure Layers
          </h2>
          <p className="mt-4 text-muted max-w-2xl mx-auto text-base sm:text-lg">
            ValueWeave is organized as modular infrastructure for district opportunity discovery, readiness, collaboration, manufacturing, scaling, and future AI guidance.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((feature) => <InfrastructureCard key={feature.href} {...feature} />)}
        </div>
      </div>
    </section>
  );
}
