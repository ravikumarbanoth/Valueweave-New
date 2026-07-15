import InfrastructureCard from "@/components/platform/InfrastructureCard";

const SECTIONS = [
  {
    href: "/collaborators",
    emoji: "🤝",
    title: "Co-founders",
    description: "Use the existing collaborator marketplace to find people ready to build with you.",
    accent: "teal",
    items: ["Existing", "Profiles", "Matching"],
  },
  {
    href: "/network",
    emoji: "🧑‍🏫",
    title: "Experts",
    description: "Future expert directory for domain, finance, operations, and technical guidance.",
    accent: "blue",
    items: ["Planned"],
  },
  {
    href: "/network",
    emoji: "🌱",
    title: "Mentors",
    description: "Future mentor network for founders, students, and local business owners.",
    accent: "green",
    items: ["Planned"],
  },
  {
    href: "/network",
    emoji: "💼",
    title: "Investors",
    description: "Future capital and investor discovery layer for qualified opportunities.",
    accent: "amber",
    items: ["Planned"],
  },
  {
    href: "/network",
    emoji: "🏫",
    title: "Institutions",
    description: "Future institutional partnerships across colleges, industry bodies, and local agencies.",
    accent: "violet",
    items: ["Planned"],
  },
  {
    href: "/network",
    emoji: "🌐",
    title: "Communities",
    description: "Future community layer for district, sector, and skill-based groups.",
    accent: "rose",
    items: ["Planned"],
  },
];

export default function NetworkSections() {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {SECTIONS.map((section) => <InfrastructureCard key={section.title} {...section} />)}
    </div>
  );
}
