// /opportunities/[id] serves two purposes (Next.js forbids a sibling
// [state] segment alongside [id], so state landing pages share this
// dynamic segment):
//   /opportunities/<uuid>      → opportunity detail (existing client flow)
//   /opportunities/telangana   → state opportunity index (SEO)
//   /opportunities/ap          → Andhra Pradesh index (SEO alias)

import Link from "next/link";
import { STATE_SLUGS, districtsForState, getOpportunityCountsByDistrict } from "@/lib/collab";
import { buildBaseMetadata, breadcrumbJsonLd, pageSummaryJsonLd, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import SnapshotPanel from "@/components/geo/SnapshotPanel";
import OpportunityDetailClient from "./OpportunityDetailClient";

export const revalidate = 300;

export async function generateStaticParams() {
  return Object.keys(STATE_SLUGS).map((id) => ({ id }));
}

export async function generateMetadata({ params }) {
  const stateName = STATE_SLUGS[params.id];
  if (!stateName) return {};
  return buildBaseMetadata({
    title: `Startup Opportunities in ${stateName} — District-wise | ValueWeave`,
    description: `Browse open startup and collaboration opportunities across ${stateName} districts — healthcare, education, agriculture, technology, and manufacturing.`,
    alternates: { canonical: `${BASE_URL}/opportunities/${params.id}` },
  });
}

export default async function OpportunityIdOrStatePage({ params }) {
  const stateName = STATE_SLUGS[params.id];
  if (!stateName) return <OpportunityDetailClient />;

  const districts = districtsForState(stateName);
  const counts = await getOpportunityCountsByDistrict(stateName);
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Opportunities", url: `${BASE_URL}/explore` },
    { name: stateName, url: `${BASE_URL}/opportunities/${params.id}` },
  ];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify([
            breadcrumbJsonLd(breadcrumbs),
            pageSummaryJsonLd({
              url: `${BASE_URL}/opportunities/${params.id}`,
              title: `Startup Opportunities in ${stateName}`,
              summary: `Browse open startup and collaboration opportunities across ${stateName} districts.`,
              about: stateName,
              keywords: [stateName, "opportunities", "collaboration", "startup", "district business"],
            }),
          ]),
        }}
      />
      <main className="pb-16">
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-14">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-teal-500/20 text-teal-300 border border-teal-500/30 mb-4">OPPORTUNITY MARKETPLACE</span>
            <h1 data-testid="state-opps-title" className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
              Startup Opportunities<br className="hidden md:block" /> in {stateName}
            </h1>
            <p className="text-white/60 text-base sm:text-lg max-w-2xl mx-auto">
              {total > 0 ? `${total}+ open opportunities` : "Curated opportunities"} across {districts.length} districts —
              find what to build and who to build it with.
            </p>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
          <SnapshotPanel
            title="Opportunity Snapshot"
            items={{
              "Key Takeaways": `${stateName} has ${districts.length} district opportunity pages and ${total || "curated"} open opportunity signals.`,
              "Who should read this": `Builders, students, MSMEs, and collaborators exploring opportunities in ${stateName}.`,
              "Investment Range": "Varies by posted opportunity and sector",
              "District Relevance": districts.map((d) => d.name),
              "Business Potential": "Use this page to compare district demand and find collaboration-ready business opportunities.",
            }}
          />
        </section>

        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {districts.map((d) => (
              <Link
                key={d.slug}
                href={`/opportunities/${params.id}/${d.slug}`}
                data-testid={`state-district-${d.slug}`}
                className="group card-base p-5 hover:border-amber-400 hover:shadow-md hover:-translate-y-1 transition-all duration-200"
              >
                <h2 className="font-display font-bold text-lg text-ink group-hover:text-amber-700 transition-colors">{d.name}</h2>
                <p className="text-sm text-muted mt-1">
                  {counts[d.name] ? `${counts[d.name]} open opportunities` : "Opportunities available"}
                </p>
                <span className="mt-3 inline-flex items-center gap-1 text-amber-700 text-sm font-display font-bold">
                  View opportunities <span className="group-hover:translate-x-1 transition-transform">→</span>
                </span>
              </Link>
            ))}
          </div>

          <div className="mt-10 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-6 text-center">
            <h3 className="font-display font-bold text-lg mb-1">Not sure which opportunity fits you?</h3>
            <p className="text-sm text-muted mb-4 max-w-md mx-auto">Take the 7-minute Discover Yourself assessment to get matched by archetype, district, and budget.</p>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              <Link href="/discover" className="btn-primary">🧭 Discover Yourself</Link>
              <Link href="/explore" className="btn-secondary">Browse all opportunities</Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
