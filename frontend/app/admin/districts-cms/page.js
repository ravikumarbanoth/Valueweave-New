import AdminShell from "@/components/admin/AdminShell";
import KnowledgeEntityManager from "@/components/admin/KnowledgeEntityManager";

export const dynamic = "force-dynamic";
export const metadata = { title: "District CMS | ValueWeave Admin", robots: { index: false, follow: false } };

export default function DistrictCmsPage() {
  return (
    <AdminShell>
      <KnowledgeEntityManager
        table="kg_district_profiles"
        title="District Intelligence CMS"
        description="Manage district profiles, economic signals, skill gaps, opportunity gaps, rich text, GEO summaries, and publish status. No seed data is required."
        fields={[
          { name: "state", label: "State", type: "text", required: true },
          { name: "population", label: "Population", type: "number" },
          { name: "major_industries", label: "Major Industries", type: "array", help: "Comma-separated" },
          { name: "key_crops", label: "Key Crops", type: "array", help: "Comma-separated" },
          { name: "economic_activities", label: "Economic Activities", type: "array", help: "Comma-separated" },
          { name: "skill_gaps", label: "Skill Gaps", type: "array", help: "Comma-separated" },
          { name: "opportunity_gaps", label: "Opportunity Gaps", type: "array", help: "Comma-separated" },
          { name: "msme_presence", label: "MSME Presence", type: "textarea" },
          { name: "logistics_score", label: "Logistics Score", type: "number" },
          { name: "education_score", label: "Education Score", type: "number" },
          { name: "healthcare_score", label: "Healthcare Score", type: "number" },
          { name: "industrial_score", label: "Industrial Score", type: "number" },
          { name: "tourism_score", label: "Tourism Score", type: "number" },
        ]}
      />
    </AdminShell>
  );
}
