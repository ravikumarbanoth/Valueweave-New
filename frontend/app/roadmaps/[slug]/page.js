import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { getKgEntityBySlug, kgStructuredData } from "@/lib/knowledge-graph";

export const revalidate = 300;

export async function generateMetadata({ params }) {
  const roadmap = await getKgEntityBySlug("roadmaps", params.slug);
  if (!roadmap) return {};
  return { title: roadmap.meta_title || `${roadmap.title} Roadmap | ValueWeave`, description: roadmap.meta_description || roadmap.summary || roadmap.description };
}

export default async function RoadmapDetailPage({ params }) {
  const roadmap = await getKgEntityBySlug("roadmaps", params.slug);
  if (!roadmap) notFound();
  return <><AppNavbar /><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("roadmaps", roadmap)) }} /><PublicEntityDetail entity={roadmap} typeLabel="Roadmap" backHref="/roadmaps" backLabel="Back to roadmaps" titleField="title" fields={[{ key: "description", label: "Description" }, { key: "estimated_cost", label: "Estimated Cost" }]} /></>;
}
