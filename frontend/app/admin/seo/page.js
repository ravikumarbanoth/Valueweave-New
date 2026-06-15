import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-server";
import { DISTRICTS } from "@/lib/districts-data";
import IDEAS from "@/lib/idea-library/ideas.json";
import { SearchCheck, CheckCircle, AlertCircle, XCircle, Link2, FileText, Map, Briefcase, Lightbulb } from "lucide-react";

export const dynamic = "force-dynamic";
export const metadata = {
  title: "SEO Command Center | ValueWeave Admin",
  robots: { index: false, follow: false },
};

function StatusIcon({ status }) {
  if (status === "ok") return <CheckCircle size={14} className="text-green-500 shrink-0" />;
  if (status === "warn") return <AlertCircle size={14} className="text-amber-500 shrink-0" />;
  return <XCircle size={14} className="text-red-500 shrink-0" />;
}

function ScoreRing({ score }) {
  const color = score >= 80 ? "text-green-600" : score >= 60 ? "text-amber-600" : "text-red-500";
  const bg = score >= 80 ? "bg-green-50" : score >= 60 ? "bg-amber-50" : "bg-red-50";
  return (
    <div className={`flex flex-col items-center justify-center w-28 h-28 rounded-full border-4 ${score >= 80 ? "border-green-200" : score >= 60 ? "border-amber-200" : "border-red-200"} ${bg}`}>
      <span className={`text-3xl font-display font-extrabold ${color}`}>{score}</span>
      <span className="text-[10px] text-stone-500 font-semibold uppercase tracking-wide">SEO Score</span>
    </div>
  );
}

async function fetchSEOData() {
  try {
    const sb = createClient();
    const [
      { data: articles, count: articleCount },
      { data: opportunities, count: oppCount },
    ] = await Promise.all([
      sb.from("research_articles")
        .select("id,title,slug,seo_title,seo_description,keywords,cover_image,status")
        .order("created_at", { ascending: false })
        .limit(500),
      sb.from("opportunities")
        .select("id,title,description,category,district")
        .limit(500),
    ]);

    const publishedArticles = (articles || []).filter((a) => a.status === "published");
    const totalResearchURLs = publishedArticles.length;
    const totalDistrictURLs = DISTRICTS.length;
    const totalIdeaURLs = (IDEAS || []).length;
    const totalOppURLs = (opportunities || []).length;
    const totalURLs = totalResearchURLs + totalDistrictURLs + totalIdeaURLs + totalOppURLs;

    // SEO completeness for articles
    let articlesMissingTitle = 0;
    let articlesMissingDesc = 0;
    let articlesMissingKeywords = 0;
    let articlesMissingImage = 0;

    publishedArticles.forEach((a) => {
      if (!a.seo_title && !a.title) articlesMissingTitle++;
      if (!a.seo_description) articlesMissingDesc++;
      if (!a.keywords || a.keywords.length === 0) articlesMissingKeywords++;
      if (!a.cover_image) articlesMissingImage++;
    });

    const articlesFullySEO = publishedArticles.filter(
      (a) => a.seo_title && a.seo_description && a.keywords?.length > 0
    ).length;

    const metadataScore = totalResearchURLs > 0
      ? Math.round((articlesFullySEO / totalResearchURLs) * 100)
      : 100;

    // Opportunities missing description
    const oppsMissingDesc = (opportunities || []).filter((o) => !o.description || o.description.length < 50).length;
    const contentScore = totalOppURLs > 0
      ? Math.round(((totalOppURLs - oppsMissingDesc) / totalOppURLs) * 100)
      : 100;

    // Overall SEO score (weighted)
    const seoScore = Math.round((metadataScore * 0.5 + contentScore * 0.3 + (totalURLs > 0 ? 80 : 50) * 0.2));

    // Per-article SEO scores
    const articleSEO = publishedArticles.slice(0, 20).map((a) => {
      let score = 0;
      if (a.seo_title || a.title) score += 25;
      if (a.seo_description) score += 30;
      if (a.keywords?.length > 0) score += 25;
      if (a.cover_image) score += 20;
      return { title: a.seo_title || a.title, slug: a.slug, score };
    });

    // Recommendations
    const recommendations = [];
    if (articlesMissingDesc > 0) recommendations.push({ severity: "error", text: `${articlesMissingDesc} published articles missing meta description — add via Research Publisher` });
    if (articlesMissingKeywords > 0) recommendations.push({ severity: "warn", text: `${articlesMissingKeywords} articles missing keywords — impacts long-tail ranking` });
    if (articlesMissingTitle > 0) recommendations.push({ severity: "error", text: `${articlesMissingTitle} articles missing SEO title — Google uses page title as fallback` });
    if (articlesMissingImage > 0) recommendations.push({ severity: "warn", text: `${articlesMissingImage} articles missing cover image — reduces social sharing CTR` });
    if (oppsMissingDesc > 0) recommendations.push({ severity: "warn", text: `${oppsMissingDesc} opportunities have short/missing descriptions — affects indexability` });
    if (recommendations.length === 0) recommendations.push({ severity: "ok", text: "All content has complete SEO metadata. Great work!" });

    return {
      totalURLs,
      totalResearchURLs,
      totalDistrictURLs,
      totalIdeaURLs,
      totalOppURLs,
      totalSitemapURLs: totalURLs + 5, // +5 for static pages
      seoScore,
      metadataScore,
      contentScore,
      articlesMissingTitle,
      articlesMissingDesc,
      articlesMissingKeywords,
      articlesMissingImage,
      oppsMissingDesc,
      articleSEO,
      recommendations,
    };
  } catch (e) {
    console.error("SEO fetch error:", e);
    return {
      totalURLs: 0, totalResearchURLs: 0, totalDistrictURLs: 0, totalIdeaURLs: 0, totalOppURLs: 0,
      totalSitemapURLs: 0, seoScore: 0, metadataScore: 0, contentScore: 0,
      articlesMissingTitle: 0, articlesMissingDesc: 0, articlesMissingKeywords: 0, articlesMissingImage: 0,
      oppsMissingDesc: 0, articleSEO: [], recommendations: [],
    };
  }
}

