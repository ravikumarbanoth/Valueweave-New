import AdminShell from "@/components/admin/AdminShell";
import KnowledgeEntityManager from "@/components/admin/KnowledgeEntityManager";

export const dynamic = "force-dynamic";
export const metadata = { title: "Resources CMS | ValueWeave Admin", robots: { index: false, follow: false } };

export default function ResourcesAdminPage() {
  return (
    <AdminShell>
      <KnowledgeEntityManager
        table="kg_resources"
        title="Resource Directory CMS"
        description="Manage land, machinery, training centers, mentors, suppliers, distributors, investors, warehouses, and other entrepreneurship resources."
        fields={[
          { name: "type", label: "Resource Type", type: "text" },
          { name: "description", label: "Description", type: "textarea" },
          { name: "provider_name", label: "Provider Name", type: "text" },
          { name: "location", label: "Location", type: "text" },
          { name: "contact_url", label: "Contact URL", type: "text" },
          { name: "cost_range", label: "Cost Range", type: "text" },
        ]}
      />
    </AdminShell>
  );
}
