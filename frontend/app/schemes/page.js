import AppNavbar from "@/components/AppNavbar";
import GraphSourceNote from "@/components/knowledge/GraphSourceNote";
import SchemeSupportDirectory from "@/components/schemes/SchemeSupportDirectory";
import { getKgEntities } from "@/lib/knowledge-graph";
import { withGraphFallback } from "@/lib/kg-fallback";
import {
  getSchemeSupportCategories,
  schemeSupportMetadata,
  schemeSupportResources,
} from "@/lib/scheme-support-resources";

export const revalidate = 300;
export const metadata = {
  title: "Schemes and Support Resources | ValueWeave",
  description: "Explore government schemes, training centres, entrepreneurship support, awareness portals, and grievance resources.",
};

export default async function SchemesPage() {
  const cms = await getKgEntities("schemes");
  const { items, source } = await withGraphFallback("schemes", cms);
  const graphItems = items.map((item) => ({
    ...item,
    href: source === "GRAPH" ? `/knowledge/scheme/${item.slug}` : `/schemes/${item.slug}`,
  }));

  return (
    <>
      <AppNavbar />
      <GraphSourceNote source={source} kind="schemes" browseHref="/knowledge?type=scheme" />
      <SchemeSupportDirectory
        records={schemeSupportResources}
        categories={getSchemeSupportCategories()}
        metadata={schemeSupportMetadata}
        graphItems={graphItems}
      />
    </>
  );
}
