// Collaborator marketplace index — profiles created by the Discover
// Yourself assessment, browsable by sector via /collaborators/[sector].

import Link from "next/link";
import { getCollaborators, MARKETPLACE_SECTORS } from "@/lib/collab";
import { buildBaseMetadata, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";
import CollaboratorCard from "@/components/CollaboratorCard";

export const revalidate = 120;

export const metadata = buildBaseMetadata({
  title: "Find Collaborators & Co-founders — Telangana & Andhra Pradesh | ValueWeave",
  description:
    "Browse builders, innovators, and partners open to collaborate across Telangana and Andhra Pradesh districts — matched by archetype, founder role, sector, and budget.",
  alternates: { canonical: `${BASE_URL}/collaborators` },
});

export default async function CollaboratorsPage() {
  const collaborators = await getCollaborators({ limit: 48 });
  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Collaborators", url: `${BASE_URL}/collaborators` },
  ];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd(breadcrumbs)) }} />
      <main className="pb-16">
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-14">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">COLLABORATOR MARKETPLACE</span>
            <h1 data-testid="collaborators-title" className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
              Find Your Co-Builder
            </h1>
            <p className="text-white/60 text-base sm:text-lg max-w-xl mx-auto">
              Builders, innovators, and operators across Telangana and Andhra Pradesh — profiled by the Discover Yourself assessment.
            </p>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
          {/* Sector filter links (SEO pages) */}
          <div className="flex flex-wrap gap-2 mb-8">
            <span className="chip bg-ink text-white">🌐 All sectors</span>
            {MARKETPLACE_SECTORS.map((s) => (
              <Link key={s.id} href={`/collaborators/${s.id}`} className="chip bg-stone-100 text-stone-600 hover:bg-stone-200 transition-colors">
                {s.emoji} {s.label}
              </Link>
            ))}
          </div>

          {collaborators.length === 0 ? (
            <div className="card-base !border-dashed !border-2 p-12 text-center">
              <div className="text-5xl mb-3">🧭</div>
              <h3 className="font-display font-bold text-lg mb-2">Be the first collaborator in your district</h3>
              <p className="text-muted text-sm mb-5 max-w-md mx-auto">
                Take the 7-minute Discover Yourself assessment to create your collaborator profile —
                archetype, founder role, sectors, and budget — and get matched with opportunities.
              </p>
              <Link href="/discover" className="btn-primary">🧭 Take the assessment</Link>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {collaborators.map((c) => <CollaboratorCard key={c.user_id} collaborator={c} />)}
            </div>
          )}

          <div className="mt-10 bg-gradient-to-r from-amber-50 to-teal-50 border border-amber-200 rounded-2xl p-6 text-center">
            <h3 className="font-display font-bold text-lg mb-1">Want to appear here?</h3>
            <p className="text-sm text-muted mb-4 max-w-md mx-auto">Complete the assessment and publish your collaborator profile — opportunities and co-founders will find you.</p>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              <Link href="/discover" className="btn-primary">🧭 Discover Yourself</Link>
              <Link href="/explore" className="btn-secondary">Browse opportunities</Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
