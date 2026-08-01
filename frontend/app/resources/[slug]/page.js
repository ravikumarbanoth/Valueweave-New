import { notFound, redirect } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { getKgEntityBySlug, kgStructuredData } from "@/lib/knowledge-graph";
import { detailWithGraphFallback, rowHref } from "@/lib/kg-fallback";

export const revalidate = 300;

export async function generateMetadata({ params }) {
  const resource = await getKgEntityBySlug("resources", params.slug);
  if (!resource) return {};
  return { title: resource.meta_title || `${resource.name} Resource | ValueWeave`, description: resource.meta_description || resource.summary || resource.description };
}

// Same pattern as /skills and /schemes: the CMS answers if it has the record,
// otherwise hand off to the researched graph's own detail page rather than 404
// on something the platform demonstrably holds.
//
// The redirect target comes from rowHref, not a hardcoded string, because a
// resource can be a training provider, a bank or an institution and those are
// three different URLs.
export default async function ResourceDetailPage({ params }) {
  const cms = await getKgEntityBySlug("resources", params.slug);
  const { row, source } = await detailWithGraphFallback("resources", params.slug, cms);
  if (!row) notFound();
  if (source === "GRAPH") redirect(rowHref("resources", row));
  const resource = row;
  return <><AppNavbar /><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("resources", resource)) }} /><PublicEntityDetail entity={resource} typeLabel="Resource" backHref="/resources" backLabel="Back to resources" fields={[{ key: "type", label: "Resource Type" }, { key: "provider_name", label: "Provider" }, { key: "location", label: "Location" }, { key: "cost_range", label: "Cost Range" }, { key: "contact_url", label: "Contact URL" }]} /></>;
}
