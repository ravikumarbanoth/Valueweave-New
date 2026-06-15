import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import GeneratorClient from "./GeneratorClient";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Opportunity Generator | ValueWeave Admin",
  robots: { index: false, follow: false },
};

async function fetchDemandSuggestions() {
  try {
    const sb = createClient();
    const [{ data: searches }, { data: requests }, { data: collabSectors }] = await Promise.all([
      sb.from("search_events").select("sector,district").not("sector", "is", null).limit(2000),
      sb.from("user_requests").select("sector,district").not("sector", "is", null).limit(1000),
      sb.from("collaborator_profiles").select("top_sectors,district").limit(500),
    ]);

    const map = {};
    const addKey = (sector, district, field) => {
      if (!sector) return;
      const k = `${sector}||${district || ""}`;
      if (!map[k]) map[k] = { sector, district: district || null, searches: 0, requests: 0, collabs: 0 };
      map[k][field]++;
    };

    (searches || []).forEach(({ sector, district }) => addKey(sector, district, "searches"));
    (requests || []).forEach(({ sector, district }) => addKey(sector, district, "requests"));
    (collabSectors || []).forEach(({ top_sectors, district }) => {
      (top_sectors || []).forEach((s) => addKey(s, district, "collabs"));
    });

    return Object.values(map)
      .map((v) => ({ ...v, score: v.searches + v.requests * 2 + v.collabs }))
      .filter((v) => v.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 12);
  } catch {
    return [];
  }
}

export default async function OpportunityGeneratorPage() {
  const demandSuggestions = await fetchDemandSuggestions();

  return (
    <AdminShell>
      <div className="p-6 max-w-4xl space-y-6">
        <div>
          <span className="chip bg-amber-100 text-amber-700 border border-amber-200">BULK GENERATOR</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">Opportunity Generator</h1>
          <p className="text-stone-500 text-sm mt-1">
            Bulk-generate SEO-optimized opportunity records with templated descriptions, skill requirements, and collaborator roles. Preview before publishing.
          </p>
        </div>
        <GeneratorClient demandSuggestions={demandSuggestions} />
      </div>
    </AdminShell>
  );
}
