import { notFound } from "next/navigation";
import ModuleShell from "@/components/platform/ModuleShell";
import DistrictModuleCards from "../components/DistrictModuleCards";
import { DISTRICTS } from "@/lib/districts-data";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import staticDistricts from "@/data/districts.json";

export function generateStaticParams() {
  const slugs = new Set([...DISTRICTS.map((district) => district.slug), ...staticDistricts.map((district) => district.slug)]);
  return Array.from(slugs).map((slug) => ({ slug }));
}

export function generateMetadata({ params }) {
  const district = DISTRICTS.find((item) => item.slug === params.slug);
  const districtKnowledge = staticDistricts.find((item) => item.slug === params.slug);
  if (!district && !districtKnowledge) return {};
  const name = districtKnowledge?.name || district.name;
  return buildBaseMetadata({
    title: `${name} District Intelligence | ValueWeave`,
    description: districtKnowledge?.summary || `Planned district intelligence workspace for ${name}: overview, industries, resources, infrastructure, skills, manufacturing opportunities, and schemes.`,
    alternates: { canonical: `${BASE_URL}/districts/${params.slug}` },
  });
}

export default function DistrictDetailPage({ params }) {
  const district = DISTRICTS.find((item) => item.slug === params.slug);
  const districtKnowledge = staticDistricts.find((item) => item.slug === params.slug);
  if (!district && !districtKnowledge) notFound();

  const name = districtKnowledge?.name || district.name;
  return (
    <ModuleShell
      badge="DISTRICT INTELLIGENCE"
      title={`${name} District Intelligence`}
      description={districtKnowledge?.summary || district.profileSummary || "A modular district workspace for future local economic intelligence."}
    >
      <DistrictModuleCards districtName={name} districtKnowledge={districtKnowledge} />
    </ModuleShell>
  );
}
