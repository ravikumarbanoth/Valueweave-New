import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { getKgEntityBySlug, kgStructuredData } from "@/lib/knowledge-graph";

export const revalidate = 300;

export async function generateMetadata({ params }) {
  const resource = await getKgEntityBySlug("resources", params.slug);
  if (!resource) return {};
  return { title: resource.meta_title || `${resource.name} Resource | ValueWeave`, description: resource.meta_description || resource.summary || resource.description };
}

export default async function ResourceDetailPage({ params }) {
  const resource = await getKgEntityBySlug("resources", params.slug);
  if (!resource) notFound();
  return <><AppNavbar /><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("resources", resource)) }} /><PublicEntityDetail entity={resource} typeLabel="Resource" backHref="/resources" backLabel="Back to resources" fields={[{ key: "type", label: "Resource Type" }, { key: "provider_name", label: "Provider" }, { key: "location", label: "Location" }, { key: "cost_range", label: "Cost Range" }, { key: "contact_url", label: "Contact URL" }]} /></>;
}
