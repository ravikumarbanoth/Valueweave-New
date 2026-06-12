// District intelligence profile page — existing ValueWeave theme.
// Server component (no interactivity needed).

import Link from "next/link";
import { Breadcrumb, ScoreBadge, SectionHeader } from "@/components/ui/index";
import { ArticleCard } from "@/components/research/ArticleCard";

const DEMAND_COLORS = {
  high: "bg-teal-100 text-teal-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-stone-100 text-stone-600",
};

const GROWTH_ICON = { high: "🚀", medium: "📈", low: "📊" };

export function DistrictProfile({ district, relatedLinks, relatedArticles }) {
  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      {/* ── Hero ── */}
      <section className="relative overflow-hidden bg-ink">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-teal-500/25 blur-3xl" />
        <div className="absolute -bottom-24 -left-20 w-96 h-96 rounded-full bg-amber-500/20 blur-3xl" />
        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 pt-12 pb-12">
          <Breadcrumb
            items={[
              { label: "Home", href: "/" },
              { label: "Districts", href: "/district" },
              { label: district.name },
            ]}
          />
          <div className="mt-6 flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <p className="text-teal-300 text-sm font-display font-semibold mb-2">
                {district.region} · {district.state}
              </p>
              <h1 data-testid="district-title" className="font-display font-extrabold tracking-tight text-4xl md:text-5xl text-white leading-tight">
                {district.name}
              </h1>
              <p className="text-white/70 mt-3 text-base sm:text-lg max-w-2xl leading-relaxed">
                {district.profileSummary}
              </p>
            </div>

            <div className="flex flex-wrap gap-4 md:flex-col md:items-end">
              <div className="bg-white/10 border border-white/15 rounded-xl px-5 py-3">
                <p className="text-white/60 text-xs uppercase tracking-wider mb-0.5">Population</p>
                <p className="text-white font-display font-extrabold text-xl">{district.populationLabel}</p>
              </div>
              <div className="bg-white/10 border border-white/15 rounded-xl px-5 py-3">
                <p className="text-white/60 text-xs uppercase tracking-wider mb-0.5">Literacy</p>
                <p className="text-white font-display font-extrabold text-xl">{district.demographics.literacyRate}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-10">
          <div className="space-y-12">
            {/* ── Key Industries ── */}
            <section>
              <SectionHeader eyebrow="Economy" title="Key Industries" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {district.keyIndustries.map((ind) => (
                  <div key={ind.name} className="card-base p-5 hover:border-amber-300 transition-colors">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h3 className="font-display font-bold text-ink">{ind.name}</h3>
                      {ind.employmentShare && (
                        <span className="text-xs font-display font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full shrink-0">
                          {ind.employmentShare}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted leading-relaxed">{ind.description}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* ── Emerging Sectors ── */}
            <section>
              <SectionHeader eyebrow="Growth Signals" title="Emerging Sectors" />
              <div className="space-y-3">
                {district.emergingSectors.map((sector) => (
                  <div key={sector.name} className="card-base p-4 flex items-start gap-4 hover:border-teal-300 transition-colors">
                    <div className="mt-0.5 text-lg">{GROWTH_ICON[sector.growthSignal]}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="font-display font-bold text-ink text-sm">{sector.name}</h3>
                        <span className={`text-xs font-display font-semibold px-2 py-0.5 rounded-full ${
                          sector.growthSignal === "high" ? "bg-teal-100 text-teal-700" : "bg-amber-100 text-amber-700"
                        }`}>
                          {sector.growthSignal.toUpperCase()} GROWTH
                        </span>
                      </div>
                      <p className="text-sm text-muted leading-relaxed">{sector.description}</p>
                      {sector.investmentRange && (
                        <p className="text-xs text-amber-600 font-display font-semibold mt-1">
                          Investment: {sector.investmentRange}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* ── Top Opportunities ── */}
            <section>
              <SectionHeader eyebrow="Opportunities" title="Top Business Ideas for This District" />
              <div className="space-y-3">
                {district.topOpportunities.map((opp, i) => (
                  <div key={i} className="card-base p-5 hover:border-amber-300 transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <h3 className="font-display font-bold text-ink">
                          {opp.ideaSlug ? (
                            <Link href={`/ideas/${opp.ideaSlug}`} className="hover:text-amber-600 transition-colors">
                              {opp.title} →
                            </Link>
                          ) : (
                            opp.title
                          )}
                        </h3>
                        <div className="flex flex-wrap gap-2 mt-2">
                          <span className="text-xs bg-stone-100 text-stone-600 px-2 py-0.5 rounded-full">{opp.sector}</span>
                          <span className="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">{opp.investmentRange}</span>
                          <span className="text-xs bg-stone-50 text-stone-500 px-2 py-0.5 rounded-full">Team: {opp.teamSize}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-right">
                          <p className="text-xs text-stone-400 mb-0.5">Fit Score</p>
                          <ScoreBadge score={opp.fitScore} variant="fit" />
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-stone-400 mb-0.5">Demand</p>
                          <ScoreBadge score={opp.demandScore} variant="demand" />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5">
                <Link
                  href={`/opportunity-radar/${district.state === "Telangana" ? "telangana" : "andhra-pradesh"}`}
                  className="inline-flex items-center gap-2 text-amber-700 hover:text-amber-800 font-display font-bold text-sm"
                >
                  View full {district.state} Opportunity Radar →
                </Link>
              </div>
            </section>

            {/* ── Skills Demand ── */}
            <section>
              <SectionHeader eyebrow="Workforce" title="Local Skills in Demand" />
              <div className="flex flex-wrap gap-2">
                {district.skillsDemand.map((s) => (
                  <div key={s.skill} className={`px-3 py-2 rounded-xl text-sm font-medium ${DEMAND_COLORS[s.demandLevel]}`}>
                    <span className="font-display font-bold">{s.skill}</span>
                    <span className="ml-2 text-xs opacity-70">{s.sector}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* ── Government Schemes ── */}
            <section>
              <SectionHeader eyebrow="Support" title="Government Schemes Available" />
              <div className="space-y-3">
                {district.governmentSchemes.map((scheme) => (
                  <div key={scheme.name} className="card-base p-4 hover:border-teal-300 transition-colors">
                    <h3 className="font-display font-bold text-ink text-sm">
                      {scheme.url ? (
                        <a href={scheme.url} target="_blank" rel="noopener noreferrer" className="hover:text-teal-600 transition-colors">
                          {scheme.name} ↗
                        </a>
                      ) : (
                        scheme.name
                      )}
                    </h3>
                    <p className="text-xs text-stone-400 mt-0.5">{scheme.authority}</p>
                    <p className="text-sm text-muted mt-2 leading-relaxed">{scheme.benefit}</p>
                    <p className="text-xs text-teal-700 bg-teal-50 px-2 py-1 rounded-lg mt-2 inline-block">
                      Eligible: {scheme.eligibility}
                    </p>
                  </div>
                ))}
              </div>
              <p className="text-xs text-stone-400 mt-3">
                Verify eligibility and current terms on the official scheme portal before relying on them.
              </p>
            </section>

            {/* ── Infrastructure ── */}
            <section>
              <SectionHeader eyebrow="Logistics" title="Infrastructure & Connectivity" />
              <div className="card-base p-6 grid sm:grid-cols-2 gap-5">
                <div>
                  <p className="text-xs text-stone-400 uppercase tracking-wider mb-1">Road & Digital</p>
                  <p className="text-sm text-ink leading-relaxed">{district.infrastructure.connectivity}</p>
                </div>
                <div>
                  <p className="text-xs text-stone-400 uppercase tracking-wider mb-1">Nearest Airport</p>
                  <p className="text-sm text-ink">{district.infrastructure.nearestAirport}</p>
                </div>
                <div>
                  <p className="text-xs text-stone-400 uppercase tracking-wider mb-1">Railway Hub</p>
                  <p className="text-sm text-ink">{district.infrastructure.nearestRailwayHub}</p>
                </div>
                <div>
                  <p className="text-xs text-stone-400 uppercase tracking-wider mb-1">Industrial Areas</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {district.infrastructure.industrialAreas.map((a) => (
                      <span key={a} className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full">
                        {a}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* ── Related Research ── */}
            {relatedArticles.length > 0 && (
              <section>
                <SectionHeader eyebrow="Research" title="Related Articles" />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {relatedArticles.map((a) => (
                    <ArticleCard key={a.slug} article={a} />
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* ── Sidebar ── */}
          <aside className="space-y-5">
            <div className="card-base p-5 lg:sticky lg:top-20">
              <p className="text-sm font-display font-bold text-muted mb-4 uppercase tracking-wider">Demographics</p>
              <div className="space-y-1 text-sm">
                {[
                  ["Literacy Rate", district.demographics.literacyRate],
                  ["Urban : Rural", district.demographics.urbanRuralRatio],
                  ["Youth (under 25)", district.demographics.youthPopulation],
                  ["Languages", district.demographics.mainLanguages.join(", ")],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between gap-2 py-2 border-b border-stone-100 last:border-0">
                    <span className="text-muted">{label}</span>
                    <span className="font-display font-bold text-ink text-right">{value}</span>
                  </div>
                ))}
              </div>

              <div className="mt-5 space-y-2">
                <Link href="/explore" className="btn-primary w-full !py-2.5 text-sm">
                  Explore opportunities
                </Link>
                <Link href="/ideas" className="btn-secondary w-full !py-2.5 text-sm">
                  Browse Idea Library
                </Link>
              </div>
            </div>

            {relatedLinks.length > 0 && (
              <div className="card-base p-5">
                <p className="text-sm font-display font-bold text-muted mb-4 uppercase tracking-wider">Related Pages</p>
                <div className="space-y-2">
                  {relatedLinks.slice(0, 8).map((link) => (
                    <Link
                      key={link.href + link.label}
                      href={link.href}
                      className="flex items-center gap-2 text-sm text-muted hover:text-amber-700 transition-colors py-1.5"
                    >
                      <span className="text-amber-400">→</span>
                      {link.label}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>
    </main>
  );
}
