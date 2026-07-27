import { redirect, notFound } from "next/navigation";
import { getKgEntityBySlug } from "@/lib/knowledge-graph";
import { detailWithGraphFallback } from "@/lib/kg-fallback";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { kgStructuredData } from "@/lib/knowledge-graph";

export const revalidate = 300;

const FIELDS = [
  { key: "category", label: "Category" },
  { key: "required_training", label: "Required Training" },
  { key: "tools_needed", label: "Tools Needed" },
  { key: "income_range", label: "Income Range" },
  { key: "future_demand", label: "Future Demand" },
  { key: "difficulty_level", label: "Difficulty Level" },
  { key: "investment_needed", label: "Investment Needed" },
];

export async function generateMetadata({ params }) {
  const row = await getKgEntityBySlug("skills", params.slug);
  if (!row) return {};
  return { title: row.meta_title || `${row.name} | ValueWeave`, description: row.meta_description || row.summary || "" };
}

// CMS first. When the CMS has no such record — which is the case until an admin
// publishes — hand off to the researched knowledge graph's detail page rather
// than 404ing on a record the platform demonstrably holds. One redirect, no
// duplicated detail view. See lib/kg-fallback.js.
export default async function DetailPage({ params }) {
  const cms = await getKgEntityBySlug("skills", params.slug);
  const { row, source } = await detailWithGraphFallback("skills", params.slug, cms);
  if (!row) notFound();
  if (source === "GRAPH") redirect(`/knowledge/skill/${params.slug}`);

  return (
    <>
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("skills", row)) }} />
      <PublicEntityDetail entity={row} typeLabel="Skill" backHref="/skills" backLabel="Back to skills" fields={FIELDS} />
    </>
  );
}
