import ModuleDashboard from "@/components/platform/ModuleDashboard";

function KnowledgePanel({ title, value }) {
  if (!value) return null;
  return (
    <div className="card-base p-5 min-h-[165px]">
      <h3 className="font-display font-bold text-base text-ink mb-3">{title}</h3>
      {Array.isArray(value) ? (
        <div className="flex flex-wrap gap-2">
          {value.map((item) => <span key={item} className="chip bg-stone-50 text-stone-600 border border-stone-100">{item}</span>)}
        </div>
      ) : (
        <p className="text-sm text-muted leading-relaxed">{value}</p>
      )}
    </div>
  );
}

export default function DistrictModuleCards({ districtName = "District", districtKnowledge = null }) {
  if (districtKnowledge) {
    return (
      <div className="space-y-8">
        <section className="card-base p-6">
          <span className="chip bg-emerald-50 text-emerald-700 border border-emerald-100 mb-3">STATIC KNOWLEDGE PREVIEW</span>
          <h2 className="font-display font-extrabold text-2xl text-ink mb-3">{districtKnowledge.name} Economic Profile</h2>
          <p className="text-muted leading-relaxed">{districtKnowledge.overview}</p>
        </section>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <KnowledgePanel title="Major Industries" value={districtKnowledge.majorIndustries} />
          <KnowledgePanel title="Resources" value={districtKnowledge.resources} />
          <KnowledgePanel title="Industrial Parks" value={districtKnowledge.industrialParks} />
          <KnowledgePanel title="Educational Institutions" value={districtKnowledge.educationalInstitutions} />
          <KnowledgePanel title="MSMEs" value={districtKnowledge.msmes} />
          <KnowledgePanel title="Manufacturing Opportunities" value={districtKnowledge.manufacturingOpportunities} />
          <KnowledgePanel title="Infrastructure" value={districtKnowledge.infrastructure} />
          <KnowledgePanel title="Government Schemes" value={districtKnowledge.governmentSchemes} />
          <KnowledgePanel title="Future Potential" value={districtKnowledge.futurePotential} />
        </div>
      </div>
    );
  }

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
