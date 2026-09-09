import { DISTRICTS } from "@/lib/districts-data";
import { getEntitiesByType, slugOf } from "@/lib/knowledge";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import DistrictsPageClient from "@/components/DistrictsPageClient";

export const revalidate = 300;

export const metadata = buildBaseMetadata({
  title: "Districts | ValueWeave",
  description: "Find out what your district is known for — the industries, the businesses people start there, the training available, and the government schemes that apply.",
  alternates: { canonical: `${BASE_URL}/districts` },
});

export default async function DistrictsPage() {
  const entities = await getEntitiesByType("District", { limit: 200 });

  const editorialSlugs = new Set(DISTRICTS.map((d) => d.slug));
  const editorialNames = new Set(DISTRICTS.map((d) => d.name.toLowerCase()));
  const researchedOnly = entities.filter(
    (e) =>
      !editorialSlugs.has(slugOf(e)) &&
      !editorialNames.has(String(e.canonical_name || "").toLowerCase())
  );

  const groups = [
    { state: "Telangana", districts: DISTRICTS.filter((d) => d.state === "Telangana") },
    { state: "Andhra Pradesh", districts: DISTRICTS.filter((d) => d.state === "Andhra Pradesh") },
  ];

  return <DistrictsPageClient entities={entities} researchedOnly={researchedOnly} groups={groups} />;
}