function StatBox({ label, value, icon: Icon, color = "stone" }) {
  const bg = { stone: "bg-stone-50", amber: "bg-amber-50", teal: "bg-teal-50", blue: "bg-blue-50", purple: "bg-purple-50" };
  const text = { stone: "text-stone-700", amber: "text-amber-700", teal: "text-teal-700", blue: "text-blue-700", purple: "text-purple-700" };
  return (
    <div className={`${bg[color]} rounded-xl p-4 flex items-center gap-3`}>
      <Icon size={18} className={text[color]} />
      <div>
        <div className="text-xl font-display font-extrabold text-ink">{value}</div>
        <div className="text-[11px] text-stone-500 font-medium">{label}</div>
      </div>
    </div>
  );
}

export default async function SEOPage() {
  const d = await fetchSEOData();

  return (
    <AdminShell>
      <div className="p-6 max-w-6xl space-y-8">

        {/* Header */}
        <div>
          <span className="chip bg-green-100 text-green-700 border border-green-200">SEO COMMAND CENTER</span>
          <h1 className="font-display font-extrabold text-2xl text-ink mt-2">SEO Command Center</h1>
          <p className="text-stone-500 text-sm mt-1">
            Content indexability, metadata completeness, and SEO health across all ValueWeave URLs.
          </p>
        </div>

        {/* Score + URL Counts */}
        <div className="flex flex-col sm:flex-row gap-6">
          <div className="flex flex-col items-center gap-3">
            <ScoreRing score={d.seoScore} />
            <div className="flex gap-3 text-center">
              <div>
                <div className="text-sm font-bold text-ink">{d.metadataScore}%</div>
                <div className="text-[10px] text-stone-400">Metadata</div>
              </div>
              <div>
                <div className="text-sm font-bold text-ink">{d.contentScore}%</div>
                <div className="text-[10px] text-stone-400">Content</div>
              </div>
            </div>
          </div>
          <div className="flex-1 grid grid-cols-2 sm:grid-cols-3 gap-3">
            <StatBox label="Total URLs" value={d.totalURLs} icon={Link2} color="stone" />
            <StatBox label="Research URLs" value={d.totalResearchURLs} icon={FileText} color="purple" />
            <StatBox label="District URLs" value={d.totalDistrictURLs} icon={Map} color="teal" />
            <StatBox label="Opportunity URLs" value={d.totalOppURLs} icon={Briefcase} color="amber" />
            <StatBox label="Idea URLs" value={d.totalIdeaURLs} icon={Lightbulb} color="blue" />
            <StatBox label="Sitemap URLs" value={d.totalSitemapURLs} icon={SearchCheck} color="stone" />
          </div>
        </div>

        {/* Issues at a Glance */}
        <div className="card-base p-5">
          <h3 className="font-display font-bold text-ink text-sm mb-4 flex items-center gap-2">
            <SearchCheck size={15} className="text-green-500" /> Issues at a Glance
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: "Missing SEO Title", value: d.articlesMissingTitle, severity: d.articlesMissingTitle > 0 ? "error" : "ok" },
              { label: "Missing Meta Desc", value: d.articlesMissingDesc, severity: d.articlesMissingDesc > 0 ? "error" : "ok" },
              { label: "Missing Keywords", value: d.articlesMissingKeywords, severity: d.articlesMissingKeywords > 0 ? "warn" : "ok" },
              { label: "Missing Cover Image", value: d.articlesMissingImage, severity: d.articlesMissingImage > 0 ? "warn" : "ok" },
            ].map(({ label, value, severity }) => (
              <div key={label} className="text-center">
                <div className={`text-2xl font-display font-extrabold ${severity === "error" ? "text-red-500" : severity === "warn" ? "text-amber-500" : "text-green-500"}`}>
                  {value}
                </div>
                <div className="text-[11px] text-stone-500 mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="card-base p-5">
          <h3 className="font-display font-bold text-ink text-sm mb-4">Recommendations</h3>
          <ul className="space-y-3">
            {d.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-3">
                <StatusIcon status={r.severity} />
                <p className="text-[13px] text-stone-700">{r.text}</p>
              </li>
            ))}
          </ul>
        </div>

        {/* Per-Article SEO Scores */}
        {d.articleSEO.length > 0 && (
          <div className="card-base p-5">
            <h3 className="font-display font-bold text-ink text-sm mb-4">Per-Article SEO Scores (Published)</h3>
            <div className="space-y-2.5">
              {d.articleSEO.map((a, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] text-stone-700 font-medium truncate">{a.title}</p>
                  </div>
                  <div className="flex-1 bg-stone-100 rounded-full h-4 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${a.score >= 80 ? "bg-green-400" : a.score >= 60 ? "bg-amber-400" : "bg-red-400"}`}
                      style={{ width: `${a.score}%` }}
                    />
                  </div>
                  <div className="w-10 text-[12px] font-bold text-right shrink-0 text-stone-700">{a.score}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AdminShell>
  );
}
