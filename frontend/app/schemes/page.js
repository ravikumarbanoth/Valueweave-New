import AppNavbar from "@/components/AppNavbar";
import PublicEntityList from "@/components/kg/PublicEntityList";
import { getKgEntities } from "@/lib/knowledge-graph";

export const revalidate = 300;
export const metadata = { title: "Government Schemes | ValueWeave", description: "Explore government schemes linked to skills, districts, and entrepreneurship opportunities." };

export default async function SchemesPage() {
  const items = await getKgEntities("schemes");
  return <><AppNavbar /><PublicEntityList title="Government Scheme Engine" eyebrow="SCHEMES" description="Find schemes, eligibility, subsidies, loan support, and application links as they are curated by the ValueWeave admin team." items={items} basePath="/schemes" emptyText="Schemes will appear here after admins publish them from the Government Scheme CMS." /></>;
}
