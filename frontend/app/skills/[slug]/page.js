import { notFound } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import PublicEntityDetail from "@/components/kg/PublicEntityDetail";
import { getKgEntityBySlug, kgStructuredData } from "@/lib/knowledge-graph";

export const revalidate = 300;

export async function generateMetadata({ params }) {
  const skill = await getKgEntityBySlug("skills", params.slug);
  if (!skill) return {};
  return { title: skill.meta_title || `${skill.name} Skill | ValueWeave`, description: skill.meta_description || skill.summary || skill.description };
}

export default async function SkillDetailPage({ params }) {
  const skill = await getKgEntityBySlug("skills", params.slug);
  if (!skill) notFound();
  return <><AppNavbar /><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(kgStructuredData("skills", skill)) }} /><PublicEntityDetail entity={skill} typeLabel="Skill" backHref="/skills" backLabel="Back to skills" fields={[{ key: "category", label: "Category" }, { key: "required_training", label: "Required Training" }, { key: "tools_needed", label: "Tools Needed" }, { key: "income_range", label: "Income Range" }, { key: "future_demand", label: "Future Demand" }, { key: "difficulty_level", label: "Difficulty Level" }, { key: "investment_needed", label: "Investment Needed" }]} /></>;
}
