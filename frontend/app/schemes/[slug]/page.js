import { redirect, notFound } from "next/navigation";
import { getKgEntityBySlug } from "@/lib/knowledge-graph";
import { detailWithGraphFallback } from "@/lib/kg-fallback";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { kgStructuredData } from "@/lib/knowledge-graph";

export const revalidate = 300;

const FIELDS = [
  { key: "department", label: "Department" },
  { key: "eligibility", label: "Eligibility" },
  { key: "subsidy", label: "Subsidy" },
  { key: "loan_amount", label: "Loan Amount" },
  { key: "target_group", label: "Target Group" },
  { key: "application_link", label: "Application Link" },
];

export async function generateMetadata({ params }) {
  const row = await getKgEntityBySlug("schemes", params.slug);
  if (!row) return {};
  return { title: row.meta_title || `${row.name} | ValueWeave`, description: row.meta_description || row.summary || "" };
}

// CMS first. When the CMS has no such record — which is the case until an admin
// publishes — hand off to the researched knowledge graph's detail page rather
// than 404ing on a record the platform demonstrably holds. One redirect, no
// duplicated detail view. See lib/kg-fallback.js.
export default async function DetailPage({ params }) {
  const cms = await getKgEntityBySlug("schemes", params.slug);
  const { row, source } = await detailWithGraphFallback("schemes", params.slug, cms);
  if (!row) notFound();
  if (source === "GRAPH") redirect(`/knowledge/scheme/${params.slug}`);

  return (
    <>
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("schemes", row)) }} />
      <PublicEntityDetail entity={row} typeLabel="Government Scheme" backHref="/schemes" backLabel="Back to schemes" fields={FIELDS} />
    </>
  );
}
