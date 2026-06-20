import AdminShell from "@/components/admin/AdminShell";
import KnowledgeEntityManager from "@/components/admin/KnowledgeEntityManager";

export const dynamic = "force-dynamic";
export const metadata = { title: "Schemes CMS | ValueWeave Admin", robots: { index: false, follow: false } };

export default function SchemesAdminPage() {
  return (
    <AdminShell>
      <KnowledgeEntityManager
        table="kg_schemes"
        title="Government Scheme Engine"
        description="Manage schemes, eligibility, subsidy and loan information, application links, target groups, and GEO-ready summaries."
        fields={[
          { name: "department", label: "Department", type: "text" },
          { name: "eligibility", label: "Eligibility", type: "textarea" },
          { name: "subsidy", label: "Subsidy", type: "text" },
          { name: "loan_amount", label: "Loan Amount", type: "text" },
          { name: "target_group", label: "Target Group", type: "text" },
          { name: "application_link", label: "Application Link", type: "text" },
        ]}
      />
    </AdminShell>
  );
}
