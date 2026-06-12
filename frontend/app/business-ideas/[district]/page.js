// District business-idea SEO pages: /business-ideas/medak, /business-ideas/warangal…
// Pure SSG from the existing Idea Library (122 ideas) — ideas whose
// district_fit names this district, topped up with beginner-friendly picks.

import Link from "next/link";
import { notFound } from "next/navigation";
import { MARKETPLACE_DISTRICTS, getMarketplaceDistrict } from "@/lib/collab";
import { IDEAS, getSector, formatINR } from "@/lib/idea-library";
import { getDistrictBySlug } from "@/lib/districts-data";
import { buildBaseMetadata, breadcrumbJsonLd, BASE_URL } from "@/lib/seo";
import AppNavbar from "@/components/AppNavbar";

const stateToSlug = (stateName) => (stateName === "Telangana" ? "telangana" : "andhra-pradesh");

export async function generateStaticParams() {
  return MARKETPLACE_DISTRICTS.map((d) => ({ district: d.slug }));
}

export async function generateMetadata({ params }) {
  const district = getMarketplaceDistrict(params.district);
  if (!district) return {};
  return buildBaseMetadata({
    title: `Best Business Ideas in ${district.name} (${district.state}) | ValueWeave`,
    description: `Practical, district-matched business ideas for ${district.name}, ${district.state} — with investment ranges, team roles, and skills needed. From the ValueWeave Idea Library.`,
    alternates: { canonical: `${BASE_URL}/business-ideas/${params.district}` },
  });
}

export default function DistrictBusinessIdeasPage({ params }) {
  const district = getMarketplaceDistrict(params.district);
  if (!district) notFound();

  const matched = IDEAS.filter((i) => i.district_fit?.includes(district.name));
  const fillers = matched.length < 6
    ? IDEAS.filter((i) => i.beginner_friendly && !matched.includes(i)).slice(0, 6 - matched.length)
    : [];
  const ideas = [...matched, ...fillers].slice(0, 18);
  const intel = getDistrictBySlug(district.slug);

  const breadcrumbs = [
    { name: "Home", url: BASE_URL },
    { name: "Business Ideas", url: `${BASE_URL}/ideas` },
    { name: district.name, url: `${BASE_URL}/business-ideas/${params.district}` },
  ];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd(breadcrumbs)) }} />
      <main className="pb-16">
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-12">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto">
            <Link href="/ideas" className="text-white/50 hover:text-white text-sm font-display font-semibold">← Full Idea Library</Link>
            <h1 data-testid="district-ideas-title" className="font-display font-extrabold tracking-tight text-3xl md:text-4xl text-white mt-3">
              Business Ideas for {district.name}
            </h1>
            <p className="text-white/60 mt-2 max-w-2xl">
              {ideas.length} practical ideas matched to {district.name}, {district.state} — with investment ranges, skills, and team roles from the ValueWeave Idea Library.
            </p>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {ideas.map((idea) => {
              const sector = getSector(idea.sector);
              return (
                <Link
                  key={idea.id}
                  href={`/ideas/${idea.slug}`}
                  data-testid={`district-idea-${idea.slug}`}
                  className="card-base p-5 flex flex-col gap-3 hover:-translate-y-1 hover:shadow-lg hover:border-amber-400 transition-all"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="text-3xl">{idea.emoji}</div>
                    <span className="chip bg-amber-50 text-amber-700">{sector.emoji} {sector.label}</span>
                  </div>
                  <h2 className="h-card line-clamp-2">{idea.title}</h2>
                  <p className="text-sm text-muted leading-relaxed line-clamp-3">{idea.short_description}</p>
                  <div className="flex items-center justify-between pt-3 border-t border-stone-100 text-xs">
                    <span className="font-display font-bold text-ink">
                      {formatINR(idea.investment_min)}–{formatINR(idea.investment_adv)}
                    </span>
                    {idea.beginner_friendly && <span className="chip bg-teal-50 text-teal-700">Beginner friendly</span>}
                  </div>
                </Link>
              );
            })}
          </div>

          <div className="mt-12 grid sm:grid-cols-3 gap-4">
            <Link href={`/opportunities/${stateToSlug(district.state)}/${district.slug}`} className="card-base p-5 hover:border-teal-300 hover:-translate-y-1 transition-all">
              <div className="text-2xl mb-2">🚀</div>
              <h3 className="font-display font-bold text-sm mb-1">Open Opportunities in {district.name}</h3>
              <p className="text-xs text-muted">Live opportunities looking for collaborators right now.</p>
            </Link>
            <Link href={intel ? `/district/${district.slug}` : "/district"} className="card-base p-5 hover:border-amber-300 hover:-translate-y-1 transition-all">
              <div className="text-2xl mb-2">📊</div>
              <h3 className="font-display font-bold text-sm mb-1">{district.name} District Intelligence</h3>
              <p className="text-xs text-muted">Industries, government schemes, and growth signals.</p>
            </Link>
            <Link href="/discover" className="card-base p-5 hover:border-violet-300 hover:-translate-y-1 transition-all">
              <div className="text-2xl mb-2">🧭</div>
              <h3 className="font-display font-bold text-sm mb-1">Discover Yourself</h3>
              <p className="text-xs text-muted">Get ideas matched to your archetype, budget, and district.</p>
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
