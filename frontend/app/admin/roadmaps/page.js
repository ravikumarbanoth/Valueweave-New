import AdminShell from "@/components/admin/AdminShell";
import KnowledgeEntityManager from "@/components/admin/KnowledgeEntityManager";

export const dynamic = "force-dynamic";
export const metadata = { title: "Roadmaps CMS | ValueWeave Admin", robots: { index: false, follow: false } };

export default function RoadmapsAdminPage() {
  return (
    <AdminShell>
      <KnowledgeEntityManager
        table="kg_roadmaps"
        title="Entrepreneurship Roadmaps"
        description="Create roadmap shells with costs, summaries, and rich text. Detailed steps are stored in kg_roadmap_steps and can be expanded in the next admin iteration."
        titleField="title"
        fields={[
          { name: "description", label: "Description", type: "textarea" },
          { name: "estimated_cost", label: "Estimated Cost", type: "text" },
        ]}
      />
    </AdminShell>
  );
}
