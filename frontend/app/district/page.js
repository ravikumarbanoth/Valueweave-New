import Link from "next/link";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import { DISTRICTS } from "@/lib/districts-data";
import AppNavbar from "@/components/AppNavbar";

export const metadata = buildBaseMetadata({
  title: "District Opportunity Profiles — Telangana & Andhra Pradesh | ValueWeave",
  description:
    "Explore business opportunities, emerging sectors, government schemes, and collaborator networks for every major district in Telangana and Andhra Pradesh.",
  alternates: { canonical: `${BASE_URL}/district` },
});

export default function DistrictIndexPage() {
  const telangana = DISTRICTS.filter((d) => d.state === "Telangana");
  const ap = DISTRICTS.filter((d) => d.state === "Andhra Pradesh");

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main>
        {/* Hero */}
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-16">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-teal-500/25 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-teal-500/20 text-teal-300 border border-teal-500/30 mb-4">DISTRICT INTELLIGENCE</span>
            <h1 data-testid="district-index-title" className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
              Know Your District.<br className="hidden md:block" /> Build with Confidence.
            </h1>
            <p className="text-white/60 text-base sm:text-lg max-w-2xl mx-auto">
              Deep-dive profiles on population, industries, schemes, opportunities, and skills demand — built for Bharat&apos;s builders.
            </p>
          </div>
        </section>

        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-14 space-y-14 pb-20">
          <StateSection state="Telangana" districts={telangana} emoji="🌿" />
          <StateSection state="Andhra Pradesh" districts={ap} emoji="🌊" />
        </div>
      </main>
    </div>
  );
}

function StateSection({ state, districts, emoji }) {
  return (
    <section>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-2xl">{emoji}</span>
        <h2 className="font-display font-extrabold tracking-tight text-2xl text-ink">{state}</h2>
        <span className="text-sm text-muted">{districts.length} districts</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {districts.map((district) => (
          <Link
            key={district.slug}
            href={`/district/${district.slug}`}
            data-testid={`district-card-${district.slug}`}
            className="group card-base p-5 hover:border-teal-300 hover:shadow-md hover:-translate-y-1 transition-all duration-200"
          >
            <div className="flex items-start justify-between gap-2 mb-3">
              <div>
                <h3 className="font-display font-bold text-ink text-lg group-hover:text-teal-700 transition-colors">
                  {district.name}
                </h3>
                <p className="text-xs text-stone-400 mt-0.5">{district.region}</p>
              </div>
              <span className="text-xs font-display font-bold text-amber-600 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full shrink-0">
                {district.populationLabel}
              </span>
            </div>

            <p className="text-sm text-muted line-clamp-2 mb-3 leading-relaxed">{district.profileSummary}</p>

            {district.emergingSectors[0] && (
              <div className="flex items-center gap-2">
                <span className="text-xs">📈</span>
                <span className="text-xs text-teal-700 font-display font-semibold">
                  {district.emergingSectors[0].name}
                </span>
              </div>
            )}

            <div className="mt-3 flex items-center gap-1 text-amber-700 text-sm font-display font-bold">
              View Profile
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
