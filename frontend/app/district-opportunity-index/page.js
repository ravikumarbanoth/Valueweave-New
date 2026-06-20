import AppNavbar from "@/components/AppNavbar";
import { createClient } from "@/lib/supabase-server";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const dynamic = "force-dynamic";
export const metadata = buildBaseMetadata({
  title: "District Opportunity Index | ValueWeave",
  description: "Dynamic district scoring across opportunity density, skill availability, demand, industry strength, research coverage, and collaborator availability.",
  alternates: { canonical: `${BASE_URL}/district-opportunity-index` },
});

async function fetchIndex() {
  try {
    const sb = createClient();
    const [{ data: districts }, { data: opportunities }, { data: skills }, { data: relationships }, { data: collaborators }] = await Promise.all([
      sb.from("kg_district_profiles").select("id,name,slug,state,logistics_score,education_score,healthcare_score,industrial_score,tourism_score,status").eq("status", "published").limit(500),
      sb.from("opportunities").select("id,district,category,status").eq("status", "open").limit(1000),
      sb.from("kg_skills").select("id,status").eq("status", "published").limit(1000),
      sb.from("kg_relationships").select("source_type,target_type,target_external_id,relationship_type").limit(2000),
      sb.from("collaborator_profiles").select("district,open_to_collaborate").eq("open_to_collaborate", true).limit(1000),
    ]);

    return (districts || []).map((district) => {
      const oppCount = (opportunities || []).filter((o) => (o.district || "").toLowerCase() === district.name.toLowerCase()).length;
      const collaboratorCount = (collaborators || []).filter((c) => (c.district || "").toLowerCase() === district.name.toLowerCase()).length;
      const districtLinks = (relationships || []).filter((r) => r.target_external_id === district.slug || r.target_external_id === district.name);
      const opportunityDensity = Math.min(100, oppCount * 10);
      const skillAvailability = Math.min(100, (skills || []).length * 4 + districtLinks.filter((r) => r.target_type === "skill").length * 5);
      const industryStrength = Math.round(((district.logistics_score || 0) + (district.education_score || 0) + (district.healthcare_score || 0) + (district.industrial_score || 0) + (district.tourism_score || 0)) / 5);
      const researchCoverage = Math.min(100, districtLinks.filter((r) => r.target_type === "research_article" || r.source_type === "research_article").length * 20);
      const collaboratorAvailability = Math.min(100, collaboratorCount * 10);
      const demandScore = Math.round((opportunityDensity + industryStrength + collaboratorAvailability) / 3);
      const total = Math.round(opportunityDensity * 0.25 + skillAvailability * 0.15 + demandScore * 0.2 + industryStrength * 0.2 + researchCoverage * 0.1 + collaboratorAvailability * 0.1);
      return { ...district, opportunityDensity, skillAvailability, demandScore, industryStrength, researchCoverage, collaboratorAvailability, total };
    }).sort((a, b) => b.total - a.total);
  } catch {
    return [];
  }
}

function ScoreBar({ label, value }) {
  return <div><div className="flex justify-between text-xs mb-1"><span className="text-stone-500">{label}</span><span className="font-bold text-ink">{value || 0}</span></div><div className="h-2 bg-stone-100 rounded-full overflow-hidden"><div className="h-full bg-amber-500" style={{ width: `${Math.max(0, Math.min(100, value || 0))}%` }} /></div></div>;
}

export default async function DistrictOpportunityIndexPage() {
  const rows = await fetchIndex();
  return (
    <div className="min-h-screen bg-cream font-body pb-16">
      <AppNavbar />
      <section className="bg-ink text-white px-4 sm:px-6 py-14"><div className="max-w-5xl mx-auto"><span className="chip bg-teal-500/20 text-teal-300 border border-teal-500/30 mb-4">DISTRICT OPPORTUNITY INDEX</span><h1 className="font-display font-extrabold tracking-tight text-3xl sm:text-5xl mb-4">District Opportunity Index</h1><p className="text-white/65 max-w-2xl">Dynamic scoring based on opportunity density, skill availability, demand, industry strength, research coverage, and collaborator availability.</p></div></section>
      <section className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        {rows.length === 0 ? <div className="card-base p-10 text-center"><h2 className="font-display font-bold text-xl text-ink mb-2">No published district CMS entries yet</h2><p className="text-muted text-sm">Publish districts from /admin/districts-cms to generate the index.</p></div> : <div className="space-y-4">{rows.map((row) => <div key={row.id} className="card-base p-5"><div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4"><div><h2 className="font-display font-bold text-xl text-ink">{row.name}</h2><p className="text-sm text-muted">{row.state}</p></div><div className="w-20 h-20 rounded-full bg-amber-50 border-4 border-amber-200 flex items-center justify-center"><span className="font-display font-extrabold text-2xl text-amber-700">{row.total}</span></div></div><div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3"><ScoreBar label="Opportunity Density" value={row.opportunityDensity} /><ScoreBar label="Skill Availability" value={row.skillAvailability} /><ScoreBar label="Demand Score" value={row.demandScore} /><ScoreBar label="Industry Strength" value={row.industryStrength} /><ScoreBar label="Research Coverage" value={row.researchCoverage} /><ScoreBar label="Collaborator Availability" value={row.collaboratorAvailability} /></div></div>)}</div>}
      </section>
    </div>
  );
}
