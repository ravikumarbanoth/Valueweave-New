import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import { DISTRICTS } from "@/lib/districts-data";
import { MapPin, TrendingUp, Briefcase, UserCheck, BookOpen, Lightbulb } from "lucide-react";
import Link from "next/link";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "District Intelligence | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function HeatCell({ value, max }) {
  const pct = max > 0 ? value / max : 0;
  const opacity = Math.max(0.05, pct);
  return (
    <div
      className="flex items-center justify-center h-12 rounded-xl text-sm font-bold text-teal-800"
      style={{ background: `rgba(13,148,136,${opacity})` }}
    >
      {value}
    </div>
  );
}

async function fetchDistrictData() {
  try {
    const sb = createClient();
    const [
      { data: oppsByDistrict },
      { data: collabsByDistrict },
      { data: articlesByDistrict },
      { data: requestsByDistrict },
      { data: viewsByDistrict },
    ] = await Promise.all([
      sb.from("opportunities").select("district").not("district", "is", null).limit(2000),
      sb.from("collaborator_profiles").select("district").not("district", "is", null).limit(1000),
      sb.from("research_articles").select("district").not("district", "is", null).eq("status", "published").limit(500),
      sb.from("user_requests").select("district").not("district", "is", null).limit(2000),
      sb.from("page_views").select("district").not("district", "is", null).limit(5000),
    ]);

    // Aggregate all by district name
    const countMap = (rows, field = "district") => {
      const m = {};
      (rows || []).forEach((r) => {
        const k = r[field];
        if (k) m[k] = (m[k] || 0) + 1;
      });
      return m;
    };

    const oppsMap = countMap(oppsByDistrict);
    const collabMap = countMap(collabsByDistrict);
    const articleMap = countMap(articlesByDistrict);
    const requestMap = countMap(requestsByDistrict);
    const viewsMap = countMap(viewsByDistrict);

    // Enrich districts data
    const enriched = DISTRICTS.map((d) => {
      const name = d.name;
      const opps = oppsMap[name] || 0;
      const collabs = collabMap[name] || 0;
      const articles = articleMap[name] || 0;
      const requests = requestMap[name] || 0;
      const visits = viewsMap[name] || 0;
      const ideas = (d.topOpportunities || []).length;
      const demand = requests * 3 + visits;
      const opportunityPotential = opps * 2 + collabs * 3 + ideas;
      return {
        slug: d.slug, name, state: d.state,
        opps, collabs, articles, requests, visits, ideas,
        demand, opportunityPotential,
      };
    });

    return { enriched };
  } catch (e) {
    console.error("Districts error:", e);
    return { enriched: DISTRICTS.map((d) => ({
      slug: d.slug, name: d.name, state: d.state,
      opps: 0, collabs: 0, articles: 0, requests: 0, visits: 0, ideas: 0,
      demand: 0, opportunityPotential: 0,
    })) };
  }
}

