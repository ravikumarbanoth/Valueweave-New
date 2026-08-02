import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";
import { withGraphFallback, rowHref } from "@/lib/kg-fallback";
import GraphSourceNote from "@/components/knowledge/GraphSourceNote";

export const revalidate = 300;
export const metadata = { title: "Resources | ValueWeave", description: "Find entrepreneurship resources including land, machinery, mentors, suppliers, investors, and training centers." };

// Backed by the researched graph, which holds 112 training providers, banks and
// institutions. Until now this page read only the hand-filled CMS table, which
// nothing populates, so it had never shown a single resource.
//
// Those three entity types live at three different detail URLs, so the link is
// resolved per row through rowHref rather than from one basePath.
export default async function ResourcesPage() {
  const cms = await getKgEntities("resources");
  const { items, source } = await withGraphFallback("resources", cms);
  return (
    <>
      <AppNavbar />
      <GraphSourceNote source={source} kind="resources" browseHref="/knowledge?type=provider" />
      <PublicEntityList
        title="Resource Directory"
        eyebrow="RESOURCES"
        description="Training centres, banks and institutions that can help you start or grow a business."
        items={items}
        basePath="/resources"
        hrefFor={source === "GRAPH" ? (item) => rowHref("resources", item) : undefined}
        emptyTitle="More training centres coming soon"
        emptyText="We add new training centres and support institutions regularly. In the meantime, see what your district is known for."
        emptyHref="/districts" emptyLabel="Explore your district"
      />
    </>
  );
}
