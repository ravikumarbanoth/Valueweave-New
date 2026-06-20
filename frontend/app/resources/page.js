import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";

export const revalidate = 300;
export const metadata = { title: "Resources | ValueWeave", description: "Find entrepreneurship resources including land, machinery, mentors, suppliers, investors, and training centers." };

export default async function ResourcesPage() {
  const items = await getKgEntities("resources");
  return <><AppNavbar /><PublicEntityList title="Resource Directory" eyebrow="RESOURCES" description="Discover useful resources for starting and growing local businesses." items={items} basePath="/resources" emptyText="Resources will appear here after admins publish them from the Resource Directory CMS." /></>;
}
