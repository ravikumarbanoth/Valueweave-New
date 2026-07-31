// District index — Platform v3.0, Step 4.
//
// This page listed 14 districts. The knowledge graph holds 61.
//
// The 14 come from lib/districts-data.js: hand-written editorial profiles with a
// narrative summary, a region and related articles. They are better writing than
// anything the graph produces, and they keep their place at the top of the page.
//
// The other 47 are researched District entities from Package001_Geography, and
// until now the only way to reach them was to guess a URL. They are listed below
// the editorial ones, clearly separated, linking to their knowledge detail page.
//
// Same route, same layout, no second index. Two sources, labelled.
import Link from "next/link";
import ModuleShell from "@/components/platform/ModuleShell";
import { DISTRICTS } from "@/lib/districts-data";
import { getEntitiesByType, hrefFor, slugOf } from "@/lib/knowledge";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import SourceBadge from "@/components/knowledge/SourceBadge";
import KnowledgeEmptyState from "@/components/knowledge/KnowledgeEmptyState";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const revalidate = 300;

export const metadata = buildBaseMetadata({
  title: "District Intelligence | ValueWeave",
  description: "Discover district-level opportunity, industry, resource, infrastructure, skill, manufacturing, and scheme intelligence.",
  alternates: { canonical: `${BASE_URL}/districts` },
});

export default async function DistrictsPage() {
  // Empty when the projection is not deployed. The editorial districts below do
  // not depend on it, so the page never loses content it already had.
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

  return (
    <ModuleShell
      badge="DISTRICT INTELLIGENCE"
      title="Discover Where Opportunities Exist"
      description="A canonical district intelligence layer for local opportunity discovery, industry context, resources, infrastructure, skills, manufacturing, and schemes."
    >
      <div className="space-y-10">
        {entities.length > 0 && (
          <p className="text-sm text-muted" data-testid="districts-coverage">
            <strong className="text-ink tabular-nums">{entities.length}</strong> districts
            researched in Package001_Geography.{" "}
            <strong className="text-ink tabular-nums">{DISTRICTS.length}</strong> have a
            written profile; the rest have researched data and no narrative yet.
          </p>
        )}

        {groups.map(({ state, districts }) => (
          <section key={state} data-testid="district-editorial-group">
            <div className="flex items-center justify-between gap-3 mb-5">
              <h2 className="font-display font-extrabold text-2xl text-ink">{state}</h2>
              <span className="text-sm text-muted">{districts.length} written profiles</span>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {districts.map((district) => (
                <Link key={district.slug} href={`/districts/${district.slug}`} data-testid="district-editorial-card" className="card-base p-5 hover:border-teal-300 hover:shadow-md hover:-translate-y-1 transition-all group">
                  <h3 className="font-display font-bold text-lg text-ink group-hover:text-teal-700 transition-colors">{district.name}</h3>
                  <p className="text-xs text-stone-400 mt-1">{district.region}</p>
                  <p className="text-sm text-muted line-clamp-2 mt-3 leading-relaxed">{district.profileSummary}</p>
                  <div className="mt-4 text-amber-700 text-sm font-display font-bold">Open district module →</div>
                </Link>
              ))}
            </div>
          </section>
        ))}

        <section data-testid="districts-researched">
          <div className="flex items-center justify-between gap-3 mb-2">
            <h2 className="font-display font-extrabold text-2xl text-ink">
              Every researched district
            </h2>
            {researchedOnly.length > 0 && (
              <span className="text-sm text-muted tabular-nums">{researchedOnly.length} more</span>
            )}
          </div>
          <p className="text-sm text-muted mb-5 max-w-2xl leading-relaxed">
            Sourced from Package001_Geography with population, area, literacy and
            headquarters, plus everything the knowledge graph links to each one. No
            written profile yet — that is an editorial gap, not a data gap.
          </p>

          {entities.length === 0 ? (
            <KnowledgeEmptyState reason="NOT_DEPLOYED" entityLabel="districts" />
          ) : researchedOnly.length === 0 ? (
            <KnowledgeEmptyState
              reason="NO_MATCH"
              entityLabel="districts"
              note="Every researched district already has a written profile above."
            />
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {researchedOnly.map((entity) => (
                <Link
                  key={entity.global_entity_id}
                  href={hrefFor(entity)}
                  data-testid="district-researched-card"
                  className="card-base p-4 hover:border-teal-300 hover:shadow-md transition-all group flex flex-col gap-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-display font-bold text-[15px] text-ink group-hover:text-teal-700 transition-colors leading-snug">
                      {entity.canonical_name}
                    </h3>
                    <ConfidenceBadge confidence={entity.confidence_score} />
                  </div>
                  <SourceBadge sourcePackage={entity.source_package} className="w-fit" />
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </ModuleShell>
  );
}
