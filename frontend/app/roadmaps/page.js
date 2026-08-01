import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";

export const revalidate = 300;
export const metadata = { title: "Entrepreneurship Roadmaps | ValueWeave", description: "Step-by-step entrepreneurship roadmaps connected to skills, resources, schemes, and opportunities." };

// The one knowledge section with no researched data behind it.
//
// A roadmap is an ordered sequence of steps with costs attached. The graph has
// no equivalent, and assembling one out of unrelated entities would be
// fabricating a guide nobody wrote — so this page has no fallback and says so.
// See the note on GRAPH_TYPES in lib/kg-fallback.js.
//
// The old copy told a student the page would fill up "after admins publish them
// from the Roadmaps CMS": it names an internal tool they cannot reach and
// implies a wait with no end. It now says what is true and points somewhere
// useful.
export default async function RoadmapsPage() {
  const items = await getKgEntities("roadmaps");
  return (
    <>
      <AppNavbar />
      <PublicEntityList
        title="Entrepreneurship Roadmaps"
        eyebrow="ROADMAPS"
        description="Step-by-step paths for starting a practical business."
        items={items}
        basePath="/roadmaps"
        titleField="title"
        emptyTitle="Not available yet"
        emptyText="We have not written step-by-step roadmaps yet. In the meantime you can explore businesses you could start, the skills they need, and the schemes that may help fund them."
      />
    </>
  );
}
