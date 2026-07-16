import ModuleDashboard from "@/components/platform/ModuleDashboard";

const cards = [
  { emoji: "🤝", title: "Co-founders", description: "Existing collaborator marketplace remains available while the network layer expands." },
  { emoji: "🧑‍🏫", title: "Experts", description: "Future directory for domain, finance, operations, technology, and compliance guidance." },
  { emoji: "💼", title: "Investors", description: "Planned capital discovery layer for qualified businesses, founders, and opportunities." },
  { emoji: "🏫", title: "Institutions", description: "Future partnerships with colleges, industry bodies, public agencies, and local anchors." },
];

export default function NetworkSections() {
  return (
    <ModuleDashboard
      primaryHref="/collaborators"
      primaryLabel="Open Collaborators"
      roadmap={[
        "Keep existing collaborator marketplace stable and accessible under the broader network layer.",
        "Add future network roles for experts, mentors, investors, institutions, and communities.",
        "Connect people and capital to districts, skills, opportunities, manufacturing, and scaling resources.",
      ]}
      capabilities={["Co-founders", "Experts", "Mentors", "Investors", "Institutions", "Communities", "Collaborator Marketplace"]}
      cards={cards}
    />
  );
}
