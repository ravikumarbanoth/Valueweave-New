import AdminShell from "@/components/admin/AdminShell";
import KnowledgeEntityManager from "@/components/admin/KnowledgeEntityManager";

export const dynamic = "force-dynamic";
export const metadata = { title: "Skills CMS | ValueWeave Admin", robots: { index: false, follow: false } };

export default function SkillsAdminPage() {
  return (
    <AdminShell>
      <KnowledgeEntityManager
        table="kg_skills"
        title="Skill Intelligence CMS"
        description="Create Bharat-first skill profiles and connect them later to districts, opportunities, roadmaps, schemes, and research through the knowledge graph."
        fields={[
          { name: "category", label: "Category", type: "text" },
          { name: "description", label: "Description", type: "textarea" },
          { name: "required_training", label: "Required Training", type: "textarea" },
          { name: "tools_needed", label: "Tools Needed", type: "array", help: "Comma-separated" },
          { name: "income_range", label: "Income Range", type: "text" },
          { name: "future_demand", label: "Future Demand", type: "text" },
          { name: "difficulty_level", label: "Difficulty Level", type: "text" },
          { name: "investment_needed", label: "Investment Needed", type: "text" },
        ]}
      />
    </AdminShell>
  );
}
