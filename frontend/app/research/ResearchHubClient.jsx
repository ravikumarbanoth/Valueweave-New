"use client";
// Research hub — search + category filter + pagination over the
// admin-published MDX articles. Existing ValueWeave theme.

import { useState, useMemo } from "react";
import { ArticleCard } from "@/components/research/ArticleCard";
import { EmptyState } from "@/components/ui/index";
import { CATEGORY_LABELS } from "@/lib/theme";

const PER_PAGE = 12;
const CATEGORIES = Object.entries(CATEGORY_LABELS);

export function ResearchHubClient({ articles }) {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [page, setPage] = useState(1);

  // Only show category chips that actually have articles, plus "All".
  const activeCategories = useMemo(() => {
    const used = new Set(articles.map((a) => a.category));
    return CATEGORIES.filter(([key]) => used.has(key));
  }, [articles]);

  const filtered = useMemo(() => {
    let results = articles;
    if (selectedCategory !== "all") {
      results = results.filter((a) => a.category === selectedCategory);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      results = results.filter(
        (a) =>
          a.title.toLowerCase().includes(q) ||
          a.metaDescription.toLowerCase().includes(q) ||
          a.sector.toLowerCase().includes(q) ||
          a.districtTags.some((d) => d.toLowerCase().includes(q)) ||
          a.stateTags.some((s) => s.toLowerCase().includes(q))
      );
    }
    return results;
  }, [articles, search, selectedCategory]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const paginated = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE);
  const showFeatured = page === 1 && !search && selectedCategory === "all";
  const featured = showFeatured ? paginated[0] : null;
  const gridArticles = showFeatured ? paginated.slice(1) : paginated;

  return (
    <main>
      {/* ── Hero ── */}
      <section className="relative overflow-hidden bg-ink px-4 sm:px-6 py-16">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
        <div className="relative max-w-5xl mx-auto text-center">
          <span className="chip bg-amber-500/20 text-amber-300 border border-amber-500/30 mb-4">
            VALUEWEAVE RESEARCH HUB
          </span>
          <h1 data-testid="research-hub-title" className="font-display font-extrabold tracking-tight text-3xl sm:text-4xl md:text-5xl text-white leading-tight mb-4">
            Opportunity Research<br className="hidden md:block" /> for Bharat&apos;s Builders
          </h1>
          <p className="text-white/60 text-base sm:text-lg max-w-2xl mx-auto mb-8">
            Market analysis, investment guides, and district-level insights to help you start, plan, and grow the right business.
          </p>
          <div className="max-w-xl mx-auto">
            <input
              type="text"
              data-testid="research-search"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search by sector, district, or keyword…"
              className="w-full bg-white rounded-full px-6 py-3.5 text-ink placeholder-stone-400 shadow-lg focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm"
            />
          </div>
        </div>
      </section>

      {/* ── Category Filters ── */}
      <section className="sticky top-16 z-30 bg-cream/95 backdrop-blur-md border-b border-stone-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-2 overflow-x-auto">
          {[["all", "All"], ...activeCategories].map(([key, label]) => (
            <button
              key={key}
              data-testid={`research-cat-${key}`}
              onClick={() => { setSelectedCategory(key); setPage(1); }}
              className={`shrink-0 px-4 py-1.5 rounded-full text-xs font-display font-semibold transition-colors min-h-[32px] ${
                selectedCategory === key
                  ? "bg-ink text-white"
                  : "bg-stone-100 text-stone-600 hover:bg-stone-200"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      {/* ── Articles ── */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10 pb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-display font-extrabold tracking-tight text-xl sm:text-2xl text-ink">
            {search
              ? `"${search}" — ${filtered.length} result${filtered.length !== 1 ? "s" : ""}`
              : selectedCategory !== "all"
              ? `${CATEGORY_LABELS[selectedCategory]} Research`
              : "Latest Research"}
          </h2>
          <span data-testid="research-count" className="text-xs font-display font-semibold text-muted hidden md:block">
            {filtered.length} article{filtered.length !== 1 ? "s" : ""}
          </span>
        </div>

        {paginated.length === 0 ? (
          <EmptyState
            title="No articles found"
            description="Try a different keyword, district, or category."
            action={
              <button onClick={() => { setSearch(""); setSelectedCategory("all"); setPage(1); }} className="btn-secondary">
                Clear filters
              </button>
            }
          />
        ) : (
          <>
            {featured && (
              <div className="mb-8">
                <ArticleCard article={featured} featured />
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {gridArticles.map((article) => (
                <ArticleCard key={article.slug} article={article} />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-12">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 rounded-full border-2 border-stone-200 text-sm font-display font-semibold text-stone-600 hover:border-amber-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  ← Prev
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`w-9 h-9 rounded-full text-sm font-display font-bold transition-colors ${
                      p === page ? "bg-ink text-white" : "border-2 border-stone-200 text-stone-600 hover:border-amber-400"
                    }`}
                  >
                    {p}
                  </button>
                ))}
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 rounded-full border-2 border-stone-200 text-sm font-display font-semibold text-stone-600 hover:border-amber-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}