export default async function DistrictsPage({ searchParams }) {
  const { enriched } = await fetchDistrictData();
  const sortBy = searchParams?.sort || "opportunityPotential";

  const sorted = [...enriched].sort((a, b) => (b[sortBy] || 0) - (a[sortBy] || 0));
  const tsDistricts = sorted.filter((d) => d.state === "Telangana");
  const apDistricts = sorted.filter((d) => d.state === "Andhra Pradesh");

  const maxVisits = Math.max(...enriched.map((d) => d.visits), 1);
  const maxOpps = Math.max(...enriched.map((d) => d.opps), 1);

  const SORT_OPTIONS = [
    { key: "visits", label: "Traffic" },
    { key: "demand", label: "Demand" },
    { key: "opportunityPotential", label: "Opportunity Potential" },
    { key: "opps", label: "Opportunities" },
  ];

  const COLS = [
    { label: "District", key: null },
    { label: "Visits", key: "visits" },
    { label: "Opportunities", key: "opps" },
    { label: "Collaborators", key: "collabs" },
    { label: "Requests", key: "requests" },
    { label: "Ideas", key: "ideas" },
    { label: "Articles", key: "articles" },
    { label: "Opp. Potential", key: "opportunityPotential" },
  ];

  function DistrictTable({ districts }) {
    return (
      <div className="overflow-x-auto">
        <table className="w-full text-[12px]">
          <thead>
            <tr className="border-b border-stone-200">
              {COLS.map((c) => (
                <th key={c.label} className="text-left py-2.5 px-3 text-[10px] font-semibold text-stone-400 uppercase tracking-widest whitespace-nowrap">
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {districts.map((d, i) => (
              <tr key={d.slug} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
                <td className="py-2.5 px-3">
                  <Link
                    href={`/district/${d.slug}`}
                    className="font-semibold text-ink hover:text-amber-700 transition-colors flex items-center gap-1.5"
                  >
                    <span className="text-stone-300 text-[11px] w-5">{i + 1}</span>
                    {d.name}
                  </Link>
                </td>
                <td className="py-2.5 px-3 text-stone-600 font-medium">{d.visits}</td>
                <td className="py-2.5 px-3">
                  <span className={`font-bold ${d.opps > 20 ? "text-teal-600" : "text-stone-600"}`}>{d.opps}</span>
                </td>
                <td className="py-2.5 px-3 text-stone-600 font-medium">{d.collabs}</td>
                <td className="py-2.5 px-3 text-stone-600 font-medium">{d.requests}</td>
                <td className="py-2.5 px-3 text-stone-600 font-medium">{d.ideas}</td>
                <td className="py-2.5 px-3 text-stone-600 font-medium">{d.articles}</td>
                <td className="py-2.5 px-3">
                  <span className={`chip text-[11px] font-bold ${d.opportunityPotential > 30 ? "bg-green-100 text-green-700" : "bg-stone-100 text-stone-500"}`}>
                    {d.opportunityPotential}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="chip bg-teal-100 text-teal-700 border border-teal-200">DISTRICT INTELLIGENCE</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2">District Intelligence</h1>
            <p className="text-stone-500 text-sm mt-1">
              Per-district performance across Telangana and Andhra Pradesh
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {SORT_OPTIONS.map(({ key, label }) => (
              <Link
                key={key}
                href={`?sort=${key}`}
                className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-colors ${
                  sortBy === key
                    ? "bg-teal-500 text-white"
                    : "bg-white border border-stone-200 text-stone-500 hover:border-teal-500 hover:text-teal-700"
                }`}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>

        {/* Heatmap */}
        <div className="card-base p-5">
          <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
            <MapPin size={15} className="text-teal-500" /> Opportunity Heatmap
          </h3>
          <div className="grid grid-cols-4 sm:grid-cols-7 gap-2">
            {sorted.map((d) => (
              <div key={d.slug} className="text-center">
                <HeatCell value={d.opps} max={maxOpps} />
                <p className="text-[10px] text-stone-500 mt-1 truncate">{d.name}</p>
              </div>
            ))}
          </div>
          <p className="text-[11px] text-stone-400 mt-3">Color intensity = opportunity count relative to top district</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Districts Tracked", value: DISTRICTS.length, icon: MapPin, color: "teal" },
            { label: "Total Opportunities", value: enriched.reduce((s, d) => s + d.opps, 0), icon: Briefcase, color: "amber" },
            { label: "Total Collaborators", value: enriched.reduce((s, d) => s + d.collabs, 0), icon: UserCheck, color: "blue" },
            { label: "Total Requests", value: enriched.reduce((s, d) => s + d.requests, 0), icon: TrendingUp, color: "rose" },
          ].map(({ label, value, icon: Icon, color }) => {
            const bg = { teal: "bg-teal-50 text-teal-700", amber: "bg-amber-50 text-amber-700", blue: "bg-blue-50 text-blue-700", rose: "bg-rose-50 text-rose-700" };
            return (
              <div key={label} className="card-base p-4">
                <div className={`inline-flex p-2 rounded-lg mb-2 ${bg[color]}`}><Icon size={14} /></div>
                <div className="text-xl font-display font-extrabold text-ink">{value.toLocaleString()}</div>
                <div className="text-[10px] text-stone-400 uppercase tracking-widest font-semibold mt-0.5">{label}</div>
              </div>
            );
          })}
        </div>

        {/* Telangana Table */}
        <div className="card-base overflow-hidden">
          <div className="p-5 border-b border-stone-100 flex items-center gap-2">
            <MapPin size={15} className="text-teal-500" />
            <h3 className="font-display font-bold text-ink text-sm">Telangana Districts</h3>
            <span className="chip bg-teal-50 text-teal-700 text-[10px] ml-auto">{tsDistricts.length} districts</span>
          </div>
          <DistrictTable districts={tsDistricts} />
        </div>

        {/* Andhra Pradesh Table */}
        <div className="card-base overflow-hidden">
          <div className="p-5 border-b border-stone-100 flex items-center gap-2">
            <MapPin size={15} className="text-blue-500" />
            <h3 className="font-display font-bold text-ink text-sm">Andhra Pradesh Districts</h3>
            <span className="chip bg-blue-50 text-blue-700 text-[10px] ml-auto">{apDistricts.length} districts</span>
          </div>
          <DistrictTable districts={apDistricts} />
        </div>

      </div>
    </AdminShell>
  );
}
