import Link from "next/link";
import ModuleShell from "@/components/platform/ModuleShell";
import { DISTRICTS } from "@/lib/districts-data";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const metadata = buildBaseMetadata({
  title: "District Intelligence | ValueWeave",
  description: "Discover district-level opportunity, industry, resource, infrastructure, skill, manufacturing, and scheme intelligence.",
  alternates: { canonical: `${BASE_URL}/districts` },
});

export default function DistrictsPage() {
  const groups = [
    { state: "Telangana", districts: DISTRICTS.filter((district) => district.state === "Telangana") },
    { state: "Andhra Pradesh", districts: DISTRICTS.filter((district) => district.state === "Andhra Pradesh") },
  ];

  return (
    <ModuleShell
      badge="DISTRICT INTELLIGENCE"
      title="Discover Where Opportunities Exist"
      description="A canonical district intelligence layer for local opportunity discovery, industry context, resources, infrastructure, skills, manufacturing, and schemes."
    >
      <div className="space-y-10">
        {groups.map(({ state, districts }) => (
          <section key={state}>
            <div className="flex items-center justify-between gap-3 mb-5">
              <h2 className="font-display font-extrabold text-2xl text-ink">{state}</h2>
              <span className="text-sm text-muted">{districts.length} districts</span>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {districts.map((district) => (
                <Link key={district.slug} href={`/districts/${district.slug}`} className="card-base p-5 hover:border-teal-300 hover:shadow-md hover:-translate-y-1 transition-all group">
                  <h3 className="font-display font-bold text-lg text-ink group-hover:text-teal-700 transition-colors">{district.name}</h3>
                  <p className="text-xs text-stone-400 mt-1">{district.region}</p>
                  <p className="text-sm text-muted line-clamp-2 mt-3 leading-relaxed">{district.profileSummary}</p>
                  <div className="mt-4 text-amber-700 text-sm font-display font-bold">Open district module →</div>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </ModuleShell>
  );
}
