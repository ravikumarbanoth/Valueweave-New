import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";
import { withGraphFallback } from "@/lib/kg-fallback";
import GraphSourceNote from "@/components/knowledge/GraphSourceNote";

export const revalidate = 300;
export const metadata = { title: "Government Schemes | ValueWeave", description: "Explore government schemes linked to skills, districts, and entrepreneurship opportunities." };

export default async function SchemesPage() {
  const cms = await getKgEntities("schemes");
  // Served by the 40 researched schemes unless an admin has published their own.
  // See lib/kg-fallback.js for which side is canonical and why.
  const { items, source } = await withGraphFallback("schemes", cms);
  return (
    <>
      <AppNavbar />
      <GraphSourceNote source={source} kind="schemes" browseHref="/knowledge?type=scheme" />
      <PublicEntityList title="Government Scheme Engine" eyebrow="SCHEMES" description="Find schemes, eligibility, subsidies, loan support, and application links." items={items} basePath={source === "GRAPH" ? "/knowledge/scheme" : "/schemes"} emptyTitle="We are still gathering this"
        emptyText="We have not finished collecting government schemes. Please check back soon." />
    </>
  );
}
