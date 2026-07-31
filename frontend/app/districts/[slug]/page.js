// District detail — Platform v3.0, Step 4.
//
// WHAT THIS PAGE USED TO DO
// -------------------------
// One slug (`medak`) rendered a "STATIC KNOWLEDGE PREVIEW" from data/districts.json.
// The other thirteen rendered a ModuleDashboard of four "Coming Soon" cards
// promising a district overview, industries, resources and schemes — all four of
// which the knowledge graph already held, for 61 districts, with provenance.
//
// The placeholder is gone. The page now resolves the district through the Step 0
// vocabulary crosswalk (100% coverage for the editorial districts, including the
// curated cases: Anantapur → Ananthapuramu, Nellore → Sri Potti Sriramulu Nellore,
// Vijayawada → NTR) and renders DistrictIntelligencePanel — the same component
// `/district/[slug]` uses, not a second one.
//
// The static overview is kept where it exists. It is editorial writing about a
// real place and the graph does not replace it; it sits above the researched
// panel with its own label, the way every other editorial/researched pair on this
// platform is arranged.
import { notFound } from "next/navigation";
import Link from "next/link";
import ModuleShell from "@/components/platform/ModuleShell";
import { DISTRICTS } from "@/lib/districts-data";
import staticDistricts from "@/data/districts.json";
import DistrictIntelligencePanel from "@/components/knowledge/DistrictIntelligencePanel";
import { getDistrictKnowledge, resolveTerms } from "@/lib/knowledge";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";

export const revalidate = 300;

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
    description:
      districtKnowledge?.summary ||
      district?.profileSummary ||
      `Researched industries, businesses, schemes, institutions and agriculture linked to ${name}.`,
    alternates: { canonical: `${BASE_URL}/districts/${params.slug}` },
  });
}

/**
 * The district's researched knowledge, or a named reason there is none.
 *
 * A district that does not resolve in the crosswalk is a different failure from
 * one that resolves to an entity with no edges, and the panel says which.
 */
async function loadDistrictKnowledge(districtName) {
  const { resolved } = await resolveTerms("district", [districtName]);
  const hit = resolved[0];
  if (!hit) {
    return {
      grouped: {},
      status: "NO_DATA_SOURCE",
      note: `"${districtName}" has no entry in the district vocabulary crosswalk, so no researched entity can be linked to it. The crosswalk covers 33 district terms.`,
    };
  }
  return { grouped: await getDistrictKnowledge(hit.global_entity_id), status: null, note: null };
}

export default async function DistrictDetailPage({ params }) {
  const district = DISTRICTS.find((item) => item.slug === params.slug);
  const districtKnowledge = staticDistricts.find((item) => item.slug === params.slug);
  if (!district && !districtKnowledge) notFound();

  const name = districtKnowledge?.name || district.name;
  const knowledge = await loadDistrictKnowledge(name);

  return (
    <ModuleShell
      badge="DISTRICT INTELLIGENCE"
      title={`${name} District Intelligence`}
      description={
        districtKnowledge?.summary ||
        district?.profileSummary ||
        `Everything Packages 001–008 record about ${name}.`
      }
    >
      <div className="space-y-8">
        {districtKnowledge && (
          <section className="card-base p-6" data-testid="district-editorial-overview">
            <span className="chip bg-emerald-50 text-emerald-700 border border-emerald-100 mb-3">
              EDITORIAL PROFILE
            </span>
            <h2 className="font-display font-extrabold text-2xl text-ink mb-3">
              {districtKnowledge.name} Economic Profile
            </h2>
            <p className="text-muted leading-relaxed">{districtKnowledge.overview}</p>
            <p className="text-[11px] text-stone-400 mt-4 leading-relaxed">
              Written by hand, carrying no source or confidence score. The researched
              records below are a different kind of claim and are kept separate.
            </p>
          </section>
        )}

        <DistrictIntelligencePanel
          testId="district-intelligence"
          districtName={name}
          grouped={knowledge.grouped}
          status={knowledge.status}
          note={knowledge.note}
        />

        <div className="flex flex-wrap gap-2" data-testid="district-next-steps">
          {district && (
            <Link href={`/district/${district.slug}`} className="btn-secondary text-sm">
              Full {name} profile and articles →
            </Link>
          )}
          <Link href="/knowledge?type=district" className="btn-secondary text-sm">
            Compare all researched districts →
          </Link>
          <Link href="/districts" className="btn-secondary text-sm">
            All districts →
          </Link>
        </div>
      </div>
    </ModuleShell>
  );
}
