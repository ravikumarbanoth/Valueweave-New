"use client";

import Link from "next/link";
import { ArticleCard } from "@/components/research/ArticleCard";
import { useLanguage } from "@/lib/language";

export default function HomeResearchArticlesClient({ articles }) {
  const { t } = useLanguage();

  return (
    <section data-testid="home-research-articles" className="py-20 sm:py-24 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <span className="chip bg-amber-100 text-amber-700 mb-4">{t("home.research_chip", "RESEARCH")}</span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl tracking-tight leading-tight text-ink">
            {t("home.research_title", "Latest Research Articles")}
          </h2>
          <p className="mt-4 text-muted max-w-2xl mx-auto text-base sm:text-lg leading-relaxed">
            {t(
              "home.research_subtitle",
              "Explore practical research, emerging business opportunities, industry insights and ideas that can help you build your future."
            )}
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <ArticleCard key={article.slug} article={article} />
          ))}
        </div>

        <div className="text-center mt-10">
          <Link href="/research" data-testid="home-research-explore-all" className="btn-primary">
            {t("home.research_explore_all", "Explore All Research →")}
          </Link>
        </div>
      </div>
    </section>
  );
}
