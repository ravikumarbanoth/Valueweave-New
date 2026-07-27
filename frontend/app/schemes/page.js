import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";
import { withGraphFallback } from "@/lib/kg-fallback";
import GraphSourceNote from "@/components/knowledge/GraphSourceNote";

export const revalidate = 300;
export const metadata = { title: "Government Schemes | ValueWeave", description: "Explore government schemes linked to skills, districts, and entrepreneurship opportunities." };

export default async function SchemesPage() {
  const cms = await getKgEntities("schemes");
  // Falls back to the 40 researched schemes in the knowledge graph when the CMS
  // is empty — which it is until an admin publishes. See lib/kg-fallback.js.
  const { items, source } = await withGraphFallback("schemes", cms);
  return (
    <>
      <AppNavbar />
      <GraphSourceNote source={source} kind="schemes" browseHref="/knowledge?type=scheme" />
      <PublicEntityList title="Government Scheme Engine" eyebrow="SCHEMES" description="Find schemes, eligibility, subsidies, loan support, and application links." items={items} basePath={source === "GRAPH" ? "/knowledge/scheme" : "/schemes"} emptyText="Schemes will appear here once the knowledge base is synced or an admin publishes them." />
    </>
  );
}
