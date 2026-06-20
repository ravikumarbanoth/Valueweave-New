import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";

export const revalidate = 300;
export const metadata = { title: "Entrepreneurship Roadmaps | ValueWeave", description: "Step-by-step entrepreneurship roadmaps connected to skills, resources, schemes, and opportunities." };

export default async function RoadmapsPage() {
  const items = await getKgEntities("roadmaps");
  return <><AppNavbar /><PublicEntityList title="Entrepreneurship Roadmaps" eyebrow="ROADMAPS" description="Explore step-by-step paths for starting practical businesses. Roadmaps are published gradually from the admin dashboard." items={items} basePath="/roadmaps" titleField="title" emptyText="Roadmaps will appear here after admins publish them from the Roadmaps CMS." /></>;
}
