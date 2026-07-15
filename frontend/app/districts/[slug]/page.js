import { notFound } from "next/navigation";
import ModuleShell from "@/components/platform/ModuleShell";
import DistrictModuleCards from "../components/DistrictModuleCards";
import { DISTRICTS } from "@/lib/districts-data";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export function generateStaticParams() {
  return DISTRICTS.map((district) => ({ slug: district.slug }));
}

export function generateMetadata({ params }) {
  const district = DISTRICTS.find((item) => item.slug === params.slug);
  if (!district) return {};
  return buildBaseMetadata({
    title: `${district.name} District Intelligence | ValueWeave`,
    description: `Planned district intelligence workspace for ${district.name}: overview, industries, resources, infrastructure, skills, manufacturing opportunities, and schemes.`,
    alternates: { canonical: `${BASE_URL}/districts/${district.slug}` },
  });
}

export default function DistrictDetailPage({ params }) {
  const district = DISTRICTS.find((item) => item.slug === params.slug);
  if (!district) notFound();

  return (
    <ModuleShell
      badge="DISTRICT INTELLIGENCE"
      title={`${district.name} District Intelligence`}
      description={district.profileSummary || "A modular district workspace for future local economic intelligence."}
    >
      <DistrictModuleCards districtName={district.name} />
    </ModuleShell>
  );
}
