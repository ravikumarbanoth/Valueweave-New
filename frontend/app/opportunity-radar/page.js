import Link from "next/link";
import { buildBaseMetadata, BASE_URL } from "@/lib/seo";
import { SEGMENT_LABELS, getAllSegments, RADAR_OPPORTUNITIES } from "@/lib/radar-data";
import AppNavbar from "@/components/AppNavbar";

export const metadata = buildBaseMetadata({
  title: "Opportunity Radar — Top Business Ideas Ranked for Bharat | ValueWeave",
  description:
    "Ranked business opportunities by fit score, demand, and district suitability across Telangana, Andhra Pradesh, healthcare, agriculture, and more.",
  alternates: { canonical: `${BASE_URL}/opportunity-radar` },
});

const SEGMENT_ICONS = {
  telangana: "🌿",
  "andhra-pradesh": "🌊",
  students: "🎓",
  healthcare: "🏥",
  agriculture: "🌾",
  "under-5-lakhs": "💡",
};

const SEGMENT_DESC = {
  telangana: "Top ranked opportunities across all districts of Telangana",
  "andhra-pradesh": "High-potential ideas for Andhra Pradesh's growing economy",
  students: "Low-investment, high-skill opportunities ideal for fresh graduates",
  healthcare: "Rural and urban health sector businesses in high demand",
  agriculture: "Agri-processing, value chain, and farm-tech opportunities",
  "under-5-lakhs": "Start strong with under ₹5 lakh investment — vetted ideas",
};

export default function OpportunityRadarPage() {
  const segments = getAllSegments();
  const trending = RADAR_OPPORTUNITIES.filter((o) => o.trending).slice(0, 5);

  return (
    <div className="min-h-screen bg-cream font-body">
      <AppNavbar />
      <main className="pb-16">
        {/* Hero */}
        <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-16">
          <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
          <div className="relative max-w-4xl mx-auto text-center">
            <span className="chip bg-teal-500/20 text-teal-300 border border-teal-500/30 mb-4">
              VALUEWEAVE OPPORTUNITY RADAR
            </span>
            <h1 data-testid="radar-title" className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
              Ranked. Scored. Ready<br className="hidden md:block" /> for You to Build.
            </h1>
            <p className="text-white/60 text-base sm:text-lg max-w-xl mx-auto">
              Business ideas ranked by fit score, market demand, and district suitability — connected to the Idea Library and Research Hub.
            </p>
          </div>
        </section>

        {/* Segments Grid */}
        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-14">
          <h2 className="font-display font-extrabold tracking-tight text-2xl text-ink mb-8 text-center">
            Explore by Segment
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {segments.map((seg) => (
              <Link
                key={seg}
                href={`/opportunity-radar/${seg}`}
                data-testid={`radar-segment-${seg}`}
                className="group card-base p-6 hover:border-amber-400 hover:shadow-md hover:-translate-y-1 transition-all duration-200"
              >
                <div className="text-3xl mb-3">{SEGMENT_ICONS[seg]}</div>
                <h3 className="font-display font-bold text-ink text-lg mb-1 group-hover:text-amber-700 transition-colors">
                  {SEGMENT_LABELS[seg]}
                </h3>
                <p className="text-sm text-muted leading-relaxed">{SEGMENT_DESC[seg]}</p>
                <div className="mt-4 flex items-center gap-1 text-amber-700 font-display font-bold text-sm">
                  View Rankings <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Trending */}
        <section className="max-w-5xl mx-auto px-4 sm:px-6">
          <h2 className="font-display font-extrabold tracking-tight text-2xl text-ink mb-6">
            🔥 Trending Right Now
          </h2>
          <div className="space-y-3">
            {trending.map((item, i) => (
              <Link
                key={item.id}
                href={`/opportunity-radar/${item.segment}`}
                className="flex items-center gap-4 card-base px-5 py-4 hover:border-amber-400 hover:shadow-sm transition-all"
              >
                <span className="text-2xl font-display font-extrabold text-stone-200 w-8 shrink-0">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-bold text-ink truncate">{item.title}</p>
                  <p className="text-sm text-muted">{item.sector} · {item.investmentRange}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <div className="text-right">
                    <p className="text-xs text-stone-400">Fit</p>
                    <span className="inline-block bg-teal-100 text-teal-700 font-display font-bold text-sm px-2.5 py-0.5 rounded-full">
                      {item.fitScore}
                    </span>
                  </div>
                  <div className="text-right hidden sm:block">
                    <p className="text-xs text-stone-400">Demand</p>
                    <span className="inline-block bg-amber-100 text-amber-700 font-display font-bold text-sm px-2.5 py-0.5 rounded-full">
                      {item.demandScore}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
