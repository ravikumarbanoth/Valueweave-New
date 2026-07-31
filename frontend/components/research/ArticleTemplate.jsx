"use client";
// Research article layout. The MDX body is rendered server-side (RSC) and
// passed in via the `mdx` prop so this client component (FAQ accordion)
// never needs the raw source.

import Link from "next/link";
import { useState } from "react";
import { Breadcrumb, CategoryBadge } from "@/components/ui/index";
import { ArticleCard } from "./ArticleCard";
import SnapshotPanel from "@/components/geo/SnapshotPanel";
import ResearchVideoEmbed from "@/components/research/ResearchVideoEmbed";

export function ArticleTemplate({ article, relatedLinks, relatedArticles, mdx }) {
  const [openFaq, setOpenFaq] = useState(null);
  const districtRelevance = article.districtTags.length > 0
    ? article.districtTags.map((d) => d.replace(/-/g, " "))
    : "Relevant for district-first and local business readers";

  return (
    <main className="min-h-screen bg-cream font-body pb-16">
      {/* ── Hero ── */}
      <div className="relative overflow-hidden bg-ink">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-amber-500/20 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-teal-500/20 blur-3xl" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 pt-12 pb-10">
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            <CategoryBadge category={article.category} />
            {article.video && <span className="chip bg-white/15 text-white border border-white/20">▶ Video Available</span>}
            {article.investmentRange?.label && (
              <span className="chip bg-white/15 text-white border border-white/20">{article.investmentRange.label}</span>
            )}
            {article.stateTags.map((s) => (
              <span key={s} className="chip bg-white/10 text-white/80 border border-white/15 capitalize">{s}</span>
            ))}
          </div>
          <h1 data-testid="research-title" className="font-display font-extrabold tracking-tight text-2xl sm:text-3xl md:text-4xl text-white leading-tight">
            {article.title}
          </h1>
          <p className="text-white/60 text-sm mt-4">
            {article.readingTime} min read · Updated{" "}
            {new Date(article.updatedAt).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
            {" · "}{article.author}
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <Breadcrumb
            items={[
              { label: "Home", href: "/" },
              { label: "Research", href: "/research" },
              { label: article.title },
            ]}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-10">
          {/* ── Main content ── */}
          <article>
            {article.coverImage && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={article.coverImage}
                alt={article.title}
                className="w-full max-h-96 object-cover rounded-2xl border border-stone-200 mb-8"
              />
            )}

            <SnapshotPanel
              title="Research Snapshot"
              items={{
                "Key Takeaways": article.metaDescription,
                "Who should read this": `Entrepreneurs, students, local operators, and collaborators exploring ${article.sector || article.category}.`,
                "Investment Range": article.investmentRange?.label || "Varies by execution",
                "District Relevance": districtRelevance,
                "Business Potential": `Useful for validating ${article.category} opportunities and local demand signals.`,
              }}
              faq={article.faq}
            />

            <ResearchVideoEmbed
              url={article.video?.youtubeUrl}
              title={article.video?.title}
              description={article.video?.description}
            />

            <div>{mdx}</div>

            {/* District Suitability Chips */}
            {article.districtTags.length > 0 && (
              <div className="mt-10 p-5 bg-teal-50 border border-teal-200 rounded-2xl">
                <p className="text-sm font-display font-bold text-teal-700 mb-3 uppercase tracking-wider">
                  Most Suitable Districts
                </p>
                <div className="flex flex-wrap gap-2">
                  {article.districtTags.map((d) => (
                    <Link
                      key={d}
                      href={`/district/${d.toLowerCase().replace(/\s+/g, "-")}`}
                      className="px-3 py-1.5 bg-white text-teal-700 border border-teal-200 rounded-full text-sm font-display font-semibold hover:bg-teal-600 hover:text-white hover:border-teal-600 transition-colors capitalize"
                    >
                      {d.replace(/-/g, " ")}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* FAQ */}
            {article.faq.length > 0 && (
              <section className="mt-12">
                <h2 className="font-display font-extrabold tracking-tight text-2xl text-ink mb-6">
                  Frequently Asked Questions
                </h2>
                <div className="space-y-3">
                  {article.faq.map((faq, i) => (
                    <div key={i} className="card-base overflow-hidden">
                      <button
                        onClick={() => setOpenFaq(openFaq === i ? null : i)}
                        className="w-full flex items-center justify-between gap-3 px-5 py-4 text-left"
                      >
                        <span className="font-display font-bold text-ink text-sm">{faq.question}</span>
                        <span className={`text-amber-500 transition-transform shrink-0 ${openFaq === i ? "rotate-180" : ""}`}>▼</span>
                      </button>
                      {openFaq === i && (
                        <div className="px-5 pb-4 text-sm text-muted leading-relaxed border-t border-stone-100 pt-3">
                          {faq.answer}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </article>

          {/* ── Sidebar ── */}
          <aside className="space-y-6">
            <div className="card-base p-5 lg:sticky lg:top-20">
              <p className="text-sm font-display font-bold text-muted mb-4 uppercase tracking-wider">Quick Snapshot</p>
              <div className="space-y-1">
                {article.investmentRange?.label && (
                  <div className="flex justify-between items-center py-2 border-b border-stone-100">
                    <span className="text-sm text-muted">Investment</span>
                    <span className="text-sm font-display font-bold text-amber-700">{article.investmentRange.label}</span>
                  </div>
                )}
                <div className="flex justify-between items-center py-2 border-b border-stone-100">
                  <span className="text-sm text-muted">Sector</span>
                  <span className="text-sm font-display font-bold text-ink capitalize">{article.sector}</span>
                </div>
                {article.video && (
                  <div className="flex justify-between items-center py-2 border-b border-stone-100">
                    <span className="text-sm text-muted">Video</span>
                    <span className="text-sm font-display font-bold text-teal-700">Available</span>
                  </div>
                )}
                <div className="flex justify-between items-center py-2">
                  <span className="text-sm text-muted">Reading time</span>
                  <span className="text-sm font-display font-bold text-ink">{article.readingTime} min</span>
                </div>
              </div>

              <div className="mt-5 space-y-2">
                <Link href="/explore" className="btn-primary w-full !py-2.5 text-sm">Explore Opportunities</Link>
                <Link href="/opportunity-radar" className="btn-secondary w-full !py-2.5 text-sm">View Opportunity Radar</Link>
              </div>
            </div>

            {relatedLinks.length > 0 && (
              <div className="card-base p-5">
                <p className="text-sm font-display font-bold text-muted mb-4 uppercase tracking-wider">Explore Further</p>
                <div className="space-y-2">
                  {relatedLinks.slice(0, 6).map((link) => (
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

        {/* Related Articles */}
        {relatedArticles.length > 0 && (
          <section className="mt-16">
            <h2 className="font-display font-extrabold tracking-tight text-2xl text-ink mb-6">Related Research</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {relatedArticles.map((a) => (
                <ArticleCard key={a.slug} article={a} />
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
