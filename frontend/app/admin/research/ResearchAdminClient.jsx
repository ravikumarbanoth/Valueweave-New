"use client";
// Admin Research Publisher — article list with search, filters, counts,
// and publish/unpublish/delete actions. Database articles are editable;
// legacy MDX files are listed read-only below.

import { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase-browser";
import { CATEGORY_LABELS } from "@/lib/theme";
import { isValidYouTubeUrl } from "@/lib/youtube";

const STATUS_FILTERS = [
  { id: "", label: "All" },
  { id: "published", label: "Published" },
  { id: "draft", label: "Drafts" },
];

export default function ResearchAdminClient({ mdxArticles }) {
  const supabase = createClient();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setErr("");
    const { data, error } = await supabase
      .from("research_articles")
      .select("id, title, slug, excerpt, category, district, status, published_at, updated_at, youtube_url, video_title, video_view_count")
      .order("updated_at", { ascending: false });
    if (error) setErr(`Could not load articles: ${error.message}`);
    setArticles(data || []);
    setLoading(false);
  }, [supabase]);

  useEffect(() => { load(); }, [load]);

  const counts = useMemo(() => ({
    published: articles.filter((a) => a.status === "published").length,
    draft: articles.filter((a) => a.status === "draft").length,
    video: articles.filter((a) => isValidYouTubeUrl(a.youtube_url)).length,
  }), [articles]);

  const filtered = useMemo(() => {
    return articles.filter((a) => {
      if (status && a.status !== status) return false;
      if (category && (a.category || "").toLowerCase() !== category.toLowerCase()) return false;
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          (a.title || "").toLowerCase().includes(q) ||
          (a.slug || "").toLowerCase().includes(q) ||
          (a.district || "").toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [articles, search, category, status]);

  const usedCategories = useMemo(
    () => [...new Set(articles.map((a) => a.category).filter(Boolean))].sort(),
    [articles]
  );

  async function setArticleStatus(article, newStatus) {
    setBusyId(article.id);
    const patch = newStatus === "published"
      ? { status: "published", published_at: article.published_at || new Date().toISOString() }
      : { status: "draft" };
    const { error } = await supabase.from("research_articles").update(patch).eq("id", article.id);
    if (error) setErr(`Update failed: ${error.message}`);
    else await load();
    setBusyId(null);
  }

  async function deleteArticle(article) {
    if (!window.confirm(`Delete "${article.title}" permanently? This cannot be undone.`)) return;
    setBusyId(article.id);
    const { error } = await supabase.from("research_articles").delete().eq("id", article.id);
    if (error) setErr(`Delete failed: ${error.message}`);
    else await load();
    setBusyId(null);
  }

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 py-10 pb-20">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <span className="chip bg-amber-100 text-amber-700 mb-3">ADMIN · RESEARCH PUBLISHER</span>
          <h1 data-testid="admin-research-title" className="font-display font-extrabold tracking-tight text-3xl">
            Research Articles
          </h1>
          <p className="text-muted text-sm mt-1">
            Create, edit, and publish directly from the browser. Published articles go live on /research immediately.
          </p>
        </div>
        <Link href="/admin/research/new" data-testid="admin-new-article" className="btn-primary">
          + New Article
        </Link>
      </div>

      {/* Counts */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="card-base p-4">
          <p className="text-xs text-muted uppercase tracking-wider mb-1">Published</p>
          <p data-testid="admin-count-published" className="font-display font-extrabold text-2xl text-teal-600">{counts.published}</p>
        </div>
        <div className="card-base p-4">
          <p className="text-xs text-muted uppercase tracking-wider mb-1">Drafts</p>
          <p data-testid="admin-count-draft" className="font-display font-extrabold text-2xl text-amber-600">{counts.draft}</p>
        </div>
        <div className="card-base p-4">
          <p className="text-xs text-muted uppercase tracking-wider mb-1">Video Present?</p>
          <p className="font-display font-extrabold text-2xl text-blue-600">{counts.video}</p>
        </div>
        <div className="card-base p-4">
          <p className="text-xs text-muted uppercase tracking-wider mb-1">Legacy MDX files</p>
          <p className="font-display font-extrabold text-2xl text-stone-500">{mdxArticles.length}</p>
        </div>
      </div>

      {err && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mb-4">
          {err}
        </div>
      )}

      {/* Filters */}
      <div className="card-base p-3 sm:p-4 mb-5">
        <input
          data-testid="admin-search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by title, slug, or district…"
          className="input-field mb-3"
        />
        <div className="flex flex-wrap items-center gap-2">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s.id}
              onClick={() => setStatus(s.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-display font-semibold transition-colors ${
                status === s.id ? "bg-ink text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200"
              }`}
            >
              {s.label}
            </button>
          ))}
          <span className="w-px h-5 bg-stone-200 mx-1" />
          <select
            data-testid="admin-category-filter"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-lg border border-stone-200 bg-white px-2.5 py-1.5 text-xs font-display font-semibold text-ink outline-none focus:border-amber-500"
          >
            <option value="">All categories</option>
            {usedCategories.map((c) => (
              <option key={c} value={c}>{CATEGORY_LABELS[c] || c}</option>
            ))}
          </select>
          <span className="text-xs text-muted ml-auto">{filtered.length} shown</span>
        </div>
      </div>

      {/* DB article list */}
      <div className="card-base overflow-hidden mb-10">
        {loading ? (
          <div className="p-6 flex flex-col gap-3">
            {[1, 2, 3].map((i) => <div key={i} className="skeleton h-12 w-full" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center">
            <div className="text-4xl mb-3">📝</div>
            <p className="text-muted text-sm mb-4">
              {articles.length === 0
                ? "No database articles yet. Write your first one in the browser."
                : "Nothing matches your filters."}
            </p>
            {articles.length === 0 && (
              <Link href="/admin/research/new" className="btn-primary">Write your first article</Link>
            )}
          </div>
        ) : (
          filtered.map((a) => {
            const validVideo = isValidYouTubeUrl(a.youtube_url);
            return (
              <div key={a.id} data-testid={`admin-article-${a.slug}`} className="px-5 py-4 border-b border-stone-100 last:border-0 flex flex-wrap items-center gap-3">
                <div className="flex-1 min-w-[220px]">
                  <Link href={`/admin/research/${a.id}`} className="font-display font-bold text-sm text-ink hover:text-amber-700">
                    {a.title || "(untitled)"}
                  </Link>
                  <p className="text-xs text-muted mt-0.5">
                    /research/{a.slug} · {a.district || "no district"} · updated {new Date(a.updated_at).toLocaleDateString("en-IN")}
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    <span className={`chip ${validVideo ? "bg-blue-50 text-blue-700" : "bg-stone-100 text-stone-500"}`}>
                      {validVideo ? "▶ Video Present" : "No video"}
                    </span>
                    <span className={`chip ${!a.youtube_url || validVideo ? "bg-teal-50 text-teal-700" : "bg-red-50 text-red-700"}`}>
                      Embed {a.youtube_url ? (validVideo ? "valid" : "invalid") : "not set"}
                    </span>
                    <span className="chip bg-stone-50 text-stone-500">Video views: {a.video_view_count || 0}</span>
                  </div>
                </div>
                <span className={`chip ${a.status === "published" ? "bg-teal-100 text-teal-700" : "bg-amber-100 text-amber-700"}`}>
                  {a.status}
                </span>
                <div className="flex items-center gap-1.5">
                  <Link href={`/admin/research/${a.id}`} className="btn-ghost !px-3 !py-1.5 text-xs border border-stone-200">
                    Edit
                  </Link>
                  {a.status === "published" ? (
                    <>
                      <Link href={`/research/${a.slug}`} target="_blank" className="btn-ghost !px-3 !py-1.5 text-xs border border-stone-200">
                        View
                      </Link>
                      <button
                        disabled={busyId === a.id}
                        onClick={() => setArticleStatus(a, "draft")}
                        className="btn-ghost !px-3 !py-1.5 text-xs border border-stone-200 disabled:opacity-50"
                      >
                        Unpublish
                      </button>
                    </>
                  ) : (
                    <button
                      disabled={busyId === a.id}
                      onClick={() => setArticleStatus(a, "published")}
                      className="text-xs font-display font-bold px-3 py-1.5 rounded-full bg-teal-500 hover:bg-teal-600 text-white transition-colors disabled:opacity-50"
                    >
                      Publish
                    </button>
                  )}
                  <button
                    disabled={busyId === a.id}
                    onClick={() => deleteArticle(a)}
                    className="text-xs font-display font-semibold px-3 py-1.5 rounded-full text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Legacy MDX section */}
      {mdxArticles.length > 0 && (
        <div className="card-base overflow-hidden">
          <div className="px-5 py-3 border-b border-stone-100 bg-stone-50">
            <span className="font-display font-bold text-sm">Legacy file-based articles (MDX)</span>
            <p className="text-xs text-muted mt-0.5">
              Managed via content/research/*.mdx in the repo. Still served on /research —
              a database article with the same slug takes priority.
            </p>
          </div>
          {mdxArticles.map((a) => (
            <div key={a.slug} className="px-5 py-3 border-b border-stone-100 last:border-0 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <Link href={`/research/${a.slug}`} target="_blank" className="font-display font-semibold text-sm text-ink hover:text-amber-700">
                  {a.title}
                </Link>
                <p className="text-xs text-muted">/research/{a.slug}</p>
              </div>
              <span className={`chip ${a.published ? "bg-teal-50 text-teal-700" : "bg-stone-100 text-stone-500"}`}>
                {a.published ? "Published" : "Draft"} · file
              </span>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
