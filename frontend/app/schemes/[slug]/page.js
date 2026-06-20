import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { getKgEntityBySlug, kgStructuredData } from "@/lib/knowledge-graph";

export const revalidate = 300;

export async function generateMetadata({ params }) {
  const scheme = await getKgEntityBySlug("schemes", params.slug);
  if (!scheme) return {};
  return { title: scheme.meta_title || `${scheme.name} Scheme | ValueWeave`, description: scheme.meta_description || scheme.summary || scheme.eligibility };
}

export default async function SchemeDetailPage({ params }) {
  const scheme = await getKgEntityBySlug("schemes", params.slug);
  if (!scheme) notFound();
  return <><AppNavbar /><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("schemes", scheme)) }} /><PublicEntityDetail entity={scheme} typeLabel="Government Scheme" backHref="/schemes" backLabel="Back to schemes" fields={[{ key: "department", label: "Department" }, { key: "eligibility", label: "Eligibility" }, { key: "subsidy", label: "Subsidy" }, { key: "loan_amount", label: "Loan Amount" }, { key: "target_group", label: "Target Group" }, { key: "application_link", label: "Application Link" }]} /></>;
}
