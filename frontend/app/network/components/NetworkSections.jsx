// Collaboration module — Platform v3.0, Step 4.
//
// Two cards here were never "Coming Soon" in reality. The collaborator
// marketplace is a live Supabase feature with real users, and Package002 holds
// 66 researched institutions. Both were sitting behind a placeholder chip.
//
// Mentors, investors and communities stay unavailable, and stay on the page. The
// brief names mentors explicitly as something to relabel rather than remove, and
// no package holds an investor or a community either.
import ModuleDashboard from "@/components/platform/ModuleDashboard";
import { typeCounts } from "@/lib/knowledge";

export default async function NetworkSections() {
  const counts = await typeCounts();
  const institutions = counts.Institution || 0;

  const cards = [
    {
      emoji: "🤝",
      title: "Co-founders",
      description:
        "The collaborator marketplace: real people, real profiles, filtered by district and sector.",
      status: "LIVE",
      href: "/collaborators",
    },
    {
      emoji: "🏫",
      title: "Institutions",
      description:
        "Universities, colleges and training institutions across both states, with the district each one is in.",
      ...(institutions > 0
        ? { status: "LIVE", href: "/knowledge?type=institution", count: institutions }
        : {
            status: "NOT_AVAILABLE_YET",
            dependency:
              "We have researched 66 institutions — this section is still being connected.",
          }),
    },
    {
      emoji: "🧑‍🏫",
      title: "Experts & mentors",
      description: "Domain, finance, operations, technology and compliance guidance.",
      status: "NO_DATA_SOURCE",
      dependency:
        "No package holds mentors or experts. The collaborator marketplace has real " +
        "people but does not model expertise or seniority.",
    },
    {
      emoji: "💼",
      title: "Investors",
      description: "Capital discovery for qualified businesses and founders.",
      status: "NO_DATA_SOURCE",
      dependency:
        "We list 21 kinds of funder — banks, NBFCs, angel networks — but not " +
        "individual investors or how much they invest. Browse the funder types below.",
    },
  ];

  return (
    <ModuleDashboard
      primaryHref="/collaborators"
      primaryLabel="Open Collaborators"
      dependency={
        "Communities, events and a startup workspace are not built. The parts of the " +
        "network that do work — the collaborator marketplace and 66 institutions — " +
        "are open above."
      }
      roadmap={[
        "Keep existing collaborator marketplace stable and accessible under the broader network layer.",
        "Add future network roles for experts, mentors, investors, institutions, and communities.",
        "Connect people and capital to districts, skills, opportunities, manufacturing, and scaling resources.",
      ]}
      capabilities={[
        { label: "Collaborator marketplace", status: "LIVE", href: "/collaborators" },
        { label: "Institutions", status: institutions ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=institution", count: institutions },
        { label: "Financial institutions", status: counts.FinancialInstitution ? "LIVE" : "NOT_AVAILABLE_YET", href: "/knowledge?type=bank", count: counts.FinancialInstitution },
        { label: "Experts", dependency: "No expertise or seniority model exists." },
        { label: "Mentors", dependency: "No package holds mentors." },
        { label: "Investors", dependency: "No individual investor, ticket size or mandate data." },
        { label: "Communities", dependency: "No package holds communities or groups." },
        { label: "Events", dependency: "No package holds events." },
      ]}
      cards={cards}
    />
  );
}
