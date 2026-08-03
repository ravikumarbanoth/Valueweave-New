import { notFound } from "next/navigation";
import Link from "next/link";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import { getRadarBySegment, getAllSegments, SEGMENT_LABELS } from "@/lib/radar-data";
import { ScoreBadge } from "@/components/ui/index";
import AppNavbar from "@/components/AppNavbar";

export async function generateStaticParams() {
  return getAllSegments().map((segment) => ({ segment }));
}

export async function generateMetadata({ params }) {
  const label = SEGMENT_LABELS[params.segment];
  if (!label) return {};
  return buildBaseMetadata({
    title: `${label} Business Opportunities — Ranked | ValueWeave`,
    description: `Top-ranked business opportunities for ${label} — scored by fit, demand, and district suitability. Find your next venture.`,
    alternates: { canonical: `${BASE_URL}/opportunity-radar/${params.segment}` },
  });
}

export default function RadarSegmentPage({ params }) {
  const segment = params.segment;
  if (!getAllSegments().includes(segment)) notFound();

  const opportunities = getRadarBySegment(segment);
  const label = SEGMENT_LABELS[segment];

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main className="pb-16">
        {/* Hero */}
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-12">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto">
            <Link href="/opportunity-radar" className="text-white/50 hover:text-white text-sm inline-flex items-center gap-1 transition-colors font-display font-semibold">
              ← All Segments
            </Link>
            <h1 data-testid="radar-segment-title" className="font-display font-extrabold tracking-tight text-3xl md:text-4xl text-white mt-3">
              {label}
            </h1>
            <p className="text-white/60 mt-2">
              {opportunities.length} opportunities ranked by fit score, demand, and investment
            </p>
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
          {/* Step 4 — the same disclosure the radar index carries. Fit and demand
              are editorial judgements from lib/radar-data.js, and this page renders
              them as a /100 badge with a progress bar, which is the most
              measurement-like presentation in the application. */}
          <div
            data-testid="radar-methodology"
            className="rounded-2xl border border-dashed border-stone-200 bg-stone-50 p-4 mb-8"
          >
            <p className="text-xs text-muted leading-relaxed">
              <strong className="font-display text-ink">Fit and demand are editorial
              judgements</strong>, assigned by hand and carrying no source. They are not
              comparable with the confidence scores on researched knowledge.{" "}
              <Link href="/knowledge?type=business" className="underline hover:text-ink">
                Researched business opportunities →
              </Link>
            </p>
          </div>

          {/* Segment nav */}
          <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-8">
            {getAllSegments().map((seg) => (
              <Link
                key={seg}
                href={`/opportunity-radar/${seg}`}
                className={`shrink-0 px-4 py-1.5 rounded-full text-xs font-display font-semibold transition-colors min-h-[44px] inline-flex items-center ${
                  seg === segment ? "bg-ink text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                {SEGMENT_LABELS[seg]}
              </Link>
            ))}
          </div>

          <div className="space-y-4">
            {opportunities.map((item, i) => (
              <div
                key={item.id}
                className={`card-base p-5 transition-all hover:shadow-md ${
                  item.trending ? "!border-amber-300" : "hover:border-amber-200"
                }`}
              >
                <div className="flex items-start gap-4">
                  <span className="text-3xl font-display font-extrabold text-stone-200 w-10 shrink-0 leading-none mt-1">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <h2 className="font-display font-bold text-ink text-lg">
                        {item.ideaSlug ? (
                          <Link href={`/ideas/${item.ideaSlug}`} className="hover:text-amber-600 transition-colors">
                            {item.title}
                          </Link>
                        ) : item.researchSlug ? (
                          <Link href={`/research/${item.researchSlug}`} className="hover:text-amber-600 transition-colors">
                            {item.title}
                          </Link>
                        ) : (
                          item.title
                        )}
                      </h2>
                      {item.trending && (
                        <span className="text-xs font-display font-bold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
                          🔥 TRENDING
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="text-xs bg-stone-100 text-stone-600 px-2 py-0.5 rounded-full">{item.sector}</span>
                      <span className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full">{item.investmentRange}</span>
                      <span className="text-xs bg-stone-50 text-stone-400 px-2 py-0.5 rounded-full">{item.stateTag}</span>
                    </div>

                    <div className="flex flex-wrap items-center gap-4">
                      <div>
                        <p className="text-xs text-stone-400 mb-0.5">Fit Score</p>
                        <ScoreBadge score={item.fitScore} label="/100" variant="fit" />
                      </div>
                      <div>
                        <p className="text-xs text-stone-400 mb-0.5">Demand Score</p>
                        <ScoreBadge score={item.demandScore} label="/100" variant="demand" />
                      </div>
                      <div className="flex-1 min-w-[120px]">
                        <p className="text-xs text-stone-400 mb-1">Fit Strength</p>
                        <div className="w-full bg-stone-100 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-amber-400 to-teal-500 h-2 rounded-full"
                            style={{ width: `${item.fitScore}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {item.districtSuitability.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {item.districtSuitability.map((d) => (
                          <Link
                            key={d}
                            href={`/district/${d}`}
                            className="text-xs bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full capitalize hover:bg-teal-600 hover:text-white hover:border-teal-600 transition-colors"
                          >
                            {d.replace(/-/g, " ")}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* CTA */}
                  <div className="shrink-0 hidden sm:flex flex-col gap-2 items-end">
                    {item.ideaSlug && (
                      <Link
                        href={`/ideas/${item.ideaSlug}`}
                        className="text-xs bg-amber-500 hover:bg-amber-600 text-white font-display font-bold px-3 py-1.5 rounded-full transition-colors"
                      >
                        View Idea
                      </Link>
                    )}
                    {item.researchSlug && (
                      <Link
                        href={`/research/${item.researchSlug}`}
                        className="text-xs border-2 border-teal-400 text-teal-700 hover:bg-teal-50 font-display font-bold px-3 py-1.5 rounded-full transition-colors"
                      >
                        Read Research
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
