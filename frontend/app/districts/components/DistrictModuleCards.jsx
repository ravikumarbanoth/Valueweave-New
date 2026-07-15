import ModuleDashboard from "@/components/platform/ModuleDashboard";

export default function DistrictModuleCards({ districtName = "District" }) {
  return (
    <ModuleDashboard
      primaryHref="/districts"
      primaryLabel="Explore Districts"
      roadmap={[
        `Create a structured ${districtName} profile covering industries, resources, infrastructure, skills, and schemes.`,
        "Connect local opportunities to readiness paths, collaborators, manufacturing resources, and capital.",
        "Prepare district intelligence for future search, recommendations, GEO, and AI-readable knowledge graph use.",
      ]}
      capabilities={["District Overview", "Industries", "Resources", "Infrastructure", "Skills", "Manufacturing Opportunities", "Government Schemes"]}
      cards={[
        { emoji: "🗺️", title: "District Overview", description: `Planned overview for ${districtName} economic context, local strengths, and opportunity direction.` },
        { emoji: "🏭", title: "Industries", description: "Future map of active, emerging, and priority industries in this district." },
        { emoji: "🧰", title: "Resources", description: "Future local resources, institutions, suppliers, training, and support systems." },
        { emoji: "🏛️", title: "Government Schemes", description: "Planned scheme discovery connected to district and business-stage relevance." },
      ]}
    />
  );
}
