import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import Link from "next/link";
import { Star, FileText, Briefcase, MapPin, Lightbulb, Zap, ArrowRight, Search, MessageSquare, Users } from "lucide-react";
import IDEAS from "@/lib/idea-library/ideas.json";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "Recommendations | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function PriorityBadge({ score }) {
  if (score >= 80) return <span className="chip bg-green-100 text-green-700 border border-green-200 text-[11px] font-bold">{score} · HIGH</span>;
  if (score >= 50) return <span className="chip bg-amber-100 text-amber-700 border border-amber-200 text-[11px] font-bold">{score} · MEDIUM</span>;
  return <span className="chip bg-stone-100 text-stone-500 text-[11px] font-bold">{score} · LOW</span>;
}

function ReasonTag({ icon: Icon, text, color }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-medium ${color}`}>
      <Icon size={10} />
      {text}
    </span>
  );
}

async function fetchRecommendations() {
  try {
    const sb = createClient();

    const [
      { data: searches },
      { data: requests },
      { data: interests },
      { data: articles },
      { data: opportunities },
      { data: collabSectors },
    ] = await Promise.all([
      sb.from("search_events").select("query,sector,district").limit(5000),
      sb.from("user_requests").select("title,sector,district,type").limit(2000),
      sb.from("page_views").select("page_type,sector,district,page_slug").eq("page_type", "opportunity").limit(5000),
      sb.from("research_articles").select("title,slug,category,district").eq("status", "published").limit(500),
      sb.from("opportunities").select("title,category,district").limit(500),
      sb.from("collaborator_profiles").select("top_sectors").limit(500),
    ]);

    // Build demand signals per keyword
    const demandMap = {};

    const bump = (key, field, amount = 1, meta = {}) => {
      if (!key || key.trim().length < 3) return;
      const k = key.toLowerCase().trim();
      if (!demandMap[k]) demandMap[k] = { searches: 0, requests: 0, interests: 0, collabs: 0, sector: null, district: null };
      demandMap[k][field] += amount;
      if (meta.sector && !demandMap[k].sector) demandMap[k].sector = meta.sector;
      if (meta.district && !demandMap[k].district) demandMap[k].district = meta.district;
    };

    (searches || []).forEach(({ query, sector, district }) => bump(query, "searches", 1, { sector, district }));
    (requests || []).forEach(({ title, sector, district }) => bump(title, "requests", 1, { sector, district }));
    (collabSectors || []).forEach(({ top_sectors }) => {
      (top_sectors || []).forEach((s) => bump(s, "collabs", 1));
    });
    (interests || []).forEach(({ sector, district }) => {
      if (sector) bump(sector, "interests", 1, { sector, district });
    });

    // Existing content
    const existingArticleTitles = new Set((articles || []).map((a) => a.title.toLowerCase()));
    const existingIdeaTitles = new Set((IDEAS || []).map((i) => (i.title || "").toLowerCase()));
    const existingOppTitles = new Set((opportunities || []).map((o) => o.title.toLowerCase()));

    const hasContent = (kw) => {
      const k = kw.toLowerCase();
      return [...existingArticleTitles, ...existingIdeaTitles, ...existingOppTitles]
        .some((t) => t.includes(k.split(" ")[0]) || k.includes(t.split(" ")[0]));
    };

    // Score and sort
    const scored = Object.entries(demandMap)
      .map(([keyword, v]) => {
        const rawScore = v.searches * 1 + v.requests * 2 + v.interests * 3 + v.collabs * 1;
        const existing = hasContent(keyword);
        const score = Math.min(100, Math.max(0, Math.round(rawScore - (existing ? 20 : 0))));
        return { keyword, score, existing, ...v };
      })
      .filter((r) => r.score > 0)
      .sort((a, b) => b.score - a.score);

    // Categorize
    const researchRecs = scored.filter((r) => !r.existing && (r.sector || r.searches > 3)).slice(0, 8);
    const ideaRecs = scored.filter((r) => r.score >= 30).slice(0, 8);
    const oppRecs = scored.filter((r) => r.interests > 0 || r.requests > 1).slice(0, 8);
    const districtRecs = Object.entries(
      (searches || []).reduce((m, { district }) => {
        if (district) m[district] = (m[district] || 0) + 1;
        return m;
      }, {})
    ).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([district, count]) => ({ district, count }));

    return { researchRecs, ideaRecs, oppRecs, districtRecs, totalSignals: (searches?.length || 0) + (requests?.length || 0) };
  } catch (e) {
    console.error("Recommendations error:", e);
    return { researchRecs: [], ideaRecs: [], oppRecs: [], districtRecs: [], totalSignals: 0 };
  }
}

function RecCard({ item, type }) {
  const isNew = !item.existing;

  return (
    <div className="card-base p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <p className="font-display font-bold text-ink text-sm capitalize">{item.keyword}</p>
          {(item.sector || item.district) && (
            <p className="text-[11px] text-stone-400 mt-0.5 capitalize">
              {[item.sector, item.district].filter(Boolean).join(" · ")}
            </p>
          )}
        </div>
        <PriorityBadge score={item.score} />
      </div>

      {/* Signal breakdown */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {item.searches > 0 && <ReasonTag icon={Search} text={`${item.searches} searches`} color="bg-blue-50 text-blue-600" />}
        {item.requests > 0 && <ReasonTag icon={MessageSquare} text={`${item.requests} requests`} color="bg-purple-50 text-purple-600" />}
        {item.interests > 0 && <ReasonTag icon={Briefcase} text={`${item.interests} interests`} color="bg-amber-50 text-amber-700" />}
        {item.collabs > 0 && <ReasonTag icon={Users} text={`${item.collabs} collabs`} color="bg-teal-50 text-teal-600" />}
        {isNew && <ReasonTag icon={Lightbulb} text="No existing content" color="bg-green-50 text-green-700" />}
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-1.5">
        {type === "research" && (
          <Link
            href={`/admin/research/new?prefill=${encodeURIComponent(item.keyword)}`}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[11px] font-semibold hover:bg-purple-100 transition-colors"
          >
            <FileText size={11} /> Write Article
          </Link>
        )}
        {type === "opportunity" && (
          <Link
            href={`/admin/opportunity-generator?sector=${encodeURIComponent(item.sector || "")}&keyword=${encodeURIComponent(item.keyword)}`}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-[11px] font-semibold hover:bg-amber-100 transition-colors"
          >
            <Zap size={11} /> Generate Opportunity
          </Link>
        )}
        {type === "idea" && (
          <Link
            href={`/admin/content-opportunities`}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200 text-[11px] font-semibold hover:bg-teal-100 transition-colors"
          >
            <Lightbulb size={11} /> View Content Gaps
          </Link>
        )}
      </div>
    </div>
  );
}

export default async function RecommendationsPage() {
  const { researchRecs, ideaRecs, oppRecs, districtRecs, totalSignals } = await fetchRecommendations();

  const EMPTY_MSG = "Recommendations appear automatically as users search, request content, and express interest. No data or configuration required — just user activity.";

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-yellow-100 text-yellow-800 border border-yellow-200">RECOMMENDATIONS</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2 flex items-center gap-2">
            <Star size={22} className="text-amber-500" />
            Content Recommendation Engine
          </h1>
          <p className="text-stone-500 text-sm mt-1">
            Automatically surfaced from {totalSignals} user demand signals — no configuration required
          </p>
        </div>

        {totalSignals === 0 && (
          <div className="card-base p-6 bg-stone-50 text-center">
            <Star size={28} className="text-stone-300 mx-auto mb-3" />
            <p className="text-stone-500 text-sm">{EMPTY_MSG}</p>
          </div>
        )}

        {/* Suggested Research Articles */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <FileText size={16} className="text-purple-500" />
            <h2 className="font-display font-bold text-ink">Suggested Research Articles</h2>
            <Link href="/admin/research/new" className="ml-auto text-[11px] text-amber-600 font-semibold hover:underline flex items-center gap-1">
              New Article <ArrowRight size={11} />
            </Link>
          </div>
          {researchRecs.length === 0 ? (
            <p className="text-sm text-stone-400 italic">{EMPTY_MSG}</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {researchRecs.map((r) => <RecCard key={r.keyword} item={r} type="research" />)}
            </div>
          )}
        </section>

        {/* Suggested Opportunities */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Briefcase size={16} className="text-amber-500" />
            <h2 className="font-display font-bold text-ink">Suggested Opportunities to Generate</h2>
            <Link href="/admin/opportunity-generator" className="ml-auto text-[11px] text-amber-600 font-semibold hover:underline flex items-center gap-1">
              Generator <ArrowRight size={11} />
            </Link>
          </div>
          {oppRecs.length === 0 ? (
            <p className="text-sm text-stone-400 italic">{EMPTY_MSG}</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {oppRecs.map((r) => <RecCard key={r.keyword} item={r} type="opportunity" />)}
            </div>
          )}
        </section>

        {/* Suggested Business Ideas */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb size={16} className="text-teal-500" />
            <h2 className="font-display font-bold text-ink">Suggested Business Ideas to Publish</h2>
          </div>
          {ideaRecs.length === 0 ? (
            <p className="text-sm text-stone-400 italic">{EMPTY_MSG}</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {ideaRecs.map((r) => <RecCard key={r.keyword + "-idea"} item={r} type="idea" />)}
            </div>
          )}
        </section>

        {/* Suggested District Reports */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <MapPin size={16} className="text-blue-500" />
            <h2 className="font-display font-bold text-ink">Districts Needing More Content</h2>
          </div>
          {districtRecs.length === 0 ? (
            <p className="text-sm text-stone-400 italic">{EMPTY_MSG}</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {districtRecs.map(({ district, count }) => (
                <div key={district} className="card-base p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-display font-bold text-ink text-sm capitalize">{district}</span>
                    <span className="chip bg-blue-50 text-blue-700 text-[11px]">{count} searches</span>
                  </div>
                  <div className="flex gap-1.5">
                    <Link
                      href={`/admin/research/new?prefill=${encodeURIComponent(district)}`}
                      className="text-[11px] text-purple-600 hover:underline font-semibold"
                    >
                      Write report
                    </Link>
                    <span className="text-stone-300">·</span>
                    <Link href={`/district/${district.toLowerCase().replace(/\s+/g, "-")}`} className="text-[11px] text-stone-400 hover:underline">
                      View page
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

      </div>
    </AdminShell>
  );
}
