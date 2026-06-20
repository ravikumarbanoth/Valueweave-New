// Research article card — existing ValueWeave theme. Uses a gradient header
// (category emoji) instead of cover images so no image assets are required.

import Link from "next/link";
import { CategoryBadge, InvestmentBadge } from "@/components/ui/index";

const CATEGORY_EMOJI = {
  agriculture: "🌾",
  healthcare: "🏥",
  technology: "💻",
  manufacturing: "🏭",
  energy: "⚡",
  retail: "🏪",
  education: "🎓",
  logistics: "🚚",
  "food-processing": "🥫",
  handicrafts: "🧵",
};

const CATEGORY_GRADIENT = {
  agriculture: "from-emerald-100 to-teal-50",
  healthcare: "from-rose-100 to-amber-50",
  technology: "from-blue-100 to-teal-50",
  energy: "from-amber-100 to-yellow-50",
  manufacturing: "from-stone-200 to-amber-50",
  retail: "from-violet-100 to-amber-50",
  education: "from-sky-100 to-teal-50",
  logistics: "from-orange-100 to-amber-50",
  "food-processing": "from-red-100 to-amber-50",
  handicrafts: "from-pink-100 to-amber-50",
};

export function ArticleCard({ article, featured }) {
  return (
    <Link
      href={`/research/${article.slug}`}
      data-testid={`research-card-${article.slug}`}
      className={`group flex flex-col card-base overflow-hidden hover:border-amber-400 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 ${
        featured ? "md:flex-row" : ""
      }`}
    >
      {/* Cover image when provided, themed gradient otherwise */}
      <div
        className={`relative flex items-center justify-center overflow-hidden bg-gradient-to-br ${
          CATEGORY_GRADIENT[article.category] || "from-amber-100 to-teal-50"
        } ${featured ? "md:w-2/5 min-h-[180px]" : "h-36"}`}
      >
        {article.coverImage ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={article.coverImage} alt="" className="absolute inset-0 w-full h-full object-cover" />
        ) : (
          <span className={featured ? "text-7xl" : "text-5xl"}>
            {CATEGORY_EMOJI[article.category] || "📊"}
          </span>
        )}
        <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
          <CategoryBadge category={article.category} />
          {article.video && <span className="chip bg-white/90 text-ink shadow-sm">▶ Video Available</span>}
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-col flex-1 p-5">
        {article.districtTags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {article.districtTags.slice(0, 3).map((d) => (
              <span key={d} className="text-xs font-medium text-muted bg-stone-100 px-2 py-0.5 rounded-full capitalize">
                {d.replace(/-/g, " ")}
              </span>
            ))}
          </div>
        )}

        <h3
          className={`font-display font-bold text-ink leading-snug group-hover:text-amber-700 transition-colors ${
            featured ? "text-xl md:text-2xl mb-3" : "text-base mb-2"
          }`}
        >
          {article.title}
        </h3>

        <p className="text-sm text-muted line-clamp-2 mb-4 flex-1">{article.metaDescription}</p>

        <div className="flex items-center justify-between pt-3 border-t border-stone-100">
          {article.investmentRange?.label
            ? <InvestmentBadge label={article.investmentRange.label} />
            : <span className="text-xs text-stone-400">{article.author || "ValueWeave Research"}</span>}
          <span className="text-xs text-stone-400">{article.readingTime} min read</span>
        </div>
      </div>
    </Link>
  );
}
