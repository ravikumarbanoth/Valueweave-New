"use client";
import Link from "next/link";
import ConfidenceBadge from "@/components/knowledge/ConfidenceBadge";
import { useLanguage } from "@/lib/language";

function isArticle(row) {
  return row.entity_type === "ResearchArticle";
}

export default function GroupedResults({ groups, total, query, resolved, analysis }) {
  const { t } = useLanguage();

  return (
    <div className="flex flex-col gap-6" data-testid="search-results">
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <p className="text-[13px] text-muted" data-testid="search-count">
            {total} {total === 1 ? t("search.result_one", "result") : t("search.result_many", "results")} {t("search.for", "for")} “{query}”
          </p>
          {resolved && (
            <p className="text-[12px] text-stone-500" data-testid="search-resolved">
              {t("search.understood_as", "Understood as")} <span className="font-display font-bold text-ink">{resolved}</span>
            </p>
          )}
        </div>
        {analysis?.intent && analysis.intent !== "unknown" && (
          <div className="text-[12px] text-stone-500" data-testid="search-intent">
            {t("search.detected_intent", "Detected intent:")} <span className="font-display font-bold text-ink">{analysis.intentLabel}</span>.
            {analysis.gaps?.length > 0 && (
              <span> We have no {analysis.gaps.join(" and ")} for this query yet.</span>
            )}
          </div>
        )}
      </div>

      {groups.map((group) => (
        <section key={group.id} data-testid="search-group" data-group={group.id}>
          <div className="flex items-baseline justify-between gap-3 mb-2">
            <h2 className="font-display font-bold text-ink text-[15px]">{group.label}</h2>
            {group.total > group.items.length && (
              <span className="text-[11px] text-muted">
                {t("search.showing", "showing")} {group.items.length} {t("search.of", "of")} {group.total}
              </span>
            )}
          </div>

          <ul className="grid gap-3 sm:grid-cols-2" data-testid="search-list">
            {group.items.map((row) => (
              <li key={row.global_entity_id}>
                <Link
                  href={row._href || "/knowledge"}
                  data-testid="search-item"
                  data-entity-type={row.entity_type}
                  className="card-base p-4 flex flex-col gap-2 h-full hover:border-stone-300 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-display font-bold text-ink text-[15px] leading-snug">
                      {row.canonical_name}
                    </span>
                    {isArticle(row)
                      ? <span className="chip bg-teal-50 text-teal-700 border border-teal-200 shrink-0">
                          {t("search.read", "Read")}
                        </span>
                      : <ConfidenceBadge confidence={row.confidence_score} />}
                  </div>

                  {isArticle(row) && row._summary && (
                    <p className="text-[12px] text-muted line-clamp-2">{row._summary}</p>
                  )}

                  {row._via && (
                    <p className="text-[11px] text-stone-400" data-testid="search-via">
                      {t("search.matched", "matched")} “{row._via}”
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
