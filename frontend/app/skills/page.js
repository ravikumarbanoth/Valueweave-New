import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";

export const revalidate = 300;
export const metadata = { title: "Skills | ValueWeave", description: "Explore Bharat-first skills connected to opportunities, districts, schemes, resources, and roadmaps." };

export default async function SkillsPage() {
  const items = await getKgEntities("skills");
  return <><AppNavbar /><PublicEntityList title="Skill Intelligence" eyebrow="SKILLS" description="Explore practical skills and how they connect to local entrepreneurship opportunities." items={items} basePath="/skills" emptyText="Skills will appear here after admins publish them from the Skill Intelligence CMS." /></>;
}
