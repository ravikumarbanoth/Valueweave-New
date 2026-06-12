// District opportunity SEO pages: /opportunities/telangana/medak,
// /opportunities/ap/guntur, etc. Server-rendered with ISR; lists live
// open opportunities for the district with internal links into the
// District Intelligence, Idea Library, and Collaborator pages.

import Link from "next/link";
import { notFound } from "next/navigation";
import {
  STATE_SLUGS, MARKETPLACE_DISTRICTS, getMarketplaceDistrict, getOpenOpportunities, MARKETPLACE_SECTORS,
} from "@/lib/collab";
import { getDistrictBySlug } from "@/lib/districts-data";
import { buildBaseMetadata, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import OpportunityCard from "@/components/OpportunityCard";

export const revalidate = 300;

const stateToSlug = (stateName) => (stateName === "Telangana" ? "telangana" : "andhra-pradesh");

export async function generateStaticParams() {
  return MARKETPLACE_DISTRICTS.map((d) => ({ id: stateToSlug(d.state), district: d.slug }));
}

export async function generateMetadata({ params }) {
  const stateName = STATE_SLUGS[params.id];
  const district = getMarketplaceDistrict(params.district);
  if (!stateName || !district || district.state !== stateName) return {};
  return buildBaseMetadata({
    title: `Startup Opportunities in ${district.name} — Collaborate & Build | ValueWeave`,
    description: `Open startup and collaboration opportunities in ${district.name}, ${stateName}: healthcare, education, agriculture, technology, and manufacturing. Find co-founders and partners.`,
    alternates: { canonical: `${BASE_URL}/opportunities/${params.id}/${params.district}` },
  });
}

export default async function DistrictOpportunitiesPage({ params }) {
  const stateName = STATE_SLUGS[params.id];
  const district = getMarketplaceDistrict(params.district);
  if (!stateName || !district || district.state !== stateName) notFound();

  const opportunities = await getOpenOpportunities({ district: district.name, limit: 40 });
  const intel = getDistrictBySlug(district.slug); // rich District Intelligence profile, when available

  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Opportunities", url: `${BASE_URL}/explore` },
    { name: stateName, url: `${BASE_URL}/opportunities/${params.id}` },
    { name: district.name, url: `${BASE_URL}/opportunities/${params.id}/${params.district}` },
  ];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd(breadcrumbs)) }} />
      <main className="pb-16">
        {/* Hero */}
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-12">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto">
            <Link href={`/opportunities/${params.id}`} className="text-white/50 hover:text-white text-sm font-display font-semibold">
              ← All {stateName} districts
            </Link>
            <h1 data-testid="district-opps-title" className="font-display font-extrabold tracking-tight text-3xl md:text-4xl text-white mt-3">
              Startup Opportunities in {district.name}
            </h1>
            <p className="text-white/60 mt-2 max-w-2xl">
              {opportunities.length > 0
                ? `${opportunities.length} open opportunities in ${district.name}, ${stateName} — express interest, find collaborators, and start building.`
                : `Curated opportunities for ${district.name}, ${stateName}.`}
            </p>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
          {opportunities.length === 0 ? (
            <div className="card-base !border-dashed !border-2 p-12 text-center">
              <div className="text-5xl mb-3">🌱</div>
              <h3 className="font-display font-bold text-lg mb-2">Opportunities are being curated for {district.name}</h3>
              <p className="text-muted text-sm mb-4 max-w-sm mx-auto">Browse the full marketplace meanwhile, or post the first opportunity for your district.</p>
              <Link href="/explore" className="btn-primary">Browse all opportunities</Link>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {opportunities.map((opp) => <OpportunityCard key={opp.id} opp={opp} />)}
            </div>
          )}

          {/* Internal links: district intelligence + ideas + collaborators */}
          <div className="mt-12 grid sm:grid-cols-3 gap-4">
            <Link href={intel ? `/district/${district.slug}` : "/district"} className="card-base p-5 hover:border-teal-300 hover:-translate-y-1 transition-all">
              <div className="text-2xl mb-2">📊</div>
              <h3 className="font-display font-bold text-sm mb-1">{district.name} District Intelligence</h3>
              <p className="text-xs text-muted">Industries, schemes, demographics, and emerging sectors.</p>
            </Link>
            <Link href={`/business-ideas/${district.slug}`} className="card-base p-5 hover:border-amber-300 hover:-translate-y-1 transition-all">
              <div className="text-2xl mb-2">💡</div>
              <h3 className="font-display font-bold text-sm mb-1">Business Ideas for {district.name}</h3>
              <p className="text-xs text-muted">Idea Library picks matched to this district.</p>
            </Link>
            <Link href="/collaborators" className="card-base p-5 hover:border-violet-300 hover:-translate-y-1 transition-all">
              <div className="text-2xl mb-2">🤝</div>
              <h3 className="font-display font-bold text-sm mb-1">Find Collaborators</h3>
              <p className="text-xs text-muted">Builders, innovators, and partners open to collaborate.</p>
            </Link>
          </div>

          {/* Sector quick links */}
          <div className="mt-8 flex flex-wrap gap-2 items-center">
            <span className="text-xs font-display font-bold text-muted uppercase tracking-wider mr-1">Collaborators by sector:</span>
            {MARKETPLACE_SECTORS.map((s) => (
              <Link key={s.id} href={`/collaborators/${s.id}`} className="chip bg-stone-100 text-stone-600 hover:bg-stone-200 transition-colors">
                {s.emoji} {s.label}
              </Link>
            ))}
          </div>

          <div className="mt-10 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-6 text-center">
            <h3 className="font-display font-bold text-lg mb-1">Building something in {district.name}?</h3>
            <p className="text-sm text-muted mb-4 max-w-md mx-auto">Post your opportunity and let collaborators in your district find you.</p>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              <Link href="/opportunities/new" className="btn-primary">Post an opportunity →</Link>
              <Link href="/discover" className="btn-secondary">🧭 Take the assessment</Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
