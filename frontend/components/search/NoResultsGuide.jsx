"use client";
import Link from "next/link";
import RequestContentWidget from "@/components/RequestContentWidget";
import { useLanguage } from "@/lib/language";

export default function NoResultsGuide({ guidance, query, scopeLabel, mode = "empty" }) {
  const { t } = useLanguage();
  const { didYouMean = [], related = [], terms = [], resolved = null,
          planned = [] } = guidance || {};
  const hasSomething = didYouMean.length > 0 || related.length > 0;
  const empty = mode !== "thin";

  return (
    <div className="flex flex-col gap-6" data-testid="no-results" data-mode={mode}>
      {empty && (
      <div className="card-base p-5 sm:p-6 flex flex-col gap-2">
        <h2 className="font-display font-bold text-ink text-lg">
          {t("search.could_not_find", "We couldn’t find")} “{query}”{scopeLabel ? ` in ${scopeLabel}` : ""}
        </h2>
        {resolved && (
          <p className="text-[12px] text-stone-500" data-testid="no-results-resolved">
            {t("search.we_read_that_as", "We read that as")} <span className="font-display font-bold text-ink">{resolved}</span>.
          </p>
        )}
        <p className="text-sm text-muted">
          {hasSomething
            ? t("search.nearby_help", "That exact thing isn’t in our research yet. Here’s what is nearby — and if none of it helps, tell us and we’ll go and find it.")
            : t("search.add_to_list", "That isn’t in our research yet. Tell us what you were looking for and we’ll add it to the list — we read every one of these.")}
        </p>
      </div>
      )}

      {didYouMean.length > 0 && (
        <section data-testid="did-you-mean">
          <h3 className="font-display font-bold text-ink text-[15px] mb-2">{t("search.did_you_mean", "Did you mean")}</h3>
          <ul className="flex flex-col gap-2">
            {didYouMean.map((hit) => (
              <li key={hit.href}>
                <Link
                  href={hit.href}
                  data-testid="did-you-mean-item"
                  className="card-base px-4 py-3 min-h-[44px] flex items-center justify-between gap-3
                             hover:border-amber-300 transition-colors"
                >
                  <span className="font-display font-bold text-ink text-[14px]">{hit.name}</span>
                  <span className="text-[11px] text-stone-400 shrink-0">{hit.kind}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {related.map((group) => (
        <section key={group.id} data-testid="related-group" data-group={group.id}>
          <h3 className="font-display font-bold text-ink text-[15px] mb-2">
            {t("search.related", "Related")} {group.label.toLowerCase()}
          </h3>
          <ul className="grid gap-3 sm:grid-cols-2">
            {group.items.map((row) => (
              <li key={row.global_entity_id}>
                <Link
                  href={row._href || "/knowledge"}
                  data-testid="related-item"
                  className="card-base p-4 flex flex-col gap-1 h-full hover:border-stone-300 transition-colors"
                >
                  <span className="font-display font-bold text-ink text-[14px] leading-snug">
                    {row.canonical_name}
                  </span>
                  {row._via && (
                    <span className="text-[11px] text-stone-400">{t("search.matched", "matched")} “{row._via}”</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}

      {terms.length > 0 && (
        <section data-testid="search-suggestions">
          <h3 className="font-display font-bold text-ink text-[15px] mb-2">{t("search.try_searching", "Try searching")}</h3>
          <div className="flex flex-wrap gap-2">
            {terms.map((term) => (
              <Link
                key={term}
                href={`/knowledge?q=${encodeURIComponent(term)}`}
                className="chip bg-white text-stone-600 border border-stone-200
                           hover:border-amber-300 hover:bg-amber-50 transition-colors min-h-[44px]
                           inline-flex items-center"
              >
                {term}
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="card-base p-5 flex flex-col gap-3" data-testid="request-topic">
        <div>
          <h3 className="font-display font-bold text-ink text-[15px]">
            {empty
              ? t("search.request_topic_title", `Should we research “${query}”?`)
              : `Want more on “${query}”?`}
          </h3>
          <p className="text-sm text-muted mt-1">
            {t("search.request_topic_desc", "Ask for it and we will look into it. This is how most of what is on ValueWeave got here.")}
          </p>
        </div>
        <RequestContentWidget
          defaultType="research"
          prefillTitle={query}
          buttonLabel={t("search.request_topic_btn", "Request this topic")}
          compact
        />
      </section>

      {planned.length > 0 && (
        <p className="text-[12px] text-muted" data-testid="planned-sources">
          {t("search.coming_soon", "Coming to search soon:")} {planned.join(" · ")}.
        </p>
      )}

      <Link href="/knowledge" className="text-sm font-display font-bold text-amber-700 w-fit">
        {t("search.browse_all_researched", "Or browse everything we have researched →")}
      </Link>
    </div>
  );
}
