// Sector collaborator SEO pages: /collaborators/healthcare,
// /collaborators/ai-tech, etc.

import Link from "next/link";
import { notFound } from "next/navigation";
import { getCollaborators, getOpenOpportunities, MARKETPLACE_SECTORS } from "@/lib/collab";
import { buildBaseMetadata, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import CollaboratorCard from "@/components/CollaboratorCard";
import OpportunityCard from "@/components/OpportunityCard";

export const revalidate = 300;

export async function generateStaticParams() {
  return MARKETPLACE_SECTORS.map((s) => ({ sector: s.id }));
}

export async function generateMetadata({ params }) {
  const sector = MARKETPLACE_SECTORS.find((s) => s.id === params.sector);
  if (!sector) return {};
  return buildBaseMetadata({
    title: `${sector.label} Collaborators & Co-founders | ValueWeave`,
    description: `Find ${sector.label.toLowerCase()} collaborators, co-founders, and partners across Telangana and Andhra Pradesh — plus open ${sector.label.toLowerCase()} opportunities to join.`,
    alternates: { canonical: `${BASE_URL}/collaborators/${params.sector}` },
  });
}

export default async function SectorCollaboratorsPage({ params }) {
  const sector = MARKETPLACE_SECTORS.find((s) => s.id === params.sector);
  if (!sector) notFound();

  const [collaborators, opportunities] = await Promise.all([
    getCollaborators({ sector: sector.id, limit: 24 }),
    getOpenOpportunities({ category: sector.id, limit: 6 }),
  ]);

  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Collaborators", url: `${BASE_URL}/collaborators` },
    { name: sector.label, url: `${BASE_URL}/collaborators/${params.sector}` },
  ];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd(breadcrumbs)) }} />
      <main className="pb-16">
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-12">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto">
            <Link href="/collaborators" className="text-white/50 hover:text-white text-sm font-display font-semibold">← All collaborators</Link>
            <h1 data-testid="sector-collabs-title" className="font-display font-extrabold tracking-tight text-3xl md:text-4xl text-white mt-3">
              {sector.emoji} {sector.label} Collaborators
            </h1>
            <p className="text-white/60 mt-2 max-w-2xl">
              Co-founders and partners interested in {sector.label.toLowerCase()} ventures across Telangana and Andhra Pradesh.
            </p>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
          {/* Sector nav */}
          <div className="flex flex-wrap gap-2 mb-8">
            <Link href="/collaborators" className="chip bg-stone-100 text-stone-600 hover:bg-stone-200 transition-colors">🌐 All</Link>
            {MARKETPLACE_SECTORS.map((s) => (
              s.id === sector.id
                ? <span key={s.id} className="chip bg-ink text-white">{s.emoji} {s.label}</span>
                : <Link key={s.id} href={`/collaborators/${s.id}`} className="chip bg-stone-100 text-stone-600 hover:bg-stone-200 transition-colors">{s.emoji} {s.label}</Link>
            ))}
          </div>

          {collaborators.length === 0 ? (
            <div className="card-base !border-dashed !border-2 p-12 text-center mb-10">
              <div className="text-5xl mb-3">{sector.emoji}</div>
              <h3 className="font-display font-bold text-lg mb-2">No {sector.label.toLowerCase()} collaborators yet</h3>
              <p className="text-muted text-sm mb-5 max-w-md mx-auto">
                Take the assessment to become the first {sector.label.toLowerCase()} collaborator in your district.
              </p>
              <Link href="/discover" className="btn-primary">🧭 Take the assessment</Link>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
              {collaborators.map((c) => <CollaboratorCard key={c.user_id} collaborator={c} />)}
            </div>
          )}

          {opportunities.length > 0 && (
            <>
              <h2 className="font-display font-extrabold tracking-tight text-xl text-ink mb-4">
                Open {sector.label.toLowerCase()} opportunities
              </h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {opportunities.map((opp) => <OpportunityCard key={opp.id} opp={opp} />)}
              </div>
              <div className="mt-6 text-center">
                <Link href="/explore" className="btn-secondary">Browse all opportunities →</Link>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
