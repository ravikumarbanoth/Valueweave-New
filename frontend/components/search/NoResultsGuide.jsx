// What a mentor says when the answer is "we don't have that".
//
// THE DEFECT THIS FIXES
// ---------------------
// Reported from manual testing: "if no search result exists, the UI currently
// appears unresponsive". It was not unresponsive — it rendered a centred
// sentence saying nothing was found — but the reader cannot tell those apart,
// and either way the session ends there. A dead end on a platform whose whole
// promise is "we will point you somewhere" is the worst screen it has.
//
// THE QUESTION THIS PAGE IS BUILT AROUND
// --------------------------------------
// If a knowledgeable friend were sitting next to this student, what would they
// say next? Not "no results". They would say four things, in this order:
//
//   1  "Did you mean X?"          — because it is usually a spelling
//   2  "We don't cover that yet"  — plainly, once, without apologising twice
//   3  "Here is what we do have"  — actual rows, near the thing you asked for
//   4  "Tell us and we'll look"   — because the gap is ours, not theirs
//
// Every link offered is checked against the index before it is rendered (see
// `guidance` in lib/search/universal.js). A suggestion that leads to a second
// empty page is worse than no suggestion — that rule is from Phase 4 and this
// screen is where it matters most.
import Link from "next/link";
import RequestContentWidget from "@/components/RequestContentWidget";

// `mode` is "empty" when the query found nothing and "thin" when it found one
// or two rows. The difference is the first card: "We couldn't find Medak" is
// false and insulting on a page that just showed the reader Medak. In thin
// mode the caller has already written the honest sentence — "that is all we
// have researched on this so far" — and this renders only the ways out.
export default function NoResultsGuide({ guidance, query, scopeLabel, mode = "empty" }) {
  const { didYouMean = [], related = [], terms = [], resolved = null,
          planned = [] } = guidance || {};
  const hasSomething = didYouMean.length > 0 || related.length > 0;
  const empty = mode !== "thin";

  return (
    <div className="flex flex-col gap-6" data-testid="no-results" data-mode={mode}>
      {empty && (
      <div className="card-base p-5 sm:p-6 flex flex-col gap-2">
        <h2 className="font-display font-bold text-ink text-lg">
          We couldn’t find “{query}”{scopeLabel ? ` in ${scopeLabel}` : ""}
        </h2>
        {resolved && (
          <p className="text-[12px] text-stone-500" data-testid="no-results-resolved">
            We read that as <span className="font-display font-bold text-ink">{resolved}</span>.
          </p>
        )}
        <p className="text-sm text-muted">
          {hasSomething
            ? "That exact thing isn’t in our research yet. Here’s what is nearby — and if none of it helps, tell us and we’ll go and find it."
            : "That isn’t in our research yet. Tell us what you were looking for and we’ll add it to the list — we read every one of these."}
        </p>
      </div>
      )}

      {/* 1. Usually it is a spelling. Offer the correction before anything
             else, because if this is the answer nothing below matters. */}
      {didYouMean.length > 0 && (
        <section data-testid="did-you-mean">
          <h3 className="font-display font-bold text-ink text-[15px] mb-2">Did you mean</h3>
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

      {/* 3. Actual rows, grouped and labelled with the word that reached them,
             so "related" is a claim the reader can check rather than trust. */}
      {related.map((group) => (
        <section key={group.id} data-testid="related-group" data-group={group.id}>
          <h3 className="font-display font-bold text-ink text-[15px] mb-2">
            Related {group.label.toLowerCase()}
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
                    <span className="text-[11px] text-stone-400">matched “{row._via}”</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}

      {terms.length > 0 && (
        <section data-testid="search-suggestions">
          <h3 className="font-display font-bold text-ink text-[15px] mb-2">Try searching</h3>
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

      {/* 4. The gap is ours. Asking costs one tap and the request lands in the
             same queue the research team already works from. */}
      <section className="card-base p-5 flex flex-col gap-3" data-testid="request-topic">
        <div>
          <h3 className="font-display font-bold text-ink text-[15px]">
            {empty
              ? `Should we research “${query}”?`
              : `Want more on “${query}”?`}
          </h3>
          <p className="text-sm text-muted mt-1">
            Ask for it and we will look into it. This is how most of what is on
            ValueWeave got here.
          </p>
        </div>
        <RequestContentWidget
          defaultType="research"
          prefillTitle={query}
          buttonLabel="Request this topic"
          compact
        />
      </section>

      {/* Named, so a reader who searched for a mentor learns that mentors are
          coming rather than concluding the platform is empty. This list is the
          source registry — it cannot drift from what search actually covers. */}
      {planned.length > 0 && (
        <p className="text-[12px] text-muted" data-testid="planned-sources">
          Coming to search soon: {planned.join(" · ")}.
        </p>
      )}

      <Link href="/knowledge" className="text-sm font-display font-bold text-amber-700 w-fit">
        Or browse everything we have researched →
      </Link>
    </div>
  );
}
