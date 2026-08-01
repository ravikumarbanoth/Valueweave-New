import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";
import { withGraphFallback } from "@/lib/kg-fallback";
import GraphSourceNote from "@/components/knowledge/GraphSourceNote";

export const revalidate = 300;
export const metadata = { title: "Skills | ValueWeave", description: "Explore Bharat-first skills connected to opportunities, districts, schemes, resources, and roadmaps." };

export default async function SkillsPage() {
  const cms = await getKgEntities("skills");
  const { items, source } = await withGraphFallback("skills", cms);
  return (
    <>
      <AppNavbar />
      <GraphSourceNote source={source} kind="skills" browseHref="/knowledge?type=skill" />
      <PublicEntityList title="Skill Intelligence" eyebrow="SKILLS" description="Explore practical skills and how they connect to local entrepreneurship opportunities." items={items} basePath={source === "GRAPH" ? "/knowledge/skill" : "/skills"} emptyTitle="We are still gathering this"
        emptyText="We have not finished collecting skills for your area. Please check back soon." />
    </>
  );
}
