import Link from "next/link";
import { createClient } from "@/lib/supabase-server";
import { MapPin, Briefcase, ArrowRight } from "lucide-react";

async function fetchOpportunities() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return [];
  }
  try {
    const sb = createClient();
    const { data } = await sb
      .from("opportunities")
      .select("id, title, category, district, state, investment_range, status")
      .eq("status", "open")
      .order("created_at", { ascending: false })
      .limit(9);
    return data || [];
  } catch {
    return [];
  }
}

const SECTOR_COLORS = {
  Healthcare: "bg-rose-50 text-rose-700 border-rose-200",
  "Agri-tech": "bg-emerald-50 text-emerald-700 border-emerald-200",
  Agriculture: "bg-emerald-50 text-emerald-700 border-emerald-200",
  "EV Tech": "bg-green-50 text-green-700 border-green-200",
  "AI & Tech": "bg-blue-50 text-blue-700 border-blue-200",
  Retail: "bg-amber-50 text-amber-700 border-amber-200",
  Education: "bg-violet-50 text-violet-700 border-violet-200",
  Logistics: "bg-sky-50 text-sky-700 border-sky-200",
  default: "bg-stone-50 text-stone-600 border-stone-200",
};

function sectorColor(cat) {
  return SECTOR_COLORS[cat] || SECTOR_COLORS.default;
}

function OpportunityCard({ opp }) {
  return (
    // `/explore/<id>` was never a route. `app/explore/` has only `page.js`, so
    // every card on the landing page led to a 404 — the first thing a visitor
    // clicked was the first thing that broke. The detail page has always lived
    // at `/opportunities/<id>`.
    //
    // next.config.js keeps `/explore/<id>` redirecting here permanently, because
    // this link has been wrong long enough to have been shared.
    <Link
      href={`/opportunities/${opp.id}`}
      className="card-base p-5 flex flex-col gap-3 hover:-translate-y-1 hover:shadow-lg transition-all group min-h-[44px]"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-display font-bold text-sm text-ink leading-snug group-hover:text-amber-700 transition-colors flex-1">
          {opp.title}
        </h3>
        <ArrowRight size={14} className="text-stone-300 group-hover:text-amber-500 transition-colors shrink-0 mt-0.5" />
      </div>

      <div className="flex flex-wrap gap-1.5 mt-auto">
        {opp.category && (
          <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${sectorColor(opp.category)}`}>
            <Briefcase size={10} /> {opp.category}
          </span>
        )}
        {opp.district && (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border bg-stone-50 text-stone-500 border-stone-200">
            <MapPin size={10} /> {opp.district}
          </span>
        )}
        {opp.investment_range && (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border bg-amber-50 text-amber-700 border-amber-200">
            ₹ {opp.investment_range}
          </span>
        )}
      </div>
    </Link>
  );
}

export default async function HomeFeaturedOpportunities() {
  const opportunities = await fetchOpportunities();

  if (opportunities.length === 0) return null;

  return (
    <section className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-amber-100 text-amber-700 mb-4">LIVE NOW</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            Featured Opportunities
          </h2>
          <p className="mt-4 text-muted max-w-lg mx-auto text-base sm:text-lg">
            Real business opportunities from across Telangana and Andhra Pradesh.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map((opp) => (
            <OpportunityCard key={opp.id} opp={opp} />
          ))}
        </div>

        <div className="text-center mt-10">
          <Link href="/explore" className="btn-primary">
            View All Opportunities →
          </Link>
        </div>
      </div>
    </section>
  );
}
