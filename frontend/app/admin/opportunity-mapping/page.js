import AdminShell from "@/components/admin/AdminShell";
import OpportunityMappingClient from "./OpportunityMappingClient";

export const dynamic = "force-dynamic";
export const metadata = { title: "Opportunity Mapping | ValueWeave Admin", robots: { index: false, follow: false } };

export default function OpportunityMappingPage() {
  return (
    <AdminShell>
      <OpportunityMappingClient />
    </AdminShell>
  );
}
